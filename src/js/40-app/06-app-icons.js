// ============ PWA · MARCA CONJUNTA (N1) ============
// A preferência histórica primary/secondary mantém seu contrato: primary é
// Vermelho e secondary é Preto. Ela é auxiliar, nunca financeira, e coordena
// cabeçalho, favicon, apple-touch-icon e o manifesto da PRÓXIMA instalação.
const APP_ICON_STORAGE_KEY='jpwealth_v9_icon_choice';
const APP_ICON_CACHE_VERSION='20260916-transparent-r1';
const APP_ICONS={
  primary:{ label:'Vermelho', short:'Marca vermelha', description:'Wordmark vermelho no cabeçalho e ícone vermelho para a próxima instalação.', src:'assets/pwa-icon-primary-512.png', wordmark:'assets/jp-wealth-brand-red.png', manifest:'manifests/jp-wealth.webmanifest' },
  secondary:{ label:'Preto', short:'Marca preta', description:'Wordmark preto sobre placa clara no cabeçalho escuro e ícone preto para a próxima instalação.', src:'assets/pwa-icon-secondary-512.png', wordmark:'assets/jp-wealth-brand-black.png', manifest:'manifests/jp-wealth-black.webmanifest' }
};

function validAppIconChoice(value){ return Object.prototype.hasOwnProperty.call(APP_ICONS,value); }
function currentAppIconChoice(){
  try{ const saved=localStorage.getItem(APP_ICON_STORAGE_KEY); if(validAppIconChoice(saved)) return saved; }catch(e){}
  return 'primary';
}
function withIconCacheBust(path){ return `${path}?v=${APP_ICON_CACHE_VERSION}`; }
function applyAppIconChoice(choiceKey, options={}){
  const key=validAppIconChoice(choiceKey)?choiceKey:'primary';
  const icon=APP_ICONS[key];
  const faviconLink=document.querySelector('link[rel="icon"]'), appleLink=document.querySelector('link[rel="apple-touch-icon"]'), manifestLink=document.querySelector('link[rel="manifest"]');
  if(faviconLink) faviconLink.href=withIconCacheBust(icon.src);
  if(appleLink) appleLink.href=withIconCacheBust(icon.src);
  if(manifestLink) manifestLink.href=withIconCacheBust(icon.manifest);
  document.querySelectorAll('[data-jp-brand-wordmark]').forEach(image=>{ image.src=withIconCacheBust(icon.wordmark); });
  document.documentElement.dataset.brandChoice=key;
  try{ if(options.persist!==false) localStorage.setItem(APP_ICON_STORAGE_KEY,key); }catch(e){}
  return key;
}
function appIconStepText(){
  return `<div class="app-icon-ios-note"><b>Instalações já existentes</b><p>A marca do cabeçalho muda imediatamente. O ícone de um PWA já instalado é controlado pelo navegador: Chrome pode manter o ícone anterior, e iPhone/iPad normalmente exigem remover o atalho e instalar novamente.</p><ol><li>Escolha a versão e selecione <b>Aplicar marca</b>.</li><li>Para uma nova instalação, use o fluxo de instalar/adicionar à Tela de Início.</li><li>Se o ícone anterior continuar visível, remova a instalação existente e repita o fluxo.</li></ol></div>`;
}
function renderAppIconConfig(){
  const el=$('appIconConfig'); if(!el) return;
  const key=currentAppIconChoice(), icon=APP_ICONS[key];
  applyAppIconChoice(key,{persist:false});
  el.innerHTML=`<h2>Marca do JP Wealth <span class="art">cabeçalho e instalação PWA</span></h2>
    <div class="app-icon-summary" aria-label="Marca ativa">
      <div class="brand-header-preview${key==='secondary'?' black-preview':''}"><span>Cabeçalho</span><img src="${withIconCacheBust(icon.wordmark)}" alt="Prévia do wordmark ${esc(icon.label)}"></div>
      <div class="brand-pwa-preview"><span>PWA</span><img src="${withIconCacheBust(icon.src)}" alt="Prévia do ícone PWA ${esc(icon.label)}"></div>
      <div class="brand-choice-copy"><b>Versão ativa: ${esc(icon.label)}</b><p>${esc(icon.description)}</p><span class="note">A escolha é salva apenas neste navegador e não altera dados operacionais nem segue o tema.</span></div>
    </div>
    <button type="button" class="reset-btn app-icon-open-btn" id="chooseAppIconBtn">Alterar marca</button>
    <p class="note app-icon-platform-note">A versão selecionada define o manifesto oferecido na próxima instalação do PWA. O cabeçalho, favicon e ícone Apple são atualizados sem recarregar a página.</p>`;
  $('chooseAppIconBtn').addEventListener('click',openAppIconPicker);
}
function openAppIconPicker(){
  let selected=currentAppIconChoice(); const box=$('modalBox');
  $('modalOverlay').classList.add('show');
  box.classList.remove('onboarding-modal');
  const renderPicker=()=>{
    box.innerHTML=`<h3>Marca do JP Wealth</h3><div class="modal-sub">A escolha vale para o cabeçalho e para a próxima instalação do PWA.</div>
      <div class="app-icon-grid" role="radiogroup" aria-label="Escolher marca">${Object.entries(APP_ICONS).map(([key,icon])=>`<article class="app-icon-option${key===selected?' selected':''}" data-app-icon-option="${key}">
        <button type="button" class="app-icon-choice" role="radio" data-app-icon-select="${key}" aria-checked="${key===selected}">
          <span class="brand-header-preview${key==='secondary'?' black-preview':''}"><span>Cabeçalho</span><img src="${withIconCacheBust(icon.wordmark)}" alt=""></span>
          <span class="brand-pwa-preview"><span>PWA</span><img src="${withIconCacheBust(icon.src)}" alt=""></span>
          <span class="app-icon-choice-copy"><b>${esc(icon.label)}</b><small>${esc(icon.short)}</small>${key===selected?'<em>Selecionada para aplicar</em>':''}</span>
        </button>
      </article>`).join('')}</div>
      ${appIconStepText()}
      <div class="modal-actions"><button type="button" class="modal-btn cancel" id="closeAppIconBtn">Cancelar</button><button type="button" class="modal-btn confirm" id="applyAppIconBtn">Aplicar marca</button></div>`;
    box.querySelectorAll('[data-app-icon-select]').forEach(btn=>btn.addEventListener('click',()=>{ selected=btn.dataset.appIconSelect; renderPicker(); }));
    $('closeAppIconBtn').addEventListener('click',closeModal);
    $('applyAppIconBtn').addEventListener('click',()=>selectAppIcon(selected));
  };
  renderPicker();
}
function selectAppIcon(choiceKey){
  applyAppIconChoice(choiceKey,{persist:true});
  renderAppIconConfig();
  closeModal();
}
function registerAppServiceWorker(){
  if(window.JP_WEALTH_PORTABLE_BUILD===true) return;
  if(!('serviceWorker' in navigator) || !/^https?:$/.test(window.location.protocol)) return;
  window.addEventListener('load',()=>navigator.serviceWorker
    .register('./sw.js',{scope:'./',updateViaCache:'none'})
    .then(registration=>registration.update())
    .catch(()=>{}),{once:true});
}

applyAppIconChoice(currentAppIconChoice(),{persist:false});
registerAppServiceWorker();
