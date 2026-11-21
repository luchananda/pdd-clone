"""JS and CSS for mock-ups 5 and 6 (map v2: green land, ISS orbit, Sun, Moon, my location, labels, zoom, satellite view;
chart lightbox v2: caption, share on X, PDD logo watermark). Pure strings, used by build_mocks.py."""

MAPJS = r"""
(function(){
const W=960,H=500,RAD=Math.PI/180;
const LAND='#3d8b4e',LANDS='#2a6b39',WATER='#1d5d9b',GRAT='rgba(255,255,255,.14)';
const LOGO=window.PDD_LOGO||'';
function jd(t){return t/86400000+2440587.5}
function nm(a,r){a=a%r;return a<0?a+r:a}
function gmst(d){return nm(280.46061837+360.98564736629*d,360)}
function sunPos(t){var d=jd(t)-2451545,g=nm(357.529+0.98560028*d,360)*RAD,q=nm(280.459+0.98564736*d,360),L=(q+1.915*Math.sin(g)+0.020*Math.sin(2*g))*RAD,e=(23.439-0.0000004*d)*RAD;
 var ra=Math.atan2(Math.cos(e)*Math.sin(L),Math.cos(L))/RAD,dec=Math.asin(Math.sin(e)*Math.sin(L))/RAD;return {lat:dec,lon:nm(ra-gmst(d)+180,360)-180,L:L/RAD}}
function moonPos(t){var d=jd(t)-2451545,L=nm(218.316+13.176396*d,360),M=nm(134.963+13.064993*d,360)*RAD,F=nm(93.272+13.229350*d,360)*RAD,lon=(L+6.289*Math.sin(M))*RAD,lat=5.128*Math.sin(F)*RAD,e=(23.439-0.0000004*d)*RAD;
 var ra=Math.atan2(Math.sin(lon)*Math.cos(e)-Math.tan(lat)*Math.sin(e),Math.cos(lon))/RAD,dec=Math.asin(Math.sin(lat)*Math.cos(e)+Math.cos(lat)*Math.sin(e)*Math.sin(lon))/RAD;
 return {lat:dec,lon:nm(ra-gmst(d)+180,360)-180,el:nm(lon/RAD-sunPos(t).L,360)}}
function moonEmoji(el){return ['🌑','🌒','🌓','🌔','🌕','🌖','🌗','🌘'][Math.round(el/45)%8]}
var rec=null;try{if(window.satellite&&window.ISS_TLE)rec=satellite.twoline2satrec(ISS_TLE[0],ISS_TLE[1])}catch(e){}
function issAt(t){if(!rec)return null;try{var dt=new Date(t),pv=satellite.propagate(rec,dt);if(!pv.position)return null;var gd=satellite.eciToGeodetic(pv.position,satellite.gstime(dt));return {lat:satellite.degreesLat(gd.latitude),lon:satellite.degreesLong(gd.longitude)}}catch(e){return null}}
function track(t0,a,b,s){var o=[];for(var m=a;m<=b;m+=s){var p=issAt(t0+m*60000);if(p)o.push([p.lon,p.lat])}return o}
var user=null;
function objChar(o){return o.impact?'☄️':(o.pha?'💥':'🪨')}
function objType(o){return o.impact?'Will enter Earth’s atmosphere':(o.pha?'Potentially hazardous asteroid (PHA)':'Near-Earth object (NEO)')}
/* ---------- label layout: greedy, no two labels overlap, a leader line to each icon */
function layout(items){var placed=[],cw=6.4,ch=13,cand=[[16,-12],[16,14],[-16,-12],[-16,14],[0,-28],[0,30],[38,-2],[-38,-2],[30,-30],[-30,-30],[30,32],[-30,32],[54,-18],[-54,-18],[54,20],[-54,20],[0,-46],[0,48],[70,-4],[-70,-4]];
 items.slice().sort(function(a,b){return a.x-b.x}).forEach(function(it){var w=it.t.length*cw,best=null;
  for(var k=0;k<cand.length;k++){var c=cand[k],x=it.x+c[0],y=it.y+c[1],x0=c[0]>=0?x:x-w,b={x0:x0-3,x1:x0+w+3,y0:y-ch/2-2,y1:y+ch/2+2};
   if(b.x0<2||b.x1>W-2||b.y0<2||b.y1>H-2)continue;
   if(placed.some(function(p){return !(b.x1<p.x0||b.x0>p.x1||b.y1<p.y0||b.y0>p.y1)}))continue;
   if(items.some(function(o){return o!==it&&o.x>b.x0-8&&o.x<b.x1+8&&o.y>b.y0-8&&o.y<b.y1+8}))continue;best={c:c,b:b,x:x,y:y};break}
  if(!best){var c=cand[0];best={c:c,b:{x0:it.x+c[0],x1:it.x+c[0]+w,y0:it.y+c[1]-8,y1:it.y+c[1]+8},x:it.x+c[0],y:it.y+c[1]}}
  placed.push(best.b);it.lx=best.x;it.ly=best.y;it.anchor=best.c[0]>=0?'start':'end'})}
/* ---------- the drawing */
function draw(sel,big){
 var svg=d3.select(sel);if(svg.empty())return null;svg.selectAll('*').remove();
 var proj=d3.geoNaturalEarth1().fitExtent([[4,4],[W-4,H-4]],{type:'Sphere'}),path=d3.geoPath(proj),root=svg.append('g').attr('class','root');
 root.append('path').datum({type:'Sphere'}).attr('d',path).attr('fill',WATER).attr('stroke','#2c3b57');
 root.append('path').datum(d3.geoGraticule10()).attr('d',path).attr('fill','none').attr('stroke',GRAT).attr('stroke-width',.6);
 if(window.WORLD){var land=topojson.feature(WORLD,WORLD.objects.countries);root.append('g').selectAll('path').data(land.features).join('path').attr('d',path).attr('fill',LAND).attr('stroke',LANDS).attr('stroke-width',.5)}
 var now=Date.now(),sp=sunPos(now),mp=moonPos(now),anti=[sp.lon>0?sp.lon-180:sp.lon+180,-sp.lat];
 root.append('path').datum(d3.geoCircle().center(anti).radius(90)()).attr('d',path).attr('fill','rgba(2,8,24,.5)');
 var fut=track(now,0,95,1),past=track(now,-50,0,1);
 if(fut.length){root.append('path').datum({type:'LineString',coordinates:past}).attr('d',path).attr('fill','none').attr('stroke','#ffd24a').attr('stroke-width',1.6).attr('stroke-dasharray','4 4');
  root.append('path').datum({type:'LineString',coordinates:fut}).attr('d',path).attr('fill','none').attr('stroke','#ffd24a').attr('stroke-width',2)}
 var lastT=null;function icon(ll,ch,sz,title,cls){var p=proj(ll);if(!p)return null;var t=root.append('text').attr('class',cls||'ico').attr('x',p[0]).attr('y',p[1]).attr('text-anchor','middle').attr('dominant-baseline','central').attr('font-size',sz).text(ch);t.append('title').text(title);lastT=t;return p}
 var items=[];
 (window.WATCH.pts||[]).forEach(function(o,i){var p=icon([o.lon,o.lat],objChar(o),o.pha||o.impact?18:15,o.des+' · MPEC '+o.mpec+' · '+o.date,'obj');if(p){lastT.style('cursor','pointer').on('click',function(ev){ev.stopPropagation();openObj(i)});items.push({x:p[0],y:p[1],t:o.des,i:i})}});
 var ip=issAt(now);if(ip)icon([ip.lon,ip.lat],'🛰️',20,'International Space Station, now','iss');
 icon([sp.lon,sp.lat],'☀️',24,'The Sun is overhead here','sun');
 icon([mp.lon,mp.lat],moonEmoji(mp.el),22,'The Moon is overhead here','moon');
 if(user)icon([user.lon,user.lat],'📍',22,'You are here','me');
 if(big){var ex=[];function xl(ll,t){var p=proj(ll);if(p){var o={x:p[0],y:p[1]+0,t:t,i:-1};items.push(o);ex.push(o)}}xl([sp.lon,sp.lat],'Sun overhead');xl([mp.lon,mp.lat],'Moon overhead');if(ip)xl([ip.lon,ip.lat],'ISS');if(user)xl([user.lon,user.lat],'You');layout(items);var L=root.append('g').attr('class','lab');
  items.forEach(function(it){L.append('line').attr('x1',it.x).attr('y1',it.y).attr('x2',it.lx).attr('y2',it.ly).attr('stroke','#eef2fa').attr('stroke-width',.8).attr('opacity',.85);
   L.append('text').attr('x',it.lx+(it.anchor==='start'?3:-3)).attr('y',it.ly).attr('text-anchor',it.anchor).attr('dominant-baseline','central').attr('font-size',11).attr('font-family','ui-monospace,Menlo,monospace').attr('font-weight',700).attr('fill','#fff').attr('stroke','#06101f').attr('stroke-width',3).attr('paint-order','stroke').style('cursor','pointer').text(it.t).on('click',function(ev){ev.stopPropagation();if(it.i>=0)openObj(it.i)})});
  var lab=function(ll,t){var p=proj(ll);if(p)L.append('text').attr('x',p[0]).attr('y',p[1]+20).attr('text-anchor','middle').attr('font-size',10).attr('font-family','ui-monospace,Menlo,monospace').attr('fill','#fff').attr('stroke','#06101f').attr('stroke-width',3).attr('paint-order','stroke').text(t)};
  
  var z=d3.zoom().scaleExtent([1,8]).translateExtent([[0,0],[W,H]]).on('zoom',function(ev){root.attr('transform',ev.transform);root.selectAll('text.ico,text.obj,text.iss,text.sun,text.moon,text.me').attr('transform',null)});
  svg.call(z);svg.on('dblclick.zoom',null);window.__zoom={svg:svg,z:z}}
 return {proj:proj}}
/* ---------- the pop-out map */
var mm=document.getElementById('mapmodal'),card=document.getElementById('ocard2'),lmap=null,lay={},lastBase='world';
function F(n,v){return v?'<tr><td>'+n+'</td><td>'+v+'</td></tr>':''}
function openObj(i){var o=WATCH.pts[i];if(!o)return;if(mm.hidden)openMap();var q=encodeURIComponent(o.des);
 card.innerHTML='<button class="x" aria-label="Close card">×</button><a class="ct" target="_blank" rel="noopener" href="https://ssd.jpl.nasa.gov/tools/sbdb_lookup.html#/?sstr='+q+'">'+o.des+'</a><div class="cs">'+objType(o)+'</div><table>'+
  F('Announced',o.date)+F('MPEC','<a target="_blank" rel="noopener" href="https://minorplanetcenter.net/mpec/RecentMPECs.html">'+o.mpec+'</a>')+F('Over now',o.lat.toFixed(2)+'°, '+o.lon.toFixed(2)+'°')+F('Groups',(o.neo?'NEO ':'')+(o.pha?'· PHA ':'')+(o.impact?'· atmospheric entry':''))+'</table>'+
  '<div class="cl"><a target="_blank" rel="noopener" href="https://ssd.jpl.nasa.gov/tools/sbdb_lookup.html#/?sstr='+q+'">JPL Small-Body Database</a> · <a target="_blank" rel="noopener" href="https://minorplanetcenter.net/mpec/RecentMPECs.html">Minor Planet Center</a></div>';
 card.hidden=false;card.querySelector('.x').onclick=function(e){e.stopPropagation();card.hidden=true}}
function closeMap(){mm.hidden=true;card.hidden=true;document.body.style.overflow=''}
function openMap(){mm.hidden=false;document.body.style.overflow='hidden';setBase('world')}
function setBase(v){lastBase=v;mm.querySelectorAll('.mmtabs button').forEach(function(b){b.classList.toggle('on',b.dataset.v===v)});
 var sv=document.getElementById('mapbig-svg'),lm=document.getElementById('lmap'),ctl=mm.querySelector('.mmctl');
 if(v==='world'){sv.style.display='block';lm.style.display='none';ctl.style.display='flex';draw('#mapbig-svg',true)}
 else{sv.style.display='none';lm.style.display='block';ctl.style.display='none';leaflet(v)}}
function splitLine(c){var out=[],cur=[];c.forEach(function(p,i){if(i&&Math.abs(p[0]-c[i-1][0])>180){out.push(cur);cur=[]}cur.push([p[1],p[0]])});out.push(cur);return out}
function leaflet(v){if(!window.L){document.getElementById('lmap').innerHTML='<p style="padding:2rem;color:#d6dfee">The satellite view needs the Leaflet library, which could not be loaded.</p>';return}
 if(!lmap){lmap=L.map('lmap',{worldCopyJump:true,zoomControl:true}).setView([20,10],2);
  lay.street=L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19,attribution:'© OpenStreetMap contributors'});
  lay.sat=L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',{maxZoom:19,attribution:'Imagery © Esri, Maxar, Earthstar Geographics'});
  lay.marks=L.layerGroup().addTo(lmap);var zl=function(){document.getElementById('lmap').classList.toggle('hidelab',lmap.getZoom()<5)};lmap.on('zoomend',zl);zl()}
 Object.keys({sat:1,street:1}).forEach(function(k){if(lmap.hasLayer(lay[k]))lmap.removeLayer(lay[k])});lay[v].addTo(lmap);lay.marks.clearLayers();
 function mk(ll,ch,t,fn){var m=L.marker(ll,{icon:L.divIcon({className:'lem',html:ch,iconSize:[26,26],iconAnchor:[13,13]}),title:t}).addTo(lay.marks);if(fn)m.on('click',fn);return m}
 WATCH.pts.forEach(function(o,i){mk([o.lat,o.lon],objChar(o),o.des,function(){openObj(i)}).bindTooltip(o.des,{permanent:true,direction:'right',offset:[10,0],className:'lelab'})});
 var now=Date.now(),sp=sunPos(now),mp=moonPos(now),ip=issAt(now);
 mk([sp.lat,sp.lon],'☀️','Sun overhead');mk([mp.lat,mp.lon],moonEmoji(mp.el),'Moon overhead');if(ip)mk([ip.lat,ip.lon],'🛰️','ISS');if(user)mk([user.lat,user.lon],'📍','You');
 splitLine(track(now,-50,0,1)).forEach(function(l){L.polyline(l,{color:'#ffd24a',weight:2,dashArray:'4 6'}).addTo(lay.marks)});
 splitLine(track(now,0,95,1)).forEach(function(l){L.polyline(l,{color:'#ffd24a',weight:3}).addTo(lay.marks)});
 setTimeout(function(){lmap.invalidateSize()},50)}
function locate(){if(!navigator.geolocation){alert('This browser cannot share a location.');return}
 navigator.geolocation.getCurrentPosition(function(p){user={lat:p.coords.latitude,lon:p.coords.longitude};draw('#pdd-map',false);if(!mm.hidden)setBase(lastBase)},function(){var b=document.getElementById('mapme');if(b)b.textContent='📍 Location not shared'},{maximumAge:600000,timeout:15000})}
/* ---------- wiring */
function init(){
 if(!window.d3||!window.topojson||!window.WATCH){setTimeout(init,150);return}
 draw('#pdd-map',false);setInterval(function(){draw('#pdd-map',false)},30000);
 var s=document.getElementById('pdd-map');if(s){s.style.cursor='zoom-in';s.addEventListener('click',openMap)}
 var b=document.getElementById('mapbig');if(b)b.onclick=openMap;var me=document.getElementById('mapme');if(me)me.onclick=locate;
 mm.querySelector('.mmx').onclick=closeMap;mm.addEventListener('click',function(e){if(e.target===mm)closeMap()});
 mm.querySelectorAll('.mmtabs button').forEach(function(t){t.onclick=function(){setBase(t.dataset.v)}});
 var z=function(k){return function(){var Z=window.__zoom;if(!Z)return;if(k===0)Z.svg.transition().call(Z.z.transform,d3.zoomIdentity);else Z.svg.transition().call(Z.z.scaleBy,k)}};
 mm.querySelector('.zin').onclick=z(1.6);mm.querySelector('.zout').onclick=z(1/1.6);mm.querySelector('.zreset').onclick=z(0);var mel=mm.querySelector('.zme');if(mel)mel.onclick=locate;
 document.addEventListener('keydown',function(e){if(e.key==='Escape'&&!mm.hidden)closeMap()});
 document.querySelectorAll('.tw table td:first-child a, .tw table td a').forEach(function(a){var d=a.textContent.trim(),i=WATCH.pts.findIndex(function(o){return o.des===d});if(i>=0)a.addEventListener('click',function(e){e.preventDefault();openObj(i)})});
 var sh=document.getElementById('mapshare');if(sh)sh.href='https://x.com/intent/tweet?text='+encodeURIComponent('Asteroids announced today – map with the ISS, Sun and Moon')+'&url='+encodeURIComponent(location.href.split('#')[0]);
 document.querySelectorAll('[data-auto]').forEach(function(c){setInterval(function(){if(!c.matches(':hover')&&!c.querySelector('details[open]'))var bt=c.querySelector('.ctrl button:last-child');if(bt)step(bt,1)},10000)})}
init()})();
"""

