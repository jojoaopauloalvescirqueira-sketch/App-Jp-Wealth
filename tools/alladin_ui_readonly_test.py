#!/usr/bin/env python3
"""Alladin C3-S1 — superficie cadastral READ-ONLY (UI-A..UI-F congelados).

Contratos provados:
  A rota; B exatamente 4 destinos locais; C default Instrumentos; D cadastro C2
  real renderizado; E empty states TEXTUAIS; F varredura economica (nenhum
  montante, zero, %, saldo, patrimonio...); G zero save(); H S byte-identico;
  I storage byte-identico; J READ_ONLY (banner + projecao sem normalizar);
  K recordStatus/lifecycleStatus; L teclado + mobile; M/S1-T trocas repetidas
  sem crescimento de DOM e sem escrita; N refresh nao materializa via UI;
  S1-P snapshots desacoplados (mutacao no DTO nao alcanca S.alladin);
  S1-Q agregado ausente => leitura vazia SEM materializar;
  S1-R schema futuro: projeta so campos conhecidos, agregado byte-identico;
  S1-S "Caixa" e cadastro, nunca dinheiro.

Proibicao economica (UI): nada de R$, $, 0,00, %, saldo, quantidade, preco,
custo, patrimonio, rentabilidade, posicao, P&L — nem como zero. Excecao
DOCUMENTADA: percentual cadastral de ownership (owners.shareBp) seria legitimo
se exibido; a apresentacao S1 nao o exibe, entao a varredura proibe % sem
excecao ativa. Se o S2 exibir ownership, marcar a celula com
data-ald-ownership e ajustar a varredura AQUI, nunca afrouxar globalmente.
"""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import os
import re
import socket
import sys
import threading

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)

LSKEY = "jpwealth_v9_state"
FIXTURE = json.loads((ROOT / "tools/fixtures/alladin_v2.json").read_text(encoding="utf-8"))["alladin"]
FUTURO = {
    "schemaVersion": 5,
    "reportingCurrency": "BRL",
    "instruments": [{"instrumentId": "aldi_v3", "name": "Do Futuro", "campoDesconhecido": {"x": 1},
                     "recordStatus": "ACTIVE"}],
    "assets": [], "accounts": [], "cashAccounts": [],
    "colecaoNova": [{"id": 1}],
}

PROIBIDO_ECONOMICO = re.compile(
    r"R\$|US\$|(?<![\w])\$\s?\d|\d,\d\d(?!\d)|%|saldo|patrim[oô]nio|quantidade|"
    r"pre[cç]o|custo|rentabilidade|posi[cç][aã]o|P&L|valor atual|carteira",
    re.IGNORECASE)


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


