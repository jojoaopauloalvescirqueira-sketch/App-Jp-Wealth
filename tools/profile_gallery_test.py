#!/usr/bin/env python3
"""Behavioral gallery checks with disposable storage and user-confirmed metadata.

Run from the repository: python tools/profile_gallery_test.py --out ../evidence/gallery
The portable case copies only its HTML, so gallery independence is not simulated
by routing absent assets. Existing unrelated portable asset failures are reported.
"""
from __future__ import annotations

import argparse
import functools
import hashlib
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import shutil
import tempfile
import threading

from playwright.sync_api import expect, sync_playwright

from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap, assert_fixture_requests
from settings_modal_test import (PROFILE_KEY, profile_boot, open_profile, profile_raw,
    profile_close, save_profile, synthetic_png)
from finalize_session_test import hold_profile_reader, release_profile_reader

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = [
    ('Jeremy Siegel', 'Economia'), ('Charlie Munger', 'Investimentos'),
    ('Peter Lynch', 'Investimentos'), ('Jerome Powell', 'Economia'),
    ('Murray Rothbard', 'Economia'), ('Donato Bramante', 'Artes e literatura'),
    ('George Soros', 'Investimentos'), ('J. Robert Oppenheimer', 'Ciência'),
    ('Nassim Nicholas Taleb', 'Filosofia e pensamento'), ('Dante Alighieri', 'Artes e literatura'),
    ('Michelangelo', 'Artes e literatura'), ('Ludwig von Mises', 'Economia'),
    ('Warren Buffett', 'Investimentos'), ('Napoleão Bonaparte', 'História'),
    ('Adam Smith', 'Economia'), ('Friedrich Nietzsche', 'Filosofia e pensamento'),
    ('Albert Einstein', 'Ciência'), ('Isaac Newton', 'Ciência'),
    ('Leonardo da Vinci', 'Artes e literatura'),
]
CARDS = '[data-profile-avatar]'
CATALOG_PATH = 'src/js/40-app/09-profile-avatar-catalog.js'


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


def identity(root):
    files = ['index.html', 'src/styles/app.css', CATALOG_PATH,
             'src/js/40-app/09-settings-modal.js', 'src/js/manifest.json', 'sw.js',
             'build-id.js', 'dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html',
             'tools/profile_gallery_test.py']
    return {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in files}


def reveal_gallery(page):
    gallery = page.locator('#settingsProfileGallery')
    expect(gallery).to_have_count(1)
    if not gallery.evaluate('e => e.open'):
        gallery.locator('summary').click()
    expect(page.locator('#settingsProfileAvatarGroup')).to_be_visible()


def catalog(page):
    result = page.evaluate('SETTINGS_PROFILE_AVATARS.map(({id,name,group})=>({id,name,group}))')
    assert [(item['name'], item['group']) for item in result] == EXPECTED, result
    assert len({item['id'] for item in result}) == 19
    return result


def card(page, item):
    return page.locator(CARDS).filter(has=page.get_by_text(item['name'], exact=True))


def avatar(page, item):
    return page.evaluate('id=>SETTINGS_PROFILE_AVATARS.find(x=>x.id===id).avatarDataUrl', item['id'])


def check_images(page):
    facts = page.evaluate("""async () => Promise.all(SETTINGS_PROFILE_AVATARS.map(async item=>{
      const image = new Image(); image.src = item.avatarDataUrl; await image.decode();
      return {id:item.id, width:image.naturalWidth, height:image.naturalHeight,
        length:item.avatarDataUrl.length, valid:settingsProfileAvatarValid(item.avatarDataUrl)};
    }))""")
    assert len(facts) == 19
    assert all(x['valid'] and x['width'] == x['height'] == 256 and x['length'] <= 200 * 1024 for x in facts), facts
    page.wait_for_function("""() => [...document.querySelectorAll('[data-profile-avatar] img')]
      .every(image=>image.complete && image.naturalWidth>0)""")
    assert page.locator(CARDS + ' img').count() == 19
    return facts


def selected(page):
    return page.locator(CARDS + '[aria-pressed="true"]')