LBJS = r"""
(function(){
var LOGO=window.PDD_LOGO||'',wm='A',box=document.createElement('div');box.id='clb2';box.hidden=true;
box.innerHTML='<div class="lbx"><div class="lbhead"><b id="lbt"></b><button class="mmx" aria-label="Close">×</button></div><div class="lbimgw"><div id="lbim"></div><img class="wm wmA" alt="" src="'+LOGO+'"></div><div class="lbcap" id="lbc"></div><div class="lbfoot"><span class="wmsw">Watermark (mock-up options):<button data-w="A" class="on">A · corner</button><button data-w="B">B · centre, faint</button><button data-w="C">C · top right</button></span><a id="lbshare" class="xshare" target="_blank" rel="noopener"></a></div></div>';
document.body.appendChild(box);
var im=box.querySelector('#lbim'),cap=box.querySelector('#lbc'),ttl=box.querySelector('#lbt'),w=box.querySelector('.wm');
function setWM(k){wm=k;w.className='wm wm'+k;box.querySelectorAll('.wmsw button').forEach(function(b){b.classList.toggle('on',b.dataset.w===k)})}
box.querySelectorAll('.wmsw button').forEach(function(b){b.onclick=function(e){e.stopPropagation();setWM(b.dataset.w)}});window.__setWM=setWM;
function close(){box.hidden=true;im.innerHTML='';document.body.style.overflow=''}
box.querySelector('.mmx').onclick=close;box.addEventListener('click',function(e){if(e.target===box)close()});document.addEventListener('keydown',function(e){if(e.key==='Escape'&&!box.hidden)close()});
function showCard(p){var o=im.querySelector('.pcard');if(o)o.remove();var c=document.createElement('div');c.className='pcard';c.innerHTML=p.h;im.appendChild(c);var bw=im.clientWidth,bh=im.clientHeight,cw=c.offsetWidth,ch=c.offsetHeight,px=p.x*bw,py=p.y*bh,g=Math.max(p.r*bw,14)+14,l=(px+g+cw<=bw-6)?px+g:px-g-cw;if(l<6)l=Math.max(6,Math.min(bw-cw-6,px-cw/2));c.style.left=l+'px';c.style.top=Math.min(Math.max(py-ch/2,6),Math.max(6,bh-ch-6))+'px'}
document.addEventListener('contextmenu',function(e){if(e.target.closest&&(e.target.closest('.cpic')||e.target.closest('#clb2 .lbimgw')))e.preventDefault()});
document.addEventListener('click',function(e){var z=e.target.closest&&e.target.closest('.cpic');if(!z)return;e.stopImmediatePropagation();e.preventDefault();
 var fig=z.closest('figure'),fc=fig&&fig.querySelector('figcaption'),title=(z.querySelector('img')||{}).alt||'Chart',body='';
 if(fc){var t=fc.querySelector('.ct1,b');if(t)title=t.textContent.trim();var d=fc.querySelector('details');if(d){var s=d.querySelector('summary');var one='';if(s){var c2=s.cloneNode(true);c2.querySelectorAll('b').forEach(function(b){b.remove()});one=c2.textContent.trim()}
   var ps=[].map.call(d.querySelectorAll(':scope > p, :scope > .td p, :scope > .td'),function(p){return p.tagName==='DIV'&&p.querySelector('p')?'':'<p>'+p.innerHTML+'</p>'}).join('');if(one&&!/class="cs"/.test(ps))body='<p>'+one+'</p>';body+=ps}else body='<p>'+fc.innerHTML+'</p>'}
 ttl.textContent=title;cap.innerHTML='<p class="lbt2">'+title+'</p>'+body;
 var h=null;try{h=z.dataset.hot?JSON.parse(z.dataset.hot):null}catch(x){}var ww=(h&&h.w)||1200,hh=(h&&h.h)||900;
 im.innerHTML='';im.style.backgroundImage='url("'+z.dataset.zoom+'")';im.style.aspectRatio=ww+'/'+hh;im.style.width='min(100%,calc((100vh - 330px)*'+(ww/hh)+'))';
 (h&&h.pts||[]).forEach(function(p){var b=document.createElement('button');b.className='chs';b.title=p.t;b.style.left=(p.x*100)+'%';b.style.top=(p.y*100)+'%';b.style.width=(p.r*200)+'%';b.addEventListener('click',function(ev){ev.stopPropagation();showCard(p)});im.appendChild(b)});
 var sh=box.querySelector('#lbshare');sh.innerHTML=(window.X_SVG||'')+'<span>Share on X</span>';sh.href='https://x.com/intent/tweet?text='+encodeURIComponent(title+' – Planetary Defense Daily')+'&url='+encodeURIComponent(location.href.split('#')[0]);
 box.hidden=false;document.body.style.overflow='hidden'},true);
})();
"""

