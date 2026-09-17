const ui=JSON.parse(document.getElementById('ui-strings')?.textContent||'{}');
const icon=name=>`<svg class="icon icon-${name}" aria-hidden="true" focusable="false"><use href="/icons.svg#${name}"></use></svg>`;
const menuButton=document.querySelector('.menu-toggle');
const mobileNav=document.querySelector('.mobile-nav');
function setMenu(open){
 mobileNav?.classList.toggle('open',open);
 menuButton?.setAttribute('aria-expanded',String(open));
 if(menuButton)menuButton.innerHTML=`<span>${open?ui.close:ui.menu}</span>${icon(open?'close':'menu')}`;
 document.body.classList.toggle('locked',open);
 document.querySelector('main').inert=open;document.querySelector('footer').inert=open;
 if(open)document.querySelector('.language-switch')?.removeAttribute('open');
}
menuButton?.addEventListener('click',()=>setMenu(menuButton.getAttribute('aria-expanded')!=='true'));
mobileNav?.querySelectorAll('a').forEach(a=>a.addEventListener('click',()=>setMenu(false)));
document.addEventListener('keydown',e=>{
 if(e.key==='Escape'){
  if(mobileNav?.classList.contains('open')){setMenu(false);menuButton.focus();}
  const languages=document.querySelector('.language-switch[open]');if(languages){languages.removeAttribute('open');languages.querySelector('summary').focus();}
 }
 if(e.key==='Tab'&&mobileNav?.classList.contains('open')){
  const last=mobileNav.querySelector('a:last-of-type');
  if(e.shiftKey&&document.activeElement===menuButton){e.preventDefault();last.focus();}
  else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();menuButton.focus();}
 }
});
const languages=document.querySelector('.language-switch');
languages?.addEventListener('toggle',()=>{if(languages.open&&mobileNav?.classList.contains('open'))setMenu(false)});
document.addEventListener('click',e=>{if(languages?.open&&!languages.contains(e.target))languages.removeAttribute('open')});
languages?.querySelectorAll('[data-language]').forEach(a=>{
 if(location.hash)a.href+=location.hash;
 a.addEventListener('click',()=>{try{localStorage.setItem('prepinson-language',a.dataset.language)}catch{}});
});
const filmDialog=document.querySelector('#film-dialog');const film=filmDialog?.querySelector('video');
document.querySelectorAll('[data-film]').forEach(b=>b.addEventListener('click',()=>{film.src=b.dataset.film;filmDialog.showModal();document.body.classList.add('locked');film.play().catch(()=>{})}));
filmDialog?.addEventListener('close',()=>{film.pause();film.removeAttribute('src');film.load();document.body.classList.remove('locked')});
document.querySelectorAll('[data-close]').forEach(b=>b.addEventListener('click',()=>b.closest('dialog').close()));
document.querySelectorAll('dialog').forEach(d=>d.addEventListener('click',e=>{if(e.target===d){const r=d.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)d.close()}}));
const heroVideo=document.querySelector('.hero video');const pauseButton=document.querySelector('[data-pause]');
if(heroVideo){
 const update=()=>{if(pauseButton){pauseButton.innerHTML=icon(heroVideo.paused?'play':'pause');pauseButton.setAttribute('aria-label',heroVideo.paused?ui.play:ui.pause)}};
 if(matchMedia('(prefers-reduced-motion: reduce)').matches)heroVideo.pause();
 update();pauseButton?.addEventListener('click',()=>{if(heroVideo.paused)heroVideo.play().then(update).catch(()=>{});else{heroVideo.pause();update()}});
}
const lightbox=document.querySelector('#lightbox');const galleryItems=[...document.querySelectorAll('[data-gallery]')];let selected=0;
function showImage(i){selected=(i+galleryItems.length)%galleryItems.length;const source=galleryItems[selected].querySelector('img');lightbox.querySelector('img').src=source.src;lightbox.querySelector('img').alt=source.alt;lightbox.querySelector('.lightbox-label').textContent=`${selected+1} / ${galleryItems.length} — ${source.alt}`;}
galleryItems.forEach((b,i)=>b.addEventListener('click',()=>{showImage(i);lightbox.showModal();document.body.classList.add('locked')}));
lightbox?.querySelector('[data-prev]')?.addEventListener('click',()=>showImage(selected-1));lightbox?.querySelector('[data-next]')?.addEventListener('click',()=>showImage(selected+1));
lightbox?.addEventListener('keydown',e=>{if(e.key==='ArrowRight')showImage(selected+1);if(e.key==='ArrowLeft')showImage(selected-1)});lightbox?.addEventListener('close',()=>document.body.classList.remove('locked'));
const instagramWrap=document.querySelector('.instagram-embed-wrap');
if(instagramWrap){const labelFrame=()=>{const frame=instagramWrap.querySelector('iframe');if(frame)frame.title=ui.instagram;};new MutationObserver(labelFrame).observe(instagramWrap,{childList:true,subtree:true});labelFrame();}
