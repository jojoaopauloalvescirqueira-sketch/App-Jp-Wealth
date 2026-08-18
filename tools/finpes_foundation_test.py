#!/usr/bin/env python3
"""Fundacao de Financas Pessoais (PF-01): schema v1, normalizador e politica monetaria.

O agregado personalFinance e memoria financeira longitudinal. Este teste prova as
leis da fundacao, na fronteira exata que o contrato congelou:

  REPARO DE FORMA — conteiner ausente/errado volta ao vazio correto;
  CONTEUDO — jamais tocado: null nao vira 0, numero invalido nao e "consertado",
  campo desconhecido atravessa, moneyUnit nunca e reinterpretada.

Todas as fixtures sao SINTETICAS.
"""

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import os
import socket
import sys
import threading

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)

LSKEY = "jpwealth_v9_state"


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


def nova_pagina(context):
    page = context.new_page()
    erros = []
    page.on("pageerror", lambda e: erros.append(str(e)))
    page.route(
        "**/*",
        lambda route: route.continue_() if "127.0.0.1" in route.request.url
        else route.fulfill(status=200, content_type="application/json", body="{}"),
    )
    return page, erros


def abrir(browser, url, mutacao_js=None):
    """Boot em contexto novo. mutacao_js recebe o estado DEFAULT ja carregado,
    muta S como quiser, grava direto no localStorage e o teste recarrega —
    assim o estado semeado e sempre um estado real do app, nao um esqueleto."""
    context = browser.new_context(viewport={"width": 1440, "height": 900})
    context.add_init_script("window.__onbShown=true;")
    page, erros = nova_pagina(context)
    page.goto(url, wait_until="load")
    page.wait_for_function("() => typeof S === 'object' && typeof migrate === 'function'")
    if mutacao_js:
        page.evaluate(f"""() => {{
            {mutacao_js}
            localStorage.setItem({json.dumps(LSKEY)}, JSON.stringify(S));
        }}""")
        page.reload(wait_until="load")
        page.wait_for_function("() => typeof S === 'object' && typeof migrate === 'function'")
    return context, page, erros


def run_default_vazio(page, falhas):
    r = page.evaluate("""() => {
        const pf = S.personalFinance, def = DEFAULTS.personalFinance;
        return { igual: JSON.stringify(pf) === JSON.stringify(def),
                 pf: JSON.stringify(pf) };
    }""")
    if not r["igual"]:
        falhas.append(f"boot fresco: personalFinance difere de DEFAULTS: {r['pf']}")
    esperado = {"schemaVersion": 1, "moneyUnit": "BRL_CENTS", "months": {},
                "recurringIncome": [], "debts": [], "creditLines": [], "scenarios": []}
    real = json.loads(r["pf"])
    if real != esperado:
        falhas.append(f"forma de nascimento nao e a congelada: {real}")


def run_migracao_base_anterior(browser, url, falhas):
    ctx, page, erros = abrir(browser, url, mutacao_js="delete S.personalFinance;")
    r = page.evaluate("""() => JSON.stringify(S.personalFinance)""")
    real = json.loads(r)
    if real != {"schemaVersion": 1, "moneyUnit": "BRL_CENTS", "months": {},
                "recurringIncome": [], "debts": [], "creditLines": [], "scenarios": []}:
        falhas.append(f"base anterior sem o agregado deveria nascer vazio canonico; veio {real}")
    if erros:
        falhas.append(f"pageerror na migracao de base anterior: {erros}")
    ctx.close()


def run_idempotencia(page, falhas):
    r = page.evaluate("""() => {
        const a = JSON.stringify(S.personalFinance);
        personalFinanceNormalizeState();
        const b = JSON.stringify(S.personalFinance);
        personalFinanceNormalizeState();
        const c = JSON.stringify(S.personalFinance);
        return { estavel: a === b && b === c };
    }""")
    if not r["estavel"]:
        falhas.append("normalizador nao e idempotente: rodadas sucessivas alteram o agregado")