def check_no_overflow(page):
    facts = page.evaluate("""() => {
      const gallery = document.getElementById('settingsProfileGallery');
      const box = gallery.getBoundingClientRect();
      return {viewport:innerWidth, right:box.right, left:box.left,
        overflow:gallery.scrollWidth-gallery.clientWidth,
        documentOverflow:document.documentElement.scrollWidth-innerWidth,
        cards:[...gallery.querySelectorAll('[data-profile-avatar]')].filter(x=>x.offsetParent)
          .map(x=>{const r=x.getBoundingClientRect();return {w:r.width,h:r.height,left:r.left,right:r.right}})};
    }""")
    assert facts['documentOverflow'] <= 1 and facts['overflow'] <= 1, facts
    assert facts['left'] >= 0 and facts['right'] <= facts['viewport'] + 1, facts
    assert all(x['w'] >= 44 and x['h'] >= 44 and x['left'] >= facts['left'] - 1
               and x['right'] <= facts['right'] + 1 for x in facts['cards']), facts
    return facts


def served_contract(browser, url, out):
    context, page = profile_boot(browser, url)
    try:
        open_profile(page, 'Enter')
        assert not page.locator('#settingsProfileGallery').evaluate('e=>e.open'), 'Gallery is initially collapsed'
        reveal_gallery(page)
        items = catalog(page)
        assert page.locator(CARDS).all_text_contents() and page.locator(CARDS).count() == 19
        assert sorted(page.locator(CARDS).evaluate_all('els=>els.map(e=>e.dataset.profileAvatar)')) == sorted(x['id'] for x in items)
        images = check_images(page)
        assert profile_raw(page) is None and page.evaluate('window.__profileTestOps') == []
        for group in dict.fromkeys(group for _name, group in EXPECTED):
            page.locator('#settingsProfileAvatarGroup').select_option(label=group)
            names = [x['name'] for x in items if x['group'] == group]
            visible = page.locator(CARDS + ':visible')
            assert visible.count() == len(names), group
            assert visible.evaluate_all('els=>els.map(e=>e.dataset.profileAvatar)') == [x['id'] for x in items if x['group'] == group]
        page.locator('#settingsProfileAvatarGroup').select_option('all')
        page.locator('#settingsProfileAvatarSearch').fill('napoleao')
        assert page.locator(CARDS + ':visible').count() == 1
        expect(card(page, items[13])).to_be_visible()
        page.locator('#settingsProfileAvatarSearch').fill('nenhum-retrato-sintetico')
        assert page.locator(CARDS + ':visible').count() == 0
        expect(page.locator('#settingsProfileAvatarEmpty')).to_be_visible()
        page.locator('#settingsProfileAvatarSearch').fill('')
        expect(page.locator('#settingsProfileAvatarEmpty')).to_be_hidden()
        assert profile_raw(page) is None and page.evaluate('window.__profileTestOps') == []

        # User identity is independent from the person represented by an avatar.
        page.locator('#settingsProfileNameInput').fill('Pessoa sintética da galeria')
        save_profile(page)
        initial = profile_raw(page)
        first = card(page, items[0]); first.focus(); first.press('Space')
        expect(first).to_be_focused()
        expect(first).to_have_attribute('aria-pressed', 'true')
        assert selected(page).count() == 1
        assert page.locator('#settingsProfileNameInput').input_value() == 'Pessoa sintética da galeria'
        assert profile_raw(page) == initial, 'Choice must remain a draft'
        expect(page.locator('#settingsAccountAvatar img')).to_have_attribute('src', avatar(page, items[0]))
        assert page.locator('#settingsProfileAvatar img').count() == 0, 'Sidebar remains confirmed state'
        # Search lives inside the profile form; Enter must not implicitly save.
        writes_before = page.evaluate('window.__profileTestOps.length')
        page.locator('#settingsProfileAvatarSearch').fill('Einstein')
        page.locator('#settingsProfileAvatarSearch').press('Enter')
        page.wait_for_timeout(150)  # Allow any unintended asynchronous lock/write to complete.
        assert profile_raw(page) == initial, 'Enter in gallery search must not save a pending profile'
        assert page.evaluate('window.__profileTestOps.length') == writes_before
        page.locator('#settingsProfileAvatarSearch').fill('')
        page.locator('#settingsProfileCancelBtn').click()
        assert selected(page).count() == 0 and profile_raw(page) == initial
        card(page, items[16]).focus(); card(page, items[16]).press('Enter')
        save_profile(page)
        saved = profile_raw(page)
        assert json.loads(saved) == {'schemaVersion': 1, 'displayName': 'Pessoa sintética da galeria',
                                    'avatarDataUrl': avatar(page, items[16])}
        page.reload(wait_until='load'); wait_bootstrap(page); page.evaluate('closeModal()'); open_profile(page)
        reveal_gallery(page)
        expect(card(page, items[16])).to_have_attribute('aria-pressed', 'true')
        assert profile_raw(page) == saved and page.evaluate('window.__profileTestOps') == []
        card(page, items[-1]).click()
        page.locator('#settingsProfileCancelBtn').click()
        expect(card(page, items[16])).to_have_attribute('aria-pressed', 'true')
        page.locator('#settingsProfileRemovePhotoBtn').click()
        assert selected(page).count() == 0 and profile_raw(page) == saved
        page.locator('#settingsProfileCancelBtn').click()
        expect(card(page, items[16])).to_have_attribute('aria-pressed', 'true')

        # A real upload completing late cannot overtake a later gallery choice.
        hold_profile_reader(page)
        page.locator('#settingsProfilePhotoInput').set_input_files({
            'name': 'synthetic-held.png', 'mimeType': 'image/png', 'buffer': synthetic_png(80, 40)})
        page.wait_for_function('window.__profileHeldReads.length>0')
        card(page, items[2]).click()
        release_profile_reader(page)
        expect(card(page, items[2])).to_have_attribute('aria-pressed', 'true')
        expect(page.locator('#settingsAccountAvatar img')).to_have_attribute('src', avatar(page, items[2]))
        assert profile_raw(page) == saved
        page.locator('#settingsProfileCancelBtn').click()

        layouts = {}
        for width, height in [(1440, 900), (390, 844)]:
            page.set_viewport_size({'width': width, 'height': height})
            for theme in ['light', 'dark']:
                page.evaluate('(theme)=>document.documentElement.dataset.theme=theme', theme)
                page.locator('.settings-avatar-results').evaluate('e=>e.scrollTop=0')
                page.locator('#settingsProfileGallery').scroll_into_view_if_needed()
                layouts[f'{width}-{theme}'] = check_no_overflow(page)
                page.screenshot(path=str(out / f'gallery-{width}-{theme}.png'))
        page.set_viewport_size({'width': 1440, 'height': 900})
        page.keyboard.press('Escape')
        expect(page.locator('#settingsOverlay')).to_be_hidden()
        expect(page.locator('#headerConfigBtn')).to_be_focused()
        profile_close(context, page)
        return {'images': images, 'layouts': layouts}
    finally:
        context.close()


