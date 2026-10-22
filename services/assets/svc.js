/* Digital Lineup service pages: menu, motion and lead form. No libraries. */
(function(){
var d=document,w=window,RM=matchMedia('(prefers-reduced-motion: reduce)').matches,FINE=matchMedia('(hover:hover) and (pointer:fine)').matches;
function $(s,c){return (c||d).querySelector(s)}function $$(s,c){return [].slice.call((c||d).querySelectorAll(s))}
function clamp(v,a,b){return Math.max(a,Math.min(b,v))}

/* split headings into words */
$$('[data-split]').forEach(function(el){var i=0;
 (function walk(n){[].slice.call(n.childNodes).forEach(function(c){
  if(c.nodeType===3){var f=d.createDocumentFragment();c.textContent.split(/(\s+)/).forEach(function(p){if(!p)return;if(/^\s+$/.test(p)){f.appendChild(d.createTextNode(' '));return}
   var o=d.createElement('span');o.className='w';var s=d.createElement('span');s.textContent=p;s.style.setProperty('--i',i++);o.appendChild(s);f.appendChild(o)});c.parentNode.replaceChild(f,c)}
  else if(c.nodeType===1&&c.tagName!=='BR')walk(c)})})(el)});
/* scroll-fill paragraphs */
var fills=$$('[data-fill]').map(function(el){var ws=[];
 (function walk(n){[].slice.call(n.childNodes).forEach(function(c){if(c.nodeType===3){var f=d.createDocumentFragment();c.textContent.split(/(\s+)/).forEach(function(p){if(!p)return;if(/^\s+$/.test(p)){f.appendChild(d.createTextNode(' '));return}var s=d.createElement('span');s.className='fw';s.textContent=p;ws.push(s);f.appendChild(s)});c.parentNode.replaceChild(f,c)}else if(c.nodeType===1)walk(c)})})(el);
 return {el:el,ws:ws}});

/* reveal on enter */
var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}})},{threshold:.15,rootMargin:'0px 0px -6% 0px'});
$$('[data-split],[data-rv],.ft .big').forEach(function(el){io.observe(el)});

/* counters */
var cio=new IntersectionObserver(function(es){es.forEach(function(e){if(!e.isIntersecting)return;cio.unobserve(e.target);var el=e.target,to=parseFloat(el.dataset.count),dec=(el.dataset.count.split('.')[1]||'').length,t0=null;
 if(RM){el.textContent=to.toFixed(dec);return}
 (function f(t){if(!t0)t0=t;var p=clamp((t-t0)/1400,0,1),e2=1-Math.pow(1-p,4);el.textContent=(to*e2).toFixed(dec);if(p<1)requestAnimationFrame(f)})(performance.now())})},{threshold:.6});
$$('[data-count]').forEach(function(el){cio.observe(el)});

/* videos: play only when on screen */
var vio=new IntersectionObserver(function(es){es.forEach(function(e){var v=e.target;if(e.isIntersecting){if(v.preload==='none'){v.preload='auto'}var p=v.play();if(p&&p.catch)p.catch(function(){})}else v.pause()})},{threshold:.25});
$$('video[data-auto]').forEach(function(v){if(RM){v.removeAttribute('autoplay');v.controls=true;return}vio.observe(v)});
$$('.snd').forEach(function(b){b.addEventListener('click',function(){var v=b.parentNode.querySelector('video');$$('video[data-auto]').forEach(function(o){if(o!==v)o.muted=true});v.muted=!v.muted;b.classList.toggle('on',!v.muted);b.setAttribute('aria-label',v.muted?'Turn sound on':'Turn sound off')})});

/* brand book tabs */
var bookImgs=$$('.device .scr img'),bookTabs=$$('.book .tabs button'),bookCur=0;
bookTabs.forEach(function(t,i){t.addEventListener('click',function(){bookCur=i;bookTabs.forEach(function(x,j){x.classList.toggle('on',j===i);x.setAttribute('aria-selected',j===i)});bookImgs.forEach(function(im,j){im.classList.toggle('off',j!==i)});tick()})});

