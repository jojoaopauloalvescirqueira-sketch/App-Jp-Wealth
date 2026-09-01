#!/usr/bin/env python3
"""Alladin ALD-05-S1 — superficie ECONOMICA read-only (Lancamentos/Saldos/Posicoes).

A primeira superficie que exibe numero economico do Alladin. O contrato que esta
suite defende nao e "a tela mostra os dados" — e que ela NUNCA mostre um estado
tranquilizador sobre dado que o dominio recusou.

  E1  sete destinos: os quatro cadastrais intactos (rotulo e ordem) + os tres novos
  E2  alladinView continua efemero — trocar de painel nao persiste nada
  E3  Lancamentos: ordem IDENTICA a do read-model (a UI nao reordena)
  E4  Lancamentos: os dez eventTypes renderizados com rotulo do contrato
  E5  ADJUSTMENT: reason VISIVEL (e o unico que torna o ajuste auditavel)
  E6  effectiveAt E recordedAt visiveis; recordedAt jamais em title/tooltip
  E7  TRANSFER mostra as DUAS pernas, e caixas homonimas sao desambiguadas
  E8  REVERSAL e original ambos visiveis; original marcado Estornado
  E9  Saldos: valor exibido == saldoDeCaixa(); zero soma na UI
  E10 Posicoes: quantity VERBATIM — negativa fiel, >64 chars integra
  E11 BLOCKING x EMPTY (o par decisivo, nos dois sentidos)
  E12 vetores de corrupcao: id duplicado, ilegivel, schema futuro, orfao, moeda,
      container nao-array — todos bloqueiam ledger E posicoes
  E12b fronteira do sentinela: moeda divergente SO-CAIXA nao e vista por ele,
      e quem acusa e a linha de Saldos — provado, nao suposto
  E13 a sentinela impede projetar ledger silenciosamente filtrado (MD-2/A)
  E14 zero save(), S e localStorage byte-identicos
  E15 zero conteudo economico nos quatro paineis CADASTRAIS
  E16 acessibilidade: role/aria-label/aria-pressed, teclado, sem cor sozinha

Por que E11 e o caso central: `positions:[]` sob BLOCKING e `positions:[]` sob
agregado legitimamente vazio sao a MESMA estrutura de dados. Se a UI nao olhar
`available` antes, os dois viram a mesma tela — e "Nenhuma posicao em aberto"
sobre um agregado corrompido e uma mentira tranquilizadora. O caso prova os dois
sentidos: sem o controle do agregado vazio, um render que bloqueia sempre
passaria; sem o corrompido, um render que nunca bloqueia passaria.
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
PRONTO = ("() => typeof S === 'object' && typeof save === 'function' "
          "&& window.JPWAlladinUI && window.JPWAlladin")

DESTINOS = ["Instrumentos", "Bens", "Contas", "Caixa", "Lançamentos", "Saldos", "Posições"]
CADASTRAIS = ["instruments", "assets", "accounts", "cashAccounts"]
ECONOMICOS = ["ledger", "balances", "positions"]

# Varredura economica que continua valendo NOS PAINEIS CADASTRAIS (MD-1: o
# contrato foi re-escopado, nao removido — a cobertura ficou mais forte, porque
# agora existe conteudo economico no MESMO section que ela poderia vazar).
PROIBIDO_ECONOMICO = re.compile(
    r"R\$|US\$|(?<![\w])\$\s?\d|\d,\d\d(?!\d)|%|saldo|patrim[oô]nio|quantidade|"
    r"pre[cç]o|custo|rentabilidade|posi[cç][aã]o|P&L|valor atual|carteira",
    re.IGNORECASE)

# Textos de EMPTY: sob BLOCKING nenhum deles pode aparecer.
EMPTY_ECONOMICO = ("Nenhum lançamento registrado.", "Nenhuma posição em aberto.")


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


CONTEXTOS = []


def abrir(browser, url, viewport=None):
    # QA-D1: Service Worker BLOQUEADO — sem isso os fetches do boot escapam do
    # page.route apos reload, salvam por conta propria e contaminam as
    # comparacoes byte-a-byte de E14.
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


# Fixture economica montada PELO DOMINIO (nunca escrita a mao no agregado): se o
# dominio recusasse algum lancamento, a suite mediria outra coisa.
SEMEAR = """() => {
  const c=JPWAlladin.cadastro, L=JPWAlladin.ledger;
  const xp=c.addAccount({name:'XP',institution:'XP',accountType:'BROKERAGE'}).recordId;
  const btg=c.addAccount({name:'BTG',institution:'BTG',accountType:'BROKERAGE'}).recordId;
  const cx=c.addCashAccount({accountId:xp,currency:'BRL'}).recordId;
  const cy=c.addCashAccount({accountId:xp,currency:'BRL'}).recordId;   // HOMONIMA de cx
  const cb=c.addCashAccount({accountId:btg,currency:'BRL'}).recordId;
  const pe=c.addInstrument({name:'Petrobras PN',symbol:'PETR4',currency:'BRL',
    instrumentFamily:'EQUITY_LIKE',assetClass:'RENDA_VARIAVEL'}).recordId;
  L.addTransaction({eventType:'DEPOSIT',cashAccountId:cx,amount:100000,effectiveAt:'2026-01-10'});
  L.addTransaction({eventType:'WITHDRAWAL',cashAccountId:cx,amount:500,effectiveAt:'2026-01-11'});
  L.addTransaction({eventType:'TRANSFER',sourceCashAccountId:cx,destinationCashAccountId:cy,
    amount:1000,effectiveAt:'2026-01-12',flowScope:'INTERNAL'});
  L.addTransaction({eventType:'BUY',cashAccountId:cx,instrumentId:pe,quantity:'10',
    amount:30000,fees:100,taxes:50,effectiveAt:'2026-01-13'});
  L.addTransaction({eventType:'SELL',cashAccountId:cx,instrumentId:pe,quantity:'4',
    amount:14000,fees:80,taxes:20,effectiveAt:'2026-01-14'});
  L.addTransaction({eventType:'FEE',cashAccountId:cx,amount:1500,effectiveAt:'2026-01-15'});
  L.addTransaction({eventType:'TAX',cashAccountId:cx,amount:700,effectiveAt:'2026-01-16'});
  const aj=L.addTransaction({eventType:'ADJUSTMENT_CREDIT',cashAccountId:cx,amount:250,
    effectiveAt:'2026-01-17',reason:'diferenca de extrato conciliada'});
  L.addTransaction({eventType:'ADJUSTMENT_DEBIT',cashAccountId:cx,amount:90,
    effectiveAt:'2026-01-18',reason:'estorno de credito indevido do banco'});
  const rv=L.reverseTransaction(aj.recordId,{effectiveAt:'2026-01-19',reason:'conciliacao refeita'});
  JPWNavigation.navigate('alladin');
  return {xp,btg,cx,cy,cb,pe,aj:aj.recordId,rv:rv.recordId};
}"""


def ver(page, view):
    page.evaluate(f"() => JPWAlladinUI.selectView('{view}')")
    page.wait_for_timeout(150)
    return page.evaluate(
        "(v) => { const el=document.querySelector('[data-alladin-panel=\"'+v+'\"]');"
        " return el ? el.innerText : '<<painel ausente>>'; }", view)


def executar(falhas, nome, fn):
    try:
        fn()
    except Exception as exc:
        falhas.append(f"{nome}: excecao na sonda — {exc}")


def main() -> int:
    falhas: list[str] = []
    server, url = serve()
    with sync_playwright() as pw:
        browser = pw.chromium.launch()

        # ---- E1/E2: destinos e efemeridade -------------------------------
        def e1_e2():
            ctx, page, erros = abrir(browser, url)
            page.evaluate(SEMEAR)
            page.wait_for_timeout(300)
            r = page.evaluate("""() => {
              const bs=[...document.querySelectorAll('#alladinTabs button[data-alladin-view]')];
              return { rotulos: bs.map(b=>b.innerText.trim()),
                       chaves: bs.map(b=>b.dataset.alladinView),
                       paineis: [...document.querySelectorAll('[data-alladin-panel]')]
                                  .map(p=>p.dataset.alladinPanel) };
            }""")
            if r["rotulos"] != DESTINOS:
                falhas.append(f"E1: destinos divergem do contrato novo ({r['rotulos']})")
            if r["chaves"][:4] != CADASTRAIS:
                falhas.append(f"E1: destinos cadastrais mudaram de ordem/chave ({r['chaves'][:4]})")
            if r["chaves"][4:] != ECONOMICOS:
                falhas.append(f"E1: destinos economicos divergem ({r['chaves'][4:]})")
            if r["paineis"] != CADASTRAIS + ECONOMICOS:
                falhas.append(f"E1: paineis divergem ({r['paineis']})")
            # E2: selecionar painel economico nao persiste em lugar nenhum
            antes = page.evaluate("() => localStorage.getItem('%s')" % LSKEY)
            for v in ECONOMICOS:
                ver(page, v)
            depois = page.evaluate("() => localStorage.getItem('%s')" % LSKEY)
            bruto = page.evaluate("() => JSON.stringify(S)")
            if antes != depois:
                falhas.append("E2: trocar de painel economico ESCREVEU no storage")
            for v in ECONOMICOS:
                if ('"' + v + '"') in bruto and v != "positions":
                    pass  # chave homonima improvavel; a prova real e a de storage
            if erros:
                falhas.append(f"E1/E2: pageerror {erros}")
            ctx.close()
        executar(falhas, "E1/E2", e1_e2)

        # ---- E3..E8: projecao dos lancamentos ----------------------------
        def e3_e8():
            ctx, page, erros = abrir(browser, url)
            ids = page.evaluate(SEMEAR)
            page.wait_for_timeout(300)
            texto = ver(page, "ledger")
            # E3: ordem identica a do read-model — comparacao por effectiveAt
            ordem_dom = page.evaluate("""() => [...document.querySelectorAll(
                '[data-alladin-panel="ledger"] table tr')].slice(1)
                .map(tr => tr.children[0].innerText.split('\\n')[0].trim())""")
            ordem_rm = [t["effectiveAt"] for t in page.evaluate(
                "() => JPWAlladin.leitura.transactions().map(t=>({effectiveAt:t.effectiveAt}))")]
            if ordem_dom != ordem_rm:
                falhas.append(f"E3: a UI reordenou o ledger\n   dom={ordem_dom}\n   rm ={ordem_rm}")
            # E4: os dez tipos, com o rotulo do contrato
            for rotulo in ("Aporte", "Retirada", "Transferência", "Compra", "Venda",
                           "Taxa", "Imposto", "Ajuste (crédito)", "Ajuste (débito)",
                           "Estorno de Ajuste (crédito)"):
                if rotulo not in texto:
                    falhas.append(f"E4: rotulo ausente na projecao: {rotulo!r}")
            # E5: reason visivel (os dois ajustes)
            for motivo in ("diferenca de extrato conciliada", "estorno de credito indevido do banco"):
                if motivo not in texto:
                    falhas.append(f"E5: reason do ADJUSTMENT nao esta visivel: {motivo!r}")
            # E6: effectiveAt e recordedAt visiveis; recordedAt NUNCA em title
            if "2026-01-10" not in texto or "registrado em" not in texto:
                falhas.append("E6: effectiveAt/recordedAt nao estao ambos visiveis")
            titles = page.evaluate("""() => [...document.querySelectorAll(
                '[data-alladin-panel="ledger"] [title]')].map(e=>e.getAttribute('title'))""")
            if titles:
                falhas.append(f"E6: auditoria escondida em title/tooltip ({titles[:3]})")
            # E7: TRANSFER com duas pernas E caixas homonimas desambiguadas
            linha_tr = [l for l in texto.split("\n") if "→" in l]
            if not linha_tr:
                falhas.append("E7: TRANSFER nao mostrou as duas pernas")
            else:
                origem, _, destino = linha_tr[0].partition("→")
                if origem.strip() == destino.strip():
                    falhas.append(f"E7: caixas homonimas nao desambiguadas — "
                                  f"a transferencia se le como para si mesma ({linha_tr[0]!r})")
            # E8: reversal e original ambos visiveis; original Estornado
            if texto.count("Ajuste (crédito)") < 2:
                falhas.append("E8: original e estorno deveriam estar AMBOS visiveis")
            if "Estornado" not in texto:
                falhas.append("E8: o original revertido nao aparece como Estornado")
            if ids["aj"] not in texto and ids["rv"] not in texto:
                falhas.append("E8: o estorno nao referencia o original (reversalOf)")
            if erros:
                falhas.append(f"E3..E8: pageerror {erros}")
            ctx.close()
        executar(falhas, "E3..E8", e3_e8)

        # ---- E9: saldo exibido == saldoDeCaixa(), zero soma na UI ---------
        def e9():
            ctx, page, erros = abrir(browser, url)
            page.evaluate(SEMEAR)
            page.wait_for_timeout(300)
            ver(page, "balances")
            r = page.evaluate("""() => {
              const linhas=[...document.querySelectorAll('[data-alladin-panel="balances"] table tr')].slice(1);
              const dom=linhas.map(tr=>tr.children[1].innerText.trim());
              const rm=JPWAlladin.leitura.cashAccounts().map(c=>{
                const s=JPWAlladin.leitura.saldoDeCaixa(c.cashAccountId);
                return s.available ? JPWAlladin.money.format({amount:s.amount,currency:s.currency})
                                   : 'Indisponível';
              });
              return { dom, rm, rotulos:linhas.map(tr=>tr.children[0].innerText.trim()) };
            }""")
            if r["dom"] != r["rm"]:
                falhas.append(f"E9: saldo exibido diverge de saldoDeCaixa()\n   dom={r['dom']}\n   rm ={r['rm']}")
            if len(set(r["rotulos"])) != len(r["rotulos"]):
                falhas.append(f"E9: duas contas de caixa com rotulo IDENTICO ({r['rotulos']})")
            if erros:
                falhas.append(f"E9: pageerror {erros}")
            ctx.close()
        executar(falhas, "E9", e9)

        # ---- E10: quantity VERBATIM, negativa e longa ---------------------
        def e10():
            ctx, page, erros = abrir(browser, url)
            page.evaluate(SEMEAR)
            page.wait_for_timeout(300)
            # Dois casos que a ENTRADA nao consegue expressar sozinha:
            #  (a) negativo — so nasce vendendo alem da posicao;
            #  (b) string > 64 chars — o teto de 64 e do PAYLOAD de entrada, nao
            #      da verdade economica: o valor longo so aparece DERIVADO, aqui
            #      somando duas escalas distintas (50 digitos inteiros + 20 casas).
            # A forma canonica proibe zero final na fracao, entao toda quantity
            # abaixo termina em digito 1-9.
            r0 = page.evaluate("""() => {
              const c=JPWAlladin.cadastro, L=JPWAlladin.ledger;
              const cx=JPWAlladin.leitura.cashAccounts()[0].cashAccountId;
              const pe=JPWAlladin.leitura.instruments()[0].instrumentId;
              const gr=c.addInstrument({name:'Grande',symbol:'GRND',currency:'BRL',
                instrumentFamily:'EQUITY_LIKE',assetClass:'RENDA_VARIAVEL'}).recordId;
              const neg=L.addTransaction({eventType:'SELL',cashAccountId:cx,instrumentId:pe,
                quantity:'25',amount:100,effectiveAt:'2026-02-01'});
              const a=L.addTransaction({eventType:'BUY',cashAccountId:cx,instrumentId:gr,
                quantity:'99999999999999999999999999999999999999999999999999',
                amount:100,effectiveAt:'2026-02-02'});
              const b=L.addTransaction({eventType:'BUY',cashAccountId:cx,instrumentId:gr,
                quantity:'0.00000000000000000001',amount:100,effectiveAt:'2026-02-03'});
              return {neg:neg.ok, negErro:neg.erro, a:a.ok, aErro:a.erro, b:b.ok, bErro:b.erro};
            }""")
            for k in ("neg", "a", "b"):
                if not r0[k]:
                    falhas.append(f"E10: a sonda nao conseguiu semear o caso {k} "
                                  f"({r0.get(k+'Erro')!r}) — caso nao exercitado")
            page.wait_for_timeout(150)
            ver(page, "positions")
            r = page.evaluate("""() => {
              const linhas=[...document.querySelectorAll('[data-alladin-panel="positions"] table tr')].slice(1);
              return { dom: linhas.map(tr=>tr.children[2].innerText.trim()),
                       rm: JPWAlladin.leitura.posicoes().positions.map(p=>p.quantity),
                       texto: document.querySelector('[data-alladin-panel="positions"]').innerText };
            }""")
            if r["dom"] != r["rm"]:
                falhas.append(f"E10: quantity exibida NAO e a string do read-model\n"
                              f"   dom={r['dom']}\n   rm ={r['rm']}")
            neg = [q for q in r["rm"] if q.startswith("-")]
            if not neg:
                falhas.append("E10: a sonda nao produziu quantidade negativa — caso nao exercitado")
            elif neg[0] not in r["dom"]:
                falhas.append(f"E10: quantidade negativa nao foi preservada ({neg[0]!r})")
            for proibido in ("short", "vendido a descoberto", "erro", "inválid"):
                if proibido.lower() in r["texto"].lower():
                    falhas.append(f"E10: a UI inventou semantica para negativo ({proibido!r})")
            longas = [q for q in r["rm"] if len(q) > 64]
            if not longas:
                falhas.append(f"E10: a sonda nao produziu quantidade > 64 chars "
                              f"({[len(q) for q in r['rm']]}) — caso nao exercitado")
            elif longas[0] not in r["dom"]:
                falhas.append("E10: quantidade longa foi TRUNCADA na projecao — "
                              "cortar digito e inventar outro numero")
            if erros:
                falhas.append(f"E10: pageerror {erros}")
            ctx.close()
        executar(falhas, "E10", e10)

        # ---- E11: BLOCKING x EMPTY — o par decisivo, nos DOIS sentidos ----
        def e11():
            # (1) agregado legitimo e VAZIO => EMPTY, sem aviso de indisponibilidade
            ctx, page, erros = abrir(browser, url)
            page.evaluate("() => { JPWNavigation.navigate('alladin'); }")
            page.wait_for_timeout(200)
            vazio = {v: ver(page, v) for v in ECONOMICOS}
            if "Nenhum lançamento registrado." not in vazio["ledger"]:
                falhas.append(f"E11 vazio: ledger legitimo deveria mostrar EMPTY ({vazio['ledger'][:120]!r})")
            if "Nenhuma posição em aberto." not in vazio["positions"]:
                falhas.append(f"E11 vazio: posicoes legitimas deveriam mostrar EMPTY ({vazio['positions'][:120]!r})")
            for v, txt in vazio.items():
                if "indisponí" in txt.lower() or "integridade" in txt.lower():
                    falhas.append(f"E11 vazio: {v} acusou BLOCKING sobre agregado LEGITIMO ({txt[:120]!r})")
            ctx.close()

            # (2) agregado CORROMPIDO => BLOCKING, sem tabela, sem numero, sem EMPTY
            ctx, page, erros = abrir(browser, url)
            page.evaluate(SEMEAR)
            page.wait_for_timeout(250)
            page.evaluate("""() => {
              // transactionId duplicado: identidade ambigua (RT-H1)
              const t=S.alladin.transactions[0];
              S.alladin.transactions.push(JSON.parse(JSON.stringify(t)));
            }""")
            page.wait_for_timeout(50)
            corrompido = {v: ver(page, v) for v in ECONOMICOS}
            for v in ("ledger", "positions"):
                txt = corrompido[v]
                if "indisponí" not in txt.lower():
                    falhas.append(f"E11 corrompido: {v} NAO acusou indisponibilidade ({txt[:160]!r})")
                for e in EMPTY_ECONOMICO:
                    if e in txt:
                        falhas.append(f"E11 corrompido: {v} mostrou texto de EMPTY sob BLOCKING ({e!r})")
                if re.search(r"R\$|\d,\d\d", txt):
                    falhas.append(f"E11 corrompido: {v} exibiu NUMERO sob BLOCKING ({txt[:160]!r})")
            tabelas = page.evaluate("""() => ({
                ledger: document.querySelectorAll('[data-alladin-panel="ledger"] table').length,
                positions: document.querySelectorAll('[data-alladin-panel="positions"] table').length })""")
            if tabelas["ledger"] or tabelas["positions"]:
                falhas.append(f"E11 corrompido: tabela economica renderizada sob BLOCKING ({tabelas})")
            if erros:
                falhas.append(f"E11: pageerror {erros}")
            ctx.close()
        executar(falhas, "E11", e11)

        # ---- E12: vetores de corrupcao, um a um --------------------------
        def e12():
            vetores = {
                "id_duplicado": "S.alladin.transactions.push(JSON.parse(JSON.stringify(S.alladin.transactions[0])));",
                "registro_ilegivel": "S.alladin.transactions[0].amount = -1;",
                "schema_futuro": "S.alladin.schemaVersion = 7;",
                "cadastro_orfao": "S.alladin.cashAccounts.length = 0;",
                # A guarda de moeda de aldPosicoes compara trade x caixa x
                # instrumento — ela existe onde ha PAPEL. Num registro so-caixa
                # a divergencia e apanhada por saldoDeCaixa, nao pelo sentinela;
                # ver o caso E12b, que cobre exatamente essa fronteira.
                "moeda_divergente_trade":
                    "S.alladin.transactions.find(t=>t.eventType==='BUY').currency='USD';",
                "container_nao_array": "S.alladin.transactions = {};",
            }
            for nome, mutacao in vetores.items():
                ctx, page, erros = abrir(browser, url)
                page.evaluate(SEMEAR)
                page.wait_for_timeout(250)
                page.evaluate("() => { %s }" % mutacao)
                page.wait_for_timeout(50)
                for v in ("ledger", "positions"):
                    txt = ver(page, v)
                    if "indisponí" not in txt.lower():
                        falhas.append(f"E12 [{nome}] {v}: corrupcao NAO bloqueou a projecao ({txt[:130]!r})")
                    for e in EMPTY_ECONOMICO:
                        if e in txt:
                            falhas.append(f"E12 [{nome}] {v}: EMPTY exibido sob corrupcao")
                if erros:
                    falhas.append(f"E12 [{nome}]: pageerror {erros}")
                ctx.close()
        executar(falhas, "E12", e12)

        # ---- E12b: a FRONTEIRA de cobertura do sentinela, provada ----------
        # A guarda de moeda de aldPosicoes compara trade x caixa x instrumento —
        # ela so existe onde ha PAPEL. Num registro SO-CAIXA (um DEPOSIT com
        # moeda divergente) o sentinela NAO ve, e Lancamentos continua
        # projetando. Isso e correto e nao produz numero falso: Lancamentos
        # exibe FATOS (tipo, magnitude, contas), e quem fica indigno de
        # confianca e o SALDO — que a tela de Saldos marca Indisponivel naquela
        # linha. Este caso fixa a fronteira: se um dia Lancamentos passar a
        # exibir numero derivado, ela deixa de bastar.
        def e12b():
            ctx, page, erros = abrir(browser, url)
            page.evaluate(SEMEAR)
            page.wait_for_timeout(250)
            r = page.evaluate("""() => {
              const dep=S.alladin.transactions.find(t=>t.eventType==='DEPOSIT');
              dep.currency='USD';
              const cx=dep.cashAccountId;
              return { sentinela: JPWAlladin.leitura.posicoes().available,
                       saldo: JPWAlladin.leitura.saldoDeCaixa(cx).available,
                       issues: JPWAlladin.leitura.saldoDeCaixa(cx).issues };
            }""")
            if not r["sentinela"]:
                falhas.append("E12b: a fronteira mudou — o sentinela passou a ver moeda "
                              "divergente so-caixa; reavaliar o desenho e esta prova")
            if r["saldo"]:
                falhas.append(f"E12b: saldoDeCaixa NAO bloqueou moeda divergente so-caixa ({r})")
            ver(page, "balances")
            # A verificacao e POR LINHA, nao pela tela: uma conta de caixa SEM
            # lancamento tem saldo LEGITIMO de R$ 0,00, e proibir todo zero
            # apagaria um fato verdadeiro. O que nao pode existir e zero na linha
            # da conta INDISPONIVEL — esse seria fallback disfarcado de saldo.
            linhas = page.evaluate("""() => {
              const cx=S.alladin.transactions.find(t=>t.eventType==='DEPOSIT').cashAccountId;
              const alvo=JPWAlladin.leitura.cashAccounts()
                .map(c=>c.cashAccountId).indexOf(cx);
              const trs=[...document.querySelectorAll('[data-alladin-panel="balances"] table tr')].slice(1);
              return { alvo: trs[alvo] ? trs[alvo].innerText : '<<linha ausente>>',
                       todas: trs.map(tr=>tr.innerText) };
            }""")
            alvo = linhas["alvo"]
            if "Indisponível" not in alvo:
                falhas.append(f"E12b: a linha da conta divergente deveria acusar Indisponivel ({alvo!r})")
            if re.search(r"R\$", alvo):
                falhas.append(f"E12b: a linha INDISPONIVEL exibiu valor monetario ({alvo!r})")
            # controle no sentido oposto: zero LEGITIMO continua exibivel
            if not any(re.search(r"R\$\s?0,00", l) for l in linhas["todas"]):
                falhas.append("E12b: nenhuma linha mostrou zero legitimo — o controle "
                              "que separa zero verdadeiro de fallback nao foi exercitado")
            if erros:
                falhas.append(f"E12b: pageerror {erros}")
            ctx.close()
        executar(falhas, "E12b", e12b)

        # ---- E13: a sentinela impede ledger silenciosamente filtrado ------
        # `leitura.transactions()` filtra registro ilegivel EM SILENCIO e nao tem
        # envelope de qualidade (MD-2). Sem a sentinela, a tela mostraria uma
        # lista MENOR como se fosse o ledger inteiro — sem nenhum aviso. Este
        # caso prova as duas metades: o read-model realmente esconde, e a tela
        # realmente se recusa a desenhar.
        def e13():
            ctx, page, erros = abrir(browser, url)
            page.evaluate(SEMEAR)
            page.wait_for_timeout(250)
            # `aldVistaCadastral` filtra por `aldRegistroLegivel`, que e checagem
            # de FORMA (objeto nao-array) — nao de validade economica. O que
            # desaparece em silencio, portanto, e um registro nao-objeto: ele some
            # da lista sem deixar rastro, e a contagem exibida seria MENOR que o
            # ledger real, sem nenhum aviso.
            r = page.evaluate("""() => {
              const antes=JPWAlladin.leitura.transactions().length;
              S.alladin.transactions.push(null);              // registro nao-objeto
              const depois=JPWAlladin.leitura.transactions().length;
              const pos=JPWAlladin.leitura.posicoes();
              return { antes, depois, bruto:S.alladin.transactions.length,
                       silencioso: depois === antes && S.alladin.transactions.length > antes,
                       sentinelaViu: !pos.available, issues: pos.issues };
            }""")
            if not r["silencioso"]:
                falhas.append(f"E13: premissa falhou — transactions() nao filtrou em silencio ({r})")
            if not r["sentinelaViu"]:
                falhas.append(f"E13: premissa falhou — o sentinela nao viu o registro ilegivel ({r})")
            txt = ver(page, "ledger")
            if "indisponí" not in txt.lower():
                falhas.append("E13: ledger FILTRADO em silencio foi projetado como normal — "
                              "a sentinela nao segurou")
            if page.evaluate("""() => document.querySelectorAll(
                    '[data-alladin-panel="ledger"] table tr').length"""):
                falhas.append("E13: tabela renderizada sobre ledger filtrado")
            if erros:
                falhas.append(f"E13: pageerror {erros}")
            ctx.close()
        executar(falhas, "E13", e13)

        # ---- E14: zero escrita ------------------------------------------
        def e14():
            ctx, page, erros = abrir(browser, url)
            page.evaluate(SEMEAR)
            page.wait_for_timeout(300)
            page.evaluate("""() => {
              window.__saves=0; window.__so=window.save;
              window.save=function(){ window.__saves++; return window.__so.apply(this,arguments); };
              window.__S=JSON.stringify(S); window.__LS=localStorage.getItem('%s');
            }""" % LSKEY)
            for _ in range(2):
                for v in CADASTRAIS + ECONOMICOS:
                    ver(page, v)
            r = page.evaluate("""() => ({ saves: window.__saves,
                sIgual: JSON.stringify(S) === window.__S,
                lsIgual: localStorage.getItem('%s') === window.__LS })""" % LSKEY)
            if r["saves"]:
                falhas.append(f"E14: a superficie read-only chamou save() {r['saves']}x")
            if not r["sIgual"]:
                falhas.append("E14: S mudou durante navegacao read-only")
            if not r["lsIgual"]:
                falhas.append("E14: localStorage mudou durante navegacao read-only")
            if erros:
                falhas.append(f"E14: pageerror {erros}")
            ctx.close()
        executar(falhas, "E14", e14)

        # ---- E15: paineis CADASTRAIS seguem sem conteudo economico -------
        def e15():
            ctx, page, erros = abrir(browser, url)
            page.evaluate(SEMEAR)
            page.wait_for_timeout(300)
            for v in CADASTRAIS:
                txt = ver(page, v)
                m = PROIBIDO_ECONOMICO.search(txt)
                if m:
                    falhas.append(f"E15: conteudo economico vazou para o painel cadastral "
                                  f"{v} ({m.group(0)!r})")
            if erros:
                falhas.append(f"E15: pageerror {erros}")
            ctx.close()
        executar(falhas, "E15", e15)

        # ---- E16: acessibilidade ----------------------------------------
        def e16():
            ctx, page, erros = abrir(browser, url)
            page.evaluate(SEMEAR)
            page.wait_for_timeout(300)
            r = page.evaluate("""() => {
              const paineis=[...document.querySelectorAll('[data-alladin-panel]')];
              const bs=[...document.querySelectorAll('#alladinTabs button[data-alladin-view]')];
              return { semRole: paineis.filter(p=>p.getAttribute('role')!=='region')
                                        .map(p=>p.dataset.alladinPanel),
                       semLabel: paineis.filter(p=>!p.getAttribute('aria-label'))
                                        .map(p=>p.dataset.alladinPanel),
                       semPressed: bs.filter(b=>!b.hasAttribute('aria-pressed'))
                                     .map(b=>b.dataset.alladinView),
                       focaveis: bs.filter(b=>b.tabIndex >= 0).length };
            }""")
            if r["semRole"] or r["semLabel"]:
                falhas.append(f"E16: painel sem role/aria-label ({r['semRole']} / {r['semLabel']})")
            if r["semPressed"]:
                falhas.append(f"E16: tab sem aria-pressed ({r['semPressed']})")
            if r["focaveis"] != 7:
                falhas.append(f"E16: nem toda tab e alcancavel por teclado ({r['focaveis']}/7)")
            # aria-pressed acompanha a selecao do painel economico
            page.evaluate("() => JPWAlladinUI.selectView('positions')")
            page.wait_for_timeout(120)
            pressed = page.evaluate("""() => [...document.querySelectorAll(
                '#alladinTabs button[data-alladin-view]')]
                .filter(b=>b.getAttribute('aria-pressed')==='true')
                .map(b=>b.dataset.alladinView)""")
            if pressed != ["positions"]:
                falhas.append(f"E16: aria-pressed nao acompanhou a selecao ({pressed})")
            # o aviso de bloqueio precisa ser TEXTO, nao so cor
            page.evaluate("() => { S.alladin.transactions = {}; }")
            texto_bloqueio = ver(page, "positions")
            if "indisponí" not in texto_bloqueio.lower():
                falhas.append("E16: estado bloqueado nao tem portador TEXTUAL")
            if erros:
                falhas.append(f"E16: pageerror {erros}")
            ctx.close()
        executar(falhas, "E16", e16)

        for ctx in CONTEXTOS:
            try:
                ctx.close()
            except Exception:
                pass
        browser.close()
    server.shutdown()

    if falhas:
        print("ALLADIN UI LEDGER TEST FALHOU")
        for f in falhas:
            print("  - " + f)
        return 1
    print("alladin_ui_ledger_test PASS (E1-E16 + E12b: sete destinos com os quatro cadastrais "
          "intactos e sem conteudo economico; Lancamentos na ORDEM do read-model, dez "
          "eventTypes rotulados, reason do ajuste visivel, effectiveAt e recordedAt ambos "
          "visiveis fora de tooltip, transferencia com as duas pernas e caixas homonimas "
          "desambiguadas, original e estorno ambos presentes; saldo identico a "
          "saldoDeCaixa() e quantity byte-identica ao read-model, negativa fiel sem "
          "semantica de short e string longa integra; BLOCKING x EMPTY provado nos DOIS "
          "sentidos, seis vetores de corrupcao bloqueando, e a sentinela impedindo que um "
          "ledger silenciosamente filtrado seja projetado como normal; zero save(), S e "
          "storage byte-identicos, acessibilidade por role/aria/teclado e bloqueio textual)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