def blocked_contract(browser, url):
    valid = {'schemaVersion': 1, 'displayName': 'Perfil anterior sintético', 'avatarDataUrl': None}
    for raw, read_failure in [('not-json', False), (json.dumps({**valid, 'schemaVersion': 2}), False),
                              (json.dumps(valid), True)]:
        context, page = profile_boot(browser, url, raw, read_failure)
        try:
            open_profile(page); reveal_gallery(page)
            assert page.locator(CARDS).count() == 19
            assert page.locator(CARDS + ':enabled').count() == 0
            before = page.evaluate('JSON.stringify(settingsProfileState.draft)')
            page.evaluate('selectSettingsProfileAvatar(SETTINGS_PROFILE_AVATARS[0].id)')
            assert page.evaluate('JSON.stringify(settingsProfileState.draft)') == before
            assert profile_raw(page) == raw and page.evaluate('window.__profileTestOps') == []
            profile_close(context, page)
        finally:
            context.close()

    context, page = profile_boot(browser, url, json.dumps(valid))
    try:
        open_profile(page); reveal_gallery(page)
        items = catalog(page); card(page, items[0]).click()
        page.evaluate("window.__profileTestWriteFail='truncate'")
        page.locator('#settingsProfileSaveBtn').click()
        expect(page.locator('#settingsProfileStatus')).to_have_attribute('data-state', 'blocked')
        assert page.locator(CARDS + ':enabled').count() == 0
        before = page.evaluate('JSON.stringify(settingsProfileState.draft)')
        page.evaluate('selectSettingsProfileAvatar(SETTINGS_PROFILE_AVATARS[1].id)')
        assert page.evaluate('JSON.stringify(settingsProfileState.draft)') == before
        assert len(page.evaluate('window.__profileTestOps')) == 1
        profile_close(context, page)
    finally:
        context.close()

    context, page = profile_boot(browser, url, json.dumps(valid))
    try:
        open_profile(page); reveal_gallery(page)
        items = catalog(page); card(page, items[0]).click()
        other = context.new_page(); other.goto(url, wait_until='load'); wait_bootstrap(other)
        other.evaluate('(value)=>localStorage.setItem("jpwealth_local_profile_v1",JSON.stringify(value))',
                       {**valid, 'displayName': 'Alterado na outra aba'})
        expect(page.locator('#settingsProfileStatus')).to_have_attribute('data-state', 'blocked')
        assert page.locator(CARDS + ':enabled').count() == 0
        page.locator('#settingsProfileCancelBtn').click()
        assert page.locator(CARDS + ':enabled').count() == 19
        assert page.locator('#settingsProfileNameInput').input_value() == 'Alterado na outra aba'
        profile_close(context, page)
    finally:
        context.close()


