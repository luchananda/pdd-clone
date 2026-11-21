"""Extra JS/CSS for mock-up 7 (newscast tile, synced carousels, top-10 sourced carousel, three layouts after the 30/70 split)."""

JS7 = r"""
(function(){
/* ---- 1. the three carousels (cumulative tally, close approaches, impact risk) advance together */
var tally=document.querySelector('.lcol [data-carousel]'),sets=document.querySelectorAll('.ptc-set'),paused=false;
function adv(){if(paused)return;var b=tally&&tally.querySelector('.ctrl button:last-child');if(b&&window.step)step(b,1);
 sets.forEach(function(s){var im=s.querySelectorAll('img'),i=+(s.dataset.i||0),n=(i+1)%im.length;im[i].classList.remove('on');im[n].classList.add('on');s.dataset.i=n;var p=s.parentNode.querySelector('.ptn');if(p)p.textContent=(n+1)+' / '+im.length})}
[tally].concat([].slice.call(document.querySelectorAll('.poptile'))).forEach(function(e){if(e){e.addEventListener('mouseenter',function(){paused=true});e.addEventListener('mouseleave',function(){paused=false})}});
setInterval(adv,6000);
/* ---- 2. top-10 sourced carousel: 4 tiles at a time, < and ten circles > */
var tr=document.querySelector('.ttrack');
if(tr){var dots=[].slice.call(document.querySelectorAll('.tdots .dot')),pv=document.querySelector('.tcb.prev'),nx=document.querySelector('.tcb.next');
 function sw(){var t=tr.firstElementChild,n=t.nextElementSibling;return n?n.offsetLeft-t.offsetLeft:t.offsetWidth+12}
 function first(){return Math.round(tr.scrollLeft/sw())}
 function go(i){i=Math.max(0,Math.min(tr.children.length-4,i));tr.scrollTo({left:i*sw(),behavior:'smooth'})}
 function upd(){var f=first();dots.forEach(function(d,k){d.classList.toggle('on',k>=f&&k<f+4)})}
 pv.onclick=function(){go(first()-1)};nx.onclick=function(){go(first()+1)};dots.forEach(function(d,k){d.onclick=function(){go(k)}});tr.addEventListener('scroll',upd);upd()}
/* ---- 3. today's newscast: plays on click, pop-out player */
var v=document.querySelector('.ncv');
if(v){var vid=v.querySelector('video'),pb=v.querySelector('.ncplay');
 function play(){if(!vid.getAttribute('src'))vid.src=v.dataset.src;vid.controls=true;pb.style.display='none';var p=vid.play();if(p&&p.catch)p.catch(function(){})}
 pb.onclick=play;vid.addEventListener('click',function(){if(!vid.controls)play()});
 var pop=document.getElementById('castpop'),pvid=pop.querySelector('video');
 function closeP(){pop.hidden=true;pvid.pause();document.body.style.overflow=''}
 document.querySelector('.ncpop').onclick=function(){var t=vid.currentTime||0;vid.pause();pvid.src=v.dataset.src;pvid.currentTime=t;pop.hidden=false;document.body.style.overflow='hidden';var p=pvid.play();if(p&&p.catch)p.catch(function(){})};
 pop.querySelector('.mmx').onclick=closeP;pop.addEventListener('click',function(e){if(e.target===pop)closeP()});document.addEventListener('keydown',function(e){if(e.key==='Escape'&&!pop.hidden)closeP()})}
/* ---- 4. mock-up controls */
var fb=document.querySelector('.floatb'),btn=document.querySelector('.idetb');
if(fb&&btn){btn.addEventListener('click',function(){var o=fb.hidden;fb.hidden=!o;btn.setAttribute('aria-expanded',o);btn.querySelector('i').textContent=o?'−':'+'});fb.querySelector('.mmx').onclick=function(){fb.hidden=true;btn.setAttribute('aria-expanded',false);btn.querySelector('i').textContent='+'};document.addEventListener('keydown',function(e){if(e.key==='Escape'&&!fb.hidden)fb.querySelector('.mmx').click()})}
function pick(sel,fn){document.querySelectorAll(sel+' button').forEach(function(b){b.onclick=function(){document.querySelectorAll(sel+' button').forEach(function(x){x.classList.toggle('on',x===b)});fn(b)}})}
pick('.optbar .szb',function(b){document.documentElement.className=document.documentElement.className.replace(/\bpt\d+\b/g,'').trim()+' pt'+b.dataset.z});
pick('.optbar .lyb',function(b){var r=document.querySelector('.rest7');r.className='mcol rest7 l'+b.dataset.l});
pick('.optbar .wmb',function(b){window.__setWM&&window.__setWM(b.dataset.w)});
var ob=document.querySelector('.optbar .ox');if(ob)ob.onclick=function(){document.querySelector('.optbar').classList.toggle('min')};
document.documentElement.className+=' pt40';
})();
"""

