#!/usr/bin/env python3
"""Preview adapter for the existing MT5 runner; synthetic browser checks only."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/'tools/stoikus_custom_panel_preview_test.mjs'
PREVIEW=ROOT/'docs/preview/stoikus-painel-personalizavel'
def inputs():
    files=[SCRIPT]+sorted(p for p in PREVIEW.rglob('*') if p.is_file())
    files+=sorted((ROOT/'assets/stoikus').glob('stoikus-assinatura-*.svg'))
    return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
def runtime():
    env=os.environ.copy()
    python_error=None
    try:
        import playwright
        from playwright.sync_api import sync_playwright
        driver=Path(playwright.__file__).resolve().parent/'driver'
        package=driver/'package'
        node=driver/('node.exe' if os.name=='nt' else 'node')
        node=str(node) if node.is_file() else shutil.which('node')
        with sync_playwright() as instance:
            browser=Path(env.get('STOIKUS_PREVIEW_BROWSER') or instance.chromium.executable_path)
        if node and (package/'package.json').is_file() and browser.is_file():
            env['STOIKUS_PREVIEW_PLAYWRIGHT_PACKAGE']=str(package)
            env['STOIKUS_PREVIEW_BROWSER']=str(browser)
            return node,env,{'source':'python-playwright','package':str(package),'browser':str(browser)}
        python_error='Python Playwright driver/package/installed Chromium unavailable'
    except (ImportError,OSError,RuntimeError) as error:
        python_error=str(error)
    bundled=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'
    node=str(bundled) if bundled.is_file() else shutil.which('node')
    return node,env,{'source':'node-playwright','python_unavailable':python_error}
def main():
    node,env,binding=runtime()
    if not node:
        print('ENVIRONMENT_ERROR: Node runtime unavailable');return 2
    before=inputs()
    print('STOIKUS_PREVIEW_INPUTS:',json.dumps(before,sort_keys=True),flush=True)
    print('STOIKUS_PREVIEW_NODE:',node,flush=True)
    print('STOIKUS_PREVIEW_RUNTIME:',json.dumps(binding,sort_keys=True),flush=True)
    # The existing suite owns process group and timeout. Bind only this child runtime.
    result=subprocess.run([node,str(SCRIPT)],text=True,capture_output=True,cwd=ROOT,env=env)
    print(result.stdout,end='');print(result.stderr,end='')
    if inputs()!=before:
        print('JPW_TEST_RESULT: TEST_HARNESS_FAIL');return 1
    if result.returncode and any(s in result.stdout+result.stderr for s in
        ('Cannot find module','Executable does not exist',"Executable doesn't exist",'playwright install')):
        print('ENVIRONMENT_ERROR: Node/Playwright/browser dependency unavailable')
    print('Native MT5 execution NOT_RUN; isolated synthetic preview only.')
    return result.returncode
if __name__=='__main__':sys.exit(main())