def saving_and_session_guards(browser, url):
    context, page = profile_boot(browser, url)
    try:
        open_profile(page); reveal_gallery(page)
        items = catalog(page); card(page, items[0]).click()
        # Hold the actual shared Web Lock, without replacing the product writer.
        page.evaluate("""() => {
          window.__galleryLockHeld=false;
          window.__galleryLockTask=navigator.locks.request('jpwealth_state_writer_v1',
            ()=>new Promise(resolve=>{window.__galleryReleaseLock=resolve;window.__galleryLockHeld=true;}));
        }""")
        page.wait_for_function('window.__galleryLockHeld')
        page.locator('#settingsProfileSaveBtn').click()
        page.wait_for_function('settingsProfileState.saving')
        assert page.locator(CARDS + ':enabled').count() == 0
        before = page.evaluate('JSON.stringify(settingsProfileState.draft)')
        page.evaluate('selectSettingsProfileAvatar(SETTINGS_PROFILE_AVATARS[1].id)')
        assert page.evaluate('JSON.stringify(settingsProfileState.draft)') == before
        assert profile_raw(page) is None
        page.evaluate('() => { window.__galleryReleaseLock(); }')
        expect(page.locator('#settingsProfileStatus')).to_have_attribute('data-state', 'success')
        saved = profile_raw(page)
        assert json.loads(saved)['avatarDataUrl'] == avatar(page, items[0])
        assert page.locator(CARDS + ':enabled').count() == 19
        # Exercise the profile lifecycle hook itself; the existing finalization
        # suite separately proves the complete removal protocol through its UI.
        page.evaluate('handleSettingsProfileSessionWipe()')
        assert page.locator(CARDS + ':enabled').count() == 0
        assert selected(page).count() == 0
        page.evaluate('selectSettingsProfileAvatar(SETTINGS_PROFILE_AVATARS[1].id)')
        assert page.evaluate('settingsProfileState.draft.avatarDataUrl') is None
        assert profile_raw(page) == saved and len(page.evaluate('window.__profileTestOps')) == 1
        profile_close(context, page)
    finally:
        context.close()


def portable_contract(browser, root, out):
    with tempfile.TemporaryDirectory(prefix='jpw-gallery-portable-') as directory:
        portable = Path(directory) / 'JP-Wealth.html'
        shutil.copy2(root / 'dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html', portable)
        context, page = profile_boot(browser, portable.as_uri())
        try:
            open_profile(page); reveal_gallery(page)
            items = catalog(page); check_images(page)
            card(page, items[-1]).click(); assert profile_raw(page) is None
            save_profile(page); saved = profile_raw(page)
            page.reload(wait_until='load'); wait_bootstrap(page); page.evaluate('closeModal()'); open_profile(page)
            reveal_gallery(page)
            expect(card(page, items[-1])).to_have_attribute('aria-pressed', 'true')
            assert profile_raw(page) == saved
            assert not page.jpwealth_profile_observed['pageerror'], page.jpwealth_profile_observed
            assert page.evaluate('JSON.stringify(S)') == page.jpwealth_profile_before['state']
            # Gallery is self-contained. Do not misreport inherited missing
            # branding/manifest resources as full-app standalone portability.
            failures = page.jpwealth_profile_observed['failed']
            allowed_paths = ('/assets/jp-wealth-logo.png', '/assets/jp-wealth-brand-red.png',
                             '/assets/pwa-icon-primary.png', '/manifests/jp-wealth.webmanifest')
            unexpected = [entry for entry in failures if not any(path in entry[0] for path in allowed_paths)]
            assert not unexpected, unexpected
            assert_fixture_requests(context)
            page.screenshot(path=str(out / 'gallery-portable-standalone.png'))
            return {'gallery': 'PASS', 'unrelated_missing_local_resources': failures}
        finally:
            context.close()