/* custom cursor */
var cur=$('.cur'),cx=-100,cy=-100,tx=-100,ty=-100;
if(cur&&FINE&&!RM){cur.style.opacity=1;
 addEventListener('mousemove',function(e){tx=e.clientX;ty=e.clientY},{passive:true});
 d.addEventListener('mouseover',function(e){var t=e.target.closest('[data-cur],a,button,summary,label,input,select,textarea');cur.classList.remove('big','link');$('span',cur).textContent='';
  if(!t)return;if(t.dataset.cur){cur.classList.add('big');$('span',cur).textContent=t.dataset.cur}else if(!t.matches('input,select,textarea'))cur.classList.add('link')});
 (function loop(){cx+=(tx-cx)*.2;cy+=(ty-cy)*.2;cur.style.transform='translate3d('+cx+'px,'+cy+'px,0)';requestAnimationFrame(loop)})();
}else if(cur)cur.remove();

/* deliverables: floating image follows the cursor */
var fl=$('.float');
if(fl&&FINE&&!RM){var fx=0,fy=0,gx=0,gy=0,fon=false,fims=$$('img',fl);
 $$('.dl-row').forEach(function(r,i){r.addEventListener('mouseenter',function(){fon=true;fl.classList.add('on');fims.forEach(function(im,j){im.classList.toggle('on',j===i)})});r.addEventListener('mouseleave',function(){fon=false;fl.classList.remove('on')})});
 addEventListener('mousemove',function(e){gx=e.clientX+30;gy=e.clientY-170},{passive:true});
 (function loop(){fx+=(gx-fx)*.12;fy+=(gy-fy)*.12;fl.style.left=fx+'px';fl.style.top=fy+'px';requestAnimationFrame(loop)})();
}

/* scroll-driven motion */
var cols=$$('.collage .col'),coll=$('.collage'),cards=$$('.card'),book=$('.book'),meter=$('.book .meter i'),filmSecs=$$('.films').map(function(f){return {f:f,r:$('.reel',f)}}).filter(function(o){return o.r}),steps=$('.steps'),bar=$('.steps .bar'),stepEls=$$('.step');
var ticking=false;
function tick(){ticking=false;var vh=innerHeight;
 fills.forEach(function(f){var r=f.el.getBoundingClientRect(),p=clamp((vh*.88-r.top)/(r.height+vh*.45),0,1),n=Math.round(p*f.ws.length);f.ws.forEach(function(s,i){s.classList.toggle('on',i<n)})});
 if(RM)return;
 if(coll){var r=coll.getBoundingClientRect();if(r.bottom>0&&r.top<vh){var p=(vh-r.top)/(vh+r.height);cols.forEach(function(c,i){c.style.transform='translate3d(0,'+((i%2?1:-1)*(p-.5)*220)+'px,0)'})}}
 cards.forEach(function(c,i){var nx=cards[i+1],sh=$('.shade',c);if(!nx){c.style.transform='';return}
  var nr=nx.getBoundingClientRect(),cr=c.getBoundingClientRect(),p=clamp((cr.bottom-nr.top)/cr.height,0,1);c.style.transform='scale('+(1-p*.08)+')';if(sh)sh.style.opacity=(p*.45).toFixed(3)});
 if(book){var b=book.getBoundingClientRect(),p=clamp(-b.top/(b.height-vh),0,1),im=bookImgs[bookCur];if(meter)meter.style.width=(p*100)+'%';
  if(im&&im.complete){var scr=im.parentNode,max=im.offsetHeight-scr.offsetHeight;bookImgs.forEach(function(x){x.style.transform='translate3d(0,'+(-Math.max(0,x.offsetHeight-scr.offsetHeight)*p)+'px,0)'})}}
 filmSecs.forEach(function(o){var r2=o.f.getBoundingClientRect();if(r2.bottom>0&&r2.top<vh){var p2=clamp((vh-r2.top)/(vh+r2.height),0,1),max2=Math.max(0,o.r.scrollWidth-innerWidth+40);o.r.style.transform='translate3d('+(-max2*p2)+'px,0,0)'}});
 if(steps){var s=steps.getBoundingClientRect(),p3=clamp((vh*.6-s.top)/s.height,0,1);bar.style.height=(p3*(s.height-16))+'px';stepEls.forEach(function(st){st.classList.toggle('on',st.getBoundingClientRect().top<vh*.6)})}
}
addEventListener('scroll',function(){if(!ticking){ticking=true;requestAnimationFrame(tick)}},{passive:true});
addEventListener('resize',tick);addEventListener('load',tick);bookImgs.forEach(function(im){im.addEventListener('load',tick)});tick();