def run_forma_vs_conteudo(browser, url, falhas):
    """O caso central: conteiner errado e reparado; CONTEUDO hostil atravessa intacto."""
    mut = """
      S.personalFinance = {
        schemaVersion: 'sete',                 // invalida -> vira 1
        moneyUnit: 'BRL_CENTS',
        extensaoFutura: {origem:'teste'},      // campo desconhecido no agregado
        months: {
          '2026-07': {
            createdAt: '2026-07-01T00:00:00.000Z',
            campoDesconhecido: 'sobrevive',
            incomes: [
              {id:'pfi_t1', name:'Salario Sintetico', projectedAmount:1200000,
               receivedAmount:null, status:'PROJETADA', ruleId:null},
              {id:'pfi_t2', name:'Hostil', projectedAmount:-5000,     // fora de dominio: PRESERVA
               receivedAmount:'abc', status:'RECEBIDA', ruleId:null}, // invalido: PRESERVA
            ],
            expenses: 'nao-e-lista',           // forma errada DENTRO do mes: fica como esta
            debtSnapshots: [], allocations: [], notes: [],
          },
          'AGOSTO': {qualquer:'chave fora do padrao tambem atravessa'},
        },
        recurringIncome: {},                   // forma errada de conteiner -> []
        debts: [],
        creditLines: [{id:'pfc_t1', institution:'Banco Tau', instrument:'Cartao',
                       type:'CARTAO', totalLimit:500000, used:550000, extra:'fica'}],
        scenarios: null,                       // -> []
      };
    """
    ctx, page, erros = abrir(browser, url, mutacao_js=mut)
    r = page.evaluate("""() => {
        const pf = S.personalFinance;
        const m = pf.months['2026-07'];
        return {
          schemaVersion: pf.schemaVersion,
          extensao: pf.extensaoFutura && pf.extensaoFutura.origem,
          mesFora: JSON.stringify(pf.months['AGOSTO']),
          campoMes: m && m.campoDesconhecido,
          nulo: m && m.incomes[0].receivedAmount,
          nuloTipo: m && typeof m.incomes[0].receivedAmount,
          hostilNegativo: m && m.incomes[1].projectedAmount,
          hostilTexto: m && m.incomes[1].receivedAmount,
          expensesForma: m && typeof m.expenses,
          recorrentes: Array.isArray(pf.recurringIncome) && pf.recurringIncome.length,
          cenarios: Array.isArray(pf.scenarios) && pf.scenarios.length,
          extraCredito: pf.creditLines[0] && pf.creditLines[0].extra,
          estouro: pf.creditLines[0] && pf.creditLines[0].used,
        };
    }""")
    if r["schemaVersion"] != 1:
        falhas.append(f"schemaVersion invalida deveria virar 1; veio {r['schemaVersion']}")
    if r["extensao"] != "teste":
        falhas.append("campo desconhecido no nivel do agregado foi perdido")
    if "fora do padrao" not in (r["mesFora"] or ""):
        falhas.append(f"chave de mes fora do padrao deveria atravessar intacta; veio {r['mesFora']}")
    if r["campoMes"] != "sobrevive":
        falhas.append("campo desconhecido no nivel do mes foi perdido")
    if not (r["nulo"] is None and r["nuloTipo"] == "object"):
        falhas.append(f"null virou outra coisa: {r['nulo']} ({r['nuloTipo']}) — null nunca vira 0")
    if r["hostilNegativo"] != -5000:
        falhas.append(f"montante negativo hostil foi 'consertado' silenciosamente: {r['hostilNegativo']}")
    if r["hostilTexto"] != "abc":
        falhas.append(f"valor invalido foi coagido: {r['hostilTexto']} — correcao silenciosa e fabricacao")
    if r["expensesForma"] != "string":
        falhas.append(f"conteudo interno do mes foi reconstruido (expenses: {r['expensesForma']}) — o normalizador nao percorre registros")
    if r["recorrentes"] != 0:
        falhas.append("conteiner de forma errada nao voltou ao vazio correto")
    if r["cenarios"] != 0:
        falhas.append("scenarios null nao voltou a []")
    if r["extraCredito"] != "fica":
        falhas.append("campo desconhecido em registro foi perdido")
    if r["estouro"] != 550000:
        falhas.append(f"used>totalLimit foi clampado: {r['estouro']}")
    if erros:
        falhas.append(f"pageerror no cenario forma-vs-conteudo: {erros}")
    ctx.close()


