#!/usr/bin/env python3
"""Caracterizacao da Camada 3 — Historico de Operacoes Unicas.

O Historico e memoria institucional: a propriedade mais importante nao e
"mostra os numeros certos", e sim que CONSULTAR nao altera nada. Navegar,
filtrar, ordenar, buscar, abrir e fechar detalhe tem de deixar o estado
financeiro identico ao inicial.

A segunda propriedade e epistemologica: desconhecido nao vira zero. Um registro
sem duracao sai da mediana de duracao e continua contando no total de operacoes.

Todas as fixtures sao SINTETICAS.
"""

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import os
import socket
import threading

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)


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


def prepare_page(browser, url):
    context = browser.new_context(viewport={"width": 1440, "height": 900})
    context.add_init_script("window.__onbShown=true;")
    page = context.new_page()
    observed = {"pageerror": [], "console": []}
    page.on("pageerror", lambda e: observed["pageerror"].append(str(e)))
    page.on("console", lambda m: observed["console"].append(m.text) if m.type == "error" else None)
    page.route(
        "**/*",
        lambda route: route.continue_()
        if "127.0.0.1" in route.request.url
        else route.fulfill(status=200, content_type="application/json", body="{}"),
    )
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_function("() => !!window.JPWHistoryUI && !!window.JPWExec")
    return context, page, observed


# Tres registros: um positivo com duracao, um negativo SEM duracao (openedAt
# desconhecido) e um neutro com integridade degradada.
SEMEAR = """
  window.__semearHist = () => {
    S.operationHistory = {schemaVersion:1, records:[
      {schemaVersion:1, operationId:'op_aaa', instrument:'EURUSD', direction:'BUY',
       openedAt:'2026-05-01T10:00:00.000Z', openedAtSource:'genesis_transition',
       closedAt:'2026-05-11T10:00:00.000Z', closedAtSource:'formal_confirmation',
       referenceBalance:10000, referenceBalanceType:'cycle_initial_balance',
       netResult:500, defenseCount:2, defenseCountSource:'manual',
       maxAccountPhaseReached:1, maxAccountPhaseIntegrity:'observed',
       phaseCaptureFault:null, maxGridPhaseReached:1,
       ordersSnapshot:[{phase:1,gridIndex:0,label:'G1',par:'EURUSD',tipo:'BUY',lote:1,
                        entry:1.1,sl:1.09,tp:1.2,result:500,status:'Fechada',
                        openedAt:'2026-05-01T10:00:00.000Z',closedAt:'2026-05-11T10:00:00.000Z'}],
       finalizedAt:'2026-05-11T10:00:00.000Z'},
      {schemaVersion:1, operationId:'op_bbb', instrument:'GBPUSD', direction:'SELL',
       openedAt:null, openedAtSource:null,
       closedAt:'2026-06-20T10:00:00.000Z', closedAtSource:'formal_confirmation',
       referenceBalance:10000, referenceBalanceType:'cycle_initial_balance',
       netResult:-300, defenseCount:1, defenseCountSource:'manual',
       maxAccountPhaseReached:null, maxAccountPhaseIntegrity:'observed',
       phaseCaptureFault:null, maxGridPhaseReached:null,
       ordersSnapshot:[], finalizedAt:'2026-06-20T10:00:00.000Z'},
      {schemaVersion:1, operationId:'op_ccc', instrument:'EURUSD', direction:'BUY',
       openedAt:'2026-07-01T10:00:00.000Z', openedAtSource:'manual_legacy',
       closedAt:'2026-07-03T10:00:00.000Z', closedAtSource:'formal_confirmation',
       referenceBalance:10000, referenceBalanceType:'cycle_initial_balance',
       netResult:0, defenseCount:0, defenseCountSource:'manual',
       maxAccountPhaseReached:2, maxAccountPhaseIntegrity:'degraded',
       phaseCaptureFault:{at:'2026-07-02T00:00:00.000Z', reason:'falha sintetica'},
       maxGridPhaseReached:2, ordersSnapshot:[], finalizedAt:'2026-07-03T10:00:00.000Z'}
    ]};
    S.params.saldoIni = 10000;
    S.phases.forEach((ph,i) => { ph.orders = emptyOrders([5,4,3,2][i]); });
    S.activeOperation = null;
    // Estado de APRESENTACAO tambem e zerado: sem isto um caso herdaria o
    // detalhe aberto do anterior e o proximo Enter FECHARIA em vez de abrir —
    // foi exatamente assim que o teste de teclado falhou na primeira execucao.
    histState.instrument='all'; histState.direction='all'; histState.result='all';
    histState.query=''; histState.selected=null;
  };
  window.__fotoFin = () => JSON.stringify({
    ciclo: S.cycleRealizado, params: S.params, phases: S.phases,
    registros: S.operationHistory.records, activeOperation: S.activeOperation,
    logs: S.transitionLog.length, unlocked: S.phaseUnlocked
  });
"""


