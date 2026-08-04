// ============ PWA · BIBLIOTECA DE ÍCONES (N1) ============
const APP_ICON_STORAGE_KEY='jpwealth_v9_icon_theme';
const APP_ICON_CACHE_VERSION='20260803';
const APP_ICON_THEMES={
  'flat-knight':{
    label:'Knight Flat', short:'Geometria plana', description:'A marca atual: alto contraste e leitura imediata em telas pequenas.',
    manifest:'manifests/jp-wealth-flat-knight.webmanifest', favicon:'icons/flat-knight/favicon-32.png', apple:'icons/flat-knight/apple-touch-icon.png', preview:'icons/flat-knight/icon-192.png'
  },
  'relief-knight':{
    label:'Knight Relief', short:'Relevo esculpido', description:'O cavalo em relevo marfim sobre vermelho texturizado.',
    manifest:'manifests/jp-wealth-relief-knight.webmanifest', favicon:'icons/relief-knight/favicon-32.png', apple:'icons/relief-knight/apple-touch-icon.png', preview:'icons/relief-knight/icon-192.png'
  },
  'marble-knight':{
    label:'Knight Marble', short:'Mármore clássico', description:'A versão escultórica em mármore branco, com presença institucional.',
    manifest:'manifests/jp-wealth-marble-knight.webmanifest', favicon:'icons/marble-knight/favicon-32.png', apple:'icons/marble-knight/apple-touch-icon.png', preview:'icons/marble-knight/icon-192.png'
  }
};

function validAppIconTheme(value){ return Object.prototype.hasOwnProperty.call(APP_ICON_THEMES,value); }
function currentAppIconTheme(){
  const fromUrl=new URLSearchParams(window.location.search).get('icon');
  if(validAppIconTheme(fromUrl)) return fromUrl;
  try{ const saved=localStorage.getItem(APP_ICON_STORAGE_KEY); if(validAppIconTheme(saved)) return saved; }catch(e){}
  return 'flat-knight';
}
function withIconCacheBust(path){ return `${path}?v=${APP_ICON_CACHE_VERSION}`; }
function applyAppIconTheme(themeKey, options={}){
  const key=validAppIconTheme(themeKey)?themeKey:'flat-knight';
  const theme=APP_ICON_THEMES[key];
  const manifest=$('appManifest'), favicon=$('appFavicon'), apple=$('appAppleTouchIcon'), color=$('appThemeColor');
  if(manifest) manifest.href=withIconCacheBust(theme.manifest);
  if(favicon) favicon.href=withIconCacheBust(theme.favicon);
  if(apple) apple.href=withIconCacheBust(theme.apple);
  if(color) color.content='#a60812';
  document.documentElement.dataset.iconTheme=key;
  document.body.dataset.iconTheme=key;
  try{ if(options.persist!==false) localStorage.setItem(APP_ICON_STORAGE_KEY,key); }catch(e){}
  if(options.replaceUrl){
    const url=new URL(window.location.href); url.searchParams.set('icon',key);
    window.history.replaceState({},'',url);
  }
  return key;
}
function iconAsset(themeKey, size){
  const suffix=size==='180'?'apple-touch-icon.png':`icon-${size}.png`;
  return withIconCacheBust(`icons/${themeKey}/${suffix}`);
}
function appIconStepText(){
  return `<div class="app-icon-ios-note"><b>Importante no iPhone e iPad</b><p>No iPhone e iPad, para aplicar o novo ícone, remova o atalho atual da Tela de Início e adicione o app novamente após escolher esta opção.</p><ol><li>Escolha o ícone.</li><li>Abra o menu Compartilhar do Safari.</li><li>Toque em “Adicionar à Tela de Início”.</li><li>Se já houver um atalho instalado, remova o antigo primeiro.</li></ol></div>`;
}
function renderAppIconConfig(){
  const el=$('appIconConfig'); if(!el) return;
  const key=currentAppIconTheme(), theme=APP_ICON_THEMES[key];
  applyAppIconTheme(key,{persist:false});
  el.innerHTML=`<h2>Ícone do app <span class="art">identidade para instalação PWA</span></h2>
    <div class="app-icon-summary">
      <img src="${iconAsset(key,'180')}" alt="Prévia do ícone selecionado: ${esc(theme.label)}">
      <div><b>${esc(theme.label)}</b><p>${esc(theme.description)}</p><span class="note">A escolha é salva apenas neste navegador e não altera os dados operacionais.</span></div>
    </div>
    <button type="button" class="reset-btn app-icon-open-btn" id="chooseAppIconBtn">Escolher ícone</button>
    <p class="note app-icon-platform-note">A escolha define o manifesto usado quando o app for instalado ou reinstalado. No desktop e no Android, o comportamento pode variar conforme o navegador.</p>`;
  $('chooseAppIconBtn').addEventListener('click',openAppIconPicker);
}
function openAppIconPicker(){
  const selected=currentAppIconTheme(), box=$('modalBox');
  $('modalOverlay').classList.add('show');
  box.classList.remove('onboarding-modal');
  box.innerHTML=`<h3>Escolher ícone do app</h3><div class="modal-sub">Selecione a identidade visual que será usada no próximo atalho/instalação.</div>
    <div class="app-icon-grid">${Object.entries(APP_ICON_THEMES).map(([key,theme])=>`<article class="app-icon-option${key===selected?' selected':''}" data-app-icon-option="${key}">
      <button type="button" class="app-icon-choice" data-app-icon-select="${key}" aria-pressed="${key===selected}">
        <img src="${iconAsset(key,'192')}" alt="${esc(theme.label)}">
        <span class="app-icon-choice-copy"><b>${esc(theme.label)}</b><small>${esc(theme.short)}</small>${key===selected?'<em>Selecionado</em>':''}</span>
      </button><button type="button" class="modal-btn confirm app-icon-apply" data-app-icon-apply="${key}">${key===selected?'Usar esta versão':'Escolher esta versão'}</button>
    </article>`).join('')}</div>
    ${appIconStepText()}
    <div class="modal-actions"><button type="button" class="modal-btn cancel" id="closeAppIconBtn">Fechar</button></div>`;
  box.querySelectorAll('[data-app-icon-select]').forEach(btn=>btn.addEventListener('click',()=>selectAppIcon(btn.dataset.appIconSelect)));
  box.querySelectorAll('[data-app-icon-apply]').forEach(btn=>btn.addEventListener('click',()=>selectAppIcon(btn.dataset.appIconApply)));
  $('closeAppIconBtn').addEventListener('click',closeModal);
}
function selectAppIcon(themeKey){
  const key=applyAppIconTheme(themeKey,{persist:true,replaceUrl:true});
  const url=new URL(window.location.href); url.searchParams.set('icon',key);
  window.location.assign(url.href);
}
function registerAppServiceWorker(){
  if(!('serviceWorker' in navigator) || !/^https?:$/.test(window.location.protocol)) return;
  window.addEventListener('load',()=>navigator.serviceWorker.register('./sw.js',{scope:'./'}).catch(()=>{}),{once:true});
}

applyAppIconTheme(currentAppIconTheme(),{persist:false});
registerAppServiceWorker();