POPJS = r"""
(function(){
document.querySelectorAll('[data-pop]').forEach(function(b){b.addEventListener('click',function(){var p=document.getElementById(b.dataset.pop);if(p){p.hidden=false;document.body.style.overflow='hidden'}})});
document.querySelectorAll('.pop').forEach(function(p){var x=p.querySelector('.mmx');var c=function(){p.hidden=true;document.body.style.overflow=''};x.onclick=c;p.addEventListener('click',function(e){if(e.target===p)c()});document.addEventListener('keydown',function(e){if(e.key==='Escape'&&!p.hidden)c()})});
})();
"""

UIJS = r"""
(function(){
var fb=document.querySelector('.floatb'),btn=document.querySelector('.idetb');
if(fb&&btn){btn.addEventListener('click',function(){var o=fb.hidden;fb.hidden=!o;btn.setAttribute('aria-expanded',o);btn.querySelector('i').textContent=o?'−':'+'});fb.querySelector('.mmx').onclick=function(){fb.hidden=true;btn.setAttribute('aria-expanded',false);btn.querySelector('i').textContent='+'};document.addEventListener('keydown',function(e){if(e.key==='Escape'&&!fb.hidden)fb.querySelector('.mmx').click()})}
var g=document.querySelector('.m5'),slotL=document.getElementById('adslotL'),slotR=document.getElementById('adslotRow'),ads=document.getElementById('adtiles');
function split(n){if(!g)return;g.classList.remove('s1','s2','s3');g.classList.add('s'+n);if(n===1)slotR.appendChild(ads);else slotL.appendChild(ads);document.querySelectorAll('.optbar .sp button').forEach(function(b){b.classList.toggle('on',b.dataset.s==n)})}
document.querySelectorAll('.optbar .sp button').forEach(function(b){b.onclick=function(){split(+b.dataset.s)}});
document.querySelectorAll('.optbar .wmb button').forEach(function(b){b.onclick=function(){window.__setWM&&window.__setWM(b.dataset.w);document.querySelectorAll('.optbar .wmb button').forEach(function(x){x.classList.toggle('on',x===b)})}});
var ob=document.querySelector('.optbar .ox');if(ob)ob.onclick=function(){document.querySelector('.optbar').classList.toggle('min')};
split(3)})();
"""