def run_money_unit_sentinela(browser, url, falhas):
    # unidade DESCONHECIDA com dados: preservada, jamais convertida
    mut = """
      S.personalFinance = { schemaVersion:1, moneyUnit:'USD_CENTS',
        months:{'2026-01':{incomes:[{id:'pfi_x',name:'X',projectedAmount:100,
          receivedAmount:null,status:'PROJETADA',ruleId:null}],
          expenses:[],debtSnapshots:[],allocations:[],notes:[]}},
        recurringIncome:[], debts:[], creditLines:[], scenarios:[] };
    """
    ctx, page, erros = abrir(browser, url, mutacao_js=mut)
    # sonda com guarda: se a mutacao destruir o mes, a acusacao deve ser a
    # PROPRIEDADE (dado perdido/convertido), nunca um TypeError incidental.
    r = page.evaluate("""() => {
        const m = S.personalFinance.months && S.personalFinance.months['2026-01'];
        const i = m && Array.isArray(m.incomes) && m.incomes[0];
        return { unidade: S.personalFinance.moneyUnit,
                 valor: i ? i.projectedAmount : 'PERDIDO' };
    }""")
    if r["unidade"] != "USD_CENTS":
        falhas.append(f"moneyUnit desconhecida foi alterada: {r['unidade']} — reinterpretacao proibida")
    if r["valor"] != 100:
        falhas.append(f"valor sob unidade desconhecida foi convertido ou destruido: {r['valor']}")
    ctx.close()

    # unidade AUSENTE com dados: continua ausente (desconhecida); AUSENTE vazio: nasce BRL_CENTS
    mut2 = """
      S.personalFinance = { schemaVersion:1,
        months:{'2026-01':{incomes:[],expenses:[],debtSnapshots:[],allocations:[],notes:[]}},
        recurringIncome:[], debts:[], creditLines:[], scenarios:[] };
    """
    ctx, page, erros2 = abrir(browser, url, mutacao_js=mut2)
    r = page.evaluate("""() => ({ tem: 'moneyUnit' in S.personalFinance })""")
    if r["tem"]:
        falhas.append("moneyUnit ausente COM dados foi semeada — isso reinterpreta dado de unidade desconhecida")
    ctx.close()

    mut3 = """
      S.personalFinance = { schemaVersion:1, months:{},
        recurringIncome:[], debts:[], creditLines:[], scenarios:[] };
    """
    ctx, page, erros3 = abrir(browser, url, mutacao_js=mut3)
    r = page.evaluate("""() => S.personalFinance.moneyUnit""")
    if r != "BRL_CENTS":
        falhas.append(f"agregado vazio sem moneyUnit deveria nascer BRL_CENTS; veio {r}")
    ctx.close()


def run_politica_monetaria(page, falhas):
    """Contrato canonico de parseBRLCents/formatBRLCents — a fronteira de entrada
    de TODO o dominio financeiro. Tres estados que jamais se confundem:
    null (vazio), inteiro (valido), NaN (invalido)."""
    r = page.evaluate("""() => {
        const casos_parse = [
          // [entrada, esperado]  — esperado 'NaN' representa invalido
          ['0', 0], ['0,00', 0], ['0.10', 10], ['0,10', 10],
          ['1420,50', 142050], ['1420.50', 142050], ['1.420,50', 142050],
          ['1.420', 142000], ['1.42', 142], ['1420', 142000],
          ['1420,5', 142050], ['12', 1200], ['  250  ', 25000],
          ['-80', -8000], ['−1.879,00', -187900],       // sinal reconhecido (guarda decide)
          ['', null], ['   ', null],                     // vazio = nao informado
          ['abc', 'NaN'], ['12a', 'NaN'], ['1420,505', 'NaN'],
          ['1,420', 'NaN'], ['1,420.50', 'NaN'],         // ambiguidade/3 casas
          ['1.4205,5', 'NaN'], ['1 420', 'NaN'],         // milhar quebrado, espaco interno
          ['12.34.56', 'NaN'],
          ['99999999999999', 'NaN'],                     // 14 digitos: overflow recusado
          ['10000000000000', 'NaN'],                     // 14 digitos CUJOS CENTAVOS ainda cabem em safe int:
                                                         // so o corte de comprimento recusa — o caso que separa
                                                         // a regra explicita do acidente do isSafeInteger
          ['9999999999999', 999999999999900],            // 13 digitos: teto aceito
        ];
        const erros = [];
        for(const [ent, esp] of casos_parse){
          const got = parseBRLCents(ent);
          const ok = (esp==='NaN') ? Number.isNaN(got) : Object.is(got, esp);
          if(!ok) erros.push(`parse(${JSON.stringify(ent)}) => ${got}, esperava ${esp}`);
        }
        const casos_fmt = [
          [142050, 'R$ 1.420,50'], [0, 'R$ 0,00'], [null, '—'],
          [-187900, '-R$ 1.879,00'], [30, 'R$ 0,30'], [1000000000, 'R$ 10.000.000,00'],
          [10.5, '—'],                                   // nao-inteiro nao e centavo
          // teto do dominio do formatador: MAX_SAFE_INTEGER. A aritmetica de
          // STRING e exata aqui; divisao float erraria o centavo (erro > 0,005).
          [9007199254740991, 'R$ 90.071.992.547.409,91'],
          [-9007199254740991, '-R$ 90.071.992.547.409,91'],
        ];
        for(const [ent, esp] of casos_fmt){
          const got = formatBRLCents(ent);
          if(got!==esp) erros.push(`format(${ent}) => ${JSON.stringify(got)}, esperava ${JSON.stringify(esp)}`);
        }
        // exatidao que o float nao daria: R$0,10 + R$0,20 em centavos
        const soma = parseBRLCents('0,10') + parseBRLCents('0,20');
        if(soma !== 30) erros.push(`0,10+0,20 => ${soma} centavos, esperava 30 exato`);
        if(formatBRLCents(soma) !== 'R$ 0,30') erros.push('formatacao da soma nao e R$ 0,30');
        // guarda semantica: negativo recusado onde o dominio exige >= 0
        if(pfAmountInDomain(-8000, {allowNull:false}) !== false)
          erros.push('guarda aceitou montante negativo em campo >= 0');
        if(pfAmountInDomain(null, {allowNull:true}) !== true)
          erros.push('guarda recusou null onde nao informado e aceitavel');
        if(pfAmountInDomain(null, {allowNull:false}) !== false)
          erros.push('guarda aceitou null onde o ato exige valor');
        if(pfAmountInDomain(142050, {allowNull:false}) !== true)
          erros.push('guarda recusou valor valido');
        if(pfAmountInDomain(10.5, {allowNull:false}) !== false)
          erros.push('guarda aceitou nao-inteiro como centavo');
        return erros;
    }""")
    for e in r:
        falhas.append("politica monetaria: " + e)