def run_empty_state(page):
    """Sem operacoes: diz isso, e nao fabrica cards com zeros."""
    r = page.evaluate(
        """() => {
          S.operationHistory = {schemaVersion:1, records:[]};
          JPWHistoryUI.render();
          const root = document.getElementById('execHistory');
          return {txt: root.textContent, stats: root.querySelectorAll('.hist-stat').length};
        }"""
    )
    assert "Sem operações finalizadas" in r["txt"], f"estado vazio nao declarado: {r['txt'][:120]}"
    assert r["stats"] == 0, (
        f"{r['stats']} cards estatisticos fabricados para historico vazio — "
        "0/0%/duracao zero leriam como observacao"
    )


def run_stats_denominators(page):
    """Desconhecido sai da metrica que o exige, nao do total."""
    r = page.evaluate(
        """() => {
          __semearHist();
          JPWHistoryUI.render();
          const root = document.getElementById('execHistory');
          const cards = [...root.querySelectorAll('.hist-stat')].map(c => ({
            l: c.querySelector('.hist-stat-l').textContent,
            v: c.querySelector('.hist-stat-v').textContent,
            n: c.querySelector('.hist-stat-n') ? c.querySelector('.hist-stat-n').textContent : null
          }));
          return {cards, linhas: root.querySelectorAll('.hist-row').length};
        }"""
    )
    por = {c["l"]: c for c in r["cards"]}
    assert por["Operações finalizadas"]["v"] == "3", (
        f"total de operacoes divergente: {por['Operações finalizadas']['v']} — "
        "registro sem duracao NAO pode sumir do total"
    )
    assert por["Duração mediana"]["n"] == "n = 2", (
        f"denominador da duracao errado: {por['Duração mediana']['n']!r} — "
        "op_bbb nao tem openedAt e deve sair SO desta metrica"
    )
    assert por["Defesas medianas"]["n"] == "n = 3", (
        f"denominador das defesas errado: {por['Defesas medianas']['n']!r}"
    )
    assert "1 de 3" in (por["Taxa de operações positivas"]["n"] or ""), (
        f"taxa sem par explicito: {por['Taxa de operações positivas']}"
    )
    assert r["linhas"] == 3, f"lista nao mostrou as 3 operacoes: {r['linhas']}"


def run_degraded_flagged(page):
    """Integridade degradada aparece e a operacao continua nas estatisticas."""
    r = page.evaluate(
        """() => {
          __semearHist();
          JPWHistoryUI.render();
          const root = document.getElementById('execHistory');
          [...root.querySelectorAll('.hist-row')].find(
            tr => tr.dataset.histId === 'op_ccc').click();
          const det = root.querySelector('[data-hist-detail="op_ccc"]');
          const total = root.querySelector('.hist-stat .hist-stat-v').textContent;
          return {temMarca: !!det.querySelector('.hist-degradada'),
                  txt: det.querySelector('.hist-degradada') ? det.querySelector('.hist-degradada').textContent : '',
                  total};
        }"""
    )
    assert r["temMarca"], "registro degradado nao foi sinalizado no detalhe"
    assert "degradada" in r["txt"], f"marca sem o termo esperado: {r['txt']!r}"
    assert r["total"] == "3", (
        "a operacao degradada foi excluida das estatisticas — a lacuna e de uma "
        "evidencia auxiliar, nao do resultado financeiro"
    )


def run_return_from_snapshot(page):
    """Retorno vem do snapshot, nao do saldo atual."""
    r = page.evaluate(
        """() => {
          __semearHist();
          JPWHistoryUI.render();
          const pega = () => [...document.querySelectorAll('#execHistory .hist-row')]
            .find(tr => tr.dataset.histId === 'op_aaa').cells[8].textContent;
          const antes = pega();
          S.params.saldoIni = 999999;      // saldo atual muda
          JPWHistoryUI.render();
          return {antes, depois: pega()};
        }"""
    )
    assert r["antes"] == r["depois"], (
        f"retorno historico mudou com o saldo atual: {r['antes']} -> {r['depois']} — "
        "o denominador tem de vir do snapshot"
    )
    assert r["antes"] == "5.00%", f"retorno inesperado: {r['antes']}"


def run_filters_and_search(page):
    """Filtros e busca recortam a lista sem tocar os registros."""
    r = page.evaluate(
        """() => {
          __semearHist();
          JPWHistoryUI.render();
          const n = () => document.querySelectorAll('#execHistory .hist-row').length;
          const sel = (id, v) => { const e = document.getElementById(id); e.value = v;
                                   e.dispatchEvent(new Event('change')); };
          const todos = n();
          sel('histInstrument', 'EURUSD');   const porInstr = n();
          sel('histInstrument', 'all');
          sel('histResult', 'Negativa');     const porRes = n();
          sel('histResult', 'all');
          const q = document.getElementById('histQuery');
          q.value = 'op_ccc'; q.dispatchEvent(new Event('input'));
          const porBusca = n();
          q.value = ''; q.dispatchEvent(new Event('input'));
          return {todos, porInstr, porRes, porBusca, final: n(),
                  registros: S.operationHistory.records.length};
        }"""
    )
    assert r["todos"] == 3 and r["final"] == 3, f"lista nao voltou ao total: {r}"
    assert r["porInstr"] == 2, f"filtro de instrumento: {r['porInstr']}"
    assert r["porRes"] == 1, f"filtro de resultado: {r['porRes']}"
    assert r["porBusca"] == 1, f"busca: {r['porBusca']}"
    assert r["registros"] == 3, "filtrar alterou os registros"