CSS = r"""
/* ===== mock 5/6 ===== */
.m5{grid-template-columns:30% minmax(0,1fr)!important;gap:30px!important;align-items:start}
.m5.s3{align-items:stretch}
.m5.s3 .lcol{display:flex;flex-direction:column}.m5.s3 .lcol>#swx{flex:1;display:flex;flex-direction:column}
.m5.s3 #adslotL{flex:1;display:flex;flex-direction:column}.m5.s3 #adslotL .adl{flex:1}.m5.s3 #adslotL .adl .tile{flex:1;justify-content:center}
.m5 .mcol>#swx{align-self:stretch;margin:0!important;width:100%!important}
.m5.s3 .mcol{display:flex;flex-direction:column}.m5.s3 .iotd{display:flex;flex-direction:column;flex:1}.m5.s3 .iimg{flex:1 1 auto;min-height:420px;position:relative}.m5.s3 .iimg img{position:absolute;inset:0;width:100%;height:100%;max-height:none}
.m5.s3 #adslotL .adl .tile{flex-direction:row;text-align:left;gap:12px;padding:12px 12px 12px 14px;align-items:center;flex-wrap:nowrap}.m5.s3 #adslotL .adl .tile .ti{flex:0 0 64px;height:64px}.m5.s3 #adslotL .adl .tile .ti img,.m5.s3 #adslotL .adl .tile .xl{width:64px;height:64px;max-height:64px}.m5.s3 #adslotL .adl .tile .tt{display:none}.m5.s3 #adslotL .adl .tile .tb{margin-left:auto;white-space:nowrap}
.adrow5{margin:1rem 0}.adrow5 .adl{display:grid!important;grid-template-columns:repeat(3,minmax(0,1fr))!important;gap:14px!important}
.rest5{zoom:.84;margin-top:1.6rem}
#swx .sub{font:700 14.2px/1.4 system-ui,"Helvetica Neue",Arial,sans-serif!important}
#swx .subrow{display:flex;align-items:center;justify-content:space-between;gap:8px;margin:.4rem 0 .5rem}
#swx .mbtns{display:flex;gap:6px}
#swx .mapcap{font:400 14px/1.5 Georgia,"Times New Roman",serif!important;color:#a2afc6!important;margin:.5rem 0 .7rem}
#swx .mapcap a{color:#de7c7c}
#swx .map-key{font:600 10.5px/1.5 ui-monospace,Menlo,monospace!important;color:#a2afc6!important;margin:.35rem 0 0}
#swx hr.wline{border:0;border-top:3px solid #eef2fa;margin:1.3rem 0 1rem}
#swx .adl{display:flex!important;flex-direction:column;gap:12px;grid-template-columns:none!important;padding:0!important;margin:0!important}
#swx .dd2.cum .slide figcaption{display:block!important;margin-top:.5rem}
#swx .dd2.cum .tdd{margin:0}
.iotd{margin:0 0 1rem;position:relative}
.iimg{display:block;border:1px solid #2c3b57;background:#0f1a2e}.iimg img{display:block;width:100%;height:auto;max-height:520px;object-fit:cover;object-position:center 35%}
.icap{padding:.7rem 0 0}.icap p{margin:0 0 .4rem;font:400 16px/1.55 Georgia,"Times New Roman",serif;color:#d6dfee}
.icap .ic1 b{font:700 19px/1.25 "Playfair Display",Georgia,serif;color:#eef2fa}
.icap .ai{font:600 10px ui-monospace,Menlo,monospace;letter-spacing:.12em;text-transform:uppercase;color:#de7c7c;margin-left:.5rem}
.icap a{color:#de7c7c;text-decoration:none}.icap a:hover{text-decoration:underline}
.iact{display:flex;align-items:center;justify-content:space-between;gap:12px;border-top:1px solid #2c3b57;border-bottom:1px solid #2c3b57;margin:.6rem 0 1rem;padding:.4rem 0}
.idetb{display:flex;align-items:center;gap:.6rem;background:none;border:0;color:#eef2fa;cursor:pointer;font:700 11.5px system-ui,Arial,sans-serif;letter-spacing:.14em;text-transform:uppercase;padding:.2rem 0}
.idetb i{font:400 26px/1 system-ui;color:#de7c7c;font-style:normal}
.xshare{display:inline-flex;align-items:center;gap:.45rem;font:600 13px system-ui,Arial,sans-serif;color:#eef2fa!important;border:1px solid #2c3b57;padding:.4rem .9rem;text-decoration:none!important}.xshare:hover{background:#16233a}.xshare svg{width:14px;height:14px}.xshare .xs{display:inline-flex}
.floatb{position:absolute;left:14px;right:14px;bottom:76px;z-index:30;background:rgba(11,21,38,.95);border:1px solid #2c3b57;border-top:3px solid #de7c7c;box-shadow:0 10px 30px rgba(0,0,0,.55);padding:.9rem 3rem .9rem 1.1rem}
.floatb b{font:700 11.5px system-ui,Arial,sans-serif;letter-spacing:.14em;text-transform:uppercase;color:#de7c7c}.floatb p{margin:.4rem 0 0!important}
.floatb .mmx{position:absolute;right:8px;top:6px}
.mmx{background:#16233a;border:1px solid #2c3b57;color:#eef2fa;font:400 26px/1 system-ui;width:36px;height:36px;cursor:pointer;border-radius:3px}.mmx:hover{border-color:#de7c7c;color:#de7c7c}
#swx.look4 h2.look{font:900 32.3px/1.06 "Playfair Display",Georgia,serif!important;color:#de7c7c!important;border-bottom:1px solid #2c3b57;margin:0 0 .7rem;letter-spacing:.01em}
.m5 .mcol>.lead,.rest5>.lead{margin-top:1.6rem;padding-top:1rem;border-top:3px solid #eef2fa}
/* pop-out map */
.mm{position:fixed;inset:0;background:rgba(2,6,16,.84);z-index:120;display:flex;align-items:center;justify-content:center;overflow:auto;padding:2vh 0}.mm[hidden]{display:none}
.mmbox{width:min(70vw,1300px);max-height:96vh;overflow:auto;background:#0f1a2e;border:1px solid #2c3b57;box-shadow:0 20px 60px rgba(0,0,0,.6)}
.mmhead,.lbhead{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:.6rem .8rem;border-bottom:1px solid #2c3b57;position:sticky;top:0;background:#0f1a2e;z-index:5}
.mmhead>b,.lbhead>b{font:700 20px "Playfair Display",Georgia,serif;color:#eef2fa}
.mmtabs{display:flex;gap:6px;margin-left:auto}.mmtabs button,.mmctl button,.wmsw button,.optbar button{background:#16233a;border:1px solid #2c3b57;color:#d6dfee;font:600 12px system-ui,Arial,sans-serif;padding:.35rem .7rem;cursor:pointer;border-radius:3px}
.mmtabs button.on,.wmsw button.on,.optbar button.on{background:#de7c7c;color:#0b1526;border-color:#de7c7c}
.mmmap{position:relative;background:#0b1526}.mmmap>svg{display:block;width:100%;height:auto;cursor:grab}
#lmap{display:none;height:min(62vh,640px);width:100%}.hidelab .lelab{display:none}.lem{font-size:20px;line-height:26px;text-align:center}.lelab{background:rgba(11,21,38,.8);border:1px solid #2c3b57;color:#eef2fa;font:700 11px ui-monospace,Menlo,monospace}
.mmctl{position:absolute;right:10px;top:10px;display:flex;flex-direction:column;gap:5px;z-index:4}.mmctl button{width:34px;padding:.3rem 0;font-size:16px}
.wm{position:absolute;pointer-events:none;z-index:3}
.wmA{left:12px;bottom:12px;width:9%;max-width:110px;opacity:.8}.wmB{left:50%;top:50%;width:52%;transform:translate(-50%,-50%) rotate(-18deg);opacity:.14}.wmC{right:12px;top:12px;width:9%;max-width:110px;opacity:.8}
.mmmap .wm{left:12px;bottom:12px;width:8%;max-width:100px;opacity:.8}
.ocard{position:absolute;right:12px;bottom:12px;max-width:330px;z-index:6;background:rgba(162,175,198,.5);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);border:1px solid rgba(238,242,250,.65);color:#0b1526;padding:.8rem 1rem;font:400 14px/1.45 Georgia,serif;box-shadow:0 8px 24px rgba(0,0,0,.4)}
.ocard[hidden]{display:none}.ocard .x{position:absolute;right:6px;top:4px;background:none;border:0;font:400 22px/1 system-ui;color:#0b1526;cursor:pointer}
.ocard .ct{font:900 20px "Playfair Display",Georgia,serif;color:#0b1526;text-decoration:underline}.ocard .cs{font:700 10px ui-monospace,Menlo,monospace;letter-spacing:.1em;text-transform:uppercase;margin:.2rem 0 .5rem}
.ocard table{border-collapse:collapse;width:100%}.ocard td{padding:2px 0;vertical-align:top}.ocard td:first-child{font:700 10px ui-monospace,Menlo,monospace;text-transform:uppercase;letter-spacing:.08em;padding-right:10px;white-space:nowrap}.ocard a{color:#0b1526}
.ocard .cl{margin-top:8px;border-top:1px solid rgba(11,21,38,.4);padding-top:6px;font-size:12.5px}
.mmleg{display:flex;flex-wrap:wrap;gap:6px 16px;padding:.6rem .9rem;border-top:1px solid #2c3b57;font:600 11.5px ui-monospace,Menlo,monospace;color:#d6dfee}
.mmcap{margin:0;padding:.5rem .9rem .6rem;font:400 15px/1.55 Georgia,serif;color:#d6dfee}.mmcap a{color:#de7c7c}
.mmfoot,.lbfoot{display:flex;justify-content:space-between;align-items:center;gap:12px;padding:.5rem .9rem .8rem;flex-wrap:wrap}.mmfoot{justify-content:flex-end}
/* chart lightbox 2 */
#clb2{position:fixed;inset:0;background:rgba(2,6,16,.9);z-index:130;display:flex;align-items:center;justify-content:center;overflow:auto;padding:2vh 0}#clb2[hidden]{display:none}
#clb2 .lbx{width:min(70vw,1300px);max-height:96vh;overflow:auto;background:#0f1a2e;border:1px solid #2c3b57}
.lbimgw{position:relative;display:flex;justify-content:center;background:#000}#lbim{position:relative;background-repeat:no-repeat;background-position:center;background-size:100% 100%}
.lbcap{padding:.7rem 1rem .2rem;font:400 15.5px/1.6 Georgia,serif;color:#d6dfee;max-height:24vh;overflow:auto}.lbcap p{margin:0 0 .5rem}.lbcap .lbt2{font:700 19px "Playfair Display",Georgia,serif;color:#eef2fa}.lbcap a{color:#de7c7c}
.wmsw{display:flex;align-items:center;gap:6px;font:600 11px system-ui,Arial,sans-serif;color:#a2afc6}
#clb2 .chs{position:absolute;transform:translate(-50%,-50%);aspect-ratio:1;border-radius:50%;border:0;background:transparent;cursor:pointer}
/* pop-out boxes for LOOKING UP! (mock 6) */
.poptiles{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;margin:.2rem 0 1rem}
.poptile{display:flex;gap:14px;text-align:left;background:#121e33;border:1px solid #2c3b57;border-radius:6px;padding:12px;cursor:pointer;color:#d6dfee;align-items:stretch}.poptile:hover{border-color:#de7c7c}
.poptile .pt-thumb{flex:0 0 38%;background:#000;border:1px solid #2c3b57;display:flex;align-items:center;justify-content:center;overflow:hidden}.poptile .pt-thumb img{width:100%;height:100%;object-fit:cover}
.poptile .pt-body{display:flex;flex-direction:column;gap:6px;min-width:0}.poptile b{font:700 12px system-ui,Arial,sans-serif;letter-spacing:.14em;text-transform:uppercase;color:#eef2fa}
.poptile .pt-d{font:400 15px/1.45 Georgia,serif;color:#d6dfee}.poptile .pt-n{font:600 11px ui-monospace,Menlo,monospace;color:#a2afc6;letter-spacing:.06em}
.poptile .pt-open{margin-top:auto;align-self:flex-start;background:#de7c7c;color:#0b1526;font:700 12.5px "Helvetica Neue",Arial,sans-serif;letter-spacing:.04em;padding:.4rem .8rem;border-radius:3px}
.pop{position:fixed;inset:0;background:rgba(2,6,16,.86);z-index:125;overflow:auto;display:flex;justify-content:center;padding:3vh 0}.pop[hidden]{display:none}
.popbox{width:calc(76vw/.84);zoom:.84;background:#0f1a2e;border:1px solid #2c3b57;align-self:flex-start;max-width:1500px}
.popbox .pophead{display:flex;justify-content:space-between;align-items:center;padding:.6rem .9rem;border-bottom:1px solid #2c3b57;position:sticky;top:0;background:#0f1a2e;z-index:5}
.popbox .pophead b{font:700 13px system-ui,Arial,sans-serif;letter-spacing:.16em;text-transform:uppercase;color:#de7c7c}
/* mock-up only: option switcher */
.optbar{position:fixed;right:12px;bottom:12px;z-index:140;background:rgba(11,21,38,.96);border:1px solid #de7c7c;padding:.5rem .7rem;font:600 11px system-ui,Arial,sans-serif;color:#d6dfee;display:flex;flex-direction:column;gap:6px;max-width:340px}
.optbar .row{display:flex;gap:5px;align-items:center;flex-wrap:wrap}.optbar .ox{position:absolute;right:4px;top:2px;background:none;border:0;color:#a2afc6;cursor:pointer;font-size:14px}.optbar.min .row{display:none}
@media(max-width:1100px){.m5{grid-template-columns:minmax(0,1fr)!important}.poptiles{grid-template-columns:1fr}.mmbox,#clb2 .lbx{width:96vw}}
"""
