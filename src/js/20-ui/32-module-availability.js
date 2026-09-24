// Presentation and explicit user commands for the one availability preference.
(function(){
  'use strict';
  const policy=window.JPWModuleAvailability;
  const names={research:'Research',forex:'Forex','personal-finance':'Finanças Pessoais',alladin:'Alladin'};
  let previous={},notice=null;
  const el=id=>document.getElementById(id);
  function status(text){const target=el('moduleAvailabilityStatus');if(target)target.textContent=text;}
  function manage(id,opener){
    if(typeof openSettingsModal!=='function')return;
    if(typeof closeShellMenu==='function')closeShellMenu({restoreFocus:false});
    openSettingsModal('editor',opener||document.activeElement);
    const target=el('moduleAvailabilityCard');
    if(target){target.scrollIntoView({block:'nearest'});target.focus({preventScroll:true});}
    const button=target?.querySelector('[data-module-toggle="'+id+'"]');
    if(button&&!button.disabled)button.focus({preventScroll:true});
  }
  function deny(id,opener){
    if(!names[id])return false;
    if(notice?.open)return false;
    if(!notice){
      notice=document.createElement('dialog');notice.id='moduleUnavailableDialog';notice.className='module-availability-dialog';
      notice.setAttribute('aria-labelledby','moduleUnavailableTitle');
      notice.innerHTML='<h2 id="moduleUnavailableTitle">Módulo congelado</h2><p id="moduleUnavailableText"></p><div class="module-availability-actions"><button type="button" class="reset-btn" data-availability-stay>Continuar aqui</button><button type="button" class="reset-btn" data-availability-dashboard>Dashboard</button><button type="button" class="reset-btn" data-availability-manage>Gerenciar disponibilidade</button></div>';
      document.body.append(notice);
    }
    const returnTo=opener instanceof HTMLElement?opener:document.activeElement;
    el('moduleUnavailableText').textContent=names[id]+': congelado — desenvolvimento pausado. Seus dados permanecem preservados. O acesso operacional está indisponível.';
    let shouldRestore=true;
    const close=()=>notice.close();
    const leaveNotice=()=>{shouldRestore=false;close();window.JPWNotifications?.close(false);};
    notice.querySelector('[data-availability-stay]').onclick=close;
    notice.querySelector('[data-availability-dashboard]').onclick=()=>{leaveNotice();if(window.JPWNavigation.navigate('dashboard'))window.JPWNavigation.focusCurrentScreen();};
    notice.querySelector('[data-availability-manage]').onclick=()=>{leaveNotice();manage(id,returnTo);};
    notice.onclose=()=>{
      if(!shouldRestore)return;
      if(returnTo?.isConnected&&!returnTo.closest('[hidden],[inert]')&&returnTo.getClientRects().length)returnTo.focus({preventScroll:true});
    };
    notice.showModal();notice.querySelector('button').focus();return false;
  }
  function render(){
    const snapshot=policy.snapshot(),list=el('moduleAvailabilityList');if(!list)return;
    if(!list.children.length)for(const [id,name] of Object.entries(names)){
      const row=document.createElement('div');row.className='module-availability-row';row.dataset.moduleRow=id;
      const copy=document.createElement('div'),title=document.createElement('h3'),description=document.createElement('p');
      title.textContent=name;description.id='module-description-'+id;copy.append(title,description);
      const action=document.createElement('button');action.type='button';action.className='reset-btn';action.dataset.moduleToggle=id;action.setAttribute('aria-describedby',description.id);
      action.addEventListener('click',()=>request(id));row.append(copy,action);list.append(row);
    }
    for(const [id,name] of Object.entries(names)){
      const frozen=policy.getState(id)==='frozen',row=list.querySelector('[data-module-row="'+id+'"]');
      row.dataset.state=frozen?'frozen':'active';
      row.querySelector('p').textContent=frozen?'Congelado — desenvolvimento pausado. O módulo está fora da navegação; seus dados permanecem preservados.':'Ativo — disponível no aplicativo. Este estado não certifica a conclusão ou a ausência de defeitos do módulo.';
      const action=row.querySelector('button');action.textContent=frozen?'Descongelar':'Congelar';action.setAttribute('aria-label',(frozen?'Descongelar ':'Congelar ')+name);
      action.disabled=snapshot.readable===false||snapshot.valid===false||!!snapshot.blocked;
    }
    const issue=el('moduleAvailabilityIssue');
    if(issue){
      issue.hidden=!(snapshot.issues?.length||snapshot.readable===false||snapshot.blocked);
      issue.textContent=issue.hidden?'':'A configuração de disponibilidade não pôde ser confirmada ou contém informação incompatível. O conteúdo original foi preservado. Releia a configuração; se continuar inválida, exporte um Backup Completo de recuperação. Nenhum padrão foi gravado automaticamente.';
    }
  }
  function request(id){
    const before=policy.snapshot(),next=policy.getState(id)==='frozen'?'active':'frozen';
    if(next==='frozen'&&window.JPWModuleWork?.hasPending(id)){
      status('Congelamento não aplicado. '+names[id]+' tem formulário, rascunho ou confirmação em andamento. Conclua ou resolva esse trabalho pelo fluxo existente.');return false;
    }
    const text=next==='frozen'?'Congelar '+names[id]+'? O módulo sairá da navegação e seus acessos operacionais serão interrompidos. Dados e histórico serão preservados.':'Descongelar '+names[id]+'? Os acessos serão restaurados, sem abrir o módulo ou executar ações pendentes. Isso não autoriza desenvolvimento de novas funcionalidades.';
    if(!confirm(text)){status('Alteração cancelada. Disponibilidade preservada.');return false;}
    if(next==='frozen'&&window.JPWModuleWork?.hasPending(id)){status('O módulo passou a ter trabalho pendente. Nada foi alterado.');return false;}
    const result=policy.setState(id,next,{expectedRaw:before.raw});
    if(!result.ok){render();status('Alteração não confirmada. O último estado confirmado foi preservado. Releia a configuração antes de tentar novamente.');return false;}
    status(names[id]+(next==='frozen'?' congelado.':' descongelado.')+' Preferência confirmada neste navegador e origem.');
    return true;
  }
  function apply(snapshot,reason){
    const focused=document.activeElement;
    for(const tab of document.querySelectorAll('#nav > .tab[data-primary]')){
      const frozen=!policy.canAccess(tab.dataset.primary);tab.hidden=frozen;
      if(frozen)tab.dataset.moduleFrozen='true';else delete tab.dataset.moduleFrozen;
      const surface=tab.dataset.navSurface;
      if(surface)for(const toggle of document.querySelectorAll('[data-nav-expand="'+surface+'"]')){
        toggle.hidden=frozen;if(frozen)toggle.dataset.moduleFrozen='true';else delete toggle.dataset.moduleFrozen;
      }
    }
    for(const id of Object.keys(names)){
      const state=policy.getState(id);
      if(state==='frozen')window.JPWModuleWork?.suspend(id,reason);
      else if(previous[id]==='frozen')window.JPWModuleWork?.resume(id);
    }
    const current=window.JPWNavigation?.current(),frozen=current&&!policy.canAccess(current.primary);
    const banner=el('moduleAvailabilitySuspended');
    if(banner){
      banner.hidden=!frozen;
      if(frozen){
        banner.querySelector('span').textContent=names[current.primary]+(reason==='storage'?' foi congelado em outra aba.':' está congelado.')+' Novas ações estão suspensas. Preenchimento em memória não é gravação durável; preserve-o pelo Backup Completo.';
        banner.querySelector('[data-module-manage]').dataset.moduleManage=current.primary;
      }
    }
    if(frozen&&!window.JPWModuleWork?.hasPending(current.primary)){
      if(window.JPWNavigation.navigate('dashboard')){if(banner)banner.hidden=true;window.JPWNavigation.focusCurrentScreen();}
    }
    if(typeof syncNavSubState==='function')syncNavSubState();
    if(typeof renderNavOrderEditor==='function')renderNavOrderEditor();
    if(typeof scheduleNavPill==='function')scheduleNavPill();
    window.JPWDashMacro?.render();window.JPWNotifications?.refresh();render();
    if(focused?.closest('[data-module-frozen="true"]')){
      const home=document.querySelector('#nav > [data-primary="dashboard"]');
      if(home?.getClientRects().length)home.focus({preventScroll:true});else window.JPWNavigation?.focusCurrentScreen();
    }
    previous={...snapshot.states};
  }
  window.JPWModuleAvailabilityUI=Object.freeze({manage,deny,request,requestChange:(id,next)=>{if(!['active','frozen'].includes(next))return false;if(policy.getState(id)===next)return true;return request(id);},apply,render});
  document.addEventListener('click',event=>{
    const button=event.target.closest('[data-module-manage]');if(button){event.preventDefault();manage(button.dataset.moduleManage,button);}
  });
  el('moduleAvailabilityReload')?.addEventListener('click',()=>{policy.reload('manual');status('Configuração relida. Confira os estados e eventuais avisos acima.');});
  policy.subscribe(apply);apply(policy.snapshot(),'initial');
})();