def run_sorted_desc(page):
    """Ordenacao padrao: mais recente primeiro."""
    r = page.evaluate(
        """() => {
          __semearHist();
          JPWHistoryUI.render();
          return [...document.querySelectorAll('#execHistory .hist-row')]
            .map(tr => tr.dataset.histId);
        }"""
    )
    assert r == ["op_ccc", "op_bbb", "op_aaa"], f"ordem nao e closedAt DESC: {r}"


def run_zero_financial_mutation(page):
    """FLUXO COMPLETO de consulta: estado financeiro final === inicial."""
    r = page.evaluate(
        """() => {
          __semearHist();
          save();                       // parte de um estado ja persistido
          const antes = __fotoFin();
          // navegar
          JPWExec.ui.selectView('history');
          JPWHistoryUI.render();
          // filtrar
          const sel = (id,v)=>{const e=document.getElementById(id); e.value=v; e.dispatchEvent(new Event('change'));};
          sel('histInstrument','EURUSD');
          sel('histDirection','BUY');
          sel('histResult','Positiva');
          // pesquisar
          const q=document.getElementById('histQuery');
          q.value='op_'; q.dispatchEvent(new Event('input'));
          // abrir detalhe
          const linha=document.querySelector('#execHistory .hist-row');
          if(linha) linha.click();
          // fechar detalhe
          const linha2=document.querySelector('#execHistory .hist-row');
          if(linha2) linha2.click();
          // limpar filtros
          sel('histInstrument','all'); sel('histDirection','all'); sel('histResult','all');
          const q2=document.getElementById('histQuery'); q2.value=''; q2.dispatchEvent(new Event('input'));
          // trocar de submenu e voltar
          JPWExec.ui.selectView('overview');
          JPWExec.ui.selectView('history');
          return {antes, depois: __fotoFin()};
        }"""
    )
    assert r["antes"] == r["depois"], (
        "consultar o Historico MUTOU estado financeiro — navegar, filtrar, "
        "ordenar, buscar e abrir detalhe devem ser somente leitura"
    )


def run_detail_is_read_only(page):
    """Detalhe nao oferece editar, excluir ou corrigir."""
    r = page.evaluate(
        """() => {
          __semearHist();
          JPWHistoryUI.render();
          document.querySelector('#execHistory .hist-row').click();
          const det = document.querySelector('#execHistory .hist-detail');
          return {
            inputs: det.querySelectorAll('input,select,textarea,button').length,
            txt: det.textContent
          };
        }"""
    )
    assert r["inputs"] == 0, (
        f"o detalhe oferece {r['inputs']} controle(s) editaveis — historico "
        "institucional nao e planilha livre"
    )
    assert "somente leitura" in r["txt"], "o detalhe nao declara ser somente leitura"


def run_keyboard_and_semantics(page):
    """Tabelas semanticas e linha operavel por teclado."""
    r = page.evaluate(
        """() => {
          __semearHist();
          JPWHistoryUI.render();
          const root = document.getElementById('execHistory');
          const tr = root.querySelector('.hist-row');
          tr.focus();
          tr.dispatchEvent(new KeyboardEvent('keydown',{key:'Enter',bubbles:true}));
          const abriu = !!root.querySelector('.hist-detail');
          return {
            ths: root.querySelectorAll('.hist-table th[scope="col"]').length,
            role: tr.getAttribute('role'),
            tabindex: tr.getAttribute('tabindex'),
            abriu
          };
        }"""
    )
    assert r["ths"] >= 9, f"cabecalhos sem scope: {r['ths']}"
    assert r["role"] == "button" and r["tabindex"] == "0", f"linha nao operavel por teclado: {r}"
    assert r["abriu"], "Enter nao abriu o detalhe"


def main():
    server, url = serve()
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            context, page, observed = prepare_page(browser, url)
            page.evaluate(SEMEAR)
            run_empty_state(page)
            run_stats_denominators(page)
            run_degraded_flagged(page)
            run_return_from_snapshot(page)
            run_filters_and_search(page)
            run_sorted_desc(page)
            run_zero_financial_mutation(page)
            run_detail_is_read_only(page)
            run_keyboard_and_semantics(page)
            assert not observed["pageerror"], f"pageerror: {observed['pageerror']}"
            assert not observed["console"], f"console error: {observed['console']}"
            context.close()
            browser.close()
    finally:
        server.shutdown()
    print("OPERATION HISTORY TEST PASS")


if __name__ == "__main__":
    main()
