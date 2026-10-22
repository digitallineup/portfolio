/* Shared site footer: wordmark fit + draggable pills (needs /js/matter.min.js). */
(function(){function start(){
var rm=matchMedia('(prefers-reduced-motion: reduce)').matches;
  // footer wordmark fit
  (function(){
    var w=document.querySelector('[data-fit]'); if(!w) return; var s=w.firstElementChild;
    function fit(){var sm=matchMedia('(max-width:700px)').matches;var want=sm?'DIGITAL<br>LINEUP':'DIGITAL LINEUP';if(s.innerHTML!==want)s.innerHTML=want;s.style.fontSize='100px';var r=s.getBoundingClientRect().width,avail=w.clientWidth-parseFloat(getComputedStyle(w).paddingLeft)*2;s.style.fontSize=(100*avail/r)+'px';}
    fit();addEventListener('resize',fit);addEventListener('load',fit);
  })();
  // footer pill physics
  (function(){
    var pit=document.querySelector('[data-pit]'); if(!pit) return;
    var small=matchMedia('(max-width:700px)');
    if(rm||small.matches){pit.classList.add('ready','static');return;}
    var started=false, M, eng, run, raf, bodies=[], pills=[].slice.call(pit.querySelectorAll('.pill')), w, h, lastW=0, lastH=0;
    function teardown(){ if(!eng) return; cancelAnimationFrame(raf); M.Runner.stop(run); M.Composite.clear(eng.world,false,true); M.Engine.clear(eng); eng=null; }
    function build(){
      M=window.Matter; teardown();
      pit.classList.remove('ready'); w=pit.clientWidth; h=pit.clientHeight; lastW=w; lastH=h;
      eng=M.Engine.create({enableSleeping:true}); var W=eng.world, T=600, n=pills.length; bodies=[];
      M.Composite.add(W,[M.Bodies.rectangle(w/2,h+T/2,w+T*2,T,{isStatic:true}),M.Bodies.rectangle(-T/2,h/2-h,T,h*4,{isStatic:true}),M.Bodies.rectangle(w+T/2,h/2-h,T,h*4,{isStatic:true})]);
      pills.forEach(function(p,i){
        p.style.transform='translate(-50%,-50%)';
        var r=p.getBoundingClientRect(),pw=r.width,ph=r.height;
        var x=w*((i+.5)/n)+(Math.random()-.5)*w*.12; x=Math.min(Math.max(x,pw/2+4),w-pw/2-4);
        var bd=M.Bodies.rectangle(x,-ph-i*(ph+30)-Math.random()*40,pw,ph,{chamfer:{radius:ph/2},restitution:.2,friction:.6,frictionAir:.02,angle:(Math.random()-.5)*.4});
        bd.pw=pw;bd.ph=ph; bodies.push(bd); M.Composite.add(W,bd);
      });
      pit.classList.add('ready');
      var mouse=M.Mouse.create(pit), mc=M.MouseConstraint.create(eng,{mouse:mouse,constraint:{stiffness:.15,damping:.1}});
      M.Composite.add(W,mc);
      mouse.element.removeEventListener('wheel',mouse.mousewheel);mouse.element.removeEventListener('DOMMouseScroll',mouse.mousewheel);
      run=M.Runner.create(); M.Runner.run(run,eng);
      (function loop(){
        bodies.forEach(function(bd,i){
          var hx=bd.pw/2, hy=bd.ph/2;
          if(bd.position.x<hx||bd.position.x>w-hx||bd.position.y>h-hy+1){M.Body.setPosition(bd,{x:Math.min(Math.max(bd.position.x,hx),w-hx),y:Math.min(bd.position.y,h-hy)});M.Body.setVelocity(bd,{x:0,y:0});}
          pills[i].style.transform='translate(-50%,-50%) translate('+bd.position.x+'px,'+bd.position.y+'px) rotate('+bd.angle+'rad)';
        });
        raf=requestAnimationFrame(loop);
      })();
    }
    function start(){ if(started||!window.Matter) return; started=true; build(); }
    var sx,sy; pit.addEventListener('pointerdown',function(e){sx=e.clientX;sy=e.clientY;});
    pills.forEach(function(p){p.addEventListener('click',function(e){if(Math.hypot(e.clientX-sx,e.clientY-sy)>6){e.preventDefault();}});});
    var rt; addEventListener('resize',function(){clearTimeout(rt);rt=setTimeout(function(){if(started&&(pit.clientWidth!==lastW||pit.clientHeight!==lastH))build();},250);});
    var pio=new IntersectionObserver(function(es){if(es[0].isIntersecting){if(window.Matter)start();else{var s=document.querySelector('script[src*="matter"]');if(!s){s=document.createElement('script');s.src='/js/matter.min.js';s.async=true;document.head.appendChild(s);}s.addEventListener('load',start);}pio.disconnect();}},{threshold:.2});
    pio.observe(pit);
    setTimeout(function(){if(!started&&!window.Matter){pit.classList.add('ready','static');}},6000);
  })();
}
if(window.requestIdleCallback)requestIdleCallback(start,{timeout:800});else setTimeout(start,0);
})();
