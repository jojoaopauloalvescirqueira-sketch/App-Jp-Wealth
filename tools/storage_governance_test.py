#!/usr/bin/env python3
"""Governança de armazenamento (JPW-HJFGDE) — schema dataGovernance, nomenclatura
progressiva, sequência só-após-sucesso, colisão, diálogo de recuperação (nunca fallback
silencioso), termo de responsabilidade no onboarding, aviso de 30 dias, migração de base
legada, wipe → DEFAULT_START_ROUTE e limpeza do handle em IndexedDB.

O File System Access API real (showDirectoryPicker) exige gesto + diálogo nativo e NÃO é
automatizável — o acesso à pasta é coberto por mocks de dgFsStatus/dgFsFileExists/
dgFsWriteFile (a lógica de orquestração é o que se testa) e por checklist manual
(docs/architecture/DB-STORAGE-GOVERNANCE.md)."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import os, socket, threading
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)

VIEWPORT = {'width': 1440, 'height': 900}

class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *_): pass

def serve():
    with socket.socket() as s:
        s.bind(('127.0.0.1', 0)); port = s.getsockname()[1]
    server = ThreadingHTTPServer(('127.0.0.1', port), Quiet)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f'http://127.0.0.1:{port}/'

def assert_no_errors(observed):
    errors = [x for x in observed['console'] if x[0] == 'error']
    assert not errors and not observed['pageerror'], {'console': errors, 'pageerror': observed['pageerror']}

def prepare_page(origem, url, mute_dialogs=True):
    # `origem` aceita um Browser OU um BrowserContext. A distinção importa: Browser
    # .new_page() cria um contexto isolado por página (storage zerado a cada chamada),
    # enquanto páginas abertas de um mesmo BrowserContext compartilham localStorage e
    # IndexedDB — é isso que permite testar persistência entre sessões (seção 8).
    # viewport é propriedade do contexto: Browser.new_page() aceita o argumento (cria o
    # contexto na hora), BrowserContext.new_page() não — lá ele foi definido em new_context().
    ehBrowser = hasattr(origem, 'new_context')
    page = origem.new_page(viewport=VIEWPORT) if ehBrowser else origem.new_page()
    observed = {'console': [], 'pageerror': []}
    page.on('console', lambda m: observed['console'].append((m.type, m.text)))
    page.on('pageerror', lambda e: observed['pageerror'].append(str(e)))
    page.goto(url, wait_until='load')
    page.wait_for_timeout(700)
    if mute_dialogs:
        page.evaluate("() => { window.alert = () => {}; window.confirm = () => false; window.prompt = () => null; }")
    page.jpwealth_observed = observed
    return page

def main():
    server, url = serve()
    with sync_playwright() as p:
        browser = p.chromium.launch()

        # ---- 1. estado virgem: schema, etapas e rota canônica -----------------------
        page = prepare_page(browser, url)
        base = page.evaluate("""() => ({
          dg: JSON.parse(JSON.stringify(S.dataGovernance)),
          steps: ONBOARDING_STEPS.map(s => s.key),
          rota: DEFAULT_START_ROUTE,
          nome: dgExportFileName(42, new Date(2026, 7, 8, 0, 26)),
        })""")
        dg = base['dg']
        assert dg['schemaVersion'] == 1 and dg['responsibility']['accepted'] is False
        assert dg['export']['lastSequence'] == 0 and dg['changeLog'] == []
        assert dg['storage']['configured'] is False
        assert base['steps'] == ['ident','instit','risk','reserves','cash','protect','database','consent']
        assert base['rota'] == 'dash'
        # §8 do ticket — exemplo literal da nomenclatura progressiva
        assert base['nome'] == 'JP_WEALTH_DB_000042_2026-08-08_0026.json', base['nome']

        # ---- 2. gate do termo de responsabilidade no onboarding ---------------------
        gate = page.evaluate("""() => {
          window.__onbShown = true; closeModal(); openOnboardingModal('new');
          document.getElementById('modalConfirm').click();
          const r1 = {
            etapa: (document.querySelector('.onb-step.active')||{}).dataset?.onbstep,
            err: document.getElementById('obDbRespErr').classList.contains('show'),
          };
          const cb = document.getElementById('obDbResp');
          cb.checked = true; cb.dispatchEvent(new Event('change'));
          r1.errSumiu = !document.getElementById('obDbRespErr').classList.contains('show');
          r1.savedPending = getSavedOnboardingStepStatus('database');
          closeModal();
          return r1;
        }""")
        assert gate['etapa'] == 'database' and gate['err'] and gate['errSumiu']
        assert gate['savedPending'] == 'pending'

        # ---- 3. exportação Downloads: sequência SÓ avança com sucesso ---------------
        fluxo = page.evaluate("""async () => {
          const r = {};
          const metaA = await exportFullBackup();               // confirm()=false → sem senhas
          r.A = {dest: metaA.destination, seq: S.dataGovernance.export.lastSequence,
                 nomeOk: /^JP_WEALTH_DB_000001_\\d{4}-\\d{2}-\\d{2}_\\d{4}\\.json$/.test(metaA.filename),
                 log: S.dataGovernance.changeLog.length};
          const origDl = dgDownloadViaAnchor;
          dgDownloadViaAnchor = () => { throw new Error('falha simulada'); };
          const metaB = await exportFullBackup();
          dgDownloadViaAnchor = origDl;
          r.B = {meta: metaB, seq: S.dataGovernance.export.lastSequence,
                 log: S.dataGovernance.changeLog.length};
          return r;
        }""")
        assert fluxo['A'] == {'dest': 'downloads', 'seq': 1, 'nomeOk': True, 'log': 1}
        assert fluxo['B'] == {'meta': None, 'seq': 1, 'log': 1}  # falha não deixa rastro

        # ---- 4. pasta autorizada simulada + colisão + diálogo de recuperação --------
        pasta = page.evaluate("""async () => {
          const r = {};
          S.dataGovernance.storage = {configured:true, folderName:'Base de Dados',
            folderDisplayPath:'Base de Dados', configuredAt:'2026-08-08T00:00'};
          const fake = {name:'Base de Dados'}, escritos = [];
          const oS = dgFsStatus, oE = dgFsFileExists, oW = dgFsWriteFile;
          dgFsStatus = async () => ({state:'authorized', handle:fake});
          let n = 0; dgFsFileExists = async () => (++n <= 2);   // seq 2 e 3 colidem
          dgFsWriteFile = async (h, nome, blob) => { escritos.push(nome); };
          const metaC = await exportFullBackup();
          r.C = {dest: metaC.destination, seq: S.dataGovernance.export.lastSequence,
                 escritos: escritos.length, seqNoNome: escritos[0].includes('000004')};
          // permissão expirada → diálogo explícito; Downloads é escolha EXPLÍCITA
          dgFsStatus = async () => ({state:'prompt', handle:fake});
          const pMeta = exportFullBackup();
          await new Promise(res => setTimeout(res, 80));
          const dlg = document.getElementById('dgRecoveryOverlay');
          r.D = {dialogo: !!dlg,
                 aviso: dlg.querySelector('.dg-dialog-warn').textContent};
          dlg.querySelector('#dgActDownloads').click();
          const metaD = await pMeta;
          r.D.dest = metaD.destination; r.D.seq = S.dataGovernance.export.lastSequence;
          // Escape cancela sem exportar nada
          dgFsStatus = async () => ({state:'denied', handle:fake});
          const pMeta2 = exportFullBackup();
          await new Promise(res => setTimeout(res, 80));
          document.dispatchEvent(new KeyboardEvent('keydown', {key:'Escape', bubbles:true}));
          const metaE = await pMeta2;
          r.E = {meta: metaE, seq: S.dataGovernance.export.lastSequence,
                 overlaySumiu: !document.getElementById('dgRecoveryOverlay')};
          dgFsStatus = oS; dgFsFileExists = oE; dgFsWriteFile = oW;
          return r;
        }""")
        assert pasta['C'] == {'dest': 'folder', 'seq': 4, 'escritos': 1, 'seqNoNome': True}
        assert pasta['D']['dialogo'] and pasta['D']['dest'] == 'downloads-exception' and pasta['D']['seq'] == 5
        assert pasta['D']['aviso'] == 'Nenhum arquivo foi exportado para a pasta configurada.'
        assert pasta['E'] == {'meta': None, 'seq': 5, 'overlaySumiu': True}

        # ---- 4b. reentrância: duplo clique NUNCA gera duas exportações --------------
        # (caça a bugs 2026-08-08: sem a guarda, duas execuções liam a mesma
        #  lastSequence e a segunda gravação sobrescrevia a primeira no caminho pasta)
        #
        # FIXTURE PRÓPRIA, deliberadamente. A corrida só é significativa no caminho de
        # PASTA — é lá que existem awaits reais entre sondar a colisão e gravar, a janela
        # em que duas execuções liam a mesma sequência. Herdar o estado da seção 4 seria
        # frágil nos dois sentidos: se a pasta viesse configurada sem handle, o fluxo
        # abriria o diálogo de recuperação e o teste travaria para sempre esperando um
        # gesto humano; se viesse desconfigurada, mediríamos o caminho de Downloads, que
        # é síncrono e não reproduz a corrida. Por isso a seção monta o cenário do zero.
        corrida = page.evaluate("""async () => {
          // (1) pré-condição consciente: pasta configurada por esta seção
          S.dataGovernance.storage = {configured:true, folderName:'Corrida',
            folderDisplayPath:'Corrida', configuredAt:new Date().toISOString()};
          // (2) filesystem mockado como AUTORIZADO — (3) nenhum diálogo nativo é aberto
          const oS=dgFsStatus, oE=dgFsFileExists, oW=dgFsWriteFile;
          const fake={name:'Corrida'}, escritos=[];
          // (4) awaits suficientes para as duas chamadas realmente se sobreporem
          const espera = ms => new Promise(r => setTimeout(r, ms));
          dgFsStatus     = async () => { await espera(15); return {state:'authorized', handle:fake}; };
          dgFsFileExists = async (h,n) => { await espera(15); return escritos.includes(n); };
          dgFsWriteFile  = async (h,n) => { await espera(40); escritos.push(n); };
          try {
            const seqAntes = S.dataGovernance.export.lastSequence;
            // (5) duas solicitações concorrentes
            const [m1, m2] = await Promise.all([exportFullBackup({quiet:true}),
                                               exportFullBackup({quiet:true})]);
            const aceita = m1 || m2, recusada = m1 ? m2 : m1;
            const seqAposCorrida = S.dataGovernance.export.lastSequence;
            // (9) a guarda foi liberada? (10) terceira exportação normal, sem lock preso
            const m3 = await exportFullBackup({quiet:true});
            return {
              exportacoesFisicas: escritos.length,              // (6) só UMA gravação
              avancoNaCorrida: seqAposCorrida - seqAntes,       // (7) sequência +1
              umaAceitaUmaRecusada: !!aceita && recusada === null, // (8) segunda recusada
              guardaLiberada: !!m3,                             // (9)
              avancoTotal: S.dataGovernance.export.lastSequence - seqAntes,
              arquivosDistintos: new Set(escritos).size === escritos.length,
              destinoPasta: !!aceita && aceita.destination === 'folder'
            };
          } finally {
            dgFsStatus=oS; dgFsFileExists=oE; dgFsWriteFile=oW;
          }
        }""")
        assert corrida == {
            'exportacoesFisicas': 2,      # 1 da corrida + 1 da terceira chamada
            'avancoNaCorrida': 1,         # a corrida avança a sequência exatamente uma vez
            'umaAceitaUmaRecusada': True,
            'guardaLiberada': True,
            'avancoTotal': 2,             # corrida (1) + terceira exportação (1)
            'arquivosDistintos': True,
            'destinoPasta': True,
        }, corrida
        # a seção devolve o estado de armazenamento como o encontrou (desconfigurado),
        # para não vazar a fixture 'Corrida' para as seções seguintes
        page.evaluate("""() => { S.dataGovernance.storage =
          {configured:false, folderName:'', folderDisplayPath:'', configuredAt:''}; }""")

        # ---- 4c. FAIL-04: autoidentificação e continuidade após restore -------------
        # O arquivo exportado precisa declarar A PRÓPRIA exportação. Antes, o payload era
        # uma fotografia do estado anterior ao incremento (arquivo 000010 com
        # lastSequence=9), e restaurá-lo fazia a base reemitir o 000010. Aqui os cenários
        # rodam SEM colisão física disponível: a continuidade tem de ser semântica.
        fail04 = page.evaluate("""async () => {
          const r = {};
          const capturado = [];
          const oDl = dgDownloadViaAnchor;
          // captura o conteúdo do arquivo em vez de baixá-lo (sem tocar em Downloads)
          // síncrono de propósito: exportFullBackup não aguarda esta chamada, então um
          // push dentro de microtask chegaria tarde demais para o teste ler
          dgDownloadViaAnchor = (nome, blob) => { capturado.push({nome, blob}); };
          try {
            // destino LIMPO: sem pasta, sem suporte a FS → nenhuma sondagem de colisão
            const oSup = dgFsSupported; dgFsSupported = () => false;
            S.dataGovernance.storage = {configured:false, folderName:'', folderDisplayPath:'', configuredAt:''};
            try {
              // T1 — identidade interna do arquivo
              const m1 = await exportFullBackup({quiet:true});
              const ult = () => capturado[capturado.length-1];
              const p1 = JSON.parse(await ult().blob.text());
              const dg1 = p1.state.dataGovernance.export;
              r.T1 = { nomeFisico: ult().nome,
                       igualAoMeta: ult().nome === m1.filename,
                       payloadSeq: dg1.lastSequence, metaSeq: m1.sequence,
                       payloadFile: dg1.lastExportFile,
                       identidadeCoerente: dg1.lastSequence === m1.sequence
                                        && dg1.lastExportFile === m1.filename
                                        && S.dataGovernance.export.lastSequence === m1.sequence
                                        && S.dataGovernance.export.lastExportFile === m1.filename };
              // T2/T3 — restore em destino vazio, caminho Downloads (sem sondagem)
              const backupTxt = await ult().blob.text();
              const seqDoArquivo = m1.sequence;
              const f = new File([backupTxt], m1.filename, {type:'application/json'});
              importFullBackupFile(f);
              await new Promise(res => setTimeout(res, 700));
              r.T2 = { restaurouSeq: S.dataGovernance.export.lastSequence,
                       esperado: seqDoArquivo,
                       ok: S.dataGovernance.export.lastSequence === seqDoArquivo };
              dgFsSupported = () => false;   // boot() do import não altera isto, mas explicitamos
              S.dataGovernance.storage = {configured:false, folderName:'', folderDisplayPath:'', configuredAt:''};
              const m2 = await exportFullBackup({quiet:true});
              r.T3 = { proxima: m2.sequence, esperado: seqDoArquivo + 1,
                       ok: m2.sequence === seqDoArquivo + 1,
                       semColisaoDisponivel: true };
              // T6 — monotonicidade por duas gerações: N → N+1 → N+2
              const txt2 = await ult().blob.text();
              const f2 = new File([txt2], m2.filename, {type:'application/json'});
              importFullBackupFile(f2);
              await new Promise(res => setTimeout(res, 700));
              S.dataGovernance.storage = {configured:false, folderName:'', folderDisplayPath:'', configuredAt:''};
              const m3 = await exportFullBackup({quiet:true});
              r.T6 = { geracoes: [seqDoArquivo, m2.sequence, m3.sequence],
                       monotonica: m2.sequence === seqDoArquivo + 1 && m3.sequence === m2.sequence + 1 };
              // T4 — falha de escrita não avança nada
              const antes = { seq: S.dataGovernance.export.lastSequence,
                              arq: S.dataGovernance.export.lastExportFile,
                              log: S.dataGovernance.changeLog.length,
                              bk: S.dataGovernance.backup.lastConfirmedAt };
              dgDownloadViaAnchor = () => { throw new Error('falha física simulada'); };
              const mFalha = await exportFullBackup({quiet:true});
              r.T4 = { retornoNulo: mFalha === null,
                       seqIntacta: S.dataGovernance.export.lastSequence === antes.seq,
                       arquivoIntacto: S.dataGovernance.export.lastExportFile === antes.arq,
                       logSemSucesso: S.dataGovernance.changeLog.length === antes.log,
                       backupIntacto: S.dataGovernance.backup.lastConfirmedAt === antes.bk };
              // removida a falha, a próxima exportação retoma em N+1
              dgDownloadViaAnchor = (nome, blob) => { capturado.push({nome, blob}); };
              const mOk = await exportFullBackup({quiet:true});
              r.T4.retomouEmNmais1 = mOk.sequence === antes.seq + 1;
            } finally { dgFsSupported = oSup; }
          } finally { dgDownloadViaAnchor = oDl; }
          return r;
        }""")
        assert fail04['T1']['identidadeCoerente'], fail04['T1']          # I9
        assert fail04['T1']['igualAoMeta'], fail04['T1']
        assert fail04['T2']['ok'], fail04['T2']
        assert fail04['T3']['ok'], fail04['T3']                          # I10
        assert fail04['T6']['monotonica'], fail04['T6']
        assert all(fail04['T4'][k] for k in
                   ('retornoNulo','seqIntacta','arquivoIntacto','logSemSucesso',
                    'backupIntacto','retomouEmNmais1')), fail04['T4']

        # ---- 5. backup confirmado ≠ exportação; aviso de 30 dias; banner ------------
        backup = page.evaluate("""() => {
          const r = {};
          window.confirm = () => true;
          dgConfirmBackup();
          r.confirmado = {seq: S.dataGovernance.backup.lastConfirmedExportSequence,
                          seqVigente: S.dataGovernance.export.lastSequence,
                          age: dgBackupAgeDays(), due: dgBackupDue()};
          S.dataGovernance.backup.lastConfirmedAt = new Date(Date.now() - 31*86400000).toISOString();
          r.retro = {age: dgBackupAgeDays(), due: dgBackupDue()};
          window.__dgBannerDismissed = false; renderDgBackupBanner();
          const b = document.getElementById('dgBackupBanner');
          r.banner = {existe: !!b, z: getComputedStyle(b).zIndex,
                      texto: b.textContent.includes('31 dia')};
          b.querySelector('#dgBannerClose').click();
          r.dispensado = !document.getElementById('dgBackupBanner');
          r.mudancas = dgChangesSinceLastBackup().length;
          window.confirm = () => false;
          return r;
        }""")
        # PROPRIEDADE, não número absoluto: a confirmação cobre a sequência VIGENTE no
        # momento do gesto, qualquer que seja ela. Prender um literal aqui (era `== 5`)
        # amarrava a seção ao histórico das anteriores — inserir um teste no meio da
        # suíte quebrava esta asserção sem que nada no produto tivesse mudado.
        assert backup['confirmado']['seq'] == backup['confirmado']['seqVigente'], backup['confirmado']
        assert backup['confirmado']['age'] == 0 and backup['confirmado']['due'] is False
        assert backup['retro'] == {'age': 31, 'due': True}
        assert backup['banner'] == {'existe': True, 'z': '50', 'texto': True}  # sanduíche: abaixo da Central (60)
        assert backup['dispensado'] and backup['mudancas'] >= 4

        # ---- 6. migração de base LEGADA (sem dataGovernance) ------------------------
        legado = page.evaluate("""() => {
          const legacy = {params:{saldoIni:5000,saldoAtu:5100,inicio:'2026-01-01',mdd:0.15,
            alarm:0.13,genLev:0.4,genRisk:0.01,fw:1,vrmN:1.2,vrmHV:1.5,refM:0.02,refA:0.24},
            ledger:[{data:'2026-01-02',resultado:50,saldo:5050,nota:''}], phases:[], theme:'dark'};
          const imp = normalizeImportedState({tipo:'jpwealth_full_backup', state:legacy});
          return {temDg: !!imp.dataGovernance, resp: imp.dataGovernance.responsibility.accepted,
                  seq: imp.dataGovernance.export.lastSequence,
                  ledger: imp.ledger.length, atualIntacto: S.params.saldoIni !== 5000};
        }""")
        assert legado == {'temDg': True, 'resp': False, 'seq': 0, 'ledger': 1, 'atualIntacto': True}

        # ---- 7. status 'missing' + wipe → DEFAULT_START_ROUTE + handle limpo --------
        wipe = page.evaluate("""async () => {
          const r = {};
          await dgFsStoreHandle({name:'Base de Dados', fake:true});
          S.dataGovernance.storage = {configured:true, folderName:'Outra Pasta',
            folderDisplayPath:'Outra Pasta', configuredAt:'2026-08-08T00:00'};
          r.missing = (await dgFsStatus()).state;   // nome diverge → missing (§6.5)
          navigateToScreen('contab');
          window.prompt = () => 'APAGAR'; window.confirm = () => true;
          wipeAllData();
          await new Promise(res => setTimeout(res, 120));
          r.tela = document.querySelector('.screen.active').id;
          r.dgZerado = S.dataGovernance.export.lastSequence === 0
            && S.dataGovernance.responsibility.accepted === false;
          r.handle = await dgFsLoadHandle();
          window.prompt = () => null; window.confirm = () => false;
          return r;
        }""")
        assert wipe['missing'] == 'missing'
        assert wipe['tela'] == 'dash' and wipe['dgZerado'] and wipe['handle'] is None

        assert_no_errors(page.jpwealth_observed)
        page.close()

        # ---- 8. persistência entre sessões ------------------------------------------
        # browser.new_page() abre um BrowserContext NOVO E ISOLADO a cada chamada, então
        # duas páginas criadas assim nunca compartilham localStorage/IndexedDB — o teste
        # anterior era incapaz, por construção, de provar persistência. Aqui as duas
        # páginas nascem do MESMO contexto: fechar a primeira e abrir a segunda simula a
        # sessão seguinte com o mesmo perfil de navegador.
        contexto = browser.new_context(viewport=VIEWPORT)
        page = prepare_page(contexto, url)
        page.evaluate("async () => { window.__onbShown = true; closeModal(); await exportFullBackup(); }")
        gravado = page.evaluate("""() => ({seq: S.dataGovernance.export.lastSequence,
          arq: S.dataGovernance.export.lastExportFile,
          log: S.dataGovernance.changeLog.length})""")
        assert gravado['seq'] == 1 and gravado['arq'].startswith('JP_WEALTH_DB_000001_'), gravado
        page.close()

        page = prepare_page(contexto, url)   # MESMO contexto: o estado tem de atravessar
        persist = page.evaluate("""() => ({seq: S.dataGovernance.export.lastSequence,
          arq: S.dataGovernance.export.lastExportFile,
          log: S.dataGovernance.changeLog.map(e => e.entity + '/' + e.action)})""")
        assert persist['seq'] == gravado['seq'], persist        # sobreviveu ao fechamento
        assert persist['arq'] == gravado['arq'], persist        # mesmo arquivo registrado
        assert 'database/exported' in persist['log'], persist
        assert_no_errors(page.jpwealth_observed)
        page.close()
        contexto.close()

        browser.close()
    server.shutdown()
    print('STORAGE GOVERNANCE TEST OK — schema, sequência, colisão, diálogo, termo, 30 dias, migração, wipe e persistência verificados.')

if __name__ == '__main__':
    main()
