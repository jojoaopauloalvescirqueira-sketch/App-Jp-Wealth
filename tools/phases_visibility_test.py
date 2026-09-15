#!/usr/bin/env python3
"""V11: six current containers and four LEGACY containers remain recordable.
Unlock flags and quarantine do not disable recording. Rendering preserves all
state and storage; the old guarded visual contract was explicitly superseded.
"""

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import os
import socket
import sys
import threading

import notes_launcher_test as launcher
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
    context = browser.new_context(viewport={"width":1440,"height":900}, service_workers="block", reduced_motion="reduce")
    page, observed = launcher.prepare(context, url)
    page.evaluate("() => {window.confirm=()=>true;window.prompt=()=> 'Correção sintética justificada';}")
    return context, page, observed["pageerror"]


# Le o painel DEPOIS de renderizar, sem tocar em estado. Devolve, por cartao:
# indice, rotulo do crachao, se tem corpo com controles, e se tem botao MIGRAR.
LER_PAINEL = """
() => {
  const antes = JSON.stringify({state:S,raw:localStorage.getItem(LSKEY),writes:__notesLauncherWrites.length});
  renderPhases();
  const depois = JSON.stringify({state:S,raw:localStorage.getItem(LSKEY),writes:__notesLauncherWrites.length});
  const cont = document.getElementById('phaseContainer');
  const cartoes = [...cont.querySelectorAll('.phase[data-phase]')].map(el => {
    const corpo = el.querySelector('.phase-body');
    const controles = corpo ? [...corpo.querySelectorAll('input,select,textarea,button')] : [];
    return {
      idx: +el.dataset.phase,
      cracha: (el.querySelector('.badge')||{}).textContent || '',
      ativa: !!el.querySelector('.here'),
      controles: controles.length,
      habilitados: controles.filter(c => !c.disabled).length,
      texto: el.textContent || ''
    };
  });
  return {
    antes, depois,
    ativaIdx: getMaxUnlockedIdx(),
    cartoes,
    migrar: [...cont.querySelectorAll('[data-migrate]')].map(b => +b.dataset.migrate)
  };
}
"""


def montar(page, liberadas):
    """liberadas = quantas fases o Estatuto ja liberou (1..4)."""
    page.evaluate(
        """(n) => {
            S.phaseUnlocked = [true, n >= 2, n >= 3, n >= 4];
            S.quarantine = null;
        }""",
        liberadas,
    )


def checar(page, liberadas, falhas):
    montar(page, liberadas)
    r=page.evaluate(LER_PAINEL)
    expected=page.evaluate('S.phases.length')
    if [c['idx'] for c in r['cartoes']]!=list(range(expected)):
        falhas.append(f"Containers fora de ordem: {r}")
    for card in r['cartoes']:
        if card['habilitados']==0 or card['habilitados']!=card['controles']:
            falhas.append(f"Flag de unlock bloqueou registro: {card}")
    if r['migrar']:
        falhas.append(f"Questionário ainda libera grade: {r['migrar']}")
    if r['antes']!=r['depois']:
        falhas.append('Render alterou estado ou armazenamento')
    if expected==4 and not all('LEGACY' in c['cracha'] for c in r['cartoes']):
        falhas.append('Grade antiga sem identificação LEGACY')


def main():
    servidor, url = serve()
    falhas = []
    try:
        with sync_playwright() as pw:
            navegador = pw.chromium.launch(**launcher.launch_options())
            contexto, page, erros = prepare_page(navegador, url)
            for liberadas in (1, 2, 3, 4):
                checar(page, liberadas, falhas)
            page.evaluate('() => {S.phases=S.phases.slice(0,4);S.quarantine={fim:"2099-01-01"};}')
            for liberadas in (1,2,3,4):
                checar(page, liberadas, falhas)
            if erros:
                falhas.append(f"erro de pagina durante o render: {erros}")
            contexto.close()
            navegador.close()
    finally:
        servidor.shutdown()

    if falhas:
        print("FALHOU")
        for f in falhas:
            print("  - " + f)
        return 1
    print("PASS seis grades atuais e quatro LEGACY; registro disponível; render sem writes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
