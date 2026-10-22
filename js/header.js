/* Shared site header: border after scroll, hides on scroll down, Services mega-menu, mobile menu. */
(function(){
var d=document,hd=d.querySelector('.hd');if(!hd)return;
var FINE=matchMedia('(hover:hover) and (pointer:fine)').matches,lastY=scrollY,tk=false;
function upd(){tk=false;var y=scrollY;hd.classList.toggle('solid',y>10);
 if(!d.body.classList.contains('navopen')&&!hd.querySelector('.has.open'))hd.classList.toggle('hide',y>lastY+2&&y>300);
 if(y<lastY-2)hd.classList.remove('hide');lastY=y;}
addEventListener('scroll',function(){if(!tk){tk=true;requestAnimationFrame(upd)}},{passive:true});upd();
[].forEach.call(hd.querySelectorAll('.has'),function(h){var b=h.querySelector('button'),t;
 function open(){clearTimeout(t);h.classList.add('open');b.setAttribute('aria-expanded','true')}
 function close(){t=setTimeout(function(){h.classList.remove('open');b.setAttribute('aria-expanded','false')},140)}
 if(FINE){h.addEventListener('mouseenter',open);h.addEventListener('mouseleave',close)}
 b.addEventListener('click',function(){if(h.classList.contains('open')){clearTimeout(t);h.classList.remove('open');b.setAttribute('aria-expanded','false')}else open()});
 h.addEventListener('focusout',function(e){if(!h.contains(e.relatedTarget))close()});
 d.addEventListener('keydown',function(e){if(e.key==='Escape'){h.classList.remove('open');b.setAttribute('aria-expanded','false')}});
});
var bg=hd.querySelector('.burger'),mn=d.querySelector('.mnav');
function setNav(on){d.body.classList.toggle('navopen',on);if(mn)mn.classList.toggle('on',on);if(bg)bg.setAttribute('aria-expanded',on)}
if(bg)bg.addEventListener('click',function(e){e.stopPropagation();setNav(!d.body.classList.contains('navopen'))});
if(mn)[].forEach.call(mn.querySelectorAll('a'),function(a){a.addEventListener('click',function(){setNav(false)})});
d.addEventListener('keydown',function(e){if(e.key==='Escape')setNav(false)});
})();
