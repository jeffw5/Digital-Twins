/* Sales Advisor Circuit Breaker — shared navigation, run bar and panel renderers.
   Each page includes only the containers it needs; renderers skip missing ones. */
(function(){
const C=window.CB; C.init();
const $=id=>document.getElementById(id);
const esc=s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
const {f2,f3,clamp}=C;
const VCOL=v=>'var(--'+v.toLowerCase()+')', VSOFT=v=>'var(--'+v.toLowerCase()+'-s)';
const PAGES=[['index.html','Overview','overview'],['ops.html','Operations','ops'],['decisions.html','Decisions','decisions'],['relevancy.html','Persona relevancy','relevancy'],['review.html','Review queue','review'],['guardrails.html','Guardrails & audit','guardrails']];
let timer=null, E=null, qf='ALL';
const S=()=>C.S;

function bar(val,tau,h){
  const r=val/tau,w=clamp(r/2,.02,1)*100;
  const c=r<1?'var(--pass)':r<1.5?'var(--comply)':'var(--freeze)';
  return '<div class="trk"'+(h?' style="height:'+h+'px"':'')+'><i style="width:'+w+'%;background:'+c+'"></i><span class="t1"></span><span class="t2"></span></div>';
}
function mtbh(aid){const t=S().ag[aid].trips;return t?Math.round(S().tick*4/t)+' h':'∞';}
function commit(){C.save();render();}
function setPersona(p){S().persona=p;C.primePrev();commit();}

/* ---------- theme ---------- */
const TKEY='sacb-theme';
function curTheme(){const t=document.documentElement.getAttribute('data-theme');if(t==='dark'||t==='light')return t;return matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';}
function setTheme(t){document.documentElement.setAttribute('data-theme',t);try{localStorage.setItem(TKEY,t);}catch(e){}paintThemeBtn();}
function paintThemeBtn(){const b=$('theme-btn');if(!b)return;const d=curTheme()==='dark';
  b.innerHTML='<svg viewBox="0 0 20 20" width="16" height="16" aria-hidden="true">'+(d
    ?'<circle cx="10" cy="10" r="4" fill="currentColor"/><g stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><path d="M10 1.5v2M10 16.5v2M1.5 10h2M16.5 10h2M4 4l1.4 1.4M14.6 14.6L16 16M4 16l1.4-1.4M14.6 5.4L16 4"/></g>'
    :'<path d="M15.5 12.8A6.5 6.5 0 0 1 7.2 4.5a6.5 6.5 0 1 0 8.3 8.3z" fill="currentColor"/>')+'</svg><span>'+(d?'Light':'Dark')+'</span>';
  b.setAttribute('aria-label','Switch to '+(d?'light':'dark')+' theme');}
try{const t=localStorage.getItem(TKEY);if(t==='dark'||t==='light')document.documentElement.setAttribute('data-theme',t);}catch(e){}

/* ---------- top bar ---------- */
function buildTop(){
  const tb=$('topbar'); if(!tb) return;
  const page=tb.dataset.page, ctl=tb.dataset.controls==='1';
  tb.innerHTML='<header class="top"><div class="top-in gut"><a class="brand" href="index.html"><i aria-hidden="true"></i>Sales Advisor CB</a><nav class="nav" aria-label="Pages">'+
    PAGES.map(([h,l,k])=>'<a href="'+h+'"'+(k===page?' aria-current="page"':'')+'>'+esc(l)+(k==='review'?'<span class="n" id="navq"></span>':'')+'</a>').join('')+'</nav>'+
    '<button class="theme-btn" id="theme-btn" type="button"></button></div></header>'+
    (ctl?'<div class="runbar"><div class="runbar-in gut">'+
      '<label for="rb-p"><span class="dot" id="rb-dot"></span>Engaged persona <select id="rb-p">'+C.PERSONAS.map(p=>'<option value="'+p.id+'">'+esc(p.name)+'</option>').join('')+'</select></label>'+
      '<label for="rb-s">Relevancy sensitivity <input type="range" id="rb-s" min="0.6" max="1.6" step="0.05"><b class="mono" id="rb-sv"></b></label>'+
      '<span style="display:flex;gap:6px;align-items:center"><button class="btn solid" id="rb-run">Run</button><button class="btn" id="rb-step">Step</button><button class="btn" id="rb-reset">Reset to sample</button></span>'+
      '<span class="clock" id="rb-clock"></span><span class="live" id="rb-live">paused</span>'+
      '<label for="rb-auto"><input type="checkbox" id="rb-auto"> Sample COMPLY decisions for review</label>'+
    '</div></div>':'');
  $('theme-btn').onclick=()=>{setTheme(curTheme()==='dark'?'light':'dark');};
  paintThemeBtn();
  if(!ctl) return;
  $('rb-p').onchange=e=>setPersona(e.target.value);
  $('rb-s').oninput=e=>{S().sens=+e.target.value;commit();};
  $('rb-auto').onchange=e=>{S().auto=e.target.checked;C.save();};
  $('rb-run').onclick=()=>setRun(!timer);
  $('rb-step').onclick=()=>{C.tick();commit();};
  $('rb-reset').onclick=()=>{setRun(false);C.reset();render();};
}
function setRun(on){
  if(on&&!timer) timer=setInterval(()=>{C.tick();commit();if(S().tick>=400)setRun(false);},650);
  if(!on&&timer){clearInterval(timer);timer=null;}
  if($('rb-run')) $('rb-run').textContent=timer?'Pause':'Run';
  if($('rb-live')){$('rb-live').textContent=timer?'running':'paused';$('rb-live').classList.toggle('on',!!timer);}
}
function renderTop(){
  if($('navq')){const n=S().queue.length;$('navq').textContent=n||'';$('navq').hidden=!n;}
  if(!$('rb-p')) return;
  const P=C.PM[S().persona];
  $('rb-p').value=S().persona; $('rb-dot').style.background=P.col;
  $('rb-s').value=S().sens; $('rb-sv').textContent='×'+S().sens.toFixed(2);
  $('rb-auto').checked=S().auto;
  $('rb-clock').textContent='t+'+S().tick+' · '+(S().tick*4)+' h';
}

/* ---------- panels ---------- */
function renderKpis(){
  const el=$('kpis'); if(!el) return;
  const ev=E[S().persona]; let on=0,re=0,dr=0,chain=1;
  C.AGENTS.forEach(a=>{const s=C.agentStatus(a.id,ev);chain*=s.phi;if(s.st==='ONLINE')on++;else if(s.st==='RESTRICTED')re++;else dr++;});
  const trips=C.AGENTS.reduce((t,a)=>t+S().ag[a.id].trips,0);
  const halts=Object.values(ev).filter(e=>e.v==='HALT').length;
  const fleet=trips?Math.round(S().tick*4*6/trips)+' h':'∞';
  const P=C.PM[S().persona];
  el.innerHTML=[
    ['Agents online',on,'of 6 · '+P.short+' lens','var(--pass)'],
    ['Restricted',re,'Tier 1 · conditional autonomy','var(--comply)'],
    ['Dropped',dr,'circuit open · human fallback','var(--halt)'],
    ['Chain fidelity φ',f3(chain),'Π across the sales flow',''],
    ['Open reviews',S().queue.length,halts+' decision(s) at HALT now',S().queue.length?'var(--accent)':''],
    ['Fleet MTBH',fleet,trips+' trips in '+(S().tick*4)+' h','']
  ].map(k=>'<div class="kpi"><span>'+k[0]+'</span><b style="'+(k[3]?'color:'+k[3]:'')+'">'+k[1]+'</b><small>'+esc(k[2])+'</small></div>').join('');
}
function renderLens(){
  const el=$('lens'); if(!el) return;
  const p=C.PM[S().persona];
  el.innerHTML='<div style="display:grid;gap:4px;min-width:0"><b style="font-family:var(--f-display);font-size:16px">'+esc(p.name)+' <span class="mono muted small" style="font-weight:400">'+p.hr+' · '+esc(p.role)+'</span></b><span style="font-size:12.5px;color:var(--ink2)">'+esc(p.lens)+'</span><span class="mono small muted">Relevancy tolerance ×'+f2(p.tau)+' ÷ sensitivity '+f2(S().sens)+' = ×'+f2(p.tau/S().sens)+'</span></div>'+
   '<div class="wbars">'+C.DIMS.map((k,i)=>'<span>'+C.DL[k]+'</span><i style="width:'+(p.w[i]/2*100)+'%;background:'+p.col+'"></i><span>'+p.w[i].toFixed(1)+'</span>').join('')+'</div>';
}
function renderScen(){
  const el=$('scen'); if(!el) return;
  el.innerHTML=C.SCEN.map(s=>'<button class="sc" data-s="'+s.id+'" aria-pressed="'+!!S().on[s.id]+'"><span class="sw"></span><b>'+esc(s.name)+'</b><span class="d">Moves '+s.dims+' on '+Object.keys(s.inc).join(', ')+'</span></button>').join('');
  el.querySelectorAll('.sc').forEach(b=>b.onclick=()=>{const id=b.dataset.s;S().on[id]=!S().on[id];C.addLog('HUMAN','Condition '+(S().on[id]?'on':'off')+': '+C.SCEN.find(x=>x.id===id).name);commit();});
}
function renderPipe(){
  const el=$('pipe'); if(!el) return;
  const ev=E[S().persona]; let chain=1;
  el.innerHTML=C.AGENTS.map(a=>{const st=C.agentStatus(a.id,ev);chain*=st.phi;const k=S().ag[a.id].k;
    return '<div class="agent '+st.st+'"><div class="ah"><div><div class="aid">'+a.id+'</div><div class="an">'+esc(a.name)+'</div></div><span class="pill s-'+st.st+'">'+st.st+'</span></div>'+
     '<div class="kv"><div><span>φ</span><b>'+f2(st.phi)+'</b></div><div><span>K trust</span><b style="color:'+(k<.5?'var(--halt)':k<.7?'var(--comply)':'inherit')+'">'+f2(k)+'</b></div><div><span>MTBH</span><b>'+mtbh(a.id)+'</b></div></div>'+
     '<div class="ddots">'+C.DECS.filter(d=>d.ag===a.id).map(d=>'<a href="decisions.html#'+d.id+'" data-d="'+d.id+'" title="'+d.id+' '+esc(d.name)+' · '+ev[d.id].v+'" aria-label="'+d.id+' '+ev[d.id].v+'" style="background:'+VCOL(ev[d.id].v)+'"></a>').join('')+'</div></div>';}).join('');
  el.querySelectorAll('.ddots a').forEach(a=>a.onclick=()=>{S().sel=a.dataset.d;C.save();});
  if($('chainfill')){$('chainfill').style.width=(chain*100)+'%';$('chainv').textContent=f3(chain);}
}
function renderLedger(){
  const el=$('ledger'); if(!el) return;
  const ev=E[S().persona]; let h='';
  C.AGENTS.forEach(a=>{const st=C.agentStatus(a.id,ev);
    h+='<div class="lg-grp">'+a.id+' · '+esc(a.name)+' <span class="pill s-'+st.st+'">'+st.st+'</span></div>';
    C.DECS.filter(d=>d.ag===a.id).forEach(d=>{const e=ev[d.id];
      h+='<button class="lrow" data-d="'+d.id+'" aria-current="'+(S().sel===d.id)+'"><span class="id">'+d.id+'</span><span style="min-width:0"><span class="nm">'+esc(d.name)+'</span><span class="act">'+esc(d.act)+'</span></span><span class="mini"><span class="mb">Ds'+bar(e.ds,e.tau.s)+'</span><span class="mb">Db'+bar(e.db,e.tau.m)+'</span><span class="mb">Dr'+bar(e.dr,e.tau.r)+'</span></span><span><span class="pill v-'+e.v+'">'+e.v+'</span></span></button>';});});
  const top=el.scrollTop; el.innerHTML=h; el.scrollTop=top;
  el.querySelectorAll('.lrow').forEach(b=>b.onclick=()=>{S().sel=b.dataset.d;history.replaceState(null,'','#'+b.dataset.d);commit();});
}
function renderInsp(){
  const el=$('insp'); if(!el) return;
  const d=C.DM[S().sel], e=E[S().persona][d.id], a=C.AM[d.ag], P=C.PM[S().persona];
  if($('ins-scope')) $('ins-scope').textContent=d.id+' · '+P.short+' lens';
  const anchors={who:C.PM[d.pp].name+' ('+C.PM[d.pp].hr+')',what:'hr:'+d.svc,when:a.when,where:'Prospect worksites · IL, TX'+(S().on.expand?' + CA, NY, WA':''),why:d.out[0]+' · '+C.OUT[d.out[0]].replace(/^(Minimize|Increase) the /,'')};
  const rows=C.DIMS.map((k,i)=>'<tr class="'+(e.wm[k]>e.tau.r*.35?'hot':'')+'"><td class="mono">'+C.DL[k]+'</td><td>'+esc(anchors[k])+'</td><td class="n">'+f2(d.ex[i])+'</td><td class="n">'+f2(e.match[k])+'</td><td class="n">'+P.w[i].toFixed(1)+'</td><td class="n">'+f3(e.wm[k])+'</td></tr>').join('');
  const strip=C.PERSONAS.map(p=>{const x=E[p.id][d.id];return '<button data-p="'+p.id+'" class="'+(p.id===S().persona?'on':'')+'"><span class="dot" style="background:'+p.col+'"></span>'+esc(p.short)+'</button>'+bar(x.dr,x.tau.r,8)+'<span class="mono small">'+f3(x.dr)+'</span><span class="pill v-'+x.v+'">'+x.v+'</span>';}).join('');
  const queued=!!S().queue.find(q=>q.did===d.id);
  el.innerHTML=
   '<div style="display:grid;gap:4px"><div class="eyebrow">'+d.id+' · '+a.id+' '+esc(a.name)+'</div><h2 style="font-size:21px">'+esc(d.name)+'</h2><div class="actline">'+esc(d.act)+'</div></div>'+
   '<div class="meta"><span class="lbl">Built for</span><span class="tag">'+esc(C.PM[d.pp].short)+'</span><span class="lbl">Service</span><span class="tag">hr:'+d.svc+'</span><span class="lbl">Consequence w<sub>c</sub></span><span class="tag">'+f2(d.wc)+'</span></div>'+
   '<div class="outs">'+d.out.map(o=>'<div><b>'+o+'</b>'+esc(C.OUT[o])+'</div>').join('')+'</div>'+
   '<div style="display:grid;gap:8px"><h3>Three-axis morphism distance</h3>'+
    [['D<sub>s</sub>','structural · ontology graph edit',e.ds,e.tau.s],['D<sub>b</sub>','behavioral · output vs reference intent',e.db,e.tau.m],['D<sub>r</sub>','context relevancy · persona-weighted 5D',e.dr,e.tau.r]].map(r=>'<div class="ax"><div class="lab"><span>'+r[0]+' <i>'+r[1]+'</i></span><span class="mono">'+f3(r[2])+' / τ '+f3(r[3])+'</span></div>'+bar(r[2],r[3],9)+'</div>').join('')+'</div>'+
   '<div style="display:grid;gap:6px"><h3>Five dimensions of relevancy · '+esc(P.short)+' lens</h3><div class="scroll"><table class="t5"><thead><tr><th>Dim</th><th>Reference anchor (Z<sub>real</sub>)</th><th class="n">Exposure</th><th class="n">Live match</th><th class="n">Weight</th><th class="n">w·miss/5</th></tr></thead><tbody>'+rows+'<tr><td colspan="5" class="mono">D<sub>r</sub> = Σ</td><td class="n"><b>'+f3(e.dr)+'</b></td></tr></tbody></table></div></div>'+
   '<div style="display:grid;gap:6px"><h3>Same decision, every persona</h3><div class="pstrip">'+strip+'</div></div>'+
   (d.g?'<div class="guard '+(e.guard?'hit':'')+'"><span><b class="mono">'+d.g+'</b> '+esc(C.GUARDS[d.g].label)+'</span><b class="mono">'+(e.guard?'BREACHED':'clear')+'</b></div>':'')+
   '<div class="verdict" style="background:'+VSOFT(e.v)+';border-color:'+VCOL(e.v)+'"><span class="eyebrow" style="color:'+VCOL(e.v)+'">Circuit breaker verdict · φ '+f3(e.phi)+'</span><span class="vv" style="color:'+VCOL(e.v)+'">'+e.v+'</span><span style="font-size:12.5px">'+esc(e.v==='PASS'?'All three axes inside tolerance for this persona.':C.reason(e))+'</span></div>'+
   '<div style="display:flex;gap:8px;flex-wrap:wrap"><button class="btn" id="b-review" '+(queued?'disabled':'')+'>'+(queued?'In review queue':'Send to human review')+'</button><a class="btn" href="review.html">Open review queue</a></div>';
  el.querySelectorAll('.pstrip button').forEach(b=>b.onclick=()=>setPersona(b.dataset.p));
  const br=$('b-review'); if(br) br.onclick=()=>{C.enqueue(e,'manual');C.addLog('HUMAN','Manual review requested for '+d.id+' under '+P.hr);commit();};
}
function renderQueue(){
  const el=$('queue'); if(!el) return;
  const dn=S().done;
  if($('qhead')) $('qhead').innerHTML='<span class="tag">Open '+S().queue.length+'</span><span class="tag">Approved '+dn.approved+'</span><span class="tag">With conditions '+dn.cond+'</span><span class="tag">Rejected '+dn.rejected+'</span><span class="tag">Escalated '+dn.escalated+'</span><span class="tag">Recalibrations '+dn.recal+'</span>';
  if($('qfilter')){$('qfilter').innerHTML=['ALL','HALT','FREEZE','COMPLY'].map(v=>{const n=v==='ALL'?S().queue.length:S().queue.filter(q=>q.v===v).length;return '<button data-v="'+v+'" aria-pressed="'+(qf===v)+'">'+(v==='ALL'?'All':v)+' · '+n+'</button>';}).join('');
    $('qfilter').querySelectorAll('button').forEach(b=>b.onclick=()=>{qf=b.dataset.v;render();});}
  const list=S().queue.filter(q=>qf==='ALL'||q.v===qf);
  if(!list.length){el.innerHTML='<div class="empty">Nothing waiting'+(qf==='ALL'?'':' at '+qf)+'. Trips and sampled COMPLY decisions land here as the simulation runs.</div>';return;}
  el.innerHTML=list.map(q=>{const d=C.DM[q.did],live=E[q.pid][q.did],p=C.PM[q.pid];
    return '<div class="qi '+q.v+'"><div class="qt"><span class="pill v-'+q.v+'">'+q.v+'</span><b>'+d.id+'</b><a href="decisions.html#'+d.id+'" data-d="'+d.id+'" style="color:inherit">'+esc(d.name)+'</a></div>'+
     '<div class="meta"><span class="tag">'+d.ag+' '+esc(C.AM[d.ag].name)+'</span><span class="tag" style="display:inline-flex;gap:5px;align-items:center"><span class="dot" style="background:'+p.col+'"></span>'+esc(p.short)+'</span><span class="tag">raised t+'+q.t+'</span><span class="tag">'+(q.why==='sample'?'COMPLY sample':q.why==='manual'?'manual request':'trip')+'</span><span class="tag">now '+live.v+'</span><span class="tag">'+esc(d.act)+'</span></div>'+
     '<div class="qr">'+esc(q.r)+'</div>'+
     '<div class="qb"><button class="btn" data-q="'+q.qid+'" data-a="approve" '+(q.v==='HALT'?'disabled title="Deterministic veto: cannot be approved"':'')+'>Approve</button><button class="btn" data-q="'+q.qid+'" data-a="cond" '+(q.v==='HALT'?'disabled':'')+'>Approve with conditions</button><button class="btn" data-q="'+q.qid+'" data-a="reject">Reject &amp; correct</button><button class="btn" data-q="'+q.qid+'" data-a="escalate">Escalate</button><button class="btn" data-q="'+q.qid+'" data-a="recal">Recalibrate '+d.ag+'</button></div></div>';}).join('');
  el.querySelectorAll('.qb .btn').forEach(b=>b.onclick=()=>{C.dispose(b.dataset.q,b.dataset.a);render();});
  el.querySelectorAll('.qt a').forEach(a=>a.onclick=()=>{S().sel=a.dataset.d;C.save();});
}
function renderResolved(){
  const el=$('resolved'); if(!el) return;
  const r=S().resolved||[];
  el.innerHTML=r.length?'<table class="t5"><thead><tr><th>Decision</th><th>Was</th><th>Persona</th><th>Disposition</th><th class="n">At</th></tr></thead><tbody>'+r.slice(0,20).map(x=>'<tr><td>'+x.did+' '+esc(C.DM[x.did].name)+'</td><td><span class="pill v-'+x.v+'">'+x.v+'</span></td><td>'+esc(C.PM[x.pid].short)+'</td><td>'+esc(x.disp)+'</td><td class="n">t+'+x.at+'</td></tr>').join('')+'</tbody></table>':'<div class="empty">No dispositions yet. Decisions you approve, reject, escalate or supersede appear here.</div>';
}
function renderChart(){
  const el=$('chart'); if(!el) return;
  const W=640,H=230,L=40,R=10,T=12,B=26,H0=S().hist,n=Math.max(H0.length,2);
  const x=i=>L+(W-L-R)*i/(n-1),y=v=>T+(H-T-B)*(1-v);
  const mono='font-family="IBM Plex Mono,monospace" font-size="10" fill="var(--ink3)"';
  let g='';
  [0,.25,.5,.75,1].forEach(v=>{g+='<line x1="'+L+'" x2="'+(W-R)+'" y1="'+y(v)+'" y2="'+y(v)+'" stroke="var(--rule)"/><text x="'+(L-6)+'" y="'+(y(v)+4)+'" text-anchor="end" '+mono+'>'+v.toFixed(2)+'</text>';});
  if(H0.length){
    const step=Math.max(1,Math.ceil(H0.length/8));
    H0.forEach((h,i)=>{if(i%step===0||i===H0.length-1)g+='<text x="'+x(i)+'" y="'+(H-8)+'" text-anchor="middle" '+mono+'>t+'+h.t+'</text>';});
    Object.entries(S().dropAt[S().persona]).forEach(([aid,t])=>{const i=H0.findIndex(h=>h.t===t);if(i<0)return;
      g+='<line x1="'+x(i)+'" x2="'+x(i)+'" y1="'+T+'" y2="'+(H-B)+'" stroke="var(--halt)" stroke-dasharray="3 3"/><text x="'+(x(i)+3)+'" y="'+(T+10)+'" font-family="IBM Plex Mono,monospace" font-size="10" fill="var(--halt)">'+aid+'</text>';});
    C.PERSONAS.slice().sort((a,b)=>(a.id===S().persona)-(b.id===S().persona)).forEach(p=>{const on=p.id===S().persona;
      g+='<polyline points="'+H0.map((h,i)=>x(i).toFixed(1)+','+y(h.chain[p.id]).toFixed(1)).join(' ')+'" fill="none" stroke="'+p.col+'" stroke-width="'+(on?2.6:1.2)+'" stroke-opacity="'+(on?1:.45)+'" stroke-linejoin="round"/>';
      if(on){g+='<circle cx="'+x(H0.length-1)+'" cy="'+y(H0[H0.length-1].chain[p.id])+'" r="3.5" fill="'+p.col+'"/>';}});
  }
  el.innerHTML='<svg viewBox="0 0 '+W+' '+H+'" role="img" aria-label="Chain fidelity over time for each persona">'+g+'</svg>';
  if($('chleg')) $('chleg').innerHTML=C.PERSONAS.map(p=>{const last=H0.length?H0[H0.length-1].chain[p.id]:1;return '<span style="'+(p.id===S().persona?'font-weight:600;color:var(--ink)':'')+'"><span class="dot" style="background:'+p.col+'"></span>'+esc(p.short)+' <span class="mono">'+f2(last)+'</span></span>';}).join('');
}
function personaHead(){return C.PERSONAS.map(p=>'<th class="'+(p.id===S().persona?'on':'')+'"><span class="dot" style="background:'+p.col+';margin-right:4px"></span>'+esc(p.short)+'</th>').join('');}
function renderDrop(){
  const el=$('dm'); if(!el) return;
  el.innerHTML='<thead><tr><th>Agent</th>'+personaHead()+'</tr></thead><tbody>'+C.AGENTS.map(a=>'<tr><td>'+a.id+' '+esc(a.name)+'</td>'+C.PERSONAS.map(p=>{const t=S().dropAt[p.id][a.id];return '<td class="c" style="'+(t!=null?'color:var(--halt);font-weight:600':'color:var(--ink3)')+'">'+(t!=null?'t+'+t:'—')+'</td>';}).join('')+'</tr>').join('')+'</tbody>';
}
function renderHeat(){
  const el=$('hm'); if(!el) return;
  let h='<thead><tr><th>Decision</th>'+personaHead()+'</tr></thead><tbody>';
  C.AGENTS.forEach(a=>{h+='<tr><td class="grp" colspan="'+(C.PERSONAS.length+1)+'">'+a.id+' · '+esc(a.name)+'</td></tr>';
    C.DECS.filter(d=>d.ag===a.id).forEach(d=>{h+='<tr class="'+(S().sel===d.id?'on':'')+'"><td style="text-align:left;white-space:normal;min-width:200px">'+d.id+' '+esc(d.name)+'</td>'+C.PERSONAS.map(p=>{const e=E[p.id][d.id],r=e.dr/e.tau.r;
      const v=e.guard?'HALT':r>=1.5?'FREEZE':r>1?'COMPLY':'PASS';
      return '<td class="cell"><button data-d="'+d.id+'" data-p="'+p.id+'" title="'+esc(p.short)+' · D_r '+f3(e.dr)+' / τ '+f3(e.tau.r)+'" style="background:'+VSOFT(v)+';color:'+VCOL(v)+'">'+(e.guard?'G':f2(r))+'</button></td>';}).join('')+'</tr>';});});
  el.innerHTML=h+'</tbody>';
  el.querySelectorAll('button').forEach(b=>b.onclick=()=>{S().sel=b.dataset.d;S().persona=b.dataset.p;C.primePrev();C.save();location.href='decisions.html#'+b.dataset.d;});
}
function renderPcards(){
  const el=$('pcards'); if(!el) return;
  el.innerHTML=C.PERSONAS.map(p=>{const ev=E[p.id],c={PASS:0,COMPLY:0,FREEZE:0,HALT:0},dim={};C.DIMS.forEach(k=>dim[k]=0);
    Object.values(ev).forEach(e=>{c[e.v]++;C.DIMS.forEach(k=>dim[k]+=e.wm[k]);});
    const top=C.DIMS.slice().sort((a,b)=>dim[b]-dim[a])[0];
    let chain=1,drop=0;C.AGENTS.forEach(a=>{const s=C.agentStatus(a.id,ev);chain*=s.phi;if(s.st==='DROPPED')drop++;});
    return '<button class="pc" data-p="'+p.id+'" aria-pressed="'+(p.id===S().persona)+'"><span class="ph"><span class="dot" style="background:'+p.col+'"></span>'+esc(p.name)+'</span>'+
     '<span class="small muted">'+esc(p.role)+' · tolerance ×'+f2(p.tau)+'</span>'+
     '<span class="vcount">'+['PASS','COMPLY','FREEZE','HALT'].map(v=>'<i style="width:'+(c[v]/20*100)+'%;background:'+VCOL(v)+'"></i>').join('')+'</span>'+
     '<span class="mono small">'+c.PASS+' pass · '+c.COMPLY+' comply · '+c.FREEZE+' freeze · '+c.HALT+' halt</span>'+
     '<span class="meta"><span class="tag">φ '+f3(chain)+'</span><span class="tag" style="'+(drop?'color:var(--halt)':'')+'">'+drop+' agent(s) dropped</span><span class="tag">most misses: '+C.DL[top]+'</span></span></button>';}).join('');
  el.querySelectorAll('.pc').forEach(b=>b.onclick=()=>setPersona(b.dataset.p));
}
function renderGuards(){
  const el=$('glist'); if(!el) return;
  el.innerHTML=Object.entries(C.GUARDS).map(([k,g])=>{const hit=g.test(S()),d=C.DM[g.dec];return '<div class="guard '+(hit?'hit':'')+'"><span style="display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap"><b class="mono">'+k+' · '+esc(g.kind)+'</b><b class="mono">'+(hit?'BREACHED':'clear')+'</b></span><span>'+esc(g.label)+'</span><span class="small" style="opacity:.8">Protects '+d.id+' '+esc(d.name)+' ('+d.ag+')</span></div>';}).join('');
}
function renderDrift(){
  const el=$('drift'); if(!el) return;
  const cols=[...C.DIMS,'ds','db'],lab=k=>k==='ds'?'D_s add':k==='db'?'D_b add':C.DL[k];
  el.innerHTML='<thead><tr><th>Agent</th>'+cols.map(k=>'<th>'+lab(k)+'</th>').join('')+'<th>K trust</th><th>Trips</th></tr></thead><tbody>'+C.AGENTS.map(a=>{const d=S().drift[a.id];
    return '<tr><td>'+a.id+' '+esc(a.name)+'</td>'+cols.map(k=>{const v=d[k],n=(k==='ds'||k==='db')?v/.15:v;const pct=Math.round(clamp(n,0,1)*70);
      return '<td class="c" style="background:color-mix(in srgb, var(--freeze) '+pct+'%, transparent)">'+f2(v)+'</td>';}).join('')+'<td class="c">'+f2(S().ag[a.id].k)+'</td><td class="c">'+S().ag[a.id].trips+'</td></tr>';}).join('')+'</tbody>';
}
function renderLog(){
  const el=$('log'); if(!el) return;
  const lim=+(el.dataset.limit||120);
  el.innerHTML=S().log.slice(0,lim).map(l=>'<div class="'+l.cls+'"><span class="t">t+'+l.t+'</span>'+esc(l.msg)+'</div>').join('')||'<div class="muted">No events yet.</div>';
}

function render(){
  E=C.evalAll();
  renderTop(); renderKpis(); renderLens(); renderScen(); renderPipe(); renderLedger(); renderInsp(); renderQueue(); renderResolved(); renderChart(); renderDrop(); renderHeat(); renderPcards(); renderGuards(); renderDrift(); renderLog();
}

/* ---------- boot ---------- */
buildTop();
const h=(location.hash||'').slice(1); if(C.DM[h]){C.S.sel=h;C.save();}
render();
window.addEventListener('storage',e=>{if(e.key===C.KEY&&!timer&&C.load())render();});
window.addEventListener('hashchange',()=>{const k=location.hash.slice(1);if(C.DM[k]){C.S.sel=k;commit();}});
window.CBUI={render};
})();