/* lead form: madlib sentence, fields grow with their text */
var f=$('#lead');
if(f){
 var meas=d.createElement('span');meas.style.cssText='position:absolute;visibility:hidden;white-space:pre;left:-9999px;top:0';d.body.appendChild(meas);
 function fit(el){var cs=getComputedStyle(el);meas.style.font=cs.font;meas.style.letterSpacing=cs.letterSpacing;
  meas.textContent=el.tagName==='SELECT'?el.options[el.selectedIndex].text:(el.value||el.placeholder);
  var extra=el.tagName==='SELECT'?parseFloat(cs.fontSize)*1.35:parseFloat(cs.fontSize)*.35;el.style.width=Math.ceil(meas.getBoundingClientRect().width+extra)+'px';}
 var flds=$$('.fld input,.fld select',f);
 function fitAll(){flds.forEach(fit)}
 flds.forEach(function(el){el.addEventListener(el.tagName==='SELECT'?'change':'input',function(){fit(el)})});
 fitAll();addEventListener('resize',fitAll);addEventListener('load',fitAll);if(d.fonts&&d.fonts.ready)d.fonts.ready.then(fitAll);
 f.addEventListener('submit',function(e){e.preventDefault();var er=$('.err',f);
  var o=Object.fromEntries(new FormData(f));if(o._honey)return;
  var miss=[];if(!(o.name||'').trim())miss.push('your name');if(!/^\S+@\S+\.\S+$/.test((o.email||'').trim()))miss.push('a valid email');if(!o.service)miss.push('a service');if(!o.budget)miss.push('a budget range');
  if(miss.length){er.textContent='Please add '+miss.join(', ')+'.';er.style.display='block';var first=flds.filter(function(x){return !x.value||(x.type==='email'&&!/^\S+@\S+\.\S+$/.test(x.value))})[0];if(first)first.focus();return}
  er.style.display='none';var b=$('button[type=submit]',f),lbl=b.firstChild.textContent;b.disabled=true;b.firstChild.textContent='Sending ';
  o.page='digitallineup.com'+location.pathname;o._subject='Service page lead: '+(o.service||'')+' ('+(o.budget||'')+')';o._template='table';o._captcha='false';
  o.message=['Service: '+(o.service||''),'Budget: '+(o.budget||''),'Company: '+(o.business||''),'Page: '+location.pathname].join('\n');
  fetch(f.dataset.url,{method:'POST',mode:'no-cors',headers:{'Content-Type':'text/plain;charset=utf-8'},body:JSON.stringify(o)})
  .then(function(){f.classList.add('sent');f.scrollIntoView({behavior:RM?'auto':'smooth',block:'center'})})
  .catch(function(){b.disabled=false;b.firstChild.textContent=lbl;er.innerHTML='That did not send. Please try again, or <a href="https://wa.me/923009590042" style="text-decoration:underline">message us on WhatsApp</a>.';er.style.display='block'});
 });
}

/* about: review quotes slider */
var qs=$('[data-qs]');
if(qs){var qb=$$('blockquote',qs),qi=0,qn=$('.qn'),qt;
 function qgo(n){qb[qi].classList.remove('on');qi=(n+qb.length)%qb.length;qb[qi].classList.add('on');if(qn)qn.textContent=(qi+1)+' / '+qb.length;}
 function qauto(){clearInterval(qt);if(!RM)qt=setInterval(function(){qgo(qi+1)},6500)}
 $$('[data-q]').forEach(function(b){b.addEventListener('click',function(){qgo(qi+parseInt(b.dataset.q,10));qauto()})});
 function qfit(){var h=0;qb.forEach(function(b){h=Math.max(h,b.scrollHeight)});qs.style.minHeight=h+'px'}qfit();addEventListener('resize',qfit);addEventListener('load',qfit);
 qauto();}
/* about: giant words slide with scroll */
var gx=$$('[data-gx]');
if(gx.length&&!RM){var gsec=$('.giant'),gt=false;
 function gup(){gt=false;var r=gsec.getBoundingClientRect(),vh=innerHeight;if(r.bottom<0||r.top>vh)return;var p=(vh-r.top)/(vh+r.height);
  gx.forEach(function(el){var dir=parseFloat(el.dataset.gx);el.style.transform='translate3d('+((dir<0?-1:0)*el.scrollWidth*0.33+dir*(p-.5)*-600)+'px,0,0)'})}
 addEventListener('scroll',function(){if(!gt){gt=true;requestAnimationFrame(gup)}},{passive:true});addEventListener('resize',gup);gup();}
var yr=$('[data-year]');if(yr)yr.textContent=new Date().getFullYear();
})();
