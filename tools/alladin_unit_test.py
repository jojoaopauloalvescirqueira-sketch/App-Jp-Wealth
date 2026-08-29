#!/usr/bin/env python3
"""Alladin — testes UNITARIOS da fundacao (C1) e do modelo cadastral (C2). HD-5 opcao A.

Contrato do harness (decisao humana de 2026-08-20): Chromium ISOLADO —
sem carregar o app, sem DOM de producao, sem estado real, sem network;
funcoes puras, fixtures deterministicas, PASS/FAIL automatizado.

A pagina e about:blank; TODA requisicao de rede e abortada e contada; o unico
codigo injetado e um prelude de stubs (S, save, dgLogChange instrumentados)
seguido do MODULO SOB TESTE (src/js/10-domain/13-alladin.js), lido do disco.
Cada caso acusa pela PROPRIEDADE violada — um numero certo pelo motivo errado
e FALHA. Testes de migration/persistencia sao integracao (alladin_foundation_test.py).
"""
from pathlib import Path
import sys

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
MODULO = ROOT / "src/js/10-domain/13-alladin.js"

PRELUDE = """
window.__stub = { saves: 0, saveResult: true, logs: [] };
var S = { alladin: { schemaVersion: 3, reportingCurrency: 'BRL',
                     instruments: [], assets: [], accounts: [], cashAccounts: [],
                     transactions: [] },
          dataGovernance: { changeLog: [] } };
function save(){ window.__stub.saves += 1; return window.__stub.saveResult; }
// Espelha o dgLogChange REAL de 00-core/04-persistence.js, INCLUSIVE a poda no
// teto — que reatribui o array em vez de muta-lo. A versao anterior deste stub
// omitia a poda e, com isso, tornava INVISIVEL toda uma classe de defeito: no
// teto, um rollback por comprimento parece correto porque o comprimento nao muda.
// Um stub que simplifica o mecanismo sob teste nao e simplificacao, e cegueira.
const DG_CHANGELOG_MAX = 400;
function dgLogChange(entity, action, recordId, label){
  const e = { entity: entity, action: action, recordId: recordId, label: label };
  window.__stub.logs.push(e);
  S.dataGovernance.changeLog.push(e);   // espelha o app: e daqui que a restauracao trunca
  if(S.dataGovernance.changeLog.length > DG_CHANGELOG_MAX){
    S.dataGovernance.changeLog = S.dataGovernance.changeLog.slice(-DG_CHANGELOG_MAX);
  }
}
"""


def executar(falhas, nome, fn):
    try:
        fn()
    except Exception as exc:  # crash jamais engole as acusacoes ja acumuladas
        falhas.append(f"{nome}: excecao na sonda — {exc}")