CSS7 = r"""
/* ===== mock 7 ===== */
:root{--ptw:53.2%}html.pt30{--ptw:49.4%}html.pt40{--ptw:53.2%}html.pt50{--ptw:57%}
.poptile .pt-thumb{flex:0 0 var(--ptw)!important;position:relative;aspect-ratio:4/3;background:#000}
.poptile .pt-thumb .ptc-set{position:absolute;inset:0}.poptile .pt-thumb img{position:absolute;inset:0;width:100%;height:100%;object-fit:contain;opacity:0;transition:opacity .7s}.poptile .pt-thumb img.on{opacity:1}
.poptile .ptn{position:absolute;right:6px;bottom:4px;font:600 10px ui-monospace,Menlo,monospace;color:#eef2fa;background:rgba(0,0,0,.55);padding:1px 5px;border-radius:2px;z-index:2}
.poptile .pt-d{font-size:14px}
/* top 10 sourced */
.tops{margin:1.4rem 0 0}
.tops h2.topt{font:900 28px/1.1 "Playfair Display",Georgia,serif;color:#eef2fa;border-bottom:1px solid #2c3b57;padding-bottom:.4rem;margin:0 0 .8rem}
.tcar{display:flex;align-items:center;gap:8px}
.tcb{flex:0 0 auto;width:34px;height:34px;border:1px solid #2c3b57;background:#121e33;color:#eef2fa;font:700 20px/1 system-ui;border-radius:3px;cursor:pointer}.tcb:hover{border-color:#de7c7c}
.ttrack{display:flex;flex:1;min-width:0;overflow-x:auto;scroll-snap-type:x mandatory;gap:14px;scrollbar-width:none}.ttrack::-webkit-scrollbar{display:none}
.tt{flex:0 0 calc((100% - 42px)/4);scroll-snap-align:start;display:flex;flex-direction:column;gap:8px;min-width:0}
.ttt{font:700 15px/1.25 "Playfair Display",Georgia,serif;color:#eef2fa;min-height:3.75em;text-decoration:none;text-align:left!important;text-justify:auto}.ttt:hover{color:#de7c7c}
.tti{position:relative;display:block;aspect-ratio:16/9;overflow:hidden;border:1px solid #2c3b57;background:#0f1a2e}
.tti img.art{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.ph{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:5px}
.ph img{height:62%;width:auto;max-width:70%;object-fit:contain}.ph span{font:600 9px ui-monospace,Menlo,monospace;letter-spacing:.14em;text-transform:uppercase}
.ph1{background:#0f1a2e}.ph1 span{color:#a2afc6}.ph2{background:#d6dfee}.ph2 span{color:#2c3b57}.ph3{background:linear-gradient(135deg,#2a1a22,#0b1526)}.ph3 span{color:#de7c7c}
.ttd{font:600 10.5px ui-monospace,Menlo,monospace;letter-spacing:.08em;text-transform:uppercase;color:#a2afc6}
.tdots{display:flex;align-items:center;justify-content:center;gap:10px;margin:.8rem 0 .2rem}
.tdots .dot{width:11px;height:11px;border-radius:50%;border:0;padding:0;background:#a2afc6;opacity:.5;cursor:pointer}.tdots .dot.on{background:#de7c7c;opacity:1}
.tops .socials{margin-top:1rem}#swx .soc{display:grid!important;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;padding:0!important}
#swx .soc .tile{padding:22px 10px 12px}#swx .soc .ti{height:56px}#swx .soc .xl{width:56px;height:56px}#swx .soc .xl svg{width:30px;height:30px}#swx .soc .tt{font-size:12.5px!important}
#swx .tile.soon{opacity:.72;pointer-events:none}
/* today's newscast, left column */
.ncast{flex:1;display:flex;flex-direction:column;gap:.6rem}
.ncast .nck{font:700 12px/1.4 system-ui,Arial,sans-serif;letter-spacing:.14em;text-transform:uppercase;color:#de7c7c}
.ncv{position:relative;aspect-ratio:16/9;background:#000;border:1px solid #2c3b57;overflow:hidden}.ncv video{width:100%;height:100%;object-fit:cover;display:block}
.ncplay{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:64px;height:64px;border-radius:50%;border:0;background:rgba(222,124,124,.92);color:#0b1526;font-size:26px;cursor:pointer;padding-left:5px}.ncplay:hover{background:#de7c7c}
.ncast .ncs{margin:0;font:400 15px/1.5 Georgia,serif;color:#d6dfee}
.ncb{display:flex;align-items:center;gap:8px;margin-top:auto}
.ncb>*{position:relative;display:inline-flex;align-items:center;justify-content:center;height:36px;min-width:36px;padding:0 9px;background:#16233a;border:1px solid #2c3b57;color:#eef2fa;cursor:pointer;border-radius:3px;text-decoration:none}.ncb>*:hover{border-color:#de7c7c}
.ncb svg{width:18px;height:18px}.ncb img{height:22px;width:auto}
.ncb .ncyt{background:#c4302b;border-color:#c4302b;color:#fff;gap:6px;font:700 12px system-ui,Arial,sans-serif}
.ncb [data-tip]:hover::after{content:attr(data-tip);position:absolute;bottom:125%;left:0;background:#0b1526;border:1px solid #2c3b57;color:#eef2fa;padding:.25rem .55rem;font:600 11px system-ui,Arial,sans-serif;white-space:nowrap;z-index:9}
#castpop{position:fixed;inset:0;background:rgba(2,6,16,.9);z-index:130;display:flex;align-items:center;justify-content:center}#castpop[hidden]{display:none}
#castpop .cpb{width:min(70vw,1300px);background:#0f1a2e;border:1px solid #2c3b57}#castpop video{display:block;width:100%;background:#000}
/* three ways to lay out what follows the 30/70 block */
.rest7{display:grid;gap:26px 30px;margin-top:1.6rem;zoom:.84;grid-template-columns:7fr 3fr}.rest7>*{min-width:0}
.c-lead{grid-area:lead}.c-art2{grid-area:art2}.c-week{grid-area:week}.c-heads{grid-area:heads}.c-rail{grid-area:rail}.c-top10{grid-area:top10}.c-adcar{grid-area:adcar}.c-side{display:contents}
.rest7 .lead,.rest7 .art2{border-top:3px solid #eef2fa;padding-top:1rem}.rest7 .art2{margin:0}
.rest7 .c-rail .sp-stack{display:flex!important;flex-direction:column;gap:14px}.rest7 .c-rail,.rest7 .c-rail .pl-ad,.rest7 .c-rail .pl-rail{width:100%;margin:0}
.rest7 .top5{grid-template-columns:repeat(5,minmax(0,1fr))}.rest7 .ntrack .nc{flex-basis:calc((100% - 36px)/4)}
.rest7.la{grid-template-areas:"lead rail" "art2 rail" "heads rail" "week week" "top10 top10" "adcar adcar"}
.rest7.lb{grid-template-columns:2fr 1fr;grid-template-areas:"lead heads" "week week" "art2 rail" "top10 top10" "adcar adcar"}
.rest7.lc{grid-template-areas:"lead side" "art2 side" "week side" "top10 side" "adcar side"}
.rest7.lc .c-side{display:flex;flex-direction:column;gap:22px;grid-area:side;position:sticky;top:10px;align-self:start}.rest7.lc .c-heads,.rest7.lc .c-rail{grid-area:auto}
.optbar .szb,.optbar .lyb,.optbar .wmb{display:flex;gap:5px;flex-wrap:wrap}
@media(max-width:1100px){.rest7{grid-template-columns:1fr!important;grid-template-areas:none!important}.rest7>*,.rest7 .c-side>*{grid-area:auto!important}.tt{flex-basis:calc((100% - 14px)/2)}#swx .soc{grid-template-columns:repeat(2,minmax(0,1fr))}}
"""