def offline_contract(browser, url, out):
    context = browser.new_context(viewport={'width': 1440, 'height': 900}, service_workers='allow')
    install_bootstrap(context)
    context.add_init_script('window.__onbShown=true;')
    page = context.new_page()
    errors = []; page.on('pageerror', lambda error: errors.append(str(error)))
    try:
        page.goto(url, wait_until='load'); wait_bootstrap(page); page.evaluate('closeModal()')
        page.evaluate('async()=>{await navigator.serviceWorker.register("./sw.js");await navigator.serviceWorker.ready;}')
        page.wait_for_function('navigator.serviceWorker.controller !== null')
        cache = page.evaluate("""async path=>{
          const cache=await caches.open('jp-wealth-'+JP_WEALTH_BUILD_ID);
          const response=await cache.match(path);return {present:!!response,bytes:response?(await response.text()).length:0};
        }""", './' + CATALOG_PATH)
        assert cache['present'] and cache['bytes'] > 0, cache
        open_profile(page); reveal_gallery(page)
        items = catalog(page); card(page, items[4]).click(); save_profile(page)
        saved = page.evaluate('(key)=>localStorage.getItem(key)', PROFILE_KEY)
        context.set_offline(True)
        response = page.reload(wait_until='load')
        assert response and response.from_service_worker, 'Offline document must come from the real service worker'
        page.wait_for_function('typeof SETTINGS_PROFILE_AVATARS !== "undefined" && typeof openSettingsModal === "function"')
        page.evaluate('closeModal()'); open_profile(page); reveal_gallery(page); check_images(page)
        expect(card(page, items[4])).to_have_attribute('aria-pressed', 'true')
        card(page, items[17]).click()
        assert page.evaluate('(key)=>localStorage.getItem(key)', PROFILE_KEY) == saved
        save_profile(page)
        current = json.loads(page.evaluate('(key)=>localStorage.getItem(key)', PROFILE_KEY))
        assert current['avatarDataUrl'] == avatar(page, items[17])
        page.screenshot(path=str(out / 'gallery-pwa-offline.png'))
        assert not errors, errors
        assert_fixture_requests(context)
        return {'gallery': 'PASS', 'cached_catalog': cache, 'document_from_service_worker': True}
    finally:
        context.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--out', type=Path, default=ROOT.parent / 'evidence' / 'gallery')
    parser.add_argument('--only', choices=['all', 'served', 'portable', 'offline'], default='all')
    args = parser.parse_args(); root = args.root.resolve(); out = args.out.resolve(); out.mkdir(parents=True, exist_ok=True)
    before = identity(root)
    print('GALLERY IDENTITY ' + json.dumps(before), flush=True)
    handler = functools.partial(Quiet, directory=str(root))
    server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    url = f'http://127.0.0.1:{server.server_address[1]}/index.html'
    results = {}
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True, executable_path=os.environ.get('JP_WEALTH_CHROMIUM'))
            try:
                if args.only in ('all', 'served'):
                    results['served'] = served_contract(browser, url, out)
                    blocked_contract(browser, url)
                    saving_and_session_guards(browser, url)
                    results['blocked'] = 'PASS'
                    print('GALLERY SERVED PASS — catalog, filters, draft/save/cancel, stale upload, guards, layouts', flush=True)
                if args.only in ('all', 'portable'):
                    results['portable'] = portable_contract(browser, root, out)
                    print('GALLERY PORTABLE PASS — standalone gallery; baseline unrelated resources: ' +
                          json.dumps(results['portable']['unrelated_missing_local_resources']), flush=True)
                if args.only in ('all', 'offline'):
                    results['offline'] = offline_contract(browser, url, out)
                    print('GALLERY OFFLINE PASS — real service-worker cache, decode and explicit save', flush=True)
            finally:
                browser.close()
        assert before == identity(root), 'ENVIRONMENT_ERROR: candidate changed during gallery validation'
        (out / 'report.json').write_text(json.dumps({'result': 'PASS', 'source_sha256': before, 'checks': results},
                                                  ensure_ascii=False, indent=2) + '\n')
        print('PROFILE GALLERY PASS — ' + args.only, flush=True)
    finally:
        server.shutdown(); server.server_close()


if __name__ == '__main__':
    main()
