#!/usr/bin/env python3
"""Approved Portfolio/Management navigation: real DOM, guards and no implicit writes."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from research_navigation_test import serve, launch_browser, boot

def require(value, detail=None):
    assert value, detail

def run():
    server,url=serve(); results=[]
    try:
      with sync_playwright() as p:
        browser=launch_browser(p)
        try:
          for mode in ('sidebar','topbar','glass','submenu'):
            context,page,observed=boot(browser,url,{'width':1280,'height':900})
            try:
              page.evaluate('(mode)=>{localStorage.setItem("jpw_nav_layout",mode);mountNavigationLayout(mode)}',mode)
              require(page.locator('#researchNavTrigger .lbl').inner_text()=='Portfólio','main label')
              require(page.evaluate('JPWNavigation.children("research").map(r=>[r.id,r.label])')==[['research-forex','Análise']],'analysis only')
              require(page.evaluate('JPWNavigation.children("management").map(r=>[r.id,r.label])')==[['management-reserves','Reservas'],['management-accounting','Caixa Anual']],'management children')
              require(page.evaluate('JPWNavigation.children("forex").every(r=>!["forex-accounting","forex-reserves"].includes(r.id))'),'old children absent')
              require(page.locator('#researchStocksBr,#researchStocksGlobal,#researchReits,#researchOthers').count()==0,'placeholder removed')
              baseline=page.evaluate('JSON.stringify(S)')
              selection=page.evaluate('JSON.stringify(JPWForex.state.operationalSelection())')
              for old in ('forex-accounting','forex-reconciliation','contab','exec-accounting'):
                require(page.evaluate('(old)=>JPWNavigation.navigate(old)',old),old)
                require(page.evaluate('JPWNavigation.current().canonical')=='management-accounting',old)
              require(page.evaluate('JPWNavigation.navigate("forex-reserves")'))
              require(page.evaluate('JPWNavigation.current().canonical')=='management-reserves')
              require(page.evaluate('JSON.stringify(JPWForex.state.operationalSelection())')==selection,'selection untouched')
              require(page.evaluate('JSON.stringify(S)')==baseline,'no financial writes')
              for old in ('research-stocks-br','research-stocks-global','research-reits','research-others'):
                require(page.evaluate('(old)=>JPWNavigation.navigate(old)',old))
                require(page.evaluate('JPWNavigation.current().canonical')=='research-forex',old)
              page.evaluate('window.__guard=JPWForex.executionBoardUI.guardNavigation;JPWForex.executionBoardUI.guardNavigation=()=>false')
              before=page.evaluate('JSON.stringify(JPWNavigation.current())')
              require(not page.evaluate('JPWNavigation.navigate("forex-accounting")'),'guard refuses alias')
              require(page.evaluate('JSON.stringify(JPWNavigation.current())')==before,'atomic refused alias')
              page.evaluate('JPWForex.executionBoardUI.guardNavigation=__guard')
              require(page.evaluate('JPWModuleAvailability.setState("forex","frozen").ok'))
              require(page.evaluate('JPWNavigation.navigate("management-reserves")'),'management independent frozen forex')
              require(page.evaluate('JPWModuleAvailability.setState("management","frozen").ok'))
              require(not page.evaluate('JPWNavigation.navigate("management-reserves")'),'management freeze enforced')
              page.evaluate('document.querySelector("#moduleUnavailableDialog")?.close()')
              require(not observed['pageerror'],observed['pageerror'])
              results.append({'case':mode,'status':'PASS'})
            finally: context.close()
        finally: browser.close()
    finally: server.shutdown()
    print(json.dumps({'results':results},ensure_ascii=False))

if __name__=='__main__':run()