def run_sentinela_bloqueia_escrita(browser, url, falhas):
    """moneyUnit desconhecida: modulo bloqueado para escrita, estado preservado,
    e o bloqueio NAO e global — o resto do JP Wealth segue operante."""
    mut = """
      S.personalFinance = { schemaVersion:1, moneyUnit:'USD_CENTS',
        months:{}, recurringIncome:[], debts:[], creditLines:[], scenarios:[] };
    """
    ctx, page, erros = abrir(browser, url, mutacao_js=mut)
    r = page.evaluate("""() => ({
        suportada: pfMoneyUnitSupported(),
        bloqueio: pfWriteBlockReason(),
        unidade: S.personalFinance.moneyUnit,
        appVivo: typeof save === 'function' && typeof compute === 'function',
    })""")
    if r["suportada"] is not False:
        falhas.append("sentinela: unidade desconhecida deveria reprovar pfMoneyUnitSupported")
    if r["bloqueio"] != "READ_ONLY_UNSUPPORTED_MONEY_UNIT":
        falhas.append(f"sentinela: bloqueio de escrita ausente ou errado: {r['bloqueio']}")
    if r["unidade"] != "USD_CENTS":
        falhas.append(f"sentinela: estado nao foi preservado: {r['unidade']}")
    if not r["appVivo"]:
        falhas.append("sentinela: bloqueio vazou para o JP Wealth inteiro")
    ctx.close()

    # unidade correta: escrita liberada
    ctx, page, erros = abrir(browser, url)
    r = page.evaluate("""() => ({ bloqueio: pfWriteBlockReason() })""")
    if r["bloqueio"] is not None:
        falhas.append(f"sentinela: BRL_CENTS deveria liberar escrita; veio {r['bloqueio']}")
    ctx.close()


def run_schema_version_futura(browser, url, falhas):
    mut = """
      S.personalFinance = { schemaVersion:7, moneyUnit:'BRL_CENTS', months:{},
        recurringIncome:[], debts:[], creditLines:[], scenarios:[],
        campoDeV7:'novo mundo' };
    """
    ctx, page, erros = abrir(browser, url, mutacao_js=mut)
    r = page.evaluate("""() => ({ v: S.personalFinance.schemaVersion,
                                  extra: S.personalFinance.campoDeV7 })""")
    if r["v"] != 7:
        falhas.append(f"schemaVersion futura foi rebaixada: {r['v']} — app antigo mentiria sobre o dado")
    if r["extra"] != "novo mundo":
        falhas.append("campo de versao futura foi perdido")
    ctx.close()


def main():
    servidor, url = serve()
    falhas = []
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()

            ctx, page, erros = abrir(browser, url)
            run_default_vazio(page, falhas)
            run_idempotencia(page, falhas)
            run_politica_monetaria(page, falhas)
            if erros:
                falhas.append(f"pageerror no boot fresco: {erros}")
            ctx.close()

            run_migracao_base_anterior(browser, url, falhas)
            run_forma_vs_conteudo(browser, url, falhas)
            run_money_unit_sentinela(browser, url, falhas)
            run_sentinela_bloqueia_escrita(browser, url, falhas)
            run_schema_version_futura(browser, url, falhas)

            browser.close()
    finally:
        servidor.shutdown()

    if falhas:
        print("FALHOU")
        for f in falhas:
            print("  - " + f)
        return 1
    print("FINPES FOUNDATION TEST PASS — forma reparada, conteudo intocado, unidade jamais reinterpretada")
    return 0


if __name__ == "__main__":
    sys.exit(main())
