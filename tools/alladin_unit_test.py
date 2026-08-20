#!/usr/bin/env python3
"""Alladin ALD-01 C1 — testes UNITARIOS da Foundation Infrastructure (HD-5 opcao A).

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
var S = { alladin: { schemaVersion: 1, reportingCurrency: 'BRL',
                     instruments: [], assets: [], accounts: [], cashAccounts: [] } };
function save(){ window.__stub.saves += 1; return window.__stub.saveResult; }
function dgLogChange(entity, action, recordId, label){
  window.__stub.logs.push({ entity: entity, action: action, recordId: recordId, label: label });
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
              S.alladin.schemaVersion = 3;
              window.__stub.saves = 0; window.__stub.logs = [];
              let fnRodou = false;
              const res = aldMutate('teste_ato', () => { fnRodou = true; return {recordId: 'x'}; });
              const compat = JPWAlladin.compat();
              S.alladin.schemaVersion = 1;
              return { res, fnRodou, saves: window.__stub.saves,
                       logs: window.__stub.logs.length, compat };
            }""")
            if r["res"].get("erro") != "READ_ONLY_FUTURE_SCHEMA" or r["res"].get("ok") is not False:
                falhas.append(f"U8 recusa: {r['res']!r}")
            if r["fnRodou"] or r["saves"] != 0 or r["logs"] != 0:
                falhas.append(f"U8 vazamento sob bloqueio: fn={r['fnRodou']} saves={r['saves']} logs={r['logs']}")
            c = r["compat"]
            if not (c["readOnly"] is True and c["storedSchemaVersion"] == 3
                    and c["supportedSchemaVersion"] == 1 and c["reason"] == "READ_ONLY_FUTURE_SCHEMA"):
                falhas.append(f"U8 compat: {c!r}")
            # versao futura como STRING de digitos ('2') tambem e fail-closed
            r2 = ev("""() => {
              S.alladin.schemaVersion = '2';
              const compat = JPWAlladin.compat();
              const ato = aldMutate('probe', () => ({recordId: 'x'}));
              S.alladin.schemaVersion = 1;
              return { readOnly: compat.readOnly, stored: compat.storedSchemaVersion,
                       erro: ato.erro };
            }""")
            if not (r2["readOnly"] is True and r2["stored"] == 2
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

        browser.close()

    if falhas:
        print("alladin_unit_test FALHOU")
        for f in falhas:
            print(" -", f)
        return 1
    print("alladin_unit_test PASS (U1-U10; Chromium isolado, zero rede, zero DOM)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
