// ============ PWA · ESCOLHA DO ÍCONE (N1) ============
// Duas variantes fixas do mesmo símbolo (assets/pwa-icon-primary.png e
// assets/pwa-icon-secondary.png) — não é mais uma biblioteca de temas com
// manifesto próprio por opção. Um único manifesto (manifests/jp-wealth.
// webmanifest) já lista as duas como purpose:"any"; a escolha aqui só
// decide qual das duas vira <link rel="apple-touch-icon">/<link rel="icon">
// — o que efetivamente aparece ao instalar o PWA na Tela de Início.
const APP_ICON_STORAGE_KEY='jpwealth_v9_icon_choice';
const APP_ICON_CACHE_VERSION='20260806';
const APP_ICONS={
  primary:{ label:'Claro', short:'Fundo claro', description:'Fundo branco, marca "JP" em preto.', src:'assets/pwa-icon-primary.png' },
  secondary:{ label:'Escuro', short:'Fundo escuro', description:'Fundo preto, marca "JP" em branco.', src:'assets/pwa-icon-secondary.png' }
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
  const faviconLink=document.querySelector('link[rel="icon"]'), appleLink=document.querySelector('link[rel="apple-touch-icon"]');
  if(faviconLink) faviconLink.href=withIconCacheBust(icon.src);
  if(appleLink) appleLink.href=withIconCacheBust(icon.src);
  try{ if(options.persist!==false) localStorage.setItem(APP_ICON_STORAGE_KEY,key); }catch(e){}
  return key;
}
function appIconStepText(){
  return `<div class="app-icon-ios-note"><b>Importante no iPhone e iPad</b><p>No iPhone e iPad, para aplicar o novo ícone, remova o atalho atual da Tela de Início e adicione o app novamente após escolher esta opção.</p><ol><li>Escolha o ícone.</li><li>Abra o menu Compartilhar do Safari.</li><li>Toque em “Adicionar à Tela de Início”.</li><li>Se já houver um atalho instalado, remova o antigo primeiro.</li></ol></div>`;
}
function renderAppIconConfig(){
  const el=$('appIconConfig'); if(!el) return;
  const key=currentAppIconChoice(), icon=APP_ICONS[key];
  applyAppIconChoice(key,{persist:false});
  el.innerHTML=`<h2>Ícone do app <span class="art">identidade para instalação PWA</span></h2>
    <div class="app-icon-summary">
      <img src="${withIconCacheBust(icon.src)}" alt="Prévia do ícone selecionado: ${esc(icon.label)}">
      <div><b>${esc(icon.label)}</b><p>${esc(icon.description)}</p><span class="note">A escolha é salva apenas neste navegador e não altera os dados operacionais.</span></div>
    </div>
    <button type="button" class="reset-btn app-icon-open-btn" id="chooseAppIconBtn">Escolher ícone</button>
    <p class="note app-icon-platform-note">A escolha define o ícone usado quando o app for instalado ou reinstalado. No desktop e no Android, o comportamento pode variar conforme o navegador.</p>`;
  $('chooseAppIconBtn').addEventListener('click',openAppIconPicker);
}
function openAppIconPicker(){
  const selected=currentAppIconChoice(), box=$('modalBox');
  $('modalOverlay').classList.add('show');
  box.classList.remove('onboarding-modal');
  box.innerHTML=`<h3>Escolher ícone do app</h3><div class="modal-sub">Selecione a identidade visual que será usada no próximo atalho/instalação.</div>
    <div class="app-icon-grid">${Object.entries(APP_ICONS).map(([key,icon])=>`<article class="app-icon-option${key===selected?' selected':''}" data-app-icon-option="${key}">
      <button type="button" class="app-icon-choice" data-app-icon-select="${key}" aria-pressed="${key===selected}">
        <img src="${withIconCacheBust(icon.src)}" alt="${esc(icon.label)}">
        <span class="app-icon-choice-copy"><b>${esc(icon.label)}</b><small>${esc(icon.short)}</small>${key===selected?'<em>Selecionado</em>':''}</span>
      </button><button type="button" class="modal-btn confirm app-icon-apply" data-app-icon-apply="${key}">${key===selected?'Usar esta versão':'Escolher esta versão'}</button>
    </article>`).join('')}</div>
    ${appIconStepText()}
    <div class="modal-actions"><button type="button" class="modal-btn cancel" id="closeAppIconBtn">Fechar</button></div>`;
  box.querySelectorAll('[data-app-icon-select]').forEach(btn=>btn.addEventListener('click',()=>selectAppIcon(btn.dataset.appIconSelect)));
  box.querySelectorAll('[data-app-icon-apply]').forEach(btn=>btn.addEventListener('click',()=>selectAppIcon(btn.dataset.appIconApply)));
  $('closeAppIconBtn').addEventListener('click',closeModal);
}
function selectAppIcon(choiceKey){
  applyAppIconChoice(choiceKey,{persist:true});
  window.location.reload();
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
