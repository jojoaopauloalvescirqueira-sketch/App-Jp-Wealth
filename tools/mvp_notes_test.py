#!/usr/bin/env python3
"""Notas do MVP (14-mvp-notes.js) — CRUD, filtros, contador, visibilidade, Finalizar
Sessão, Zona de Perigo, backup/importação real e migração de estado legado."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import json, os, socket, tempfile, threading
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)

class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *_): pass

def serve():
    with socket.socket() as s:
        s.bind(('127.0.0.1', 0)); port = s.getsockname()[1]
    server = ThreadingHTTPServer(('127.0.0.1', port), Quiet)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f'http://127.0.0.1:{port}/'

def click_id(page, element_id):
    locator = page.locator('#' + element_id)
    assert locator.count() == 1, element_id
    locator.click()

def assert_no_errors(observed):
    errors = [x for x in observed['console'] if x[0] == 'error']
    assert not errors and not observed['pageerror'], {'console': errors, 'pageerror': observed['pageerror']}

def prepare_page(browser, url):
    page = browser.new_page(viewport={'width': 1440, 'height': 900})
    observed = {'console': [], 'pageerror': []}
    page.on('console', lambda m: observed['console'].append((m.type, m.text)))
    page.on('pageerror', lambda e: observed['pageerror'].append(str(e)))
    page.route('**/dist/assets/**', lambda route: route.continue_(url=route.request.url.replace('/dist/assets/', '/assets/')))
    page.route('**/api.frankfurter.dev/**', lambda route: route.fulfill(status=200, content_type='application/json', body='{"rate":1}'))
    page.goto(url, wait_until='load')
    page.wait_for_timeout(700)
    page.evaluate("""() => {
      window.__onbShown = true; closeModal();
      window.alert = () => {}; window.confirm = () => false; window.prompt = () => null;
    }""")
    page.jpwealth_observed = observed
    return page

def create_note(page, type_, title, description, priority, status):
    click_id(page, 'headerNotesBtn')
    click_id(page, 'mvpNotesNewBtn')
    page.locator('#mvpNoteType').select_option(type_)
    page.locator('#mvpNoteTitle').fill(title)
    page.locator('#mvpNoteDescription').fill(description)
    page.locator('#mvpNotePriority').select_option(priority)
    page.locator('#mvpNoteStatus').select_option(status)
    click_id(page, 'mvpNoteSaveBtn')
    click_id(page, 'mvpNotesCloseBtn')

def notes_state(page):
    return page.evaluate("S.mvpNotes.items.map(it => ({...it}))")

server, base_url = serve()
try:
    with sync_playwright() as pw:
        candidates = [
            os.environ.get('JP_WEALTH_CHROMIUM', ''),
            '/usr/bin/chromium',
            '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        ]
        executable = next((p for p in candidates if p and Path(p).exists()), None)
        options = {'headless': True, 'args': ['--no-sandbox']}
        if executable:
            options['executable_path'] = executable
        browser = pw.chromium.launch(**options)
        url = base_url + 'index.html'

        # ---- 1. botão por padrão, CRUD dos 4 tipos, contador, captura de tela/build ----
        page = prepare_page(browser, url)
        assert page.locator('#headerNotesBtn').is_visible()
        assert page.locator('#headerNotesBtn').get_attribute('title') == 'Notas do MVP'
        assert page.locator('#headerNotesBtn').get_attribute('aria-label') == 'Abrir notas do MVP'
        assert page.locator('#headerNotesBadge').is_hidden()

        create_note(page, 'task', 'Tarefa de teste', 'descrição da tarefa', 'medium', 'open')
        create_note(page, 'bug', 'Bug de teste', 'descrição do bug', 'critical', 'open')
        create_note(page, 'feature', 'Funcionalidade de teste', 'descrição da funcionalidade', 'high', 'in_progress')
        create_note(page, 'improvement', 'Melhoria de teste', 'descrição da melhoria', 'low', 'done')
        items = notes_state(page)
        assert len(items) == 4, items
        assert {it['type'] for it in items} == {'task', 'bug', 'feature', 'improvement'}
        assert all(it['screenId'] == 'dash' for it in items), items
        assert all(it['buildId'] for it in items), items
        assert all(it['createdAt'] == it['updatedAt'] for it in items), items
        ids = [it['id'] for it in items]
        assert len(set(ids)) == len(ids), 'IDs duplicados entre notas criadas'

        click_id(page, 'headerNotesBtn')
        assert page.locator('#mvpNotesHeadCount').inner_text() == '3 itens ativos'
        assert page.locator('#headerNotesBadge').inner_text() == '3'  # done não conta como ativo
        click_id(page, 'mvpNotesCloseBtn')

        # ---- 2. edição: preserva id/createdAt/screenId/buildId; move updatedAt só se algo mudou ----
        click_id(page, 'headerNotesBtn')
        bug_card = page.locator('.mvpn-card[data-type="bug"]')
        bug_before = next(it for it in items if it['type'] == 'bug')
        bug_card.click()
        assert page.locator('.mvpn-meta-facts dd').first.inner_text() == 'Dashboard'
        page.locator('#mvpNoteStatus').select_option('in_progress')
        click_id(page, 'mvpNoteSaveBtn')
        bug_after = next(it for it in notes_state(page) if it['id'] == bug_before['id'])
        assert bug_after['status'] == 'in_progress'
        assert bug_after['createdAt'] == bug_before['createdAt']
        assert bug_after['screenId'] == bug_before['screenId']
        assert bug_after['buildId'] == bug_before['buildId']
        assert bug_after['updatedAt'] != bug_before['updatedAt']

        page.locator('.mvpn-card[data-type="task"]').click()
        task_before = next(it for it in notes_state(page) if it['type'] == 'task')
        click_id(page, 'mvpNoteSaveBtn')  # salva sem alterar nada
        task_after = next(it for it in notes_state(page) if it['id'] == task_before['id'])
        assert task_after['updatedAt'] == task_before['updatedAt'], 'updatedAt não deveria mudar sem alteração real'

        # ---- 3. dirty state: recusar descarte mantém o rascunho; aceitar descarta ----
        page.locator('.mvpn-card[data-type="feature"]').click()
        page.locator('#mvpNoteTitle').fill('Rascunho não salvo')
        page.evaluate("window.confirm = () => false")
        click_id(page, 'mvpNotesCloseBtn')
        assert page.locator('#mvpNotesOverlay').evaluate("el => el.classList.contains('show')") is True
        assert page.locator('#mvpNoteTitle').input_value() == 'Rascunho não salvo'
        page.evaluate("window.confirm = () => true")
        click_id(page, 'mvpNotesCloseBtn')
        assert page.locator('#mvpNotesOverlay').evaluate("el => el.classList.contains('show')") is False
        assert not any(it['title'] == 'Rascunho não salvo' for it in notes_state(page)), 'rascunho não deveria ter sido salvo'

        # ---- 4. busca e filtros, isolados e combinados ----
        click_id(page, 'headerNotesBtn')
        page.locator('#mvpNotesSearch').fill('Bug de teste')
        assert page.locator('.mvpn-card').count() == 1
        page.locator('#mvpNotesSearch').fill('')
        page.locator('#mvpNotesFilterType').select_option('bug')
        assert page.locator('.mvpn-card').count() == 1
        page.locator('#mvpNotesFilterStatus').select_option('in_progress')
        assert page.locator('.mvpn-card').count() == 1  # bug agora está in_progress
        page.locator('#mvpNotesFilterPriority').select_option('low')
        assert page.locator('.mvpn-card').count() == 0
        assert 'Nenhuma nota encontrada' in page.locator('.mvpn-empty').inner_text()
        page.locator('#mvpNotesFilterType').select_option('all')
        page.locator('#mvpNotesFilterStatus').select_option('all')
        page.locator('#mvpNotesFilterPriority').select_option('all')

        # ---- 5. exclusão: cancelar preserva, confirmar remove só o item selecionado ----
        before_count = len(notes_state(page))
        page.locator('.mvpn-card[data-type="improvement"]').click()
        page.evaluate("window.confirm = () => false")
        click_id(page, 'mvpNoteDeleteBtn')
        assert len(notes_state(page)) == before_count, 'cancelar exclusão não deveria remover nada'
        page.evaluate("window.confirm = () => true")
        click_id(page, 'mvpNoteDeleteBtn')
        assert len(notes_state(page)) == before_count - 1
        assert not any(it['type'] == 'improvement' for it in notes_state(page))
        click_id(page, 'mvpNotesCloseBtn')

        # ---- 6. ocultar/reexibir ícone pela Central, sem reload; "Abrir Notas" com ícone oculto ----
        click_id(page, 'headerConfigBtn')
        page.evaluate("settingsNavigateToLeaf('interface')")
        page.locator('[data-mvp-notes-visibility="hide"]').click()
        assert page.locator('#headerNotesBtn').is_hidden()
        assert len(notes_state(page)) == 3, 'ocultar ícone não pode apagar registros'
        click_id(page, 'mvpNotesOpenFromSettingsBtn')
        assert page.locator('#mvpNotesOverlay').evaluate("el => el.classList.contains('show')") is True
        assert page.locator('.mvpn-card').count() == 3
        assert page.locator('#settingsModal').evaluate('el => el.inert') is True, 'Central deveria ficar inert com o drawer sobreposto'
        click_id(page, 'mvpNotesNewBtn')
        assert page.locator('.mvpn-meta-facts dd').first.inner_text() == 'Configurações'
        click_id(page, 'mvpNoteCancelBtn')
        click_id(page, 'mvpNotesCloseBtn')
        assert page.locator('#settingsModal').evaluate('el => !el.inert') is True, 'Central deveria voltar a ficar usável'
        assert page.locator('#settingsOverlay').is_visible(), 'Central deveria continuar aberta após fechar o drawer'

        # ---- 7. busca da Central encontra e leva até o card "Notas do MVP" ----
        page.locator('#settingsSearch').fill('bugs')
        assert page.locator('#settingsSearchResults [data-settings-result]').count() >= 1
        page.locator('#settingsSearchResults [data-settings-result]').first.click()
        page.wait_for_function("document.querySelector('#mvpNotesSettingsCard')?.classList.contains('settings-search-hit')")
        page.locator('#settingsSearch').fill('')
        page.locator('[data-mvp-notes-visibility="show"]').click()
        assert page.locator('#headerNotesBtn').is_visible()
        click_id(page, 'settingsCloseBtn')

        # ---- 7b. log de auditoria financeira (tela Contabilidade) não deve carregar notas ----
        page.evaluate("navigateToScreen('contab')")
        page.evaluate("""() => {
          window.URL.createObjectURL = (blob) => { window.__auditBlob = blob; return 'blob:audit'; };
          window.URL.revokeObjectURL = () => {};
          HTMLAnchorElement.prototype.click = function(){};
        }""")
        click_id(page, 'exportAuditBtn')
        audit_payload = json.loads(page.evaluate("window.__auditBlob.text()"))
        assert 'mvpNotes' not in audit_payload, 'log de auditoria financeira não deve conter notas'
        page.evaluate("navigateToScreen('dash')")

        # ---- 8. persistência após reload ----
        before_reload = notes_state(page)
        page.reload(wait_until='load')
        page.wait_for_timeout(700)
        page.evaluate("() => { window.__onbShown = true; closeModal(); }")
        after_reload = page.evaluate("S.mvpNotes.items.map(it => ({...it}))")
        assert after_reload == before_reload, (before_reload, after_reload)
        assert page.evaluate("S.mvpNotes.showHeaderIcon") is True

        # ---- 9. nenhum ID duplicado na página inteira ----
        dup = page.evaluate("""() => {
          const ids = [...document.querySelectorAll('[id]')].map(e => e.id);
          const counts = {}; ids.forEach(id => counts[id] = (counts[id]||0)+1);
          return Object.entries(counts).filter(([,c]) => c > 1);
        }""")
        assert dup == [], dup

        # ---- 10. export real (botão) inclui mvpNotes; import real (input de arquivo) restaura tudo ----
        # exportFullBackupBtn/importFullBackupInput vivem dentro da Central (categoria backup) —
        # só ficam acessíveis (não [hidden]) com o modal aberto e essa folha ativa.
        click_id(page, 'headerConfigBtn')
        page.evaluate("settingsNavigateToLeaf('backup')")
        page.evaluate("""() => {
          window.URL.createObjectURL = (blob) => { window.__lastBlob = blob; return 'blob:test'; };
          window.URL.revokeObjectURL = () => {};
          HTMLAnchorElement.prototype.click = function(){};
          window.confirm = () => false;
        }""")
        click_id(page, 'exportFullBackupBtn')
        exported = page.evaluate("window.__lastBlob.text()")
        payload = json.loads(exported)
        assert 'mvpNotes' in payload['state']
        assert payload['state']['mvpNotes']['items'], 'backup deveria incluir os itens de notas'
        exported_notes = payload['state']['mvpNotes']

        # zera via mecanismo real de reset (mesma função usada pelo botão real)
        page.evaluate("""() => {
          window.prompt = () => 'APAGAR';
          window.alert = () => {};
          wipeAllData();
        }""")
        assert page.evaluate("S.mvpNotes.items.length") == 0
        assert page.evaluate("S.mvpNotes.showHeaderIcon") is True
        assert page.evaluate("localStorage.getItem('jpwealth_v9_state')") is None
        # wipeAllData() reagenda a abertura automática do onboarding (S.onboarding.done volta a
        # false) 350ms depois — fecha antes de seguir, senão o MutationObserver de subdiálogo
        # (initSettingsSubdialogObserver, ligado a #modalOverlay) suspenderia a Central bem na
        # hora de usar o input de importação, que vive dentro dela.
        page.wait_for_timeout(500)
        page.evaluate("() => { window.__onbShown = true; closeModal(); }")
        assert page.locator('#settingsOverlay').is_visible(), 'Central deveria continuar aberta e usável após o reset'
        assert page.locator('#settingsModal').evaluate('el => !el.inert') is True

        with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as fixture:
            fixture.write(exported)
            fixture_path = fixture.name
        try:
            page.evaluate("window.confirm = () => true")
            page.locator('#importFullBackupInput').set_input_files(fixture_path)
            page.wait_for_timeout(500)
            restored = notes_state(page)
            assert len(restored) == len(exported_notes['items'])
            assert sorted(it['id'] for it in restored) == sorted(it['id'] for it in exported_notes['items'])
            assert page.evaluate("S.mvpNotes.showHeaderIcon") == exported_notes['showHeaderIcon']
        finally:
            Path(fixture_path).unlink(missing_ok=True)

        page.reload(wait_until='load')
        page.wait_for_timeout(700)
        page.evaluate("() => { window.__onbShown = true; closeModal(); }")
        assert len(page.evaluate("S.mvpNotes.items")) == len(exported_notes['items']), 'importação deveria sobreviver ao reload'

        assert_no_errors(page.jpwealth_observed)
        page.close()

        # ---- 11. Finalizar Sessão preserva notas; Zona de Perigo remove ----
        page = prepare_page(browser, url)
        create_note(page, 'task', 'Nota que deve sobreviver', '', 'medium', 'open')
        assert len(notes_state(page)) == 1
        page.evaluate("""() => {
          S.onboarding = {...S.onboarding, done: true, operador: 'Operador Teste', supervisor: 'Supervisor Teste'};
          S.params.saldoIni = 12345;
          save(); markSessionCheckpoint();
        }""")
        click_id(page, 'finalizeSessionBtn')
        click_id(page, 'sessionHasCopy')
        assert 'notas do mvp' in page.locator('#modalBox').inner_text().lower(), 'aviso de persistência de notas ausente na tela de confirmação'
        click_id(page, 'sessionProceed')
        page.locator('#sessionDeletePhrase').fill('APAGAR TUDO')
        click_id(page, 'sessionDeleteConfirm')
        page.wait_for_timeout(500)
        assert page.evaluate("S.params.saldoIni") == 0, 'dado operacional deveria ser zerado'
        assert page.evaluate("S.onboarding.operador") == ''
        assert len(notes_state(page)) == 1, 'Finalizar Sessão não deveria apagar notas'
        notice = page.locator('#sessionNotice').inner_text()
        assert 'Notas do MVP' in notice, notice
        assert json.loads(page.evaluate("localStorage.getItem('jpwealth_v9_state')"))['mvpNotes']['items'], \
            'notas deveriam ter sido regravadas no localStorage mesmo com persistência bloqueada'

        page.reload(wait_until='load')
        page.wait_for_timeout(700)
        page.evaluate("() => { window.__onbShown = true; closeModal(); }")
        assert len(notes_state(page)) == 1, 'notas deveriam sobreviver a um reload real após Finalizar Sessão'

        page.evaluate("window.prompt = () => 'APAGAR'; window.alert = () => {};")
        click_id(page, 'resetBtn')
        assert len(notes_state(page)) == 0, 'Zona de Perigo/reset deveria remover as notas'

        assert_no_errors(page.jpwealth_observed)
        page.close()

        # ---- 12. estado legado sem mvpNotes migra para estrutura padrão vazia ----
        page = prepare_page(browser, url)
        legacy_ok = page.evaluate("""() => {
          const legacy = structuredClone(DEFAULTS);
          delete legacy.mvpNotes;
          const imported = normalizeImportedState({state: legacy});
          return imported.mvpNotes
            && Array.isArray(imported.mvpNotes.items)
            && imported.mvpNotes.items.length === 0
            && imported.mvpNotes.showHeaderIcon === true;
        }""")
        assert legacy_ok, 'estado legado sem mvpNotes deveria migrar para estrutura padrão vazia'
        assert_no_errors(page.jpwealth_observed)
        page.close()

        # ---- 12b. pastas (schema v2): CRUD, visões, vínculo, busca, filtros, dirty, backup ----
        page = prepare_page(browser, url)
        assert page.evaluate('S.mvpNotes.schemaVersion') == 2
        page.locator('#headerNotesBtn').click()
        # criação via UI (prompt real interceptado); pasta nova é selecionada
        page.evaluate("window.prompt = () => 'Interface de Configurações'")
        click_id(page, 'mvpNotesNewFolderBtn')
        iface_id = page.evaluate("S.mvpNotes.folders[0].id")
        assert page.evaluate('mvpNotesUI.activeFolder') == iface_id, 'pasta recém-criada deveria ficar ativa'
        assert page.locator('#mvpNotesViewTitle').inner_text() == 'Interface de Configurações'
        # nota criada dentro da pasta herda o vínculo; em Todas as Notas/Sem pasta o padrão é null
        click_id(page, 'mvpNotesNewBtn')
        assert page.locator('#mvpNoteFolder').input_value() == iface_id
        page.locator('#mvpNoteTitle').fill('Nota da pasta Interface')
        click_id(page, 'mvpNoteSaveBtn')
        page.locator('[data-mvp-folder="all"]').click()
        click_id(page, 'mvpNotesNewBtn')
        assert page.locator('#mvpNoteFolder').input_value() == ''
        page.locator('#mvpNoteTitle').fill('Nota solta')
        click_id(page, 'mvpNoteSaveBtn')
        # visões: Todas mostra 2 (com linha de pasta); Sem pasta mostra 1; pasta mostra 1 (sem linha)
        assert page.locator('.mvpn-card').count() == 2
        assert page.locator('.mvpn-card-folder').count() == 2, 'em Todas as Notas cada card mostra sua pasta'
        page.locator('[data-mvp-folder="unfiled"]').click()
        assert page.locator('.mvpn-card').count() == 1
        page.locator(f'[data-mvp-folder="{iface_id}"]').click()
        assert page.locator('.mvpn-card').count() == 1
        assert page.locator('.mvpn-card-folder').count() == 0, 'dentro da pasta o nome dela não se repete nos cards'
        # contadores e aria-current
        assert page.locator(f'[data-mvp-folder="{iface_id}"]').get_attribute('aria-current') == 'page'
        assert page.locator(f'[data-mvp-folder="{iface_id}"] .mvpn-folder-count').inner_text() == '1'
        # busca pelo nome da pasta (em Todas as Notas)
        page.locator('[data-mvp-folder="all"]').click()
        page.locator('#mvpNotesSearch').fill('Interface de Configurações')
        assert page.locator('.mvpn-card').count() == 1
        page.locator('#mvpNotesSearch').fill('')
        # filtro preservado ao trocar de pasta
        page.locator('#mvpNotesFilterType').select_option('task')
        page.locator('[data-mvp-folder="unfiled"]').click()
        assert page.locator('#mvpNotesFilterType').input_value() == 'task', 'trocar de pasta não pode limpar filtros'
        page.locator('#mvpNotesFilterType').select_option('all')
        # mover nota entre pastas pelo editor: só folderId+updatedAt mudam
        page.locator('[data-mvp-folder="all"]').click()
        moved = page.evaluate("S.mvpNotes.items.find(it => it.title === 'Nota solta')")
        page.locator(f'[data-mvp-note-id="{moved["id"]}"]').click()
        page.locator('#mvpNoteFolder').select_option(iface_id)
        click_id(page, 'mvpNoteSaveBtn')
        after = page.evaluate(f"S.mvpNotes.items.find(it => it.id === '{moved['id']}')")
        assert after['folderId'] == iface_id and after['createdAt'] == moved['createdAt'] \
            and after['screenId'] == moved['screenId'] and after['updatedAt'] != moved['updatedAt']
        # dirty state protege a troca de pasta
        page.locator(f'[data-mvp-note-id="{moved["id"]}"]').click()
        page.locator('#mvpNoteTitle').fill('Rascunho de pasta')
        page.evaluate("window.confirm = () => false")
        page.locator('[data-mvp-folder="unfiled"]').click()
        assert page.locator('#mvpNoteTitle').input_value() == 'Rascunho de pasta', 'recusar descarte mantém o rascunho'
        page.evaluate("window.confirm = () => true")
        page.locator('[data-mvp-folder="unfiled"]').click()
        assert page.evaluate("S.mvpNotes.items.some(it => it.title === 'Rascunho de pasta')") is False
        # renomear preserva ID/vínculos; excluir com notas move para Sem pasta e preserva
        # registros. Renomear/Excluir vivem no menu "⋯" (<details> fechado) — abrir antes.
        page.evaluate("window.prompt = () => 'Central de Configurações'")
        page.locator(f'details:has([data-mvp-folder-rename="{iface_id}"]) summary').click()
        page.locator(f'[data-mvp-folder-rename="{iface_id}"]').click()
        renamed = page.evaluate(f"S.mvpNotes.folders.find(f => f.id === '{iface_id}')")
        assert renamed['name'] == 'Central de Configurações'
        assert page.evaluate(f"S.mvpNotes.items.filter(it => it.folderId === '{iface_id}').length") == 2
        page.locator(f'details:has([data-mvp-folder-delete="{iface_id}"]) summary').click()
        page.locator(f'[data-mvp-folder-delete="{iface_id}"]').click()
        assert page.evaluate('S.mvpNotes.folders.length') == 0
        assert page.evaluate('S.mvpNotes.items.length') == 2, 'excluir pasta nunca apaga notas'
        assert page.evaluate("S.mvpNotes.items.every(it => it.folderId === null)") is True
        assert page.evaluate('mvpNotesUI.activeFolder') == 'unfiled'
        page.locator('#mvpNotesCloseBtn').click()
        # backup real inclui pastas; wipe remove; import restaura pastas + vínculos
        page.evaluate("window.prompt = () => 'Pasta do backup'")
        page.locator('#headerNotesBtn').click()
        click_id(page, 'mvpNotesNewFolderBtn')
        backup_folder_id = page.evaluate("S.mvpNotes.folders[0].id")
        click_id(page, 'mvpNotesNewBtn')
        page.locator('#mvpNoteTitle').fill('Nota do backup em pasta')
        click_id(page, 'mvpNoteSaveBtn')
        page.locator('#mvpNotesCloseBtn').click()
        click_id(page, 'headerConfigBtn')
        page.evaluate("settingsNavigateToLeaf('backup')")
        page.evaluate("""() => {
          window.URL.createObjectURL = (blob) => { window.__foldersBlob = blob; return 'blob:folders'; };
          window.URL.revokeObjectURL = () => {};
          HTMLAnchorElement.prototype.click = function(){};
          window.confirm = () => false;
        }""")
        click_id(page, 'exportFullBackupBtn')
        exported_folders = page.evaluate("window.__foldersBlob.text()")
        payload_folders = json.loads(exported_folders)
        assert payload_folders['state']['mvpNotes']['folders'], 'backup deveria incluir as pastas'
        page.evaluate("""() => { window.prompt = () => 'APAGAR'; window.alert = () => {}; wipeAllData(); }""")
        assert page.evaluate('S.mvpNotes.folders.length') == 0, 'reset deveria apagar as pastas'
        page.wait_for_timeout(500)
        page.evaluate("() => { window.__onbShown = true; closeModal(); }")
        with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as fixture:
            fixture.write(exported_folders)
            folders_fixture = fixture.name
        try:
            page.evaluate("window.confirm = () => true")
            page.locator('#importFullBackupInput').set_input_files(folders_fixture)
            page.wait_for_timeout(500)
            assert page.evaluate("S.mvpNotes.folders[0].id") == backup_folder_id, 'ID da pasta deveria ser preservado no import'
            assert page.evaluate("S.mvpNotes.items[0].folderId") == backup_folder_id, 'vínculo nota↔pasta deveria ser restaurado'
        finally:
            Path(folders_fixture).unlink(missing_ok=True)
        # importação inválida: ID de pasta duplicado (primeiro preservado, ambíguo → Sem pasta),
        # referência inexistente → Sem pasta; nada disso quebra a importação inteira
        recon = page.evaluate("""() => {
          const bad = structuredClone(DEFAULTS);
          bad.mvpNotes = {schemaVersion: 2, showHeaderIcon: true,
            folders: [
              {id: 'dup', name: 'A', createdAt: 'x', updatedAt: 'x'},
              {id: 'dup', name: 'B', createdAt: 'x', updatedAt: 'x'}
            ],
            items: [
              {id: 'n1', title: 'ambígua', folderId: 'dup'},
              {id: 'n2', title: 'órfã', folderId: 'nao-existe'}
            ]};
          const imp = normalizeImportedState({state: bad});
          return {
            firstKept: imp.mvpNotes.folders[0].id === 'dup',
            dupRegenerated: imp.mvpNotes.folders[1].id !== 'dup',
            bothNull: imp.mvpNotes.items.every(it => it.folderId === null)
          };
        }""")
        assert recon == {'firstKept': True, 'dupRegenerated': True, 'bothNull': True}, recon
        # migração v1 → v2: folders=[] e folderId=null, sem perder nada
        legacy_v2 = page.evaluate("""() => {
          const legacy = structuredClone(DEFAULTS);
          legacy.mvpNotes = {schemaVersion: 1, showHeaderIcon: true, items: [
            {id: 'l1', title: 'Legada', type: 'bug', priority: 'high', status: 'open',
             screenId: 'dash', buildId: 'B', createdAt: 'c', updatedAt: 'u'}
          ]};
          const imp = normalizeImportedState({state: legacy});
          return {sv: imp.mvpNotes.schemaVersion, folders: imp.mvpNotes.folders,
                  fid: imp.mvpNotes.items[0].folderId, id: imp.mvpNotes.items[0].id};
        }""")
        assert legacy_v2 == {'sv': 2, 'folders': [], 'fid': None, 'id': 'l1'}, legacy_v2
        # idempotência: normalize(normalize(state)) === normalize(state), em igualdade
        # estrutural (sessionStableValue ordena chaves), para legado v1, v2 com pastas
        # ambíguas/duplicadas/órfãs, e v2 já bem-formado (segunda passada não deve alterar nada).
        idempotency = page.evaluate("""() => {
          const stable = x => JSON.stringify(sessionStableValue(x));
          const normalize = raw => normalizeImportedState({state: raw});
          const cases = {};

          const legacy = structuredClone(DEFAULTS);
          legacy.mvpNotes = {schemaVersion: 1, showHeaderIcon: true, items: [
            {id: 'l1', type: 'bug', title: 'Legada', description: 'd', priority: 'high',
             status: 'open', screenId: 'dash', buildId: 'B', createdAt: 'c', updatedAt: 'u'}
          ]};
          const s1a = normalize(legacy), s2a = normalize(s1a);
          cases.legacyV1 = stable(s1a.mvpNotes) === stable(s2a.mvpNotes);

          const messy = structuredClone(DEFAULTS);
          messy.mvpNotes = {schemaVersion: 2, showHeaderIcon: true,
            folders: [
              {id: 'dup', name: 'A', createdAt: 'x', updatedAt: 'x'},
              {id: 'dup', name: 'B', createdAt: 'x', updatedAt: 'x'},
              {id: 'ok', name: 'C', createdAt: 'x', updatedAt: 'x'}
            ],
            items: [
              {id: 'm1', title: 'ambígua', description: '', type: 'task', priority: 'medium', status: 'open', folderId: 'dup', screenId: 'dash', buildId: 'B', createdAt: 'c', updatedAt: 'u'},
              {id: 'm2', title: 'válida', description: '', type: 'bug', priority: 'high', status: 'open', folderId: 'ok', screenId: 'dash', buildId: 'B', createdAt: 'c', updatedAt: 'u'},
              {id: 'm3', title: 'órfã', description: '', type: 'task', priority: 'low', status: 'done', folderId: 'nao-existe', screenId: 'dash', buildId: 'B', createdAt: 'c', updatedAt: 'u'}
            ]};
          const s1b = normalize(messy), s2b = normalize(s1b);
          cases.messyV2 = stable(s1b.mvpNotes) === stable(s2b.mvpNotes);

          const clean = structuredClone(DEFAULTS);
          clean.mvpNotes = {schemaVersion: 2, showHeaderIcon: false,
            folders: [{id: 'f1', name: 'Limpa', createdAt: 'c', updatedAt: 'u'}],
            items: [{id: 'c1', type: 'feature', title: 'Nota', description: '', priority: 'critical',
              status: 'in_progress', folderId: 'f1', screenId: 'motor', buildId: 'B', createdAt: 'c', updatedAt: 'u'}]};
          const s1c = normalize(clean), s2c = normalize(s1c);
          cases.wellFormedV2 = stable(s1c.mvpNotes) === stable(s2c.mvpNotes)
            && stable(s1c.mvpNotes) === stable(clean.mvpNotes);

          return cases;
        }""")
        assert idempotency == {'legacyV1': True, 'messyV2': True, 'wellFormedV2': True}, idempotency
        assert_no_errors(page.jpwealth_observed)
        page.close()

        # ---- 13. monólito portátil (dist) ----
        page = prepare_page(browser, base_url + 'dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html')
        create_note(page, 'bug', 'Bug no monólito', '', 'high', 'open')
        assert len(notes_state(page)) == 1
        assert_no_errors(page.jpwealth_observed)
        page.close()

        browser.close()
finally:
    server.shutdown()
    server.server_close()
print('MVP NOTES OK — CRUD, filtros, contador, visibilidade, isolamento sobre a Central, Finalizar Sessão, Zona de Perigo, backup/importação real, migração, pastas (schema v2) e monólito verificados.')
