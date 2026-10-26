#!/usr/bin/env python3
"""Dante visual defaults and first-access acceptance, using disposable storage.

CHG-JPW-DANTE-PRODUCT/CONTROLS-20261024: default mascot is presentation only;
profile/save protections remain covered by settings/profile/gallery focals.
"""
import argparse
import functools
import json
import os
import threading
from http.server import SimpleHTTPRequestHandler
from pathlib import Path

from playwright.sync_api import expect, sync_playwright
from browser_fixture_server import BrowserFixtureServer
from settings_modal_test import profile_boot, profile_close, profile_raw, open_profile, save_profile

ROOT = Path(__file__).resolve().parents[1]


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


def default_contract(browser, url):
    context, page = profile_boot(browser, url)
    try:
        assert page.evaluate('SETTINGS_PROFILE_AVATARS.length') == 20, 'DANTE-P01: append mascot to the 19 portraits'
        mascot = page.evaluate("SETTINGS_PROFILE_AVATARS.find(x=>x.id==='dante-mascote')")
        assert mascot and mascot['name'] == 'Dante — mascote JP Wealth'
        assert page.evaluate("SETTINGS_PROFILE_AVATARS.find(x=>x.id==='dante-alighieri').name") == 'Dante Alighieri'
        assert page.evaluate('settingsProfileAvatarValid(SETTINGS_PROFILE_AVATARS.at(-1).avatarDataUrl)')
        for selector in ['#headerProfileAvatar', '#settingsProfileAvatar']:
            expect(page.locator(selector + ' img')).to_have_attribute('src', mascot['avatarDataUrl'])
        assert profile_raw(page) is None and page.evaluate('window.__profileTestOps') == [], 'DANTE-P02: visual fallback cannot create a profile'
        open_profile(page)
        assert page.locator('#settingsProfileNameInput').input_value() == ''
        expect(page.locator('#settingsAccountAvatar img')).to_have_attribute('src', mascot['avatarDataUrl'])
        # Changing only the name must keep the avatar absent in persisted data.
        page.locator('#settingsProfileNameInput').fill('Pessoa sintética Dante')
        save_profile(page)
        assert json.loads(profile_raw(page))['avatarDataUrl'] is None
        expect(page.locator('#headerProfileAvatar img')).to_have_attribute('src', mascot['avatarDataUrl'])
        page.locator('#settingsProfileGallery summary').click()
        page.locator('[data-profile-avatar="jeremy-siegel"]').click()
        prior = profile_raw(page)
        expect(page.locator('#headerProfileAvatar img')).to_have_attribute('src', mascot['avatarDataUrl'])
        save_profile(page)
        custom = json.loads(profile_raw(page))['avatarDataUrl']
        assert custom != mascot['avatarDataUrl'] and profile_raw(page) != prior
        expect(page.locator('#headerProfileAvatar img')).to_have_attribute('src', custom)
        page.locator('#settingsProfileRemovePhotoBtn').click()
        expect(page.locator('#settingsAccountAvatar img')).to_have_attribute('src', mascot['avatarDataUrl'])
        expect(page.locator('#headerProfileAvatar img')).to_have_attribute('src', custom)
        page.locator('#settingsProfileCancelBtn').click()
        expect(page.locator('#settingsAccountAvatar img')).to_have_attribute('src', custom)
        page.locator('#settingsProfileRemovePhotoBtn').click()
        save_profile(page)
        assert json.loads(profile_raw(page))['avatarDataUrl'] is None
        expect(page.locator('#headerProfileAvatar img')).to_have_attribute('src', mascot['avatarDataUrl'])
        # A failed mascot image must still leave initials accessible, without writes.
        raw, operations = profile_raw(page), page.evaluate('window.__profileTestOps.length')
        page.locator('#headerProfileAvatar img').evaluate("e=>e.dispatchEvent(new Event('error'))")
        expect(page.locator('#headerProfileAvatar')).to_have_text('PD')
        assert profile_raw(page) == raw and page.evaluate('window.__profileTestOps.length') == operations
        # Explicit gallery selection may persist Dante; fallback by itself cannot.
        page.locator('[data-profile-avatar="dante-mascote"]').click()
        assert profile_raw(page) == raw
        save_profile(page)
        assert json.loads(profile_raw(page))['avatarDataUrl'] == mascot['avatarDataUrl']
        profile_close(context, page)
        return 'PASS: DANTE-P01..P07 default/no-write/name-only/custom/draft/remove/image-error'
    finally:
        context.close()


