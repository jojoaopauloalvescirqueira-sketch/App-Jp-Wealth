#!/usr/bin/env python3
"""Notas do MVP (14-mvp-notes.js) — CRUD, filtros, contador, visibilidade, Finalizar
Sessão, Zona de Perigo, backup/importação real e migração de estado legado."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import json, os, re, socket, tempfile, threading
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

def open_inspector(page):
    # Os selects administrativos (tipo/prioridade/status/pasta/política) vivem no
    # inspector (v5); abri-lo é pré-requisito para interagir com eles.
    if page.locator('#mvpNotesInspector.open').count() == 0:
        click_id(page, 'mvpNotesInspectorBtn')

NEW_MODAL_FIELDS = {'type': 'mvpNotesNewType', 'priority': 'mvpNotesNewPriority',
                    'status': 'mvpNotesNewStatus', 'folderId': 'mvpNotesNewFolder',
                    'policy': 'mvpNotesNewPolicy'}

def start_new_note(page, **meta):
    """Fluxo canônico de criação (JPW-CBA987): o botão "+" abre o modal de configuração
    inicial e o editor só aparece depois de "Criar Nota". `meta` sobrescreve os selects
    do modal; sem argumentos, aceita os padrões já pré-selecionados."""
    click_id(page, 'mvpNotesNewBtn')
    assert page.locator('#mvpNotesNewOverlay').is_visible(), 'o modal de nova nota deveria abrir'
    for field, value in meta.items():
        page.locator('#' + NEW_MODAL_FIELDS[field]).select_option(value)
    click_id(page, 'mvpNotesNewConfirmBtn')
    assert page.locator('#mvpNotesNewOverlay').is_hidden(), 'o modal deveria fechar ao criar'

def create_note(page, type_, title, description, priority, status):
    click_id(page, 'headerNotesBtn')
    start_new_note(page)
    content = title + ('\n' + description if description else '')
    page.locator('#mvpNoteContent').fill(content)
    if (type_, priority, status) != ('task', 'medium', 'open'):
        open_inspector(page)
        page.locator('#mvpNoteType').select_option(type_)
        page.locator('#mvpNotePriority').select_option(priority)
        page.locator('#mvpNoteStatus').select_option(status)
        click_id(page, 'mvpNotesInspectorCloseBtn')
    click_id(page, 'mvpNotesSaveBtn')
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
        # A contagem no cabeçalho do drawer foi removida do design (barra unificada);
        # quem informa o backlog ativo é o badge do botão no header do app.
        assert page.locator('#mvpNotesHeadCount').count() == 0
        assert page.locator('#headerNotesBadge').inner_text() == '3'  # done não conta como ativo
        click_id(page, 'mvpNotesCloseBtn')

        # ---- 2. edição: preserva id/createdAt/screenId/buildId; move updatedAt só se algo mudou ----
        click_id(page, 'headerNotesBtn')
        bug_card = page.locator('.mvpn-card[data-type="bug"]')
        bug_before = next(it for it in items if it['type'] == 'bug')
        bug_card.click()
        open_inspector(page)
        assert page.locator('.mvpn-meta-facts dd').nth(3).inner_text() == 'Dashboard'  # Tela de origem
        page.locator('#mvpNoteStatus').select_option('in_progress')
        click_id(page, 'mvpNotesSaveBtn')
        bug_after = next(it for it in notes_state(page) if it['id'] == bug_before['id'])
        assert bug_after['status'] == 'in_progress'
        assert bug_after['createdAt'] == bug_before['createdAt']
        assert bug_after['screenId'] == bug_before['screenId']
        assert bug_after['buildId'] == bug_before['buildId']
        assert bug_after['updatedAt'] != bug_before['updatedAt']

        page.locator('.mvpn-card[data-type="task"]').click()
        task_before = next(it for it in notes_state(page) if it['type'] == 'task')
        # v5: sem alteração o botão Salvar nem aparece; trocar de nota sem dirty não pede
        # confirmação e não toca updatedAt.
        assert page.locator('#mvpNotesSaveBtn').is_hidden(), 'sem alteração não há o que salvar'
        page.locator('.mvpn-card[data-type="bug"]').click()
        task_after = next(it for it in notes_state(page) if it['id'] == task_before['id'])
        assert task_after['updatedAt'] == task_before['updatedAt'], 'updatedAt não deveria mudar sem alteração real'

        # ---- 3. dirty state: recusar descarte mantém o rascunho; aceitar descarta ----
        page.locator('.mvpn-card[data-type="feature"]').click()
        page.locator('#mvpNoteContent').fill('Rascunho não salvo')
        page.evaluate("window.confirm = () => false")
        click_id(page, 'mvpNotesCloseBtn')
        assert page.locator('#mvpNotesOverlay').evaluate("el => el.classList.contains('show')") is True
        assert page.locator('#mvpNoteContent').input_value() == 'Rascunho não salvo'
        page.evaluate("window.confirm = () => true")
        click_id(page, 'mvpNotesCloseBtn')
        assert page.locator('#mvpNotesOverlay').evaluate("el => el.classList.contains('show')") is False
        assert not any(it['title'] == 'Rascunho não salvo' for it in notes_state(page)), 'rascunho não deveria ter sido salvo'

        # ---- 4. busca e filtros, isolados e combinados ----
        click_id(page, 'headerNotesBtn')
        page.locator('#mvpNotesSearch').fill('Bug de teste')
        assert page.locator('.mvpn-card').count() == 1
        page.locator('#mvpNotesSearch').fill('')
        # Fase C: filtros escondidos até o botão; botão anuncia estado e popover
        assert page.locator('#mvpNotesFiltersWrap.open').count() == 0, 'filtros começam escondidos'
        assert page.locator('#mvpNotesFiltersBtn').get_attribute('aria-expanded') == 'false'
        assert page.locator('#mvpNotesFiltersBtn').get_attribute('aria-haspopup') == 'true'
        click_id(page, 'mvpNotesFiltersBtn')
        assert page.locator('#mvpNotesFiltersBtn').get_attribute('aria-expanded') == 'true'
        page.locator('#mvpNotesFilterType').select_option('bug')
        assert page.locator('.mvpn-card').count() == 1
        page.locator('#mvpNotesFilterStatus').select_option('in_progress')
        assert page.locator('.mvpn-card').count() == 1  # bug agora está in_progress
        page.locator('#mvpNotesFilterPriority').select_option('low')
        assert page.locator('.mvpn-card').count() == 0
        assert 'Nenhuma nota encontrada' in page.locator('.mvpn-empty').inner_text()
        assert page.locator('#mvpNotesFiltersCount').inner_text() == '3', 'contador de filtros ativos'
        # busca + filtro combinam (interseção, nunca sobrescrita)
        page.locator('#mvpNotesSearch').fill('Bug de teste')
        page.locator('#mvpNotesFilterPriority').select_option('critical')
        assert page.locator('.mvpn-card').count() == 1, 'busca e filtro combinados'
        page.locator('#mvpNotesFilterPriority').select_option('low')
        assert 'busca e aos filtros' in page.locator('.mvpn-empty').inner_text(), 'vazio contextual (busca+filtros)'
        click_id(page, 'mvpNotesFiltersClearBtn')
        assert page.locator('#mvpNotesFiltersCount').is_hidden(), 'limpar zera o contador'
        assert page.locator('#mvpNotesFiltersWrap.open').count() == 1, 'limpar mantém o popover aberto'
        assert page.locator('#mvpNotesSearch').input_value() == 'Bug de teste', 'limpar filtros preserva a busca'
        page.locator('#mvpNotesSearch').fill('')
        click_id(page, 'mvpNotesFiltersBtn')
        assert page.locator('#mvpNotesFiltersWrap.open').count() == 0, 'botão fecha o popover desktop'

        # ---- 5. exclusão: cancelar preserva, confirmar remove só o item selecionado ----
        before_count = len(notes_state(page))
        page.locator("[data-mvp-folder='done']").click()
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
        start_new_note(page)
        assert page.evaluate('mvpNotesCurrentScreenId()') == 'config', 'tela de origem capturada na Central'
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
        # O export é assíncrono: depois do blob, a continuação registra o sucesso e chama
        # save(). Sem esperar a conclusão, o wipe logo abaixo CORRIA com essa continuação
        # e o save() tardio regravava a chave recém-apagada (flake real: passou 2x,
        # falhou 2x). Ancorar na marca de sucesso torna a ordem determinística.
        page.wait_for_function("S.dataGovernance && S.dataGovernance.export && S.dataGovernance.export.lastExportAt !== ''")

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
        click_id(page, 'headerConfigBtn')
        page.evaluate("settingsNavigateToLeaf('backup')")
        assert page.locator('#wipeAllBtn').is_visible(), 'Zona de Perigo deve estar acessível em Configurações'
        click_id(page, 'wipeAllBtn')
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

        # ---- 12b. pastas (introduzidas no schema v2): CRUD, visões, vínculo, busca,
        #      filtros, dirty, backup. O estado de uma página nova é sempre o schema ATUAL —
        #      a menção a v2 é histórica (quando o campo folders[] nasceu), não a versão viva.
        page = prepare_page(browser, url)
        assert page.evaluate('S.mvpNotes.schemaVersion') == 5
        page.locator('#headerNotesBtn').click()
        # criação via UI (prompt real interceptado); pasta nova é selecionada
        page.evaluate("window.prompt = () => 'Interface de Configurações'")
        click_id(page, 'mvpNotesNewFolderBtn')
        iface_id = page.evaluate("S.mvpNotes.folders[0].id")
        assert page.evaluate('mvpNotesUI.activeFolder') == iface_id, 'pasta recém-criada deveria ficar ativa'
        rendered_folder_title = page.locator('#mvpNotesViewTitle').text_content()
        assert rendered_folder_title == 'Interface de Configurações', {
            'rendered': rendered_folder_title,
            'activeFolder': page.evaluate('mvpNotesUI.activeFolder'),
            'folder': page.evaluate('S.mvpNotes.folders[0]'),
        }
        # nota criada dentro da pasta herda o vínculo; em Todas as Notas/Sem pasta o padrão é null
        start_new_note(page)
        assert page.evaluate('mvpNotesUI.draft.folderId') == iface_id
        page.locator('#mvpNoteContent').fill('Nota da pasta Interface')
        click_id(page, 'mvpNotesSaveBtn')
        page.locator('[data-mvp-folder="all"]').click()
        start_new_note(page)
        assert page.evaluate('mvpNotesUI.draft.folderId') is None
        page.locator('#mvpNoteContent').fill('Nota solta')
        click_id(page, 'mvpNotesSaveBtn')
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
        # filtro preservado ao trocar de pasta (abrindo o popover para operá-lo)
        click_id(page, 'mvpNotesFiltersBtn')
        page.locator('#mvpNotesFilterType').select_option('task')
        page.locator('[data-mvp-folder="unfiled"]').click()
        assert page.evaluate("mvpNotesUI.filterType") == 'task', 'trocar de pasta não pode limpar filtros'
        # No desktop, trocar de pasta é clique fora e fecha o popover; o filtro persiste.
        click_id(page, 'mvpNotesFiltersBtn')
        page.locator('#mvpNotesFilterType').select_option('all')
        click_id(page, 'mvpNotesFiltersBtn')
        # mover nota entre pastas pelo editor: só folderId+updatedAt mudam
        page.locator('[data-mvp-folder="all"]').click()
        moved = page.evaluate("S.mvpNotes.items.find(it => it.title === 'Nota solta')")
        page.locator(f'[data-mvp-note-id="{moved["id"]}"]').click()
        open_inspector(page)
        page.locator('#mvpNoteFolder').select_option(iface_id)
        click_id(page, 'mvpNotesSaveBtn')
        after = page.evaluate(f"S.mvpNotes.items.find(it => it.id === '{moved['id']}')")
        assert after['folderId'] == iface_id and after['createdAt'] == moved['createdAt'] \
            and after['screenId'] == moved['screenId'] and after['updatedAt'] != moved['updatedAt']
        # dirty state protege a troca de pasta
        page.locator(f'[data-mvp-note-id="{moved["id"]}"]').click()
        page.locator('#mvpNoteContent').fill('Rascunho de pasta')
        page.evaluate("window.confirm = () => false")
        page.locator('[data-mvp-folder="unfiled"]').click()
        assert page.locator('#mvpNoteContent').input_value() == 'Rascunho de pasta', 'recusar descarte mantém o rascunho'
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
        start_new_note(page)
        page.locator('#mvpNoteContent').fill('Nota do backup em pasta')
        click_id(page, 'mvpNotesSaveBtn')
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
            assert page.evaluate("S.mvpNotes.items.find(it => it.title === 'Nota do backup em pasta')?.folderId") == backup_folder_id, \
                'vínculo nota↔pasta deveria ser restaurado'
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
        # migração v1 → schema atual: folders=[] e folderId=null, sem perder nada
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
        assert legacy_v2 == {'sv': 5, 'folders': [], 'fid': None, 'id': 'l1'}, legacy_v2
        # idempotência: normalize(normalize(state)) === normalize(state), em igualdade
        # estrutural (sessionStableValue ordena chaves), para legado v1, v2 com pastas
        # ambíguas/duplicadas/órfãs, e estado atual já bem-formado (segunda passada não deve alterar nada).
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
            && s1c.mvpNotes.schemaVersion === 5;

          return cases;
        }""")
        assert idempotency == {'legacyV1': True, 'messyV2': True, 'wellFormedV2': True}, idempotency
        assert_no_errors(page.jpwealth_observed)
        page.close()

        # ---- 12c. A-002: badge/visibilidade sincronizados após importação e Zona de Perigo ----
        page = prepare_page(browser, url)
        create_note(page, 'task', 'Nota local A', '', 'medium', 'open')
        create_note(page, 'task', 'Nota local B', '', 'medium', 'open')
        assert page.locator('#headerNotesBadge').inner_text() == '2'
        # importa backup com 5 notas ativas e ícone OCULTO — boot() deve sincronizar tudo
        backup5 = page.evaluate("""() => { const s = structuredClone(DEFAULTS);
          s.mvpNotes = {schemaVersion: 2, showHeaderIcon: false, folders: [], items: []};
          for (let i = 1; i <= 5; i++) s.mvpNotes.items.push({id: 'imp_' + i, type: 'bug',
            title: 'Importada ' + i, description: '', priority: 'high', status: 'open',
            folderId: null, screenId: 'dash', buildId: 'B', createdAt: 'c', updatedAt: 'u' + i});
          return JSON.stringify({tipo: 'jpwealth_full_backup', state: s}); }""")
        with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as fx:
            fx.write(backup5); cinco = fx.name
        try:
            page.evaluate("window.confirm = () => true")
            page.locator('#importFullBackupInput').set_input_files(cinco)
            page.wait_for_timeout(700)
            page.evaluate("() => { window.__onbShown = true; closeModal(); }")
        finally:
            Path(cinco).unlink(missing_ok=True)
        assert page.locator('#headerNotesBtn').is_hidden(), 'showHeaderIcon:false importado deve ocultar o botão'
        assert page.evaluate("document.getElementById('headerNotesBadge').textContent") == '5', \
            'badge deveria refletir as 5 notas ativas importadas sem precisar de CRUD'
        # o drawer (via Configurações, ícone oculto) conta o mesmo que o header
        click_id(page, 'headerConfigBtn')
        page.evaluate("settingsNavigateToLeaf('interface')")
        click_id(page, 'mvpNotesOpenFromSettingsBtn')
        assert page.locator('#mvpNotesHeadCount').count() == 0
        click_id(page, 'mvpNotesCloseBtn')
        click_id(page, 'settingsCloseBtn')
        # importa backup com 1 nota ativa e ícone VISÍVEL
        backup1 = page.evaluate("""() => { const s = structuredClone(DEFAULTS);
          s.mvpNotes = {schemaVersion: 2, showHeaderIcon: true, folders: [], items: [
            {id: 'solo', type: 'task', title: 'Só uma', description: '', priority: 'medium',
             status: 'open', folderId: null, screenId: 'dash', buildId: 'B', createdAt: 'c', updatedAt: 'u'}]};
          return JSON.stringify({tipo: 'jpwealth_full_backup', state: s}); }""")
        with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as fx:
            fx.write(backup1); um = fx.name
        try:
            page.locator('#importFullBackupInput').set_input_files(um)
            page.wait_for_timeout(700)
            page.evaluate("() => { window.__onbShown = true; closeModal(); }")
        finally:
            Path(um).unlink(missing_ok=True)
        assert page.locator('#headerNotesBtn').is_visible(), 'showHeaderIcon:true importado deve exibir o botão'
        assert page.locator('#headerNotesBadge').inner_text() == '1'
        # Zona de Perigo zera o badge no mesmo boot()
        page.evaluate("window.prompt = () => 'APAGAR'; window.alert = () => {};")
        click_id(page, 'headerConfigBtn')
        page.evaluate("settingsNavigateToLeaf('backup')")
        click_id(page, 'wipeAllBtn')
        page.wait_for_timeout(500)
        page.evaluate("() => { window.__onbShown = true; closeModal(); }")
        assert page.evaluate("document.getElementById('headerNotesBadge').hidden") is True, \
            'após a Zona de Perigo o badge deve sumir sem interação manual'
        assert page.locator('#headerNotesBtn').is_visible(), 'visibilidade volta ao padrão (mostrar)'
        assert_no_errors(page.jpwealth_observed)
        page.close()

        # ---- 14. evolução v3: Concluído (visão virtual), completedAt, resize e mobile ----
        page = prepare_page(browser, base_url + 'index.html')
        assert page.evaluate('S.mvpNotes.schemaVersion') == 5
        assert page.evaluate('S.mvpNotes.ui.drawerWidth') == 980, 'padrão v5 do drawer'
        assert page.evaluate('S.mvpNotes.ui.foldersPaneWidth') == 190
        assert page.evaluate('S.mvpNotes.ui.notesPaneWidth') == 300
        create_note(page, 'task', 'Fica ativa', '', 'medium', 'open')
        create_note(page, 'task', 'Vai concluir', '', 'medium', 'open')
        page.evaluate("""() => {
          const folder = mvpNotesCreateFolder('Pasta Origem');
          const it = S.mvpNotes.items.find(i => i.title === 'Vai concluir');
          it.folderId = folder.id; save();
        }""")
        page.evaluate("""() => {
          const it = S.mvpNotes.items.find(i => i.title === 'Vai concluir');
          mvpNotesUpdate(it.id, {type: it.type, content: it.content, priority: it.priority,
            status: 'done', folderId: it.folderId, aiImplementationPolicy: it.aiImplementationPolicy});
        }""")
        done_item = page.evaluate("S.mvpNotes.items.find(i => i.title === 'Vai concluir')")
        assert done_item['status'] == 'done' and done_item['completedAt'], 'concluir deve carimbar completedAt'
        assert done_item['folderId'], 'folderId não pode mudar ao concluir'
        assert page.evaluate('mvpNotesDoneCount()') == 1
        assert page.evaluate("mvpNotesFolderItemCount(S.mvpNotes.folders[0].id)") == 0, 'backlog da pasta não conta concluídas'
        assert page.evaluate('mvpNotesActiveCount()') == 1, 'badge do header não conta concluídas'
        click_id(page, 'headerNotesBtn')
        page.locator("[data-mvp-folder='done']").click()
        page.wait_for_timeout(150)
        assert page.locator('#mvpNotesViewTitle').text_content() == 'Concluído'
        assert page.locator('#mvpNotesFiltersWrap.open').count() == 0, 'filtros ficam ocultos até o botão (v5)'
        assert page.locator('.mvpn-card').count() == 1
        page.locator('.mvpn-card').first.click()
        open_inspector(page)
        page.locator('#mvpNoteStatus').select_option('open')
        click_id(page, 'mvpNotesSaveBtn')
        reopened = page.evaluate("S.mvpNotes.items.find(i => i.title === 'Vai concluir')")
        assert reopened['status'] == 'open' and reopened['completedAt'] is None, 'reabrir zera completedAt'
        assert reopened['folderId'] == done_item['folderId'], 'reabrir preserva a pasta original'
        assert page.evaluate('mvpNotesDoneCount()') == 0
        click_id(page, 'mvpNotesCloseBtn')
        # resize externo do drawer: faixa canônica v5 (mínimo DERIVADO, 1600), persistência e recarga
        # 721 = 150 + 240 + 320 + 2*5 + 1 — a menor largura em que as três colunas cabem
        # nos seus pisos. Conferido contra as constantes para não virar número mágico aqui.
        assert page.evaluate('MVP_NOTES_DRAWER_MIN') == page.evaluate(
            'MVP_NOTES_FOLDERS_MIN + MVP_NOTES_LIST_MIN + MVP_NOTES_EDITOR_MIN'
            ' + MVP_NOTES_PANE_HANDLE*2 + MVP_NOTES_DRAWER_CHROME'), 'mínimo do drawer deve ser derivado'
        assert page.evaluate('MVP_NOTES_DRAWER_MIN') == 721
        click_id(page, 'headerNotesBtn')
        page.evaluate('mvpNotesApplyDrawerWidth(1100); mvpNotesPersistDrawerWidth(1100)')
        click_id(page, 'mvpNotesCloseBtn')
        click_id(page, 'headerNotesBtn')
        # A renderização respeita os cintos de segurança (80vw, viewport-32); o valor
        # guardado permanece 1100 mesmo que a janela obrigue a desenhar menos.
        largura = page.evaluate("() => Math.round(document.getElementById('mvpNotesDrawer').getBoundingClientRect().width)")
        esperada = page.evaluate("() => Math.min(1100, Math.round(innerWidth*0.8), 1600, innerWidth-32)")
        assert largura == esperada, (largura, esperada)
        assert page.evaluate('mvpNotesClampWidth(100)') == 721, 'mínimo canônico derivado'
        assert page.evaluate('mvpNotesClampPersistable(99999)') == 1600, 'máximo canônico v5'
        click_id(page, 'mvpNotesCloseBtn')
        page.reload(wait_until='load')
        page.wait_for_timeout(700)
        page.evaluate("() => { window.__onbShown = true; closeModal(); window.confirm = () => false; window.prompt = () => null; }")
        assert page.evaluate('S.mvpNotes.ui.drawerWidth') == 1100, 'largura sobrevive à recarga'
        page.close()
        # mobile: navegação em camadas Pastas → Lista → Editor → voltar + folha de filtros
        page = prepare_page(browser, base_url + 'index.html')
        page.set_viewport_size({'width': 390, 'height': 800})
        click_id(page, 'headerNotesBtn')
        drawer = page.locator('#mvpNotesDrawer')
        assert drawer.get_attribute('data-mobile-stage') == 'folders'
        assert page.locator('#mvpNotesResizeHandle').is_hidden(), 'resize handle não existe em mobile'
        assert page.locator('#mvpNotesFoldersHandle').is_hidden(), 'separador Pastas|Lista some em mobile'
        assert page.locator('#mvpNotesListHandle').is_hidden(), 'separador Lista|Editor some em mobile'
        page.locator("[data-mvp-folder='all']").click()
        assert drawer.get_attribute('data-mobile-stage') == 'list'
        start_new_note(page)
        assert drawer.get_attribute('data-mobile-stage') == 'editor'
        click_id(page, 'mvpNotesBackBtn')
        assert drawer.get_attribute('data-mobile-stage') == 'list'
        click_id(page, 'mvpNotesBackBtn')
        assert drawer.get_attribute('data-mobile-stage') == 'folders'
        page.locator("[data-mvp-folder='all']").click()
        click_id(page, 'mvpNotesFiltersBtn')
        assert page.locator('#mvpNotesFiltersWrap').evaluate("el => el.classList.contains('open')") is True
        click_id(page, 'mvpNotesFiltersApplyBtn')
        assert page.locator('#mvpNotesFiltersWrap').evaluate("el => el.classList.contains('open')") is False
        assert_no_errors(page.jpwealth_observed)
        page.close()

        # ---- 14b. Fase D: separadores internos das três colunas -------------------
        # Cobertura ESTRUTURAL do motor de geometria: os gestos de ponteiro reais são
        # verificados em navegador; aqui garantimos contrato ARIA, limites, invariante,
        # teclado, duplo clique, persistência e ausência de efeito colateral no estado.
        page = prepare_page(browser, base_url + 'index.html')
        create_note(page, 'bug', 'Nota para geometria', 'corpo', 'high', 'open')
        page.set_viewport_size({'width': 1440, 'height': 900})
        click_id(page, 'headerNotesBtn')
        # contrato dos dois separadores
        for hid, rotulo in (('mvpNotesFoldersHandle', 'pastas'), ('mvpNotesListHandle', 'lista')):
            h = page.locator('#' + hid)
            assert h.get_attribute('role') == 'separator'
            assert h.get_attribute('aria-orientation') == 'vertical'
            assert h.get_attribute('tabindex') == '0'
            assert h.get_attribute('aria-valuenow') and h.get_attribute('aria-valuetext')
            assert rotulo in h.get_attribute('aria-valuetext').lower(), h.get_attribute('aria-valuetext')
            assert page.evaluate(f"getComputedStyle(document.getElementById({hid!r})).cursor") == 'ew-resize'
        # invariante fundamental: as três colunas + separadores cabem no corpo, sempre
        invariante = """() => {
          const w = id => document.getElementById(id).getBoundingClientRect().width;
          return (w('mvpNotesFolderSidebar') + w('mvpNotesListPane') + w('mvpNotesEditorPane') + 10)
                 <= w('mvpNotesBody') + 1;
        }"""
        assert page.evaluate(invariante), 'colunas não cabem no corpo do drawer'
        # teclado: passo 20, Shift 60, e a seta representa o movimento físico do separador
        base = page.evaluate("mvpNotesRenderedPanes().folders")
        page.locator('#mvpNotesFoldersHandle').press('ArrowRight')
        assert page.evaluate("mvpNotesRenderedPanes().folders") == base + 20
        page.locator('#mvpNotesFoldersHandle').press('Shift+ArrowRight')
        assert page.evaluate("mvpNotesRenderedPanes().folders") == base + 80
        page.locator('#mvpNotesFoldersHandle').press('ArrowLeft')
        assert page.evaluate("mvpNotesRenderedPanes().folders") == base + 60
        assert page.evaluate('S.mvpNotes.ui.foldersPaneWidth') == base + 60, 'tecla persiste'
        # limites de cada coluna, com o piso do editor preservado
        page.locator('#mvpNotesFoldersHandle').press('Home')
        assert page.evaluate('S.mvpNotes.ui.foldersPaneWidth') == 150
        page.locator('#mvpNotesListHandle').press('Home')
        assert page.evaluate('S.mvpNotes.ui.notesPaneWidth') == 240
        page.locator('#mvpNotesListHandle').press('End')
        limites = page.evaluate('mvpNotesPaneLimits()')
        assert page.evaluate('mvpNotesRenderedPanes().list') == limites['listMax']
        assert page.evaluate(invariante)
        editor = page.evaluate("Math.round(document.getElementById('mvpNotesEditorPane').getBoundingClientRect().width)")
        assert editor >= 320, ('editor abaixo do piso funcional', editor)
        # Libera espaço antes do reset: com a lista no máximo, 190px para Pastas violaria
        # o piso do editor e o motor corretamente apararia o valor.
        page.locator('#mvpNotesListHandle').press('Home')
        # duplo clique restaura só a própria coluna
        lista_antes = page.evaluate('mvpNotesRenderedPanes().list')
        page.locator('#mvpNotesFoldersHandle').dblclick()
        assert page.evaluate('S.mvpNotes.ui.foldersPaneWidth') == 190
        assert page.evaluate('mvpNotesRenderedPanes().list') == lista_antes, 'a outra coluna não é tocada'
        page.locator('#mvpNotesListHandle').dblclick()
        assert page.evaluate('S.mvpNotes.ui.notesPaneWidth') == 300
        # redimensionar não é edição: nada de dirty, nada de updatedAt
        page.locator('.mvpn-card').first.click()
        antes = notes_state(page)[0]['updatedAt']
        page.locator('#mvpNotesListHandle').press('ArrowLeft')
        assert page.evaluate('mvpNotesUI.draftDirty') is False, 'resize não pode sujar a nota'
        assert notes_state(page)[0]['updatedAt'] == antes, 'resize não pode tocar updatedAt'
        assert page.evaluate('mvpNotesUI.selectedId') is not None, 'seleção permanece'
        # preferências sobrevivem a fechar/reabrir
        page.evaluate('mvpNotesPersistPaneWidth("foldersPaneWidth", 260); mvpNotesPersistPaneWidth("notesPaneWidth", 380)')
        click_id(page, 'mvpNotesCloseBtn')
        click_id(page, 'headerNotesBtn')
        assert page.evaluate('mvpNotesRenderedPanes()') == {'folders': 260, 'list': 380}
        # drawer no MÍNIMO: renderização se ajusta, preferência NÃO é reescrita, e nenhuma
        # das três colunas fica abaixo do seu piso — a invariante que define o mínimo.
        page.evaluate('mvpNotesApplyDrawerWidth(MVP_NOTES_DRAWER_MIN); mvpNotesPersistDrawerWidth(MVP_NOTES_DRAWER_MIN)')
        estreito = page.evaluate('mvpNotesRenderedPanes()')
        assert estreito['list'] == 240 and estreito['folders'] == 150, estreito
        pisos = page.evaluate("""() => {
          const w = id => Math.round(document.getElementById(id).getBoundingClientRect().width);
          return {pastas: w('mvpNotesFolderSidebar'), lista: w('mvpNotesListPane'),
                  editor: w('mvpNotesEditorPane'), drawer: w('mvpNotesDrawer')};
        }""")
        assert pisos['pastas'] >= 150 and pisos['lista'] >= 240 and pisos['editor'] >= 320, pisos
        assert page.evaluate('S.mvpNotes.ui.foldersPaneWidth') == 260, 'preferência preservada'
        assert page.evaluate('S.mvpNotes.ui.notesPaneWidth') == 380, 'preferência preservada'
        assert page.evaluate(invariante)
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1"), 'sem overflow horizontal'
        # drawer largo de novo: as preferências originais voltam a valer
        page.evaluate('mvpNotesApplyDrawerWidth(1200); mvpNotesPersistDrawerWidth(1200)')
        assert page.evaluate('mvpNotesRenderedPanes()') == {'folders': 260, 'list': 380}
        # ---- PREFERÊNCIA PERSISTIDA  vs  LARGURA RENDERIZADA ----------------------
        # A normalização valida cada preferência ISOLADAMENTE e nada mais. Uma combinação
        # que não caiba no drawer atual é resolvida no DESENHO (mvpNotesFitPanes), nunca
        # reescrevendo o estado — senão um painel temporariamente estreito apagaria a
        # escolha do operador e não haveria o que restaurar ao alargar de novo.
        combinacao = page.evaluate("""() => {
          S.mvpNotes.ui = {drawerWidth: 980, foldersPaneWidth: 320, notesPaneWidth: 520};
          mvpNotesNormalizeState(); return S.mvpNotes.ui;
        }""")
        assert combinacao['foldersPaneWidth'] == 320, combinacao   # preferência intacta…
        assert combinacao['notesPaneWidth'] == 520, combinacao     # …mesmo sem caber junta
        # espaco(980) = 980 - 1 (borda) - 10 (dois separadores) = 969; excesso = 320+520+320-969 = 191,
        # cortado primeiro da Lista: 520-191 = 329. Só no desenho — o estado acima segue 320/520.
        assert page.evaluate('mvpNotesFitPanes(320, 520, 980)') == {'folders': 320, 'list': 329}, 'o ajuste é do render'
        # valores impossíveis ISOLADAMENTE continuam normalizados
        invalidos = page.evaluate("""() => {
          S.mvpNotes.ui = {drawerWidth: -5, foldersPaneWidth: -100, notesPaneWidth: 99999};
          mvpNotesNormalizeState(); return S.mvpNotes.ui;
        }""")
        assert invalidos == {'drawerWidth': 721, 'foldersPaneWidth': 150, 'notesPaneWidth': 520}, invalidos
        # backup antigo: só o drawerWidth sobe ao mínimo derivado; as colunas são preservadas
        antigo = page.evaluate("""() => {
          S.mvpNotes.ui = {drawerWidth: 700, foldersPaneWidth: 190, notesPaneWidth: 300};
          mvpNotesNormalizeState(); return S.mvpNotes.ui;
        }""")
        assert antigo == {'drawerWidth': 721, 'foldersPaneWidth': 190, 'notesPaneWidth': 300}, antigo
        # …e no drawer mínimo o DESENHO cai para os pisos, sem tocar na preferência
        page.evaluate('save(); mvpNotesApplyDrawerWidth(MVP_NOTES_DRAWER_MIN)')
        assert page.evaluate('mvpNotesRenderedPanes()') == {'folders': 150, 'list': 240}
        assert page.evaluate('mvpNotesPanePrefs()') == {'folders': 190, 'list': 300}, 'preferência preservada'
        pisos_min = page.evaluate("""() => {
          const w = id => Math.round(document.getElementById(id).getBoundingClientRect().width);
          return {pastas: w('mvpNotesFolderSidebar'), lista: w('mvpNotesListPane'), editor: w('mvpNotesEditorPane')};
        }""")
        assert pisos_min == {'pastas': 150, 'lista': 240, 'editor': 320}, pisos_min
        # ampliar o drawer restaura o desenho às preferências, SEM reload
        page.evaluate('mvpNotesApplyDrawerWidth(1100); mvpNotesPersistDrawerWidth(1100)')
        assert page.evaluate('mvpNotesRenderedPanes()') == {'folders': 190, 'list': 300}
        # reduzir de novo não altera preferência nenhuma
        page.evaluate('mvpNotesApplyDrawerWidth(MVP_NOTES_DRAWER_MIN); mvpNotesPersistDrawerWidth(MVP_NOTES_DRAWER_MIN)')
        assert page.evaluate('mvpNotesPanePrefs()') == {'folders': 190, 'list': 300}
        # e sobrevive à recarga: o estado no disco continua com 190/300
        click_id(page, 'mvpNotesCloseBtn')
        page.reload(wait_until='load')
        page.wait_for_timeout(700)
        page.evaluate("() => { window.__onbShown = true; closeModal(); window.confirm = () => false; window.prompt = () => null; }")
        assert page.evaluate('S.mvpNotes.ui.foldersPaneWidth') == 190, 'reload não pode apagar a preferência'
        assert page.evaluate('S.mvpNotes.ui.notesPaneWidth') == 300, 'reload não pode apagar a preferência'
        click_id(page, 'headerNotesBtn')
        assert page.evaluate('mvpNotesRenderedPanes()') == {'folders': 150, 'list': 240}, 'no mínimo, desenho nos pisos'
        page.evaluate('mvpNotesApplyDrawerWidth(1100); mvpNotesPersistDrawerWidth(1100)')
        assert page.evaluate('mvpNotesRenderedPanes()') == {'folders': 190, 'list': 300}, 'após reload, ampliar restaura'
        assert_no_errors(page.jpwealth_observed)
        page.close()

        # ---- 14c. Fase E: ordem MANUAL das pastas (position) -----------------------
        # PASTAS têm ordem manual; NOTAS têm ordem natural. As duas semânticas convivem e
        # esta seção verifica que não se contaminam.
        page = prepare_page(browser, base_url + 'index.html')
        page.set_viewport_size({'width': 1440, 'height': 900})
        page.evaluate("""() => {
          ['Interface', 'Dashboard', 'Motor de Lote', 'Forex'].forEach(n => mvpNotesCreateFolder(n));
          const alvo = S.mvpNotes.folders[0].id;
          ['Bug 10', 'Bug 2', 'Bug 1'].forEach(t => mvpNotesCreate({content: t + '\\ncorpo', type: 'bug',
            priority: 'high', status: 'open', folderId: alvo}));
          save();
        }""")
        click_id(page, 'headerNotesBtn')
        ordem = lambda: page.evaluate('S.mvpNotes.folders.map(f => f.name)')
        posicoes = lambda: page.evaluate('S.mvpNotes.folders.map(f => f.position)')
        assert ordem() == ['Interface', 'Dashboard', 'Motor de Lote', 'Forex']
        assert posicoes() == [0, 1, 2, 3], 'positions contíguas a partir de 0'
        # visões do sistema não são reordenáveis — nem alça, nem menu, nem marcador de linha
        for vista in ('all', 'unfiled', 'done'):
            assert page.locator(f"[data-mvp-folder-row='{vista}']").count() == 0
        assert page.locator('[data-mvp-folder-drag]').count() == 4, 'só as 4 pastas reais têm alça'
        # operação central: mover Forex para o topo
        assert page.evaluate("mvpNotesMoveFolder(S.mvpNotes.folders[3].id, 0)") is True
        assert ordem() == ['Forex', 'Interface', 'Dashboard', 'Motor de Lote']
        assert posicoes() == [0, 1, 2, 3]
        # índice fora da faixa é aparado; mover para onde já está não é alteração
        forex = page.evaluate('S.mvpNotes.folders[0].id')
        assert page.evaluate(f'mvpNotesMoveFolder({forex!r}, 0)') is False, 'sem mudança = sem save'
        assert page.evaluate(f'mvpNotesMoveFolder({forex!r}, 99)') is True
        assert ordem()[-1] == 'Forex', 'índice acima do fim vai para o fim'
        assert page.evaluate("mvpNotesMoveFolder('inexistente', 0)") is False
        # menu "⋯": Mover para cima/baixo é a via de teclado e usa a MESMA operação central
        primeira = page.evaluate('S.mvpNotes.folders[0].id')
        ultima = page.evaluate('S.mvpNotes.folders[S.mvpNotes.folders.length-1].id')
        assert page.locator(f"[data-mvp-folder-row='{primeira}'] [data-mvp-folder-up]").count() == 0
        assert page.locator(f"[data-mvp-folder-row='{ultima}'] [data-mvp-folder-down]").count() == 0
        nome_ultima = page.evaluate('S.mvpNotes.folders[S.mvpNotes.folders.length-1].name')
        page.locator(f"[data-mvp-folder-row='{ultima}'] details.mvpn-folder-kebab summary").click()
        page.locator(f"[data-mvp-folder-row='{ultima}'] [data-mvp-folder-up]").click()
        assert ordem()[-2] == nome_ultima, 'Mover para cima trocou de posição'
        assert page.locator('#mvpNotesOrderLive').inner_text().startswith(f'Pasta {nome_ultima} movida para a posição')
        assert posicoes() == [0, 1, 2, 3], 'positions seguem contíguas'
        # reordenar NÃO é edição de nota
        page.locator('.mvpn-card').first.click()
        antes_upd = notes_state(page)[0]['updatedAt']
        antes_ticket = notes_state(page)[0]['ticket']
        sel = page.evaluate('mvpNotesUI.selectedId')
        page.evaluate("mvpNotesMoveFolder(S.mvpNotes.folders[0].id, 2)")
        assert page.evaluate('mvpNotesUI.draftDirty') is False
        assert page.evaluate('mvpNotesUI.selectedId') == sel, 'nota aberta continua aberta'
        assert notes_state(page)[0]['updatedAt'] == antes_upd, 'updatedAt da nota intacto'
        assert notes_state(page)[0]['ticket'] == antes_ticket, 'ticket imutável'
        # inspector e filtro Pasta seguem a ordem MANUAL (não alfabética)
        open_inspector(page)
        manual = ordem()
        assert page.evaluate("[...document.getElementById('mvpNoteFolder').options].map(o => o.textContent).slice(1)") == manual
        assert page.evaluate("[...document.getElementById('mvpNotesFilterFolder').options].map(o => o.textContent).slice(2)") == manual
        # …enquanto as NOTAS seguem ordem natural crescente (1, 2, 10 — nunca 1, 10, 2)
        page.evaluate("mvpNotesUI.activeFolder = S.mvpNotes.folders.find(f => f.name === 'Interface').id; renderMvpNotesList()")
        assert page.locator('.mvpn-card-title').all_inner_texts() == ['Bug 1', 'Bug 2', 'Bug 10']
        # CRUD e ordem: nova vai ao fim, renomear preserva, excluir renumera
        page.evaluate("mvpNotesCreateFolder('Zulu')")
        assert ordem()[-1] == 'Zulu' and posicoes() == [0, 1, 2, 3, 4]
        pos_zulu = page.evaluate("S.mvpNotes.folders.find(f => f.name === 'Zulu').position")
        page.evaluate("mvpNotesRenameFolder(S.mvpNotes.folders.find(f => f.name === 'Zulu').id, 'Alpha')")
        assert page.evaluate("S.mvpNotes.folders.find(f => f.name === 'Alpha').position") == pos_zulu, 'renomear não move'
        page.evaluate("mvpNotesDeleteFolder(S.mvpNotes.folders[0].id)")
        assert posicoes() == [0, 1, 2, 3], 'excluir renumera as restantes'
        # persistência: a ordem manual sobrevive à recarga
        esperado = ordem()
        page.evaluate('save()')
        click_id(page, 'mvpNotesCloseBtn')
        page.reload(wait_until='load')
        page.wait_for_timeout(700)
        page.evaluate("() => { window.__onbShown = true; closeModal(); window.confirm = () => false; window.prompt = () => null; }")
        assert page.evaluate('S.mvpNotes.folders.map(f => f.name)') == esperado, 'ordem manual sobrevive à recarga'
        # importação com positions inválidas: regra de desempate documentada —
        # 1) position válida crescente; 2) empate/inválida preserva a ordem do array; 3) renumera.
        casos = page.evaluate("""() => {
          const rodar = folders => {
            S.mvpNotes = {schemaVersion: 5, showHeaderIcon: true, folders, items: [], ui: {}};
            mvpNotesNormalizeState();
            const r = S.mvpNotes.folders.map(f => f.name + ':' + f.position);
            mvpNotesNormalizeState();
            return {r, idempotente: S.mvpNotes.folders.map(f => f.name + ':' + f.position).join() === r.join()};
          };
          return {
            duplicadas: rodar([{id:'f1',name:'A',position:0},{id:'f2',name:'B',position:0},{id:'f3',name:'C',position:0}]),
            extremos:   rodar([{id:'g1',name:'A',position:-5},{id:'g2',name:'B',position:9999},{id:'g3',name:'C',position:2}]),
            texto:      rodar([{id:'h1',name:'A',position:'2'},{id:'h2',name:'B'},{id:'h3',name:'C',position:'1'}]),
            lixo:       rodar([{id:'i1',name:'A',position:null},{id:'i2',name:'B',position:'abc'},{id:'i3',name:'C',position:NaN}])
          };
        }""")
        assert casos['duplicadas']['r'] == ['A:0', 'B:1', 'C:2'], casos['duplicadas']   # empate → ordem do array
        assert casos['extremos']['r'] == ['A:0', 'C:1', 'B:2'], casos['extremos']       # -5 < 2 < 9999
        assert casos['texto']['r'] == ['C:0', 'A:1', 'B:2'], casos['texto']             # "1" < "2"; ausente vai ao fim
        assert casos['lixo']['r'] == ['A:0', 'B:1', 'C:2'], casos['lixo']               # todas inválidas → ordem do array
        for k, v in casos.items():
            assert v['idempotente'], k
        assert_no_errors(page.jpwealth_observed)
        page.close()

        # ---- 14d. Fase F: experiência mobile em três estágios ----------------------
        page = prepare_page(browser, base_url + 'index.html')
        page.set_viewport_size({'width': 390, 'height': 844})
        page.evaluate("""() => {
          const f = mvpNotesCreateFolder('Interface de Configurações');
          mvpNotesCreate({content: 'Bug 1\\ncorpo', type: 'bug', priority: 'high', status: 'open', folderId: f.id});
          mvpNotesCreate({content: 'Bug 2\\ncorpo', type: 'bug', priority: 'low', status: 'done', folderId: f.id});
          save();
        }""")
        click_id(page, 'headerNotesBtn')
        drawer = page.locator('#mvpNotesDrawer')
        visivel = lambda sel: page.evaluate(f"getComputedStyle(document.querySelector({sel!r})).display !== 'none'")
        # Estágio A — Pastas: uma camada só, sem resize e sem alça de arraste
        assert drawer.get_attribute('data-mobile-stage') == 'folders'
        assert page.locator('#mvpNotesBackBtn').is_hidden(), 'no primeiro estágio não há para onde voltar'
        assert visivel('#mvpNotesFolderSidebar') and not visivel('#mvpNotesListPane') and not visivel('#mvpNotesEditorPane')
        assert page.locator('#mvpNotesResizeHandle').is_hidden()
        assert page.locator('#mvpNotesFoldersHandle').is_hidden()
        assert page.locator('#mvpNotesListHandle').is_hidden()
        # alça ≡ existe no DOM mas fica oculta: arraste por toque não foi implementado e
        # mostrá-la seria affordance falsa — a via mobile é o menu ⋯ (Fase E).
        assert page.locator('[data-mvp-folder-drag]').count() > 0
        assert not visivel('[data-mvp-folder-drag]'), 'alça de arraste deve sumir no celular'
        assert page.locator("[data-mvp-folder-row] [data-mvp-folder-down]").count() >= 0
        # camadas invisíveis não podem continuar tabuláveis
        focaveis = """sel => {
          const raiz = document.querySelector(sel);
          return [...raiz.querySelectorAll('button,input,select,textarea,[tabindex]')]
            .filter(e => e.offsetParent !== null).length;
        }"""
        assert page.evaluate(focaveis, '#mvpNotesListPane') == 0
        assert page.evaluate(focaveis, '#mvpNotesEditorPane') == 0
        # Estágio B — Lista: o estágio é REALMENTE aplicado ao DOM (não só ao estado)
        page.locator('[data-mvp-folder-row] .mvpn-folder-btn').first.click()
        assert drawer.get_attribute('data-mobile-stage') == 'list'
        assert page.locator('#mvpNotesTitle').inner_text() == 'Interface de Configurações'
        assert page.locator('#mvpNotesBackLabel').inner_text() == 'Pastas'
        assert visivel('#mvpNotesSearch'), 'busca permanente também no celular'
        assert not visivel('#mvpNotesFolderSidebar')
        # filtros em folha inferior de largura cheia
        click_id(page, 'mvpNotesFiltersBtn')
        folha = page.evaluate("""() => {
          const w = document.getElementById('mvpNotesFiltersWrap'); const c = getComputedStyle(w);
          return {pos: c.position, bottom: c.bottom, largura: Math.round(w.getBoundingClientRect().width),
                  viewport: window.innerWidth};
        }""")
        assert folha['pos'] == 'fixed' and folha['bottom'] == '0px', folha
        assert folha['largura'] == folha['viewport'], folha
        page.keyboard.press('Escape')
        # Estágio C — Nota: volta para a VISÃO DE ORIGEM, não para uma pasta inferida
        page.locator('.mvpn-card').first.click()
        assert drawer.get_attribute('data-mobile-stage') == 'editor'
        assert page.locator('#mvpNotesBackLabel').inner_text() == 'Interface de Configurações'
        assert not visivel('#mvpNotesListPane')
        assert page.evaluate("document.activeElement.id") != 'mvpNoteContent', \
            'abrir nota existente não rouba o foco (evita abrir o teclado sem pedir)'
        # inspector em folha inferior, com alvos de toque de 44px
        open_inspector(page)
        insp = page.evaluate("""() => {
          const i = document.getElementById('mvpNotesInspector'); const c = getComputedStyle(i);
          const alt = id => Math.round(document.getElementById(id).getBoundingClientRect().height);
          return {pos: c.position, largura: Math.round(i.getBoundingClientRect().width),
                  viewport: window.innerWidth, tipo: alt('mvpNoteType'), excluir: alt('mvpNoteDeleteBtn')};
        }""")
        assert insp['pos'] == 'fixed' and insp['largura'] == insp['viewport'], insp
        assert insp['tipo'] >= 44 and insp['excluir'] >= 44, ('alvos de toque', insp)
        page.keyboard.press('Escape')
        # dirty bloqueia a volta; cancelar mantém a nota aberta
        page.evaluate("() => { const t = document.getElementById('mvpNoteContent');"
                      " t.value += '\\nlinha nova'; t.dispatchEvent(new Event('input', {bubbles: true})); }")
        assert page.evaluate('mvpNotesUI.draftDirty') is True
        page.evaluate("() => { window.confirm = () => false; }")
        click_id(page, 'mvpNotesBackBtn')
        assert drawer.get_attribute('data-mobile-stage') == 'editor', 'cancelar mantém no editor'
        page.evaluate("() => { window.confirm = () => true; }")
        click_id(page, 'mvpNotesBackBtn')
        assert drawer.get_attribute('data-mobile-stage') == 'list'
        assert page.locator('#mvpNotesTitle').inner_text() == 'Interface de Configurações'
        # visão global Concluído: sem separador redundante (o título da vista já diz isso)
        click_id(page, 'mvpNotesBackBtn')
        page.locator("[data-mvp-folder='done']").click()
        assert page.locator('#mvpNotesTitle').inner_text() == 'Concluído'
        assert page.locator('.mvpn-group-sep').count() == 0, 'separador seria redundante aqui'
        # …enquanto dentro de uma pasta o separador continua existindo
        click_id(page, 'mvpNotesBackBtn')
        page.locator('[data-mvp-folder-row] .mvpn-folder-btn').first.click()
        assert page.locator('.mvpn-group-sep').count() == 1
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1"), 'sem overflow horizontal'
        assert_no_errors(page.jpwealth_observed)
        page.close()

        # ---- 14e. JPW-RQPNMK: ação única "Limpar todos os filtros" -----------------
        page = prepare_page(browser, base_url + 'index.html')
        page.set_viewport_size({'width': 1440, 'height': 900})
        page.evaluate("""() => {
          const f = mvpNotesCreateFolder('Interface');
          mvpNotesCreate({content: 'Corrigir botão mobile\\ncorpo', type: 'bug', priority: 'high',
            status: 'open', folderId: f.id, aiImplementationPolicy: 'analysis_only'});
          mvpNotesCreate({content: 'Outra\\ncorpo', type: 'task', priority: 'low',
            status: 'open', folderId: f.id, aiImplementationPolicy: 'blocked'});
          save();
        }""")
        click_id(page, 'headerNotesBtn')
        page.locator('.mvpn-card').first.click()
        click_id(page, 'mvpNotesFiltersBtn')
        limpar = page.locator('#mvpNotesFiltersClearBtn')
        # mecanismo ÚNICO: um só botão de limpeza, visível também no desktop (antes o bloco
        # de ações era display:none fora do mobile e não havia como desfazer um filtro).
        assert page.locator('[id*="ClearBtn"]').count() == 1, 'não pode haver dois mecanismos'
        assert limpar.is_visible(), 'a ação de limpar precisa existir no popover do desktop'
        # e precisa ser CLICÁVEL onde o operador clica, não só existir no DOM
        alcanceLimpar = page.evaluate("""() => {
          const w = document.getElementById('mvpNotesFiltersWrap');
          const b = document.getElementById('mvpNotesFiltersClearBtn');
          const rw = w.getBoundingClientRect(), rb = b.getBoundingClientRect();
          const alvo = document.elementFromPoint(Math.round(rb.left + rb.width / 2),
                                                 Math.round(rb.top + rb.height / 2));
          return {dentro: rb.bottom <= rw.bottom + 1, naViewport: rb.top >= 0 && rb.bottom <= window.innerHeight,
                  noPonto: alvo ? alvo.id : 'nada'};
        }""")
        assert alcanceLimpar['dentro'] and alcanceLimpar['naViewport'], alcanceLimpar
        assert alcanceLimpar['noPonto'] == 'mvpNotesFiltersClearBtn', alcanceLimpar
        assert limpar.inner_text() == 'Limpar todos os filtros'
        assert page.locator('#mvpNotesFiltersApplyBtn').is_hidden(), '"Aplicar" é exclusivo do mobile'
        # sem filtro ativo o botão fica desabilitado de forma acessível
        assert limpar.is_disabled()
        assert 'nenhum filtro ativo' in limpar.get_attribute('aria-label')
        page.locator('#mvpNotesFilterType').select_option('bug')
        assert page.locator('#mvpNotesFiltersCount').inner_text() == '1'
        assert limpar.is_enabled()
        # busca + mais filtros; a busca NÃO entra no contador
        page.locator('#mvpNotesSearch').fill('Corrigir')
        page.locator('#mvpNotesFilterPriority').select_option('high')
        page.locator('#mvpNotesFilterPolicy').select_option('analysis_only')
        assert page.locator('#mvpNotesFiltersCount').inner_text() == '3'
        antes_upd = notes_state(page)[0]['updatedAt']
        sel = page.evaluate('mvpNotesUI.selectedId')
        limpar.click()
        # zera os seis critérios e anuncia; não toca em busca, visão, nota nem estado salvo
        assert page.evaluate("""() => [mvpNotesUI.filterType, mvpNotesUI.filterStatus,
          mvpNotesUI.filterPriority, mvpNotesUI.filterFolder, mvpNotesUI.filterPeriod,
          mvpNotesUI.filterPolicy].every(v => v === 'all')""")
        assert page.locator('#mvpNotesFiltersCount').is_hidden()
        assert page.locator('#mvpNotesSearch').input_value() == 'Corrigir', 'busca preservada'
        assert page.evaluate("mvpNotesUI.activeFolder") == 'all', 'visão preservada'
        assert page.evaluate('mvpNotesUI.selectedId') == sel, 'nota aberta preservada'
        assert page.evaluate('mvpNotesUI.draftDirty') is False, 'limpar filtros não suja a nota'
        assert notes_state(page)[0]['updatedAt'] == antes_upd, 'updatedAt intacto'
        assert page.locator('#mvpNotesFiltersLive').inner_text() == 'Todos os filtros foram removidos.'
        assert limpar.is_disabled(), 'volta a desabilitado quando não há mais o que limpar'
        # no celular a folha traz o par [Limpar todos os filtros] [Aplicar]
        page.set_viewport_size({'width': 390, 'height': 844})
        page.evaluate("() => { closeMvpNotesDrawerNow(); openMvpNotesDrawer(document.getElementById('headerNotesBtn')); }")
        page.locator("[data-mvp-folder='all']").click()
        click_id(page, 'mvpNotesFiltersBtn')
        assert page.locator('#mvpNotesFiltersApplyBtn').is_visible(), '"Aplicar" reaparece no mobile'
        alturas = page.evaluate("""() => ['mvpNotesFiltersClearBtn', 'mvpNotesFiltersApplyBtn']
          .map(id => Math.round(document.getElementById(id).getBoundingClientRect().height))""")
        assert all(h >= 44 for h in alturas), ('alvo de toque', alturas)
        assert_no_errors(page.jpwealth_observed)
        page.close()

        # ---- 14f. JPW-9A78DE: exportar a nota em Markdown --------------------------
        page = prepare_page(browser, base_url + 'index.html')
        page.set_viewport_size({'width': 1440, 'height': 900})
        page.evaluate("""() => {
          const f = mvpNotesCreateFolder('FUNÇÃO - NOTAS MVP');
          mvpNotesCreate({content: 'Exportar notas individualmente em Markdown\\n\\nCorpo com ção, ü, 日本語 🚀.'
            + '\\n\\n<script>alert(1)<' + '/script>', type: 'feature', priority: 'medium',
            status: 'in_progress', folderId: f.id, aiImplementationPolicy: 'autonomous_allowed'});
          save();
        }""")
        click_id(page, 'headerNotesBtn')
        page.locator('.mvpn-card').first.click()
        open_inspector(page)
        exportar = page.locator('#mvpNoteExportMdBtn')
        assert exportar.is_visible() and exportar.inner_text() == 'Exportar como Markdown'
        # VISÍVEL DE FATO: o rodapé do inspector é pegajoso, então a ação não pode cair
        # abaixo da dobra quando os campos + fatos técnicos passam da altura do painel.
        alcance = page.evaluate("""() => {
          const i = document.getElementById('mvpNotesInspector');
          const b = document.getElementById('mvpNoteExportMdBtn');
          const ri = i.getBoundingClientRect(), rb = b.getBoundingClientRect();
          const alvo = document.elementFromPoint(Math.round(rb.left + rb.width / 2),
                                                 Math.round(rb.top + rb.height / 2));
          return {dentro: rb.bottom <= ri.bottom + 1 && rb.top >= ri.top - 1,
                  naViewport: rb.top >= 0 && rb.bottom <= window.innerHeight,
                  noPonto: alvo ? alvo.id : 'nada',
                  precisaRolar: i.scrollHeight > i.clientHeight + 1};
        }""")
        assert alcance['dentro'] and alcance['naViewport'], alcance
        assert alcance['noPonto'] == 'mvpNoteExportMdBtn', ('botão coberto ou fora da tela', alcance)
        # ação não destrutiva: fica FORA do bloco de exclusão
        assert page.locator('.mvpn-inspector-danger #mvpNoteExportMdBtn').count() == 0
        item = notes_state(page)[0]
        md = page.evaluate("mvpNotesMarkdown(S.mvpNotes.items[0])")
        nome = page.evaluate("mvpNotesMarkdownFilename(S.mvpNotes.items[0])")
        assert nome == item['ticket'] + '-exportar-notas-individualmente-em-markdown.md', nome
        assert md.startswith('---\n') and '\n---\n' in md, 'front matter delimitado'
        assert 'ticket: ' + item['ticket'] in md
        assert 'ai_implementation_policy: autonomous_allowed' in md
        assert 'source_revision: null' in md, 'sem SHA inventado'
        assert 'completed_at: null' in md
        assert '# Exportar notas individualmente em Markdown' in md
        assert md.count('Exportar notas individualmente em Markdown') == 1, 'título não duplicado no corpo'
        assert 'ção, ü, 日本語 🚀' in md, 'unicode preservado'
        assert '<script>alert(1)</script>' in md, 'HTML do usuário vira texto, nunca execução'
        # A primeira linha da nota é o TÍTULO DO DOCUMENTO: o arquivo abre sempre com um
        # único H1, nunca com H2..H6. Marcador ATX válido (1 a 6 "#" + espaço) é removido;
        # o que não é heading válido entra como texto do H1. O title persistido não muda.
        headings = page.evaluate("""() => {
          const gerar = t => {
            const n = mvpNotesCreate({content: t + '\\nCorpo.', type: 'feature', priority: 'medium',
              status: 'open', folderId: null, aiImplementationPolicy: 'analysis_only'});
            const it = S.mvpNotes.items.find(i => i.id === n.id);
            const md = mvpNotesMarkdown(it);
            const corpo = md.split(/^---$/m)[2];
            return {h1: (md.match(/^#.*$/m) || [])[0], titulo: it.title,
                    h1s: (corpo.match(/^# /gm) || []).length};
          };
          return ['Titulo', '# Titulo', '## Titulo', '###### Titulo', '#SemEspaco', '####### Sete']
            .map(t => Object.assign({entrada: t}, gerar(t)));
        }""")
        esperado = {
            'Titulo': '# Titulo', '# Titulo': '# Titulo', '## Titulo': '# Titulo',
            '###### Titulo': '# Titulo', '#SemEspaco': '# #SemEspaco',
            '####### Sete': '# ####### Sete',
        }
        for h in headings:
            assert h['h1'] == esperado[h['entrada']], h
            assert h['titulo'] == h['entrada'], ('title persistido não é normalizado', h)
            assert h['h1s'] == 1, ('um único H1 por arquivo', h)
        # normalizar o título não mexe nos headings do CORPO
        corpo = page.evaluate("""() => {
          const n = mvpNotesCreate({content: '## Exportar notas\\n\\nTexto.\\n\\n## Seção interna\\n\\nMais.',
            type: 'feature', priority: 'medium', status: 'open', folderId: null});
          const it = S.mvpNotes.items.find(i => i.id === n.id);
          return {md: mvpNotesMarkdown(it), titulo: it.title};
        }""")
        assert corpo['md'].count('# Exportar notas') == 1, 'título uma vez só, como H1'
        assert '## Seção interna' in corpo['md'], 'headings do corpo permanecem intactos'
        assert corpo['titulo'] == '## Exportar notas', 'title persistido intocado'
        # front matter: escalares citados em estilo SIMPLES, cujo único escape é '' — assim
        # dois-pontos, aspas duplas e barra invertida entram literais e voltam idênticos.
        yaml = page.evaluate(r"""() => ({
          doisPontos: mvpNotesYamlValor('Interface: Dashboard'),
          aspasDuplas: mvpNotesYamlValor('Projeto "Forex"'),
          aspaSimples: mvpNotesYamlValor("O'Brien & Cia"),
          barra: mvpNotesYamlValor('C:\\temp\\pasta'),
          booleano: mvpNotesYamlValor('true'),
          numero: mvpNotesYamlValor('0123'),
          indicador: mvpNotesYamlValor('- item'),
          simples: mvpNotesYamlValor('autonomous_allowed'),
          vazio: mvpNotesYamlValor('')
        })""")
        assert yaml['doisPontos'] == "'Interface: Dashboard'", yaml
        assert yaml['aspasDuplas'] == '\'Projeto "Forex"\'', yaml
        assert yaml['aspaSimples'] == "'O''Brien & Cia'", 'aspa simples é dobrada'
        assert yaml['barra'] == "'C:\\temp\\pasta'", 'barra invertida NÃO vira escape'
        assert yaml['booleano'] == "'true'" and yaml['numero'] == "'0123'", 'sem troca de tipo'
        assert yaml['indicador'] == "'- item'"
        assert yaml['simples'] == 'autonomous_allowed', 'token seguro fica sem aspas'
        assert yaml['vazio'] == 'null'
        # e o valor citado volta idêntico quando relido
        volta = page.evaluate(r"""() => {
          const original = 'Interface: "Dashboard" & FIIs\\backup';
          const f = mvpNotesCreateFolder(original);
          const n = mvpNotesCreate({content: 'Nota\\ncorpo', type: 'task', priority: 'low',
            status: 'open', folderId: f.id});
          const md = mvpNotesMarkdown(S.mvpNotes.items.find(i => i.id === n.id));
          const linha = (md.match(/^folder: (.*)$/m) || [])[1];
          const lido = linha.startsWith("'") ? linha.slice(1, -1).replace(/''/g, "'") : linha;
          return {original, lido, todasLinhas: md.split(/^---$/m)[1].trim().split('\\n')
            .every(l => /^[a-z_]+: /.test(l))};
        }""")
        assert volta['lido'] == volta['original'], volta
        assert volta['todasLinhas'], 'front matter continua chave: valor em toda linha'
        # metadados HISTÓRICOS da nota, nunca os do build em execução
        hist = page.evaluate("""() => {
          const n = mvpNotesCreate({content: 'Antiga\\ncorpo', type: 'bug', priority: 'high',
            status: 'open', folderId: null});
          const it = S.mvpNotes.items.find(i => i.id === n.id);
          it.buildId = 'BUILD-ANTIGO-TESTE'; it.sourceRevision = 'REV-ANTIGA-TESTE';
          const md = mvpNotesMarkdown(it);
          return {build: (md.match(/^build_id: (.+)$/m) || [])[1],
                  rev: (md.match(/^source_revision: (.+)$/m) || [])[1],
                  contemBuildAtual: md.includes(JP_WEALTH_BUILD_ID)};
        }""")
        assert 'BUILD-ANTIGO-TESTE' in hist['build'], hist
        assert 'REV-ANTIGA-TESTE' in hist['rev'], hist
        assert hist['contemBuildAtual'] is False, 'o build em execução não substitui o da nota'
        # título vazio cai no padrão TICKET-nota.md
        vazio = page.evaluate("""() => {
          const n = mvpNotesCreate({content: '\\n\\n', type: 'task', priority: 'low', status: 'open', folderId: null});
          const it = S.mvpNotes.items.find(i => i.id === n.id);
          return {nome: mvpNotesMarkdownFilename(it), md: mvpNotesMarkdown(it)};
        }""")
        assert vazio['nome'].endswith('-nota.md'), vazio['nome']
        assert '\n# ' not in vazio['md'], 'sem H1 quando não há título'
        # exportar é leitura pura: rascunho sujo bloqueia e nada é salvo automaticamente
        antes_upd = notes_state(page)[0]['updatedAt']
        antes_ticket = notes_state(page)[0]['ticket']
        page.evaluate("() => { window.alert = () => {}; const t = document.getElementById('mvpNoteContent');"
                      " t.value += '\\nrascunho'; t.dispatchEvent(new Event('input', {bubbles: true})); }")
        assert page.evaluate('mvpNotesUI.draftDirty') is True
        assert page.evaluate('mvpNotesExportMarkdown()') is None, 'dirty bloqueia a exportação'
        assert page.locator('#mvpNotesExportLive').inner_text().startswith('Existem alterações não salvas')
        assert notes_state(page)[0]['updatedAt'] == antes_upd, 'exportar não move updatedAt'
        assert notes_state(page)[0]['ticket'] == antes_ticket, 'exportar não toca o ticket'
        assert_no_errors(page.jpwealth_observed)
        page.close()

        # ---- 14g. JPW-YX2Z43: menu "⋯" da pasta com semântica de menu contextual ----
        # <details> nativo não fecha ao clicar fora; sem isto o operador precisava clicar
        # de novo no marcador. Testado com cliques REAIS (Playwright emite pointerdown).
        page = prepare_page(browser, base_url + 'index.html')
        page.set_viewport_size({'width': 1440, 'height': 900})
        page.evaluate("""() => {
          ['Interface', 'Dashboard'].forEach(n => mvpNotesCreateFolder(n));
          mvpNotesCreate({content: 'Nota\\ncorpo', type: 'bug', priority: 'high',
            status: 'open', folderId: S.mvpNotes.folders[0].id});
          save();
        }""")
        click_id(page, 'headerNotesBtn')
        menus = page.locator('#mvpNotesFolderNavList details.mvpn-folder-kebab')
        aberto = lambda i: page.evaluate(
            "i => document.querySelectorAll('#mvpNotesFolderNavList details.mvpn-folder-kebab')[i].open", i)
        menus.nth(0).locator('summary').click()
        assert aberto(0), 'menu abre no primeiro clique'
        # clicar numa área vazia da própria sidebar dispensa o menu
        page.locator('#mvpNotesFolderSidebar').click(position={'x': 30, 'y': 8})
        assert not aberto(0), 'menu deve fechar ao clicar fora'
        # abrir o menu de outra pasta fecha o anterior
        menus.nth(0).locator('summary').click()
        menus.nth(1).locator('summary').click()
        assert not aberto(0) and aberto(1), 'apenas um menu de pasta aberto por vez'
        # Escape dispensa o menu sem fechar a gaveta
        page.keyboard.press('Escape')
        assert not aberto(1)
        assert page.evaluate('mvpNotesUI.open') is True, 'Escape do menu não fecha a gaveta'
        # escolher uma ação também fecha o menu
        menus.nth(0).locator('summary').click()
        page.locator('#mvpNotesFolderNavList [data-mvp-folder-down]').first.click()
        assert not aberto(0), 'executar a ação fecha o menu'
        # o listener é escopado: <details> de outros módulos não são afetados
        externo = page.evaluate("""() => {
          const d = [...document.querySelectorAll('details')].filter(x => !x.closest('#mvpNotesFolderNavList'))[0];
          if (!d) return null;
          d.open = true;
          const k = document.querySelector('#mvpNotesFolderNavList details.mvpn-folder-kebab');
          k.open = true;
          const sb = document.getElementById('mvpNotesFolderSidebar');
          const r = sb.getBoundingClientRect();
          sb.dispatchEvent(new PointerEvent('pointerdown', {bubbles: true, cancelable: true,
            clientX: Math.round(r.left + 30), clientY: Math.round(r.bottom - 10), pointerId: 99}));
          const res = {externo: d.open, pasta: k.open};
          d.open = false;
          return res;
        }""")
        if externo:
            assert externo['externo'] is True, 'details fora das Notas não pode ser fechado'
            assert externo['pasta'] is False, 'menu de pasta fecha'
        assert_no_errors(page.jpwealth_observed)
        page.close()

        # ---- 14h. "Todas as Notas" mostra só o backlog ATIVO ----------------------
        # Concluída sai desta visão e continua existindo em "Concluído" e ao pé da própria
        # pasta. Nenhum dado muda: status, folderId e completedAt seguem intocados.
        page = prepare_page(browser, base_url + 'index.html')
        page.evaluate("""() => {
          const f = mvpNotesCreateFolder('Interface');
          const concluir = n => {
            const it = S.mvpNotes.items.find(i => i.id === n.id);
            mvpNotesUpdate(it.id, {type: it.type, content: it.content, priority: it.priority,
              status: 'done', folderId: it.folderId, aiImplementationPolicy: it.aiImplementationPolicy});
          };
          mvpNotesCreate({content: 'Ativa na pasta\\nx', type: 'bug', priority: 'high', status: 'open', folderId: f.id});
          concluir(mvpNotesCreate({content: 'Feita na pasta\\nx', type: 'bug', priority: 'low', status: 'open', folderId: f.id}));
          mvpNotesCreate({content: 'Ativa sem pasta\\nx', type: 'task', priority: 'low', status: 'open', folderId: null});
          concluir(mvpNotesCreate({content: 'Feita sem pasta\\nx', type: 'task', priority: 'low', status: 'open', folderId: null}));
          save();
        }""")
        click_id(page, 'headerNotesBtn')
        titulos = lambda: page.locator('.mvpn-card-title').all_inner_texts()
        page.locator("[data-mvp-folder='all']").click()
        assert titulos() == ['Ativa na pasta', 'Ativa sem pasta'], titulos()
        assert page.locator('.mvpn-group-sep').count() == 0, 'sem concluídas, sem separador'
        # o contador da visão acompanha o que ela exibe
        assert page.locator("[data-mvp-folder='all'] .mvpn-folder-count").inner_text() == '2'
        assert page.evaluate('S.mvpNotes.items.length') == 4, 'nenhuma nota foi removida do estado'
        # "Concluído" continua com todas as concluídas
        page.locator("[data-mvp-folder='done']").click()
        assert sorted(titulos()) == ['Feita na pasta', 'Feita sem pasta'], titulos()
        # dentro da pasta a concluída continua ao pé da lista, atrás do separador
        page.locator('[data-mvp-folder-row] .mvpn-folder-btn').first.click()
        assert titulos() == ['Ativa na pasta', 'Feita na pasta'], titulos()
        assert page.locator('.mvpn-group-sep').count() == 1
        # concluir estando em "Todas as Notas" tira a nota da lista na hora
        page.locator("[data-mvp-folder='all']").click()
        page.evaluate("""() => {
          const it = S.mvpNotes.items.find(i => i.title === 'Ativa sem pasta');
          mvpNotesUpdate(it.id, {type: it.type, content: it.content, priority: it.priority,
            status: 'done', folderId: it.folderId, aiImplementationPolicy: it.aiImplementationPolicy});
          renderMvpNotesList();
        }""")
        assert titulos() == ['Ativa na pasta'], titulos()
        assert page.locator("[data-mvp-folder='all'] .mvpn-folder-count").inner_text() == '1'
        assert_no_errors(page.jpwealth_observed)
        page.close()

        # ---- 15. Trace ID (v4): geração, imutabilidade, cópia, busca e backup ----
        page = prepare_page(browser, base_url + 'index.html')
        assert page.evaluate('S.mvpNotes.schemaVersion') == 5
        TICKET_RE = r'^JPW-[23456789ABCDEFGHJKMNPQRSTVWXYZ]{6}$'
        create_note(page, 'bug', 'Nota com Trace ID', 'descricao', 'high', 'open')
        item = notes_state(page)[0]
        assert re.match(TICKET_RE, item['ticket']), item['ticket']
        assert item['id'] != item['ticket'], 'ticket nunca substitui o id interno'
        assert item['sourceRevision'] is None, 'sourceRevision jamais inventado'
        # determinismo: o ticket é derivado do id por hash estável
        assert page.evaluate(f"mvpNotesTicketFromSeed({item['id']!r})") == item['ticket']
        # imutável em todo o ciclo de vida
        page.evaluate("""() => {
          const it = S.mvpNotes.items[0];
          const u = p => mvpNotesUpdate(it.id, Object.assign({type:it.type,content:it.content,
            priority:it.priority,status:it.status,folderId:it.folderId,
            aiImplementationPolicy:it.aiImplementationPolicy}, p));
          u({content:'outro titulo\\ncorpo'}); u({content:'outra linha'}); u({status:'done'}); u({status:'open'});
        }""")
        assert notes_state(page)[0]['ticket'] == item['ticket'], 'ticket mudou durante o ciclo de vida'
        # migração de nota antiga sem ticket + idempotência
        migrado = page.evaluate("""() => {
          S.mvpNotes = {schemaVersion:2, showHeaderIcon:true, folders:[], items:[{id:'mvpn_legada_t',
            type:'bug', title:'Legada', description:'', priority:'low', status:'open', folderId:null,
            screenId:'dash', buildId:'x', createdAt:'2026-01-01T00:00:00.000Z', updatedAt:'2026-01-02T00:00:00.000Z'}]};
          mvpNotesNormalizeState(); const t1 = S.mvpNotes.items[0].ticket;
          mvpNotesNormalizeState(); mvpNotesNormalizeState();
          return {t1, estavel: S.mvpNotes.items[0].ticket === t1};
        }""")
        assert re.match(TICKET_RE, migrado['t1']) and migrado['estavel'], migrado
        # colisão: ticket persistido válido nunca é roubado por um derivado
        colisao = page.evaluate("""() => {
          const idB = 'mvpn_col_b', derivado = mvpNotesTicketFromSeed(idB);
          S.mvpNotes = {schemaVersion:4, showHeaderIcon:true, folders:[], items:[
            {id:idB, type:'task', title:'B', description:'', priority:'low', status:'open', folderId:null,
             screenId:'', buildId:'', createdAt:'2026-01-01T00:00:00.000Z', updatedAt:'2026-01-01T00:00:00.000Z'},
            {id:'mvpn_col_a', ticket:derivado, type:'task', title:'A', description:'', priority:'low',
             status:'open', folderId:null, screenId:'', buildId:'',
             createdAt:'2026-01-01T00:00:00.000Z', updatedAt:'2026-01-01T00:00:00.000Z'}]};
          mvpNotesNormalizeState();
          const A = S.mvpNotes.items.find(i=>i.id==='mvpn_col_a'), B = S.mvpNotes.items.find(i=>i.id===idB);
          return {aPreservado: A.ticket === derivado, distintos: A.ticket !== B.ticket};
        }""")
        assert colisao['aPreservado'] and colisao['distintos'], colisao
        page.close()

        # ---- 16. Trace Reference: conteúdo, cópia pelo card/editor e busca ----
        page = prepare_page(browser, base_url + 'index.html')
        create_note(page, 'bug', 'Falha rastreavel', 'passos', 'critical', 'open')
        ticket = notes_state(page)[0]['ticket']
        page.evaluate("""() => { window.__copiado=null;
          Object.defineProperty(navigator,'clipboard',{configurable:true,
            value:{writeText:t=>{window.__copiado=t; return Promise.resolve();}}}); }""")
        click_id(page, 'headerNotesBtn')
        assert page.locator('.mvpn-card-wrap').count() == 1
        assert page.evaluate("!document.querySelector('.mvpn-card-copy').closest('.mvpn-card')"), \
            'o botao de copiar nao pode estar aninhado dentro do card'
        antes = notes_state(page)[0]['updatedAt']
        page.locator('.mvpn-card-copy').first.click()
        page.wait_for_timeout(150)
        copiado = page.evaluate('window.__copiado')
        assert copiado.startswith('JP WEALTH — TRACE REFERENCE'), copiado[:60]
        for trecho in [f'Ticket: {ticket}', 'Tipo: Bug', 'Prioridade: Crítica', 'Status: Aberta',
                       'Falha rastreavel', 'Build ID: ', 'Source Revision: não disponível',
                       'INSTRUÇÃO AO AGENTE', 'Autorização IA: SOMENTE ANÁLISE',
                       'CONTEÚDO DA NOTA:', f'ticket {ticket}']:
            assert trecho in copiado, trecho
        assert not re.search(r'[0-9a-f]{40}', copiado), 'nenhum SHA pode ser inventado'
        assert notes_state(page)[0]['updatedAt'] == antes, 'copiar nao pode alterar a nota'
        assert page.locator('#mvpNoteContent').is_hidden(), 'copiar nao pode abrir a nota'
        # cópia pelo editor + Trace ID somente leitura
        page.locator('.mvpn-card').first.click()
        assert page.locator('#mvpNotesEditorTicket').inner_text() == ticket
        assert page.locator('#mvpNotesEditorPane input[value^="JPW-"]').count() == 0, 'ticket nao pode ser editavel'
        page.evaluate('window.__copiado=null')
        click_id(page, 'mvpNotesCopyRefBtn')
        page.wait_for_timeout(150)
        assert ticket in page.evaluate('window.__copiado')
        page.evaluate("() => mvpNotesCloseEditor()")
        # busca pelo ticket localiza exatamente a nota
        page.locator('#mvpNotesSearch').fill(ticket)
        page.wait_for_timeout(120)
        assert page.locator('.mvpn-card').count() == 1
        assert_no_errors(page.jpwealth_observed)
        page.close()

        # ---- 17. JPW-CBA987: modal de configuração inicial da nota ----------------
        page = prepare_page(browser, base_url)
        click_id(page, 'headerNotesBtn')
        overlay = page.locator('#mvpNotesNewOverlay')

        # 17.1 o modal NÃO aparece ao abrir a gaveta nem ao navegar/abrir nota existente
        assert overlay.is_hidden(), 'abrir a gaveta não pode abrir o modal de criação'

        # 17.2 o "+" abre o modal e o editor NÃO abre antes de confirmar
        click_id(page, 'mvpNotesNewBtn')
        assert overlay.is_visible(), 'o botão + deveria abrir o modal'
        assert page.evaluate('mvpNotesUI.draft') is None, 'nenhum rascunho antes de "Criar Nota"'
        assert page.locator('#mvpNoteContent').is_hidden(), 'o editor não pode abrir antes da confirmação'
        # os cinco campos existem e vêm pré-preenchidos com os padrões canônicos
        assert page.locator('#mvpNotesNewType').input_value() == 'task'
        assert page.locator('#mvpNotesNewPriority').input_value() == 'medium'
        assert page.locator('#mvpNotesNewStatus').input_value() == 'open'
        assert page.locator('#mvpNotesNewFolder').input_value() == '', 'padrão é "Sem pasta"'
        assert page.locator('#mvpNotesNewPolicy').input_value() == 'analysis_only'

        # 17.3 Cancelar: nenhuma nota, nenhum rascunho, storage intocado
        antes = page.evaluate('JSON.stringify(S.mvpNotes)')
        click_id(page, 'mvpNotesNewCancelBtn')
        assert overlay.is_hidden(), 'Cancelar deveria fechar o modal'
        assert page.evaluate('mvpNotesUI.draft') is None, 'Cancelar não pode deixar rascunho'
        assert len(notes_state(page)) == 0, 'Cancelar não pode criar nota'
        assert page.evaluate('JSON.stringify(S.mvpNotes)') == antes, 'Cancelar não pode tocar o estado'

        # 17.4 Escape fecha o modal sem fechar a gaveta por baixo
        click_id(page, 'mvpNotesNewBtn')
        assert overlay.is_visible()
        page.keyboard.press('Escape')
        assert overlay.is_hidden(), 'Escape deveria fechar o modal'
        assert page.locator('#mvpNotesOverlay').evaluate("el => el.classList.contains('show')"), \
            'Escape no modal não pode fechar a gaveta inteira'
        assert len(notes_state(page)) == 0

        # 17.5 clique fora da caixa cancela
        click_id(page, 'mvpNotesNewBtn')
        overlay.click(position={'x': 4, 'y': 4})
        assert overlay.is_hidden(), 'clique fora da caixa deveria cancelar'
        assert len(notes_state(page)) == 0

        # 17.6 Criar Nota: os cinco metadados escolhidos chegam ao rascunho e à nota salva
        page.evaluate("window.prompt = () => 'Pasta do modal'")
        click_id(page, 'mvpNotesNewFolderBtn')
        pasta_id = page.evaluate('S.mvpNotes.folders[0].id')
        start_new_note(page, type='bug', priority='critical', status='in_progress',
                       folderId=pasta_id, policy='blocked')
        assert page.locator('#mvpNoteContent').is_visible(), 'o editor abre depois de Criar Nota'
        rascunho = page.evaluate('({...mvpNotesUI.draft})')
        assert rascunho['type'] == 'bug' and rascunho['priority'] == 'critical'
        assert rascunho['status'] == 'in_progress' and rascunho['folderId'] == pasta_id
        assert rascunho['aiImplementationPolicy'] == 'blocked'
        assert page.evaluate('mvpNotesUI.draftDirty') is False, \
            'escolher metadados no modal não é edição pendente'
        assert len(notes_state(page)) == 0, 'a nota só nasce ao Salvar, como antes'

        # 17.7 a nota persistida nasce com os metadados, em campos PLANOS (schema v5)
        page.locator('#mvpNoteContent').fill('Nota nascida configurada\ncorpo')
        click_id(page, 'mvpNotesSaveBtn')
        salva = notes_state(page)
        assert len(salva) == 1
        item = salva[0]
        assert (item['type'], item['priority'], item['status']) == ('bug', 'critical', 'in_progress')
        assert item['folderId'] == pasta_id and item['aiImplementationPolicy'] == 'blocked'
        assert 'metadata' not in item, 'os metadados continuam planos — nenhuma estrutura paralela'
        assert item['title'] == 'Nota nascida configurada'

        # 17.8 abrir nota existente NÃO reabre o modal, e o inspector segue editando o mesmo dado
        page.evaluate("() => mvpNotesCloseEditor()")
        page.locator('.mvpn-card').first.click()
        assert overlay.is_hidden(), 'selecionar nota existente não pode abrir o modal'
        open_inspector(page)
        assert page.locator('#mvpNotePriority').input_value() == 'critical', \
            'o inspector continua sendo a superfície de edição pós-criação'
        assert_no_errors(page.jpwealth_observed)
        page.close()

        # ---- 18. JPW-436587: exportar e copiar o recorte visível em massa ----------
        page = prepare_page(browser, base_url)
        page.evaluate("""() => { window.__copiado = null;
          Object.defineProperty(navigator, 'clipboard', {configurable: true,
            value: {writeText: t => { window.__copiado = t; return Promise.resolve(); }}}); }""")
        # duas pastas: uma com recorte misto, outra vazia — mais uma nota sem pasta
        seed = page.evaluate("""() => {
          const a = mvpNotesCreateFolder('Interface');
          const b = mvpNotesCreateFolder('Pasta vazia');
          const nova = (content, status, policy, folderId) => mvpNotesCreate(
            {content, type: 'bug', priority: 'high', status, folderId,
             aiImplementationPolicy: policy});
          const ids = {
            ativa1: nova('Ativa um\\ncorpo um', 'open', 'blocked', a.id).id,
            ativa2: nova('Ativa dois\\ncorpo dois', 'in_progress', 'autonomous_allowed', a.id).id,
            feita:  nova('Concluida na pasta', 'done', 'analysis_only', a.id).id,
            descartada: nova('Descartada na pasta', 'discarded', 'analysis_only', a.id).id,
            fora:   nova('Nota de outra pasta', 'open', 'analysis_only', null).id,
          };
          renderMvpNotesList();
          return {pastaA: a.id, pastaB: b.id, ids};
        }""")
        click_id(page, 'headerNotesBtn')
        page.evaluate(f"() => {{ mvpNotesSwitchFolder('{seed['pastaA']}'); }}")
        acoes = page.locator('#mvpNotesBulkActions')

        # 18.1 o rótulo conta o que SERÁ levado, não o que está na tela
        assert acoes.is_visible(), 'ações em massa deveriam aparecer com notas no recorte'
        assert page.locator('#mvpNotesBulkCopyBtn').inner_text() == 'Copiar 2'
        assert page.locator('#mvpNotesBulkExportBtn').inner_text() == 'Exportar 2'
        sel = page.evaluate('(() => { const s = mvpNotesBulkSelection();'
                            ' return {visiveis: s.visiveis, levados: s.itens.length,'
                            ' tickets: s.itens.map(i => i.ticket), escopo: s.escopo}; })()')
        assert sel['visiveis'] == 4 and sel['levados'] == 2, sel
        assert sel['escopo'] == 'Interface'

        # 18.2 só notas daquela pasta; concluída e descartada ficam fora
        levados = page.evaluate('mvpNotesBulkSelection().itens.map(i => i.id)')
        assert set(levados) == {seed['ids']['ativa1'], seed['ids']['ativa2']}, levados
        assert seed['ids']['fora'] not in levados, 'nota de outra pasta não pode entrar'

        # 18.3 exportar: confirmação declara os dois números, e o estado NÃO muda
        estado_antes = page.evaluate('JSON.stringify(S.mvpNotes)')
        perguntas = page.evaluate("""() => { window.__perguntas = [];
          window.confirm = q => { window.__perguntas.push(q); return true; };
          return true; }""")
        nome = page.evaluate('mvpNotesBulkExport()')
        assert nome and nome.startswith('notas-interface-') and nome.endswith('.md'), nome
        pergunta = page.evaluate('window.__perguntas[0]')
        assert 'mostra 4 notas' in pergunta and 'as 2 ativas' in pergunta, pergunta
        assert page.evaluate('JSON.stringify(S.mvpNotes)') == estado_antes, \
            'exportar é leitura pura — não pode alterar o estado'

        # 18.4 integridade do Markdown: conteúdo, ticket, metadados e delimitadores
        md = page.evaluate('mvpNotesBulkMarkdown(mvpNotesBulkSelection())')
        assert md.startswith('<!-- jpwealth:notes-export v1 schema=5 scope="Interface" count=2 criterion="ativas" -->')
        assert md.count('<!-- jpwealth:note ') == 2, 'um delimitador por nota'
        for trecho in ['# Interface', '2 notas ativas', 'Ativa um', 'corpo um', 'Ativa dois',
                       'ticket: JPW-', 'ai_implementation_policy: blocked',
                       'ai_implementation_policy: autonomous_allowed',
                       # nome simples sai como token YAML sem aspas (mvpNotesYamlValor);
                       # "Sem pasta", com espaço, sai citado — verificado em 18.10.
                       'folder: Interface']:
            assert trecho in md, trecho
        assert 'Concluida na pasta' not in md and 'Descartada na pasta' not in md
        assert 'Nota de outra pasta' not in md

        # 18.5 copiar: preâmbulo de governança + um Trace Reference íntegro por nota
        page.evaluate('window.__copiado = null')
        click_id(page, 'mvpNotesBulkCopyBtn')
        page.wait_for_timeout(150)
        lote = page.evaluate('window.__copiado')
        assert lote.startswith('JP WEALTH — TRACE REFERENCE (LOTE)'), lote[:60]
        for trecho in ['Escopo: Interface', 'Notas neste lote: 2',
                       '1 com implementação autorizada', '1 bloqueada',
                       'REGRA DE LEITURA DESTE LOTE',
                       'Nenhuma autorização se estende de uma nota para',
                       'Nenhuma das políticas autoriza commit, push, merge ou deploy.']:
            assert trecho in lote, trecho
        # cada bloco preserva a própria instrução — nada foi removido das notas
        assert lote.count('JP WEALTH — TRACE REFERENCE\n') == 2, 'dois blocos individuais'
        assert lote.count('INSTRUÇÃO AO AGENTE') == 2
        assert 'está BLOQUEADA para implementação por IA' in lote
        assert 'AUTORIZA IMPLEMENTAÇÃO TÉCNICA' in lote
        assert page.evaluate('JSON.stringify(S.mvpNotes)') == estado_antes, \
            'copiar é leitura pura — não pode alterar o estado'

        # 18.6 pasta vazia: ações somem e a mensagem distingue "não há" de "todas excluídas"
        page.evaluate(f"() => {{ mvpNotesSwitchFolder('{seed['pastaB']}'); }}")
        assert acoes.is_hidden(), 'sem notas no recorte, as ações somem'
        assert page.evaluate('mvpNotesBulkExport()') is None
        assert page.locator('#mvpNotesExportLive').inner_text() == 'Nenhuma nota exportável encontrada.'

        # 18.7 recorte só com concluídas/descartadas → mensagem própria
        page.evaluate(f"""() => {{ mvpNotesSwitchFolder('{seed['pastaA']}');
          mvpNotesUI.filterStatus = 'done'; renderMvpNotesList(); }}""")
        assert acoes.is_hidden(), 'recorte inteiramente excluído esconde as ações'
        assert page.evaluate('mvpNotesBulkExport()') is None
        assert page.locator('#mvpNotesExportLive').inner_text().startswith('Todas as notas desta visão')
        page.evaluate("() => { mvpNotesUI.filterStatus = 'all'; renderMvpNotesList(); }")

        # 18.8 visão "Concluído": exceção declarada — ali o recorte É o histórico concluído
        page.evaluate("() => { mvpNotesSwitchFolder('done'); }")
        feito = page.evaluate('(() => { const s = mvpNotesBulkSelection();'
                              ' return {n: s.itens.length, soAtivas: s.soAtivas, escopo: s.escopo}; })()')
        assert feito == {'n': 1, 'soAtivas': False, 'escopo': 'Concluído'}, feito
        assert page.locator('#mvpNotesBulkCopyBtn').inner_text() == 'Copiar 1'
        assert 'Concluida na pasta' in page.evaluate('mvpNotesBulkMarkdown(mvpNotesBulkSelection())')

        # 18.9 rascunho sujo bloqueia as duas ações (mesma regra da exportação individual)
        page.evaluate("() => { mvpNotesSwitchFolder('all'); mvpNotesSelectNote(mvpNotesFiltered()[0].id); }")
        page.locator('#mvpNoteContent').fill('editado sem salvar')
        page.evaluate("() => { window.alert = () => {}; }")
        assert page.evaluate('mvpNotesBulkExport()') is None, 'rascunho sujo bloqueia exportar'
        assert page.locator('#mvpNotesExportLive').inner_text().startswith('Existem alterações não salvas')
        assert page.evaluate('mvpNotesBulkCopy(null)') is None, 'rascunho sujo bloqueia copiar'

        # 18.10 nota LEGADA (sem campos do v5) exporta com os fallbacks da normalização
        page.evaluate("""() => {
          mvpNotesUI.draftDirty = false; mvpNotesCloseEditor();
          S.mvpNotes.items.push({id: 'legado_1', title: 'Nota antiga', description: 'corpo antigo'});
          migrate(); mvpNotesSwitchFolder('unfiled'); renderMvpNotesList(); }""")
        legado = page.evaluate("S.mvpNotes.items.find(i => i.id === 'legado_1')")
        assert legado['type'] == 'task' and legado['priority'] == 'medium'
        assert legado['aiImplementationPolicy'] == 'analysis_only' and legado['folderId'] is None
        md_legado = page.evaluate('mvpNotesBulkMarkdown(mvpNotesBulkSelection())')
        assert 'Nota antiga' in md_legado and 'corpo antigo' in md_legado
        assert "folder: 'Sem pasta'" in md_legado and 'source_revision: null' in md_legado

        # 18.11 nome de pasta hostil não escapa do comentário HTML do cabeçalho
        hostil = page.evaluate("""() => {
          const f = mvpNotesCreateFolder('a --> <b> c');
          mvpNotesCreate({content: 'Nota hostil', type: 'task', priority: 'low',
                          status: 'open', folderId: f.id, aiImplementationPolicy: 'blocked'});
          mvpNotesSwitchFolder(f.id);
          return mvpNotesBulkMarkdown(mvpNotesBulkSelection()).split('\\n')[0]; }""")
        assert hostil.count('-->') == 1 and hostil.endswith('-->'), hostil
        assert '<b>' not in hostil, hostil

        # 18.12 nenhuma chamada de rede em qualquer das duas ações
        pedidos = []
        page.on('request', lambda r: pedidos.append(r.url))
        page.evaluate('mvpNotesBulkCopy(null); mvpNotesBulkExport();')
        page.wait_for_timeout(150)
        assert not pedidos, ('exportar/copiar não podem fazer rede', pedidos)
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
print('MVP NOTES OK — CRUD, filtros, contador, visibilidade, isolamento sobre a Central, Finalizar Sessão, Zona de Perigo, backup/importação real, migração, pastas, concluídas na pasta, resize externo e dos dois separadores internos (três colunas), ordem manual das pastas (position, arraste e menu), navegação mobile em três estágios (Pastas/Lista/Nota), limpeza única de filtros (JPW-RQPNMK), exportação individual em Markdown (JPW-9A78DE), Trace ID, política IA no Trace Reference e inspector (schema v5), modal de configuração inicial da nota (JPW-CBA987: abertura, cancelamento, Escape, clique fora, metadados na criação e campos planos), ações em massa sobre o recorte visível (JPW-436587: contagem, exclusão de concluídas/descartadas, Markdown único, preâmbulo de governança do lote, leitura pura, casos vazios, visão Concluído, rascunho sujo, nota legada, nome de pasta hostil e ausência de rede) e monólito verificados.')