def serve():
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    server = ThreadingHTTPServer(("127.0.0.1", port), QuietHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{port}/index.html"


PRONTO = "() => typeof S === 'object' && typeof save === 'function' && window.JPWAlladinUI && window.JPWAlladin"
CONTEXTOS = []


def abrir(browser, url, viewport=None):
    # QA-D1: Service Worker BLOQUEADO no contexto. Esta suite testa a superficie
    # read-only do Alladin, e o SW (que tem suite propria: service-worker-upgrade)
    # abria um tunel por baixo do page.route apos reload — fetches do boot
    # (updateFxRates) escapavam do stub, recebiam cotacao REAL, salvavam, e o
    # caso N acusava a superficie por uma escrita que nao era dela. Bloquear o
    # SW garante que TODA rede passe pelo stub do harness; nao esconde write
    # nenhum originado pelo Alladin — o caso N continua comparando o documento
    # inteiro byte a byte.
    ctx = browser.new_context(viewport=viewport or {"width": 1440, "height": 900},
                              service_workers="block")
    CONTEXTOS.append(ctx)
    ctx.add_init_script("window.__onbShown=true;")
    page = ctx.new_page()
    erros = []
    page.on("pageerror", lambda e: erros.append(str(e)))
    page.route(
        "**/*",
        lambda route: route.continue_() if "127.0.0.1" in route.request.url
        else route.fulfill(status=200, content_type="application/json", body="{}"),
    )
    page.goto(url, wait_until="load")
    page.wait_for_function(PRONTO)
    page.wait_for_timeout(400)
    page.evaluate("() => { window.alert=()=>{}; closeModal(); }")
    return ctx, page, erros


def texto_section(page):
    return page.evaluate("() => document.getElementById('alladin').innerText")


def executar(falhas, nome, fn):
    try:
        fn()
    except Exception as exc:
        falhas.append(f"{nome}: excecao na sonda — {exc}")


def main() -> int:
    servidor, url = serve()
    falhas: list[str] = []
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()

            # ---- A/B/C/D/K + G/H/I + M/S1-T: pagina povoada ----
            def povoada():
                ctx, page, erros = abrir(browser, url)
                page.evaluate("(a) => { S.alladin = a; save(); }", FIXTURE)
                s_antes = page.evaluate("() => JSON.stringify(S)")
                disco_antes = page.evaluate("() => JSON.stringify(Object.keys(localStorage).sort().map(k => [k, localStorage.getItem(k)]))")
                r = page.evaluate("""() => {
                    let saves=0; const orig=window.save;
                    window.save=function(){ saves++; return orig.apply(this,arguments); };
                    navigateToScreen('alladin');
                    const out={ ativo: document.querySelector('.screen.active').id };
                    const tabs=[...document.querySelectorAll('#alladinTabs button[data-alladin-view]')];
                    out.destinos=tabs.map(b=>b.textContent.trim());
                    out.defaultVisivel=!document.getElementById('alladinInstruments').hidden;
                    out.outrosOcultos=['alladinAssets','alladinAccounts','alladinCash']
                        .every(id=>document.getElementById(id).hidden);
                    // percorre as 4 views duas vezes (M/S1-T) medindo DOM
                    const texto={};
                    // Os paineis retem o HTML da ultima render: a 1a volta PREENCHE as
                    // quatro views (crescimento legitimo). O invariante e estabilidade
                    // ENTRE voltas repetidas: volta 2 e volta 3 identicas.
                    const porVolta=[];
                    for(let volta=0; volta<3; volta++){
                      ['instruments','assets','accounts','cashAccounts'].forEach(v=>{
                        JPWAlladinUI.selectView(v);
                        if(volta===0) texto[v]=document.querySelector('[data-alladin-panel='+JSON.stringify(v)+']').innerText;
                      });
                      porVolta.push(document.getElementById('alladin').querySelectorAll('*').length);
                    }
                    const nosMin=porVolta[1], nosMax=porVolta[2];
                    JPWAlladinUI.selectView('instruments');
                    window.save=orig;
                    return { ...out, texto, saves, nosMax, nosMin };
                }""")
                if r["ativo"] != "alladin":
                    falhas.append(f"A: rota alladin nao ativou a section ({r['ativo']})")
                if r["destinos"] != ["Instrumentos", "Bens", "Contas", "Caixa"]:
                    falhas.append(f"B: destinos locais divergem do congelado: {r['destinos']}")
                if not (r["defaultVisivel"] and r["outrosOcultos"]):
                    falhas.append("C: default nao e Instrumentos com os demais ocultos")
                t = r["texto"]
                if not ("PETR4" in t["instruments"] and "Petrobras PN" in t["instruments"]
                        and "EQUITY_LIKE" in t["instruments"] and "BRL" in t["instruments"]):
                    falhas.append(f"D: Instrumentos nao renderizou o cadastro real ({t['instruments'][:90]!r})")
                if not ("Apartamento" in t["assets"] and "IMOVEL" in t["assets"] and "MORADIA" in t["assets"]):
                    falhas.append("D: Bens nao renderizou o cadastro real")
                if not ("Corretora Sintetica CCTVM" in t["accounts"] and "BROKERAGE" in t["accounts"]):
                    falhas.append("D: Contas nao renderizou o cadastro real")
                if not ("BRL" in t["cashAccounts"] and "Corretora Sintetica" in t["cashAccounts"]):
                    falhas.append("D: Caixa nao resolveu a conta-mae do snapshot")
                if "Inativo" not in t["instruments"]:
                    falhas.append("K: recordStatus INACTIVE (USDT) nao renderizado como Inativo")
                if "Ativo · Em uso" not in t["assets"]:
                    falhas.append("K: os dois eixos de status do bem nao renderizados")
                if r["saves"] != 0:
                    falhas.append(f"G: abrir/trocar/renderizar chamou save() {r['saves']}x")
                if page.evaluate("() => JSON.stringify(S)") != s_antes:
                    falhas.append("H: S mudou apos uso da superficie")
                disco_depois = page.evaluate("() => JSON.stringify(Object.keys(localStorage).sort().map(k => [k, localStorage.getItem(k)]))")
                if disco_depois != disco_antes:
                    falhas.append("I: storage mudou apos uso da superficie")
                if r["nosMax"] != r["nosMin"]:
                    falhas.append(f"M: DOM instavel entre voltas repetidas (v2={r['nosMin']} v3={r['nosMax']})")
                secao = texto_section(page)
                m = PROIBIDO_ECONOMICO.search(secao)
                if m:
                    falhas.append(f"F (povoada): conteudo economico proibido no DOM: {m.group(0)!r}")
                if erros:
                    falhas.append(f"povoada pageerror: {erros}")
            executar(falhas, "povoada", povoada)

            # ---- E/F: base sem cadastro => empty states textuais ----
            def vazia():
                ctx, page, erros = abrir(browser, url)
                page.evaluate("""() => {
                    navigateToScreen('alladin');
                    ['instruments','assets','accounts','cashAccounts'].forEach(v=>JPWAlladinUI.selectView(v));
                    JPWAlladinUI.selectView('instruments');
                }""")
                secao = texto_section(page)
                for frase in ("Nenhum instrumento cadastrado.",):
                    if frase not in secao:
                        falhas.append(f"E: empty state textual ausente ({frase!r})")
                for v, frase in (("assets", "Nenhum bem cadastrado."),
                                 ("accounts", "Nenhuma conta cadastrada."),
                                 ("cashAccounts", "Nenhuma conta de caixa cadastrada.")):
                    tem = page.evaluate("(arg) => { JPWAlladinUI.selectView(arg); return document.getElementById('alladin').innerText; }", v)
                    if frase not in tem:
                        falhas.append(f"E: empty state de {v} ausente")
                m = PROIBIDO_ECONOMICO.search(texto_section(page))
                if m:
                    falhas.append(f"F (vazia): conteudo economico proibido: {m.group(0)!r}")
                if erros:
                    falhas.append(f"vazia pageerror: {erros}")
            executar(falhas, "vazia", vazia)

            # ---- J + S1-R: schema futuro ----
            def read_only():
                ctx, page, erros = abrir(browser, url)
                page.evaluate("(a) => { S.alladin = a; localStorage.setItem('%s', JSON.stringify(S)); }" % LSKEY, FUTURO)
                raw_antes = page.evaluate("() => localStorage.getItem('%s')" % LSKEY)
                mem_antes = page.evaluate("() => JSON.stringify(S.alladin)")
                r = page.evaluate("""() => {
                    navigateToScreen('alladin');
                    JPWAlladinUI.selectView('instruments');
                    const banner=document.getElementById('alladinReadOnlyBanner');
                    const dto=JPWAlladin.leitura.instruments()[0]||{};
                    return { bannerVisivel: !banner.hidden, bannerTexto: banner.textContent,
                             temDesconhecido: Object.prototype.hasOwnProperty.call(dto,'campoDesconhecido'),
                             nome: dto.name,
                             painel: document.getElementById('alladinInstruments').innerText };
                }""")
                if not r["bannerVisivel"] or "somente-leitura" not in r["bannerTexto"] \
                        or "podem ser consultados, mas não alterados" not in r["bannerTexto"]:
                    falhas.append(f"J: banner READ_ONLY ausente/texto errado ({r['bannerTexto'][:80]!r})")
                if r["temDesconhecido"]:
                    falhas.append("S1-R: o read-model PROJETOU campo desconhecido do schema futuro")
                if r["nome"] != "Do Futuro" or "Do Futuro" not in r["painel"]:
                    falhas.append("J: campos conhecidos do agregado futuro nao consultaveis")
                if page.evaluate("() => JSON.stringify(S.alladin)") != mem_antes:
                    falhas.append("S1-R: o agregado em memoria foi alterado (normalizacao indevida)")
                if page.evaluate("() => localStorage.getItem('%s')" % LSKEY) != raw_antes:
                    falhas.append("S1-R: o agregado no disco deixou de ser byte-identico")
                if erros:
                    falhas.append(f"read_only pageerror: {erros}")
            executar(falhas, "read_only", read_only)

            # ---- S1-P: snapshots desacoplados ----
            def desacoplado():
                ctx, page, erros = abrir(browser, url)
                page.evaluate("(a) => { S.alladin = a; save(); }", FIXTURE)
                r = page.evaluate("""() => {
                    const antes=JSON.stringify(S.alladin);
                    const insts=JPWAlladin.leitura.instruments();
                    const ativos=JPWAlladin.leitura.assets();
                    const tentativas=[];
                    try{ insts.push({instrumentId:'x'}); }catch(e){ tentativas.push('push-lista'); }
                    try{ insts[0].name='HACK'; }catch(e){ tentativas.push('campo'); }
                    try{ insts[0].symbolHistory.push({symbol:'HACK'}); }catch(e){ tentativas.push('symbolHistory'); }
                    try{ insts[0].externalIdentifiers.isin='HACK'; }catch(e){ tentativas.push('externalIdentifiers'); }
                    try{ ativos[0].owners[0].name='HACK'; }catch(e){ tentativas.push('owners'); }
                    try{ ativos[0].tags.push('HACK'); }catch(e){ tentativas.push('tags'); }
                    // Desacoplamento REAL exige duas coisas alem de "o hack nao vazou":
                    // (1) o DTO nao e o registro vivo (identidade de referencia);
                    // (2) ler NUNCA congela o agregado real — um read-model sem clone
                    //     que congela referencias vivas tornaria o dominio imutavel
                    //     em silencio (aldMutate falharia dali em diante).
                    const vivo=S.alladin.instruments[0];
                    return { intacto: JSON.stringify(S.alladin)===antes,
                             vazouHack: JSON.stringify(S.alladin).includes('HACK'),
                             mesmaReferencia: insts[0]===vivo,
                             congelouVivo: Object.isFrozen(vivo)
                               || Object.isFrozen(vivo.symbolHistory)
                               || Object.isFrozen(vivo.externalIdentifiers)
                               || Object.isFrozen(S.alladin.assets[0].owners)
                               || Object.isFrozen(S.alladin.assets[0].tags)
                               || Object.isFrozen(S.alladin.instruments) };
                }""")
                if not r["intacto"] or r["vazouHack"]:
                    falhas.append(f"S1-P: mutacao no snapshot ALCANCOU S.alladin ({r})")
                if r["mesmaReferencia"]:
                    falhas.append("S1-P: o read-model devolveu a REFERENCIA VIVA do agregado")
                if r["congelouVivo"]:
                    falhas.append("S1-P: a leitura CONGELOU o agregado real — o dominio ficaria imutavel")
            executar(falhas, "S1-P", desacoplado)

            # ---- S1-Q + N: ausencia nao materializa; refresh nao escreve ----
            def ausente():
                ctx, page, erros = abrir(browser, url)
                r = page.evaluate("""() => {
                    delete S.alladin;
                    const lidos={ i: JPWAlladin.leitura.instruments().length,
                                  a: JPWAlladin.leitura.assets().length };
                    navigateToScreen('alladin');
                    ['instruments','assets','accounts','cashAccounts'].forEach(v=>JPWAlladinUI.selectView(v));
                    return { ...lidos, aindaAusente: !('alladin' in S) };
                }""")
                if r["i"] != 0 or r["a"] != 0:
                    falhas.append(f"S1-Q: leitura com agregado ausente nao veio vazia ({r})")
                if not r["aindaAusente"]:
                    falhas.append("S1-Q/M6: abrir a superficie MATERIALIZOU S.alladin")
                # N: pos-reload (o migrate do load repoe o default — isso e do boot,
                # nao da UI), usar a superficie nao pode reescrever o disco.
                page.evaluate("() => save()")
                page.reload(wait_until="load")
                page.wait_for_function(PRONTO)
                page.wait_for_timeout(400)
                raw = page.evaluate("() => localStorage.getItem('%s')" % LSKEY)
                page.evaluate("""() => {
                    window.alert=()=>{}; closeModal();
                    navigateToScreen('alladin');
                    ['instruments','assets','accounts','cashAccounts'].forEach(v=>JPWAlladinUI.selectView(v));
                }""")
                if page.evaluate("() => localStorage.getItem('%s')" % LSKEY) != raw:
                    falhas.append("N: usar a superficie apos refresh REESCREVEU o disco")
                if erros:
                    falhas.append(f"ausente pageerror: {erros}")
            executar(falhas, "S1-Q/N", ausente)

            # ---- S1-S: Caixa e cadastro, nunca dinheiro ----
            def caixa():
                ctx, page, erros = abrir(browser, url)
                page.evaluate("(a) => { S.alladin = a; save(); }", FIXTURE)
                painel = page.evaluate("""() => {
                    navigateToScreen('alladin');
                    JPWAlladinUI.selectView('cashAccounts');
                    return document.getElementById('alladinCash').innerText;
                }""")
                m = PROIBIDO_ECONOMICO.search(painel)
                if m:
                    falhas.append(f"S1-S: a view Caixa contem conteudo monetario: {m.group(0)!r}")
                if "Conta-mãe" not in painel or "BRL" not in painel:
                    falhas.append("S1-S: Caixa nao apresenta o cadastro esperado (moeda + conta-mae)")
            executar(falhas, "S1-S", caixa)

            # ---- L: teclado + mobile ----
            def acessibilidade():
                ctx, page, erros = abrir(browser, url, viewport={"width": 390, "height": 844})
                page.evaluate("(a) => { S.alladin = a; save(); navigateToScreen('alladin'); }", FIXTURE)
                page.evaluate("() => document.querySelector('#alladinTabs button[data-alladin-view=assets]').focus()")
                page.keyboard.press("Enter")
                page.wait_for_timeout(150)
                r = page.evaluate("""() => ({
                    bensVisivel: !document.getElementById('alladinAssets').hidden,
                    aria: document.querySelector('#alladinTabs button[data-alladin-view=assets]').getAttribute('aria-pressed'),
                    scroll: !!document.querySelector('#alladinAssets .jp-table-scroll'),
                    larguraOk: document.getElementById('alladin').scrollWidth <= (window.innerWidth + 2) })""")
                if not r["bensVisivel"] or r["aria"] != "true":
                    falhas.append(f"L: ativacao por teclado nao trocou a view ({r})")
                if not r["scroll"]:
                    falhas.append("L: tabela sem contencao de scroll no mobile")
                if not r["larguraOk"]:
                    falhas.append("L: a section estoura a largura do viewport mobile")
                if erros:
                    falhas.append(f"L pageerror: {erros}")
            executar(falhas, "L", acessibilidade)

            browser.close()
    finally:
        for ctx in CONTEXTOS:
            try:
                ctx.close()
            except Exception:
                pass
        servidor.shutdown()

    if falhas:
        print("ALLADIN UI READONLY TEST FALHOU")
        for f in falhas:
            print("  - " + f)
        return 1
    print("ALLADIN UI READONLY TEST PASS (A-O + S1-P..S1-T: rota, 4 destinos, default Instrumentos, "
          "cadastro C2 real, empty states textuais, zero conteudo economico, zero save(), S e storage "
          "byte-identicos, READ_ONLY com projecao sem normalizar, snapshots desacoplados, ausencia nao "
          "materializa, refresh nao escreve, Caixa cadastral, teclado/mobile, DOM estavel)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