def welcome_contract(browser, url):
    context, page = profile_boot(browser, url)
    try:
        before = page.evaluate('JSON.stringify(S)')
        page.evaluate('JPWFirstAccess.open()')
        expect(page.locator('#jpwWelcomeExplore strong')).to_have_text('Conhecer com Dante')
        image = page.locator('#jpwWelcomeDante')
        expect(image).to_be_visible()
        page.wait_for_function('document.getElementById("jpwWelcomeDante").naturalWidth>0')
        # Boundary fakes only model unavailable API and rejected navigation;
        # the product DOM handler and no-write invariant remain real.
        page.evaluate("() => {window.__danteRealGuide=window.JPWLearningGuide;window.JPWLearningGuide=undefined;}")
        page.locator('#jpwWelcomeExplore').click()
        expect(page.locator('#jpwWelcome')).to_be_visible()
        expect(page.locator('#jpwWelcomeStatus')).to_contain_text('carregando')
        page.evaluate("""() => {
          window.__danteStarts=0;window.__danteRealNavigation=window.JPWNavigation;
          window.JPWLearningGuide={startJourney(){window.__danteStarts++;return true;}};
          window.JPWNavigation={...window.__danteRealNavigation,navigate(){return false;}};
        }""")
        page.locator('#jpwWelcomeExplore').click()
        expect(page.locator('#jpwWelcome')).to_be_visible()
        assert page.evaluate('window.__danteStarts') == 0, 'DANTE-W02: rejected navigation cannot start journey'
        page.evaluate('window.JPWNavigation=window.__danteRealNavigation')
        page.locator('#jpwWelcomeExplore').click()
        expect(page.locator('#jpwWelcome')).to_have_count(0)
        assert page.evaluate('window.__danteStarts') == 1, 'DANTE-W03: accepted click starts journey once'
        page.evaluate('window.JPWLearningGuide=window.__danteRealGuide')
        # A failed synchronous start without another UI host offers a retry.
        page.evaluate("() => {JPWFirstAccess.open();window.JPWLearningGuide={startJourney(){return false;}};}")
        page.locator('#jpwWelcomeExplore').click()
        expect(page.locator('#jpwWelcome')).to_be_visible()
        expect(page.locator('#jpwWelcomeStatus')).to_contain_text('não pôde começar')
        # A failure that opens a foreign host must keep its contents intact.
        page.evaluate("""() => {window.JPWLearningGuide={startJourney(){
          document.getElementById('modalBox').innerHTML='<p id="danteForeignDraft">Rascunho sintético preservado</p>';
          document.getElementById('modalOverlay').classList.add('show');return false;
        }};}""")
        page.locator('#jpwWelcomeExplore').click()
        expect(page.locator('#danteForeignDraft')).to_have_text('Rascunho sintético preservado')
        expect(page.locator('#jpwWelcome')).to_have_count(0)
        page.evaluate('closeModal();window.JPWLearningGuide=window.__danteRealGuide')
        # Real controller and real navigation: a welcome choice starts journey.
        assert page.evaluate('typeof JPWLearningGuide.startJourney') == 'function'
        page.evaluate('JPWFirstAccess.open()')
        page.locator('#jpwWelcomeExplore').click()
        page.wait_for_function("JPWLearningGuide.snapshot().mode==='journey' && JPWLearningGuide.snapshot().active")
        expect(page.locator('#jpwWelcome')).to_have_count(0)
        facts = page.evaluate('JPWLearningGuide.snapshot()')
        assert facts['progress']['steps'] == {}, 'DANTE-W07: entry does not mark a lesson seen or practiced'
        page.evaluate('JPWLearningGuide.pause()')
        assert page.evaluate('JSON.stringify(S)') == before
        assert profile_raw(page) is None and page.evaluate('window.__profileTestOps') == []
        profile_close(context, page)
        return 'PASS: DANTE-W01..W07 welcome/late-api/rejected-navigation/accepted-action/retry/foreign-host/real-journey/no-financial-write'
    finally:
        context.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--only', choices=['all', 'profile', 'welcome'], default='all')
    args = parser.parse_args()
    server = BrowserFixtureServer(('127.0.0.1', 0), functools.partial(Quiet, directory=str(args.root)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True, executable_path=os.environ.get('JP_WEALTH_CHROMIUM'))
            try:
                url = f'http://127.0.0.1:{server.server_port}/index.html'
                if args.only in ['all', 'profile']:
                    print(default_contract(browser, url), flush=True)
                if args.only in ['all', 'welcome']:
                    print(welcome_contract(browser, url), flush=True)
            finally:
                browser.close()
    finally:
        server.shutdown(); server.server_close()


if __name__ == '__main__':
    main()