def main() -> int:
    falhas: list[str] = []
    bloqueadas = {"n": 0}
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
        page.on("pageerror", lambda e: falhas.append(f"pageerror: {e}"))

        def abortar(route):
            bloqueadas["n"] += 1
            route.abort()

        page.route("**/*", abortar)  # sem network: tudo abortado e contado
        page.goto("about:blank")
        page.add_script_tag(content=PRELUDE)
        page.add_script_tag(content=MODULO.read_text(encoding="utf-8"))

        ev = page.evaluate

        # U1 — parse BRL: formas aceitas identicas ao precedente PF
        def u1():
            casos = {"1420": 142000, "1420,50": 142050, "1.420,50": 142050,
                     "1.420": 142000, "1420.50": 142050, "0": 0, "0,07": 7}
            for txt, esperado in casos.items():
                r = ev("t => JPWAlladin.money.parse(t, 'BRL')", txt)
                if not (isinstance(r, dict) and r.get("amount") == esperado and r.get("currency") == "BRL"):
                    falhas.append(f"U1 parse BRL '{txt}': esperado {esperado}, veio {r!r}")
            neg = ev("() => JPWAlladin.money.parse('-1.420,50', 'BRL').amount")
            if neg != -142050:
                falhas.append(f"U1 negativo: esperado -142050, veio {neg!r}")
            # "-0" normaliza para 0 exato (Object.is distingue -0 de 0)
            zeros = ev("""() => ['-0', '-0,00'].map(t =>
                Object.is(JPWAlladin.money.parse(t, 'BRL').amount, 0))""")
            if zeros != [True, True]:
                falhas.append(f"U1 '-0' nao normalizou para 0 exato: {zeros!r}")
        executar(falhas, "U1", u1)

        # U2 — parse: rejeicoes viram NaN; vazio vira null (nao informado != erro)
        def u2():
            for txt in ["abc", "1,420.50", "1.42,00", "12 34", "1420,505",
                        "12345678901234", "1.4200", "--5"]:
                ok = ev("t => Number.isNaN(JPWAlladin.money.parse(t, 'BRL'))", txt)
                if not ok:
                    falhas.append(f"U2 '{txt}': deveria ser NaN")
            if ev("() => JPWAlladin.money.parse('   ', 'BRL')") is not None:
                falhas.append("U2 vazio: deveria ser null")
        executar(falhas, "U2", u2)

        # U3 — moeda sem suporte de runtime: parse NaN, format '—' (sentinela);
        # schema extensivel: EUR nao e invalido, e ILEGIVEL ate o suporte chegar.
        def u3():
            if not ev("() => Number.isNaN(JPWAlladin.money.parse('10,00', 'EUR'))"):
                falhas.append("U3 parse EUR: deveria ser NaN (sem expoente nao ha interpretacao)")
            if ev("() => JPWAlladin.money.format({amount: 1000, currency: 'EUR'})") != "—":
                falhas.append("U3 format EUR: deveria ser '—'")
            if ev("() => JPWAlladin.money.supported('EUR')") is not False:
                falhas.append("U3 supported('EUR'): deveria ser false")
            if ev("() => JPWAlladin.money.runtimeCurrencies()") != ["BRL", "USD"]:
                falhas.append("U3 runtimeCurrencies: esperado ['BRL','USD']")
        executar(falhas, "U3", u3)

        # U4 — format por aritmetica de string; invalidos degradam para '—'
        def u4():
            casos = [({"amount": 142050, "currency": "BRL"}, "R$ 1.420,50"),
                     ({"amount": -187900, "currency": "BRL"}, "-R$ 1.879,00"),
                     ({"amount": 0, "currency": "BRL"}, "R$ 0,00"),
                     ({"amount": 123456789, "currency": "USD"}, "US$ 1.234.567,89")]
            for money, esperado in casos:
                r = ev("m => JPWAlladin.money.format(m)", money)
                if r != esperado:
                    falhas.append(f"U4 format {money}: esperado '{esperado}', veio '{r}'")
            for ruim in ["null", "undefined", "{amount: 1.5, currency: 'BRL'}",
                         "{amount: 100}", "{currency: 'BRL'}", "[142050, 'BRL']", "'142050'"]:
                r = ev(f"() => JPWAlladin.money.format({ruim})")
                if r != "—":
                    falhas.append(f"U4 format({ruim}): esperado '—', veio '{r}'")
        executar(falhas, "U4", u4)

        # U5 — round-trip exato parse(format(x)) === x, inclusive bordas
        def u5():
            perdas = ev("""() => {
              const casos = [0, 1, 7, 999, 1000, 142050, -142050, 9999999999999];
              const perdas = [];
              for (const c of casos) {
                const txt = JPWAlladin.money.format({amount: c, currency: 'BRL'});
                const volta = JPWAlladin.money.parse(txt.replace(/^-?R\\$ /, m => m.includes('-') ? '-' : ''), 'BRL');
                if (!volta || volta.amount !== c) perdas.push(c + '→' + txt + '→' + JSON.stringify(volta));
              }
              return perdas;
            }""")
            if perdas:
                falhas.append(f"U5 round-trip perdeu: {perdas}")
        executar(falhas, "U5", u5)

        # U6 — validacoes base: I16 (sem currency nao ha dinheiro), I19 (inteiro),
        # pontos-base e texto de cadastro
        def u6():
            checks = ev("""() => {
              const v = [];
              const M = JPWAlladin;
              v.push(['money valido', aldMoneyInDomain({amount: 100, currency: 'BRL'}) === true]);
              v.push(['sem currency', aldMoneyInDomain({amount: 100}) === false]);
              v.push(['float', aldMoneyInDomain({amount: 1.5, currency: 'BRL'}) === false]);
              v.push(['null sem allowNull', aldMoneyInDomain(null) === false]);
              v.push(['null com allowNull', aldMoneyInDomain(null, {allowNull: true}) === true]);
              v.push(['negativo sob nonNegative', aldMoneyInDomain({amount: -1, currency: 'BRL'}, {nonNegative: true}) === false]);
              v.push(['bp 0', aldBpInDomain(0) === true]);
              v.push(['bp 10000', aldBpInDomain(10000) === true]);
              v.push(['bp 10001', aldBpInDomain(10001) === false]);
              v.push(['bp fracionario', aldBpInDomain(0.5) === false]);
              v.push(['texto ok', aldTextInDomain('MacBook Pro') === true]);
              v.push(['texto vazio', aldTextInDomain('   ') === false]);
              v.push(['texto longo', aldTextInDomain('x'.repeat(121)) === false]);
              return v.filter(([, ok]) => !ok).map(([n]) => n);
            }""")
            for nome in checks:
                falhas.append(f"U6 validacao '{nome}' falhou")
        executar(falhas, "U6", u6)

        # U7 — aldId: prefixo, forma e unicidade em lote
        def u7():
            r = ev("""() => {
              const ids = new Set();
              for (let i = 0; i < 200; i++) ids.add(aldId('aldi'));
              const um = aldId('alda');
              // sufixo 1-8 chars: Math.random().toString(36) pode render curto
              // (heranca do padrao pfId) — exigir 6 exatos seria flake ~1e-5
              return { unicos: ids.size, forma: /^alda_[a-z0-9]+_[a-z0-9]{1,8}$/.test(um) };
            }""")
            if r["unicos"] != 200:
                falhas.append(f"U7 unicidade: {r['unicos']}/200")
            if not r["forma"]:
                falhas.append("U7 forma do id fora do padrao prefixo_ts36_rand6")
        executar(falhas, "U7", u7)

        # U8 — fail-closed no gate: schemaVersion futura recusa TODO ato sem
        # executar fn, sem log e sem save (integridade > disponibilidade)
        def u8():
            r = ev("""() => {
              S.alladin.schemaVersion = 4;
              window.__stub.saves = 0; window.__stub.logs = [];
              let fnRodou = false;
              const res = aldMutate('teste_ato', () => { fnRodou = true; return {recordId: 'x'}; });
              const compat = JPWAlladin.compat();
              S.alladin.schemaVersion = 2;
              return { res, fnRodou, saves: window.__stub.saves,
                       logs: window.__stub.logs.length, compat };
            }""")
            if r["res"].get("erro") != "READ_ONLY_FUTURE_SCHEMA" or r["res"].get("ok") is not False:
                falhas.append(f"U8 recusa: {r['res']!r}")
            if r["fnRodou"] or r["saves"] != 0 or r["logs"] != 0:
                falhas.append(f"U8 vazamento sob bloqueio: fn={r['fnRodou']} saves={r['saves']} logs={r['logs']}")
            c = r["compat"]
            if not (c["readOnly"] is True and c["storedSchemaVersion"] == 4
                    and c["supportedSchemaVersion"] == 3 and c["reason"] == "READ_ONLY_FUTURE_SCHEMA"):
                falhas.append(f"U8 compat: {c!r}")
            # versao futura como STRING de digitos ('2') tambem e fail-closed
            r2 = ev("""() => {
              S.alladin.schemaVersion = '4';
              const compat = JPWAlladin.compat();
              const ato = aldMutate('probe', () => ({recordId: 'x'}));
              S.alladin.schemaVersion = 3;
              return { readOnly: compat.readOnly, stored: compat.storedSchemaVersion,
                       erro: ato.erro };
            }""")
            if not (r2["readOnly"] is True and r2["stored"] == 4
                    and r2["erro"] == "READ_ONLY_FUTURE_SCHEMA"):
                falhas.append(f"U8 versao futura em string nao bloqueou: {r2!r}")
        executar(falhas, "U8", u8)

        # U9 — gate no caminho feliz e nas recusas de fn/persistencia
        def u9():
            r = ev("""() => {
              window.__stub.saves = 0; window.__stub.logs = [];
              const ok = aldMutate('ato_ok', (a) => ({recordId: 'r1'}), {label: 'ato_ok'});
              const recusado = aldMutate('ato_recusado', () => ({ok: false, erro: 'invalido'}));
              window.__stub.saveResult = false;
              const semDisco = aldMutate('ato_sem_disco', () => ({recordId: 'r2'}));
              // fn otimista ({ok:true}) JAMAIS mascara persistencia recusada
              // (achado da auditoria C1: spread de r nao pode vencer o veredito)
              const otimista = aldMutate('ato_otimista', () => ({ok: true, recordId: 'r3'}));
              window.__stub.saveResult = true;
              return { ok, recusado, semDisco, otimista,
                       logs: window.__stub.logs, saves: window.__stub.saves };
            }""")
            if not (r["ok"]["ok"] is True and r["ok"]["persistido"] is True):
                falhas.append(f"U9 caminho feliz: {r['ok']!r}")
            if not (r["recusado"]["ok"] is False and r["recusado"]["erro"] == "invalido"):
                falhas.append(f"U9 recusa de fn: {r['recusado']!r}")
            if not (r["semDisco"]["ok"] is False and r["semDisco"]["persistido"] is False):
                falhas.append(f"U9 save()===false nao e prova de nao-escrita: {r['semDisco']!r}")
            if not (r["otimista"]["ok"] is False and r["otimista"]["persistido"] is False
                    and r["otimista"]["erro"] == "persistencia recusada"):
                falhas.append(f"U9 fn otimista mascarou persistencia recusada: {r['otimista']!r}")
            logs = r["logs"]
            if len(logs) != 3 or logs[0]["entity"] != "alladin" or logs[0]["action"] != "ato_ok":
                falhas.append(f"U9 log operacional: {logs!r}")
            if any("R$" in str(l.get("label", "")) for l in logs):
                falhas.append("U9 privacidade: valor financeiro em label do changeLog")
        executar(falhas, "U9", u9)

        # U10 — isolamento provado: nenhuma requisicao de rede passou e o modulo
        # nao construiu DOM (superficie e window.JPWAlladin, nao interface)
        def u10():
            corpo = ev("() => document.body ? document.body.children.length : 0")
            if corpo != 0:
                falhas.append(f"U10 modulo tocou o DOM: {corpo} filhos em body")
            if bloqueadas["n"] != 0:
                falhas.append(f"U10 rede: {bloqueadas['n']} requisicao(oes) tentada(s)")
        executar(falhas, "U10", u10)


        # ---- C2 · MODELO CADASTRAL -----------------------------------------

        def reset_agregado():
            ev("""() => { S.alladin = { schemaVersion: 3, reportingCurrency: 'BRL',
                 instruments: [], assets: [], accounts: [], cashAccounts: [], transactions: [] };
                 window.__stub.logs = []; window.__stub.saves = 0; }""")

        # U11 — owners[] com isSelf (DC-2 + OP-1)
        def u11():
            reset_agregado()
            r = ev("""() => {
              const base = {name:'Apto', nature:'IMOVEL', recordMode:'INDIVIDUAL'};
              const meio = JPWAlladin.cadastro.addAsset({...base,
                 owners:[{name:'Joao', shareBp:5000, isSelf:true},{name:'Maria', shareBp:5000}]});
              const parcial = JPWAlladin.cadastro.addAsset({...base, owners:[{name:'Joao', shareBp:4000, isSelf:true}]});
              const excesso = JPWAlladin.cadastro.addAsset({...base,
                 owners:[{name:'A', shareBp:6000},{name:'B', shareBp:6000}]});
              const doisEu = JPWAlladin.cadastro.addAsset({...base,
                 owners:[{name:'A', shareBp:5000, isSelf:true},{name:'B', shareBp:5000, isSelf:true}]});
              const fracao = JPWAlladin.cadastro.addAsset({...base, owners:[{name:'A', shareBp:50.5}]});
              const vazio = JPWAlladin.cadastro.addAsset({...base, owners:[]});
              const homonimo = JPWAlladin.cadastro.addAsset({...base,
                 owners:[{name:'Joao', shareBp:5000, isSelf:true},{name:'joao', shareBp:5000}]});
              const gravado = S.alladin.assets.filter(x => x.assetId === meio.recordId)[0];
              return { meio, parcial, excesso, doisEu, fracao, vazio, homonimo,
                       ownersGravados: JSON.stringify(gravado ? gravado.owners : null) };
            }""")
            if not (r["meio"]["ok"] and r["meio"]["avisos"] == []):
                falhas.append(f"U11 50/50 com isSelf deveria passar sem aviso: {r['meio']!r}")
            if r["ownersGravados"] != '[{"name":"Joao","shareBp":5000,"isSelf":true},{"name":"Maria","shareBp":5000}]':
                falhas.append(f"U11 owners gravados divergem: {r['ownersGravados']}")
            if not (r["parcial"]["ok"] and "OWNERSHIP_PARCIAL_NAO_ATRIBUIDA" in r["parcial"]["avisos"]):
                falhas.append(f"U11 soma<100% deveria passar COM aviso: {r['parcial']!r}")
            if r["excesso"]["ok"] or r["excesso"]["erro"] != "ALD_OWNERSHIP_ACIMA_DE_100":
                falhas.append(f"U11 soma>100% deveria recusar: {r['excesso']!r}")
            if r["doisEu"]["ok"] or r["doisEu"]["erro"] != "ALD_MULTIPLOS_ISSELF":
                falhas.append(f"U11 dois isSelf deveriam recusar: {r['doisEu']!r}")
            if r["fracao"]["ok"] or r["fracao"]["erro"] != "ALD_OWNER_SHAREBP_INVALIDO":
                falhas.append(f"U11 shareBp fracionario deveria recusar: {r['fracao']!r}")
            if not r["vazio"]["ok"]:
                falhas.append(f"U11 owners vazio e legitimo: {r['vazio']!r}")
            if not (r["homonimo"]["ok"] and "OWNER_NOME_DUPLICADO" in r["homonimo"]["avisos"]):
                falhas.append(f"U11 homonimo deveria avisar sem bloquear: {r['homonimo']!r}")
        executar(falhas, "U11", u11)

        # U12 — regimes de classificacao (fechado recusa / starter aceita novo)
        def u12():
            reset_agregado()
            r = ev("""() => {
              const familiaFora = JPWAlladin.cadastro.addInstrument({name:'X', symbol:'X', currency:'BRL',
                 instrumentFamily:'PHYSICAL_ASSET', assetClass:'RENDA_VARIAVEL'});
              const modoFora = JPWAlladin.cadastro.addAsset({name:'X', nature:'IMOVEL', recordMode:'LOTE'});
              const tipoNovo = JPWAlladin.cadastro.addAccount({name:'Fintech', institution:'Nubank', accountType:'FINTECH'});
              const natureNova = JPWAlladin.cadastro.addAsset({name:'Obra', nature:'ARTE', recordMode:'INDIVIDUAL'});
              const classeNova = JPWAlladin.cadastro.addInstrument({name:'Y', symbol:'Y', currency:'BRL',
                 instrumentFamily:'ALTERNATIVE', assetClass:'PRIVATE_EQUITY'});
              const cat = JPWAlladin.catalogos();
              const conta = S.alladin.accounts.filter(x => x.accountId === tipoNovo.recordId)[0] || {};
              const bem = S.alladin.assets.filter(x => x.assetId === natureNova.recordId)[0] || {};
              const inst = S.alladin.instruments.filter(x => x.instrumentId === classeNova.recordId)[0] || {};
              return { familiaFora, modoFora, tipoNovo, natureNova, classeNova,
                       gravados:[conta.accountType, bem.nature, inst.assetClass],
                       fechados:Object.keys(cat.fechados).sort().join(','),
                       starter:Object.keys(cat.starter).sort().join(','),
                       familias:cat.fechados.instrumentFamily.length };
            }""")
            if r["familiaFora"]["ok"] or r["familiaFora"]["erro"] != "ALD_INSTRUMENT_FAMILY_INVALIDA":
                falhas.append(f"U12 fechado aceitou valor fora (PHYSICAL_ASSET): {r['familiaFora']!r}")
            if r["modoFora"]["ok"] or r["modoFora"]["erro"] != "ALD_RECORD_MODE_INVALIDO":
                falhas.append(f"U12 recordMode fechado aceitou valor fora: {r['modoFora']!r}")
            for nome in ("tipoNovo", "natureNova", "classeNova"):
                if not r[nome]["ok"]:
                    falhas.append(f"U12 STARTER recusou valor novo ({nome}) — starter nao e enum: {r[nome]!r}")
            if r["gravados"] != ["FINTECH", "ARTE", "PRIVATE_EQUITY"]:
                falhas.append(f"U12 STARTER COAGIU o valor gravado (deveria preservar): {r['gravados']!r}")
            if r["fechados"] != "instrumentFamily,lifecycleStatus,recordMode,recordStatus":
                falhas.append(f"U12 regime FECHADO divergiu do contrato §2.1: {r['fechados']}")
            if r["starter"] != "accountType,assetClass,nature,strategicPurpose":
                falhas.append(f"U12 regime STARTER divergiu do contrato §2.1: {r['starter']}")
            if r["familias"] != 8:
                falhas.append(f"U12 instrumentFamily deveria ter 8 familias: {r['familias']}")
        executar(falhas, "U12", u12)

        # U13 — DC-4: cripto exige network; duplicidade AVISA e o registro NASCE
        def u13():
            reset_agregado()
            r = ev("""() => {
              const semRede = JPWAlladin.cadastro.addInstrument({name:'Tether', symbol:'USDT',
                 currency:'USD', instrumentFamily:'CRYPTO', assetClass:'CRIPTO'});
              const eth = JPWAlladin.cadastro.addInstrument({name:'Tether', symbol:'USDT', currency:'USD',
                 instrumentFamily:'CRYPTO', assetClass:'CRIPTO', externalIdentifiers:{network:'Ethereum'}});
              const tron = JPWAlladin.cadastro.addInstrument({name:'Tether', symbol:'USDT', currency:'USD',
                 instrumentFamily:'CRYPTO', assetClass:'CRIPTO', externalIdentifiers:{network:'Tron'}});
              const p1 = JPWAlladin.cadastro.addInstrument({name:'Petrobras', symbol:'PETR4', exchange:'B3',
                 currency:'BRL', instrumentFamily:'EQUITY_LIKE', assetClass:'RENDA_VARIAVEL'});
              const p2 = JPWAlladin.cadastro.addInstrument({name:'Petrobras PN', symbol:'PETR4', exchange:'B3',
                 currency:'BRL', instrumentFamily:'EQUITY_LIKE', assetClass:'RENDA_VARIAVEL'});
              const isin1 = JPWAlladin.cadastro.addInstrument({name:'Vale', symbol:'VALE3', exchange:'B3',
                 currency:'BRL', instrumentFamily:'EQUITY_LIKE', assetClass:'RENDA_VARIAVEL',
                 externalIdentifiers:{isin:'BRVALEACNOR0'}});
              const isin2 = JPWAlladin.cadastro.addInstrument({name:'Vale ON', symbol:'VALE3F', exchange:'B3',
                 currency:'BRL', instrumentFamily:'EQUITY_LIKE', assetClass:'RENDA_VARIAVEL',
                 externalIdentifiers:{isin:' brvaleacnor0 '}});
              const proto = JPWAlladin.cadastro.addInstrument({name:'Z', symbol:'Z', currency:'BRL',
                 instrumentFamily:'EQUITY_LIKE', assetClass:'RENDA_VARIAVEL',
                 externalIdentifiers: JSON.parse('{"__proto__":"x"}')});
              return { semRede, eth, tron, p1, p2, isin2, proto, total:S.alladin.instruments.length };
            }""")
            if r["semRede"]["ok"] or r["semRede"]["erro"] != "ALD_CRYPTO_SEM_NETWORK":
                falhas.append(f"U13 cripto sem network deveria recusar: {r['semRede']!r}")
            if not (r["eth"]["ok"] and r["tron"]["ok"]):
                falhas.append("U13 USDT em redes distintas sao instrumentos legitimos")
            if r["tron"]["avisos"] != []:
                falhas.append(f"U13 redes distintas nao deveriam gerar aviso de duplicidade: {r['tron']!r}")
            if not (r["p2"]["ok"] and "DUPLICADO_SYMBOL_EXCHANGE_CURRENCY" in r["p2"]["avisos"]):
                falhas.append(f"U13 PETR4 repetido deveria AVISAR e nascer: {r['p2']!r}")
            if not (r["isin2"]["ok"] and "DUPLICADO_IDENTIFICADOR_EXTERNO:isin" in r["isin2"]["avisos"]):
                falhas.append(f"U13 ISIN repetido (caixa/espacos) deveria avisar: {r['isin2']!r}")
            if r["proto"]["ok"] or r["proto"]["erro"] != "ALD_EXTERNAL_IDENTIFIERS_INVALIDOS":
                falhas.append(f"U13 chave reservada deveria recusar em vez de sumir: {r['proto']!r}")
            if r["total"] != 6:
                falhas.append(f"U13 aviso bloqueou registro (total {r['total']}, esperado 6)")
        executar(falhas, "U13", u13)

        # U14 — DC-5: symbolHistory append-only
        def u14():
            reset_agregado()
            r = ev("""() => {
              const c = JPWAlladin.cadastro.addInstrument({name:'Empresa', symbol:'ABC3', exchange:'B3',
                 currency:'BRL', instrumentFamily:'EQUITY_LIKE', assetClass:'RENDA_VARIAVEL'});
              JPWAlladin.cadastro.editInstrument(c.recordId, {symbol:'XYZ3'});
              JPWAlladin.cadastro.editInstrument(c.recordId, {name:'Empresa S.A.'});
              JPWAlladin.cadastro.editInstrument(c.recordId, {symbol:'QWE3'});
              const inst = S.alladin.instruments[0];
              const moeda = JPWAlladin.cadastro.editInstrument(c.recordId, {currency:'USD'});
              const semAviso = JPWAlladin.cadastro.editInstrument(c.recordId, {name:'Empresa S/A'});
              const protegido = JPWAlladin.cadastro.editInstrument(c.recordId, {instrumentId:'outro'});
              const histInjetado = JPWAlladin.cadastro.editInstrument(c.recordId, {symbolHistory:[]});
              return { symbol:inst.symbol, hist:inst.symbolHistory.map(h => h.symbol),
                       temTo: inst.symbolHistory.every(h => typeof h.to === 'string'),
                       id:inst.instrumentId === c.recordId, moeda,
                       avisosEdicao:semAviso.avisos, protegido, histInjetado };
            }""")
            if r["symbol"] != "QWE3" or r["hist"] != ["ABC3", "XYZ3"]:
                falhas.append(f"U14 symbolHistory nao empurrou em ordem: {r!r}")
            if not r["temTo"]:
                falhas.append("U14 entrada de symbolHistory sem instante de aposentadoria")
            if not r["id"]:
                falhas.append("U14 instrumentId mudou na edicao — identidade deve ser imutavel")
            if r["moeda"]["ok"] or r["moeda"]["erro"] != "ALD_CURRENCY_IMUTAVEL":
                falhas.append(f"U14 moeda do instrumento deveria ser imutavel: {r['moeda']!r}")
            if r["avisosEdicao"] != []:
                falhas.append(f"U14 edicao se auto-acusou de duplicidade: {r['avisosEdicao']!r}")
            if r["protegido"]["ok"] or not str(r["protegido"]["erro"]).startswith("ALD_CAMPO_PROTEGIDO"):
                falhas.append(f"U14 troca de identidade deveria RECUSAR, nao ser descartada: {r['protegido']!r}")
            if r["histInjetado"]["ok"] or not str(r["histInjetado"]["erro"]).startswith("ALD_CAMPO_PROTEGIDO"):
                falhas.append(f"U14 symbolHistory injetado deveria recusar: {r['histInjetado']!r}")
        executar(falhas, "U14", u14)

        # U15 — falha parcial NAO muta o agregado (exigencia OP-3.2b)
        def u15():
            reset_agregado()
            r = ev("""() => {
              const conta = JPWAlladin.cadastro.addAccount({name:'XP', institution:'XP', accountType:'BROKERAGE'});
              const antes = JSON.stringify(S.alladin);
              const savesAntes = window.__stub.saves, logsAntes = window.__stub.logs.length;
              const recusas = [
                JPWAlladin.cadastro.addAsset({name:'X', nature:'IMOVEL', recordMode:'INDIVIDUAL',
                   owners:[{name:'A', shareBp:9000},{name:'B', shareBp:9000}]}),
                JPWAlladin.cadastro.addInstrument({name:'', symbol:'X', currency:'BRL',
                   instrumentFamily:'EQUITY_LIKE', assetClass:'RENDA_VARIAVEL'}),
                JPWAlladin.cadastro.addCashAccount({accountId:'inexistente', currency:'BRL'}),
                JPWAlladin.cadastro.editAsset('nao-existe', {name:'Y'}),
              ];
              return { contaOk: conta.ok && antes.indexOf(conta.recordId) >= 0,
                       igual: JSON.stringify(S.alladin) === antes,
                       saves: window.__stub.saves - savesAntes,
                       logs: window.__stub.logs.length - logsAntes,
                       erros: recusas.map(x => x.erro), oks: recusas.map(x => x.ok) };
            }""")
            if not r["contaOk"]:
                falhas.append("U15 caminho de ESCRITA morto — a comparacao seria tautologia")
            if not r["igual"]:
                falhas.append("U15 ato recusado MUTOU o agregado — falha parcial salva")
            if r["saves"] != 0 or r["logs"] != 0:
                falhas.append(f"U15 ato recusado tocou save/log: saves={r['saves']} logs={r['logs']}")
            if any(r["oks"]):
                falhas.append(f"U15 ato invalido reportou sucesso: {r['oks']!r}")
            esperados = ["ALD_OWNERSHIP_ACIMA_DE_100", "ALD_NOME_INVALIDO",
                         "ALD_ACCOUNT_NAO_ENCONTRADA", "ALD_REGISTRO_NAO_ENCONTRADO"]
            if r["erros"] != esperados:
                falhas.append(f"U15 erros nao acusam a propriedade violada: {r['erros']!r}")
        executar(falhas, "U15", u15)

        # U16 — integridade referencial e ciclo cadastral
        def u16():
            reset_agregado()
            r = ev("""() => {
              const conta = JPWAlladin.cadastro.addAccount({name:'XP', institution:'XP', accountType:'BROKERAGE'});
              const brl = JPWAlladin.cadastro.addCashAccount({accountId:conta.recordId, currency:'BRL'});
              const brl2 = JPWAlladin.cadastro.addCashAccount({accountId:conta.recordId, currency:'BRL'});
              const usd = JPWAlladin.cadastro.addCashAccount({accountId:conta.recordId, currency:'USD'});
              const eur = JPWAlladin.cadastro.addCashAccount({accountId:conta.recordId, currency:'EUR'});
              const bloqueada = JPWAlladin.cadastro.setRecordStatus('account', conta.recordId, 'INACTIVE');
              JPWAlladin.cadastro.setRecordStatus('cashaccount', brl.recordId, 'INACTIVE');
              JPWAlladin.cadastro.setRecordStatus('cashaccount', brl2.recordId, 'INACTIVE');
              JPWAlladin.cadastro.setRecordStatus('cashaccount', usd.recordId, 'INACTIVE');
              JPWAlladin.cadastro.setRecordStatus('cashaccount', eur.recordId, 'INACTIVE');
              const liberada = JPWAlladin.cadastro.setRecordStatus('account', conta.recordId, 'INACTIVE');
              const orfa = JPWAlladin.cadastro.addCashAccount({accountId:conta.recordId, currency:'BRL'});
              const statusInvalido = JPWAlladin.cadastro.setRecordStatus('account', conta.recordId, 'ARQUIVADA');
              const reativaSobInativa = JPWAlladin.cadastro.setRecordStatus('cashaccount', brl.recordId, 'ACTIVE');
              const reativaConta = JPWAlladin.cadastro.setRecordStatus('account', conta.recordId, 'ACTIVE');
              const reativaCash = JPWAlladin.cadastro.setRecordStatus('cashaccount', brl.recordId, 'ACTIVE');
              const bloqueiaDeNovo = JPWAlladin.cadastro.setRecordStatus('account', conta.recordId, 'INACTIVE');
              const trocaMoeda = JPWAlladin.cadastro.editCashAccount(usd.recordId, {currency:'BRL'});
              const cashUsd = S.alladin.cashAccounts.filter(x => x.cashAccountId === usd.recordId)[0] || {};
              return { brl2, eur, bloqueada, liberada, orfa, statusInvalido,
                       reativaSobInativa, reativaConta, reativaCash, bloqueiaDeNovo,
                       trocaMoeda, moedaGravada: cashUsd.currency,
                       registros: S.alladin.cashAccounts.length };
            }""")
            if not (r["brl2"]["ok"] and "DUPLICADO_MOEDA_NA_CONTA" in r["brl2"]["avisos"]):
                falhas.append(f"U16 segunda cash account BRL deveria avisar sem bloquear: {r['brl2']!r}")
            if not (r["eur"]["ok"] and "MOEDA_FORA_DO_SUPORTE_DE_RUNTIME" in r["eur"]["avisos"]):
                falhas.append(f"U16 EUR e valido no schema com aviso de runtime: {r['eur']!r}")
            if r["bloqueada"]["ok"] or r["bloqueada"]["erro"] != "ALD_ACCOUNT_COM_CASHACCOUNT_ATIVA":
                falhas.append(f"U16 conta com cash account ativa nao pode inativar: {r['bloqueada']!r}")
            if not r["liberada"]["ok"]:
                falhas.append(f"U16 conta sem cash account ativa deveria inativar: {r['liberada']!r}")
            if r["orfa"]["ok"] or r["orfa"]["erro"] != "ALD_ACCOUNT_INATIVA":
                falhas.append(f"U16 cash account em conta inativa deveria recusar: {r['orfa']!r}")
            if r["statusInvalido"]["ok"] or r["statusInvalido"]["erro"] != "ALD_RECORD_STATUS_INVALIDO":
                falhas.append(f"U16 recordStatus fora do enum deveria recusar: {r['statusInvalido']!r}")
            if r["reativaSobInativa"]["ok"] or r["reativaSobInativa"]["erro"] != "ALD_ACCOUNT_INATIVA":
                falhas.append(f"U16 cash account NAO pode reativar sob conta inativa: {r['reativaSobInativa']!r}")
            if not (r["reativaConta"]["ok"] and r["reativaCash"]["ok"]):
                falhas.append(f"U16 reativacao na ordem correta deveria passar: {r!r}")
            if r["bloqueiaDeNovo"]["ok"] or r["bloqueiaDeNovo"]["erro"] != "ALD_ACCOUNT_COM_CASHACCOUNT_ATIVA":
                falhas.append(f"U16 par reativado deveria voltar a bloquear a inativacao: {r['bloqueiaDeNovo']!r}")
            if not (r["trocaMoeda"]["ok"] and r["moedaGravada"] == "BRL"):
                falhas.append(f"U16 correcao de moeda da cash account falhou: {r['trocaMoeda']!r} / {r['moedaGravada']}")
            if "DUPLICADO_MOEDA_NA_CONTA" not in r["trocaMoeda"]["avisos"]:
                falhas.append(f"U16 troca para moeda ja existente deveria avisar: {r['trocaMoeda']!r}")
            if r["registros"] != 4:
                falhas.append(f"U16 cash accounts esperadas 4, vieram {r['registros']}")
        executar(falhas, "U16", u16)

        # U17 — DC-3: nenhuma natureza representa caixa; lifecycle nao e editavel
        def u17():
            reset_agregado()
            r = ev("""() => {
              const cat = JPWAlladin.catalogos();
              const natures = cat.starter.nature.join('|');
              const caixas = ['CAIXA_FISICO','CASH','Dinheiro','ESPECIE','numerario','caixa de ferramentas']
                 .map(n => JPWAlladin.cadastro.addAsset({name:'X', nature:n, recordMode:'INDIVIDUAL'}));
              const a = JPWAlladin.cadastro.addAsset({name:'Bem', nature:'BEM_PESSOAL', recordMode:'INDIVIDUAL'});
              const life = JPWAlladin.cadastro.editAsset(a.recordId, {lifecycleStatus:'SOLD'});
              const rec = S.alladin.assets[0];
              return { natures, life, lifeGravado:rec.lifecycleStatus,
                       caixas:caixas.map(x => x.erro),
                       lifecycleEnum:cat.fechados.lifecycleStatus.join('|') };
            }""")
            if r["natures"] != "BEM_PESSOAL|BEM_DURAVEL|BEM_PRODUTIVO|IMOVEL|DIREITO|COLECAO|OUTRO":
                falhas.append(f"U17 catalogo de naturezas divergiu do contrato: {r['natures']}")
            if r["caixas"] != ["ALD_NATURE_DE_CAIXA_PROIBIDA"] * 6:
                falhas.append(f"U17 DC-3 nao e invariante — caixa entrou como Asset: {r['caixas']!r}")
            if r["life"]["ok"] or r["life"]["erro"] != "ALD_LIFECYCLE_NAO_EDITAVEL_NO_C2":
                falhas.append(f"U17 lifecycleStatus nao pode ser editado no C2: {r['life']!r}")
            if r["lifeGravado"] != "ACTIVE":
                falhas.append(f"U17 lifecycleStatus foi alterado: {r['lifeGravado']}")
            if r["lifecycleEnum"] != "ACTIVE|SOLD|DISPOSED|DONATED|LOST|WRITTEN_OFF":
                falhas.append(f"U17 enum de lifecycle divergiu da spec §10.8: {r['lifecycleEnum']}")
        executar(falhas, "U17", u17)

        # U18 — nenhum ato cadastral escreve sob bloqueio de modulo
        def u18():
            reset_agregado()
            r = ev("""() => {
              S.alladin.schemaVersion = 5;
              const antes = JSON.stringify(S.alladin);
              window.__stub.saves = 0;
              const res = [
                JPWAlladin.cadastro.addInstrument({name:'X', symbol:'X', currency:'BRL',
                   instrumentFamily:'EQUITY_LIKE', assetClass:'RENDA_VARIAVEL'}),
                JPWAlladin.cadastro.addAsset({name:'X', nature:'IMOVEL', recordMode:'INDIVIDUAL'}),
                JPWAlladin.cadastro.addAccount({name:'X', institution:'Y', accountType:'BANK'}),
                JPWAlladin.cadastro.setRecordStatus('account', 'qualquer', 'INACTIVE'),
              ];
              const igual = JSON.stringify(S.alladin) === antes;
              S.alladin.schemaVersion = 2;
              return { erros:res.map(x => x.erro), saves:window.__stub.saves, igual };
            }""")
            if r["erros"] != ["READ_ONLY_FUTURE_SCHEMA"] * 4:
                falhas.append(f"U18 ato cadastral escapou do fail-closed: {r['erros']!r}")
            if r["saves"] != 0 or not r["igual"]:
                falhas.append(f"U18 houve escrita sob bloqueio: saves={r['saves']} igual={r['igual']}")
        executar(falhas, "U18", u18)


        # U19 — varredura tabular dos ramos de validacao de forma
        def u19():
            reset_agregado()
            r = ev("""() => {
              const C = JPWAlladin.cadastro;
              const base = {name:'X', nature:'IMOVEL', recordMode:'INDIVIDUAL'};
              const inst = {name:'X', symbol:'X', currency:'BRL', instrumentFamily:'EQUITY_LIKE', assetClass:'RENDA_VARIAVEL'};
              return {
                currency:      C.addInstrument({...inst, currency:'brl'}).erro,
                currencyForma: C.addInstrument({...inst, currency:'BRLL'}).erro,
                extIds:        C.addInstrument({...inst, externalIdentifiers:[1,2]}).erro,
                symbolTeto:    C.addInstrument({...inst, symbol:'X'.repeat(33)}).erro,
                assetClass:    C.addInstrument({...inst, assetClass:''}).erro,
                nature:        C.addAsset({...base, nature:''}).erro,
                tags:          C.addAsset({...base, tags:'nao-e-lista'}).erro,
                tagVazia:      C.addAsset({...base, tags:['']}).erro,
                data:          C.addAsset({...base, acquisitionDate:'15/03/2020'}).erro,
                ownersLista:   C.addAsset({...base, owners:'nao-e-lista'}).erro,
                ownerObjeto:   C.addAsset({...base, owners:['Joao']}).erro,
                ownerNome:     C.addAsset({...base, owners:[{name:'', shareBp:100}]}).erro,
                isSelfTruthy:  C.addAsset({...base, owners:[{name:'A', shareBp:100, isSelf:1}]}).erro,
                textoLongo:    C.addAsset({...base, category:'c'.repeat(81)}).erro,
                institution:   C.addAccount({name:'X', institution:'', accountType:'BANK'}).erro,
                accountType:   C.addAccount({name:'X', institution:'Y', accountType:''}).erro,
                tipoDesconh:   C.setRecordStatus('portfolio', 'x', 'ACTIVE').erro,
                registros:     S.alladin.instruments.length + S.alladin.assets.length + S.alladin.accounts.length,
              };
            }""")
            esperado = {
                "currency":"ALD_CURRENCY_INVALIDA", "currencyForma":"ALD_CURRENCY_INVALIDA",
                "extIds":"ALD_EXTERNAL_IDENTIFIERS_INVALIDOS", "symbolTeto":"ALD_SYMBOL_INVALIDO",
                "assetClass":"ALD_ASSET_CLASS_INVALIDA", "nature":"ALD_NATURE_INVALIDA",
                "tags":"ALD_TAGS_INVALIDAS", "tagVazia":"ALD_TAGS_INVALIDAS",
                "data":"ALD_ACQUISITION_DATE_INVALIDA", "ownersLista":"ALD_OWNERS_NAO_E_LISTA",
                "ownerObjeto":"ALD_OWNER_INVALIDO", "ownerNome":"ALD_OWNER_NOME_INVALIDO",
                "isSelfTruthy":"ALD_ISSELF_NAO_BOOLEANO", "textoLongo":"ALD_CAMPO_TEXTO_INVALIDO",
                "institution":"ALD_INSTITUTION_INVALIDA", "accountType":"ALD_ACCOUNT_TYPE_INVALIDO",
                "tipoDesconh":"ALD_TIPO_DESCONHECIDO",
            }
            for chave, err in esperado.items():
                if r[chave] != err:
                    falhas.append(f"U19 '{chave}': esperado {err}, veio {r[chave]!r}")
            if r["registros"] != 0:
                falhas.append(f"U19 registro invalido ENTROU no agregado: {r['registros']}")
        executar(falhas, "U19", u19)

        # U20 — persistencia recusada RESTAURA o agregado (achado da auditoria)
        def u20():
            reset_agregado()
            r = ev("""() => {
              const conta = JPWAlladin.cadastro.addAccount({name:'XP', institution:'XP', accountType:'BROKERAGE'});
              const antes = JSON.stringify(S.alladin);
              const logAntes = JSON.stringify(S.dataGovernance.changeLog);
              window.__stub.saveResult = false;
              const asset = JPWAlladin.cadastro.addAsset({name:'Fantasma', nature:'IMOVEL', recordMode:'INDIVIDUAL'});
              const edit = JPWAlladin.cadastro.editAccount(conta.recordId, {name:'XP Editada'});
              const status = JPWAlladin.cadastro.setRecordStatus('account', conta.recordId, 'INACTIVE');
              window.__stub.saveResult = true;
              return { contaOk:conta.ok && antes.indexOf(conta.recordId) >= 0,
                       igual: JSON.stringify(S.alladin) === antes,
                       logRestaurado: JSON.stringify(S.dataGovernance.changeLog) === logAntes,
                       assets: S.alladin.assets.length,
                       nome: S.alladin.accounts[0].name,
                       status: S.alladin.accounts[0].recordStatus,
                       vereditos:[asset.ok, edit.ok, status.ok],
                       erros:[asset.erro, edit.erro, status.erro] };
            }""")
            if not r["contaOk"]:
                falhas.append("U20 caminho de escrita morto — comparacao seria tautologia")
            if not r["igual"]:
                falhas.append("U20 save() recusado deixou o agregado MUTADO — registro fantasma")
            if r["assets"] != 0 or r["nome"] != "XP" or r["status"] != "ACTIVE":
                falhas.append(f"U20 mutacao sobreviveu a persistencia recusada: {r!r}")
            if not r["logRestaurado"]:
                falhas.append("U20 changeLog manteve entrada de ato que nao foi persistido")
            if any(r["vereditos"]) or r["erros"] != ["persistencia recusada"] * 3:
                falhas.append(f"U20 veredito de persistencia incorreto: {r!r}")
        executar(falhas, "U20", u20)

        # U23 — rollback do changeLog NO TETO (ALD-03-H0 · D-1). O invariante e a
        # SEQUENCIA anterior, nao o comprimento: dgLogChange reatribui o array ao
        # podar, e no teto 401->slice->400 devolve o mesmo comprimento de antes.
        # Restaurar por comprimento passaria neste ponto exato com o log corrompido.
        # O caso de controle abaixo do teto existe para que a falha, se vier, acuse
        # o teto e nao o mecanismo inteiro.
        def u23():
            for rotulo, quantas in (("controle abaixo do teto", 10), ("NO TETO", 400)):
                reset_agregado()
                r = ev("""(quantas) => {
                  S.dataGovernance.changeLog.length = 0;
                  for(let i=0;i<quantas;i++) dgLogChange('seed','pre'+i,'r'+i,'L'+i);
                  const antes = JSON.stringify(S.dataGovernance.changeLog);
                  const primeiroAntes = S.dataGovernance.changeLog[0].action;
                  const qtdAntes = S.dataGovernance.changeLog.length;
                  window.__stub.saveResult = false;
                  const r = JPWAlladin.cadastro.addAccount({name:'Fantasma', institution:'F', accountType:'BANK'});
                  window.__stub.saveResult = true;
                  const log = S.dataGovernance.changeLog;
                  return { verdicto:[r.ok, r.persistido],
                           identico: JSON.stringify(log) === antes,
                           qtd: log.length, qtdAntes: qtdAntes,
                           primeiro: log[0] ? log[0].action : null, primeiroAntes: primeiroAntes,
                           ghost: log.some(e => e.action === 'account_add'),
                           ordem: log.every((e,i) => e.action === 'pre'+i),
                           agregadoLimpo: S.alladin.accounts.length === 0 };
                }""", quantas)
                if r["verdicto"] != [False, False]:
                    falhas.append(f"U23 [{rotulo}]: o ato deveria ser recusado ({r['verdicto']})")
                if not r["identico"]:
                    falhas.append(f"U23 [{rotulo}]: o changeLog NAO voltou ao conteudo anterior "
                                  f"(antes {r['qtdAntes']}, depois {r['qtd']}, ghost={r['ghost']}, "
                                  f"primeiro {r['primeiroAntes']!r}->{r['primeiro']!r})")
                if r["ghost"]:
                    falhas.append(f"U23 [{rotulo}]: entrada FANTASMA de ato nao persistido sobreviveu no log")
                if r["primeiro"] != r["primeiroAntes"]:
                    falhas.append(f"U23 [{rotulo}]: a entrada legitima mais antiga foi evicta "
                                  f"({r['primeiroAntes']!r} -> {r['primeiro']!r})")
                if not r["ordem"]:
                    falhas.append(f"U23 [{rotulo}]: a ordem do log nao foi preservada")
                if r["qtd"] != r["qtdAntes"]:
                    falhas.append(f"U23 [{rotulo}]: quantidade divergente ({r['qtdAntes']} -> {r['qtd']})")
                if not r["agregadoLimpo"]:
                    falhas.append(f"U23 [{rotulo}]: o agregado nao foi restaurado")
        executar(falhas, "U23", u23)

        # U21 — cobertura dos edits: identidade e metadados sobrevivem
        def u21():
            reset_agregado()
            r = ev("""() => {
              const conta = JPWAlladin.cadastro.addAccount({name:'XP', institution:'XP', accountType:'BROKERAGE'});
              const antes = S.alladin.accounts[0];
              const criado = antes.createdAt;
              const ed = JPWAlladin.cadastro.editAccount(conta.recordId,
                 {name:'XP Investimentos', institution:'XP CCTVM', accountType:'BANK'});
              const prot = JPWAlladin.cadastro.editAccount(conta.recordId, {createdAt:'2000-01-01'});
              const depois = S.alladin.accounts[0];
              const asset = JPWAlladin.cadastro.addAsset({name:'Bem', nature:'IMOVEL', recordMode:'INDIVIDUAL',
                 strategicPurpose:'INVESTIMENTO', owners:[{name:'Joao', shareBp:10000, isSelf:true}]});
              const edAsset = JPWAlladin.cadastro.editAsset(asset.recordId, {name:'Bem editado', tags:['novo']});
              const bem = S.alladin.assets[0];
              return { ed, prot, id:depois.accountId === conta.recordId, criado:depois.createdAt === criado,
                       campos:[depois.name, depois.institution, depois.accountType],
                       status:depois.recordStatus,
                       edAsset, bemNome:bem.name, bemTags:JSON.stringify(bem.tags),
                       bemOwners:JSON.stringify(bem.owners), bemPurpose:bem.strategicPurpose,
                       bemLife:bem.lifecycleStatus };
            }""")
            if not r["ed"]["ok"] or r["campos"] != ["XP Investimentos", "XP CCTVM", "BANK"]:
                falhas.append(f"U21 editAccount nao aplicou os campos: {r!r}")
            if not (r["id"] and r["criado"] and r["status"] == "ACTIVE"):
                falhas.append(f"U21 edicao alterou identidade/carimbo/status: {r!r}")
            if r["prot"]["ok"] or not str(r["prot"]["erro"]).startswith("ALD_CAMPO_PROTEGIDO"):
                falhas.append(f"U21 createdAt deveria ser recusado explicitamente: {r['prot']!r}")
            if not r["edAsset"]["ok"] or r["bemNome"] != "Bem editado" or r["bemTags"] != '["novo"]':
                falhas.append(f"U21 editAsset nao aplicou os campos: {r!r}")
            if r["bemOwners"] != '[{"name":"Joao","shareBp":10000,"isSelf":true}]':
                falhas.append(f"U21 edicao parcial perdeu owners: {r['bemOwners']}")
            if r["bemPurpose"] != "INVESTIMENTO" or r["bemLife"] != "ACTIVE":
                falhas.append(f"U21 edicao perdeu strategicPurpose ou mexeu no lifecycle: {r!r}")
        executar(falhas, "U21", u21)

        browser.close()

    if falhas:
        print("alladin_unit_test FALHOU")
        for f in falhas:
            print(" -", f)
        return 1
    print("alladin_unit_test PASS (U1-U21: moeda, ids, gate, owners/isSelf, regimes, cripto, symbolHistory, falha parcial, integridade; Chromium isolado, zero rede, zero DOM)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
