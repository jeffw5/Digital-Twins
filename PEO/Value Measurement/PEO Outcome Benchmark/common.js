/* Shared lookups and helpers for every page */
(function(){
  const D = window.PEO;
  const H = window.H = {};
  H.D = D;
  H.PCOL = {P1:'var(--p1)',P2:'var(--p2)',P3:'var(--p3)',P4:'var(--p4)',P5:'var(--p5)',P6:'var(--p6)',P7:'var(--p7)'};
  H.esc = s => String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  H.P = Object.fromEntries(D.personas.map(p=>[p.id,p]));
  H.J = Object.fromEntries(D.jobs.map(j=>[j.id,j]));
  H.O = Object.fromEntries(D.outcomes.map(o=>[o.id,o]));
  H.S = Object.fromEntries(D.services.map(s=>[s.id,s]));
  H.DM = Object.fromEntries(D.domains.map(d=>[d.id,d]));
  H.STEP = Object.fromEntries(D.steps.map(s=>[s.id,s]));
  H.stepNo = id => D.steps.findIndex(s=>s.id===id)+1;
  H.slug = s => s.toLowerCase().replace(/&/g,'and').replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'');
  H.lcFirst = s => s[0].toLowerCase()+s.slice(1);
  H.groupJobs = list => {
    const groups=[];
    [...D.domains].sort((a,b)=>a.n-b.n).forEach(d=>{const js=list.filter(j=>j.kind==='core'&&j.dom[0]===d.id); if(js.length) groups.push([`D${d.n} · ${d.label}`,js]);});
    const ch=list.filter(j=>j.kind!=='core'); if(ch.length) groups.push(['Consumption chain · D5 Client Relationship & Business Development',ch]);
    return groups;
  };
  H.heat = (v,max) => { if(!v) return 'var(--h0)'; const r=v/max; return r>.8?'var(--h5)':r>.6?'var(--h4)':r>.4?'var(--h3)':r>.2?'var(--h2)':'var(--h1)'; };
  H.toast = m => { let t=document.getElementById('toast'); if(!t){t=document.createElement('div');t.id='toast';t.className='toast';document.body.appendChild(t);} t.textContent=m; t.hidden=false; clearTimeout(H._tt); H._tt=setTimeout(()=>t.hidden=true,2400); };
  const PAGES=[['index.html','Overview'],['personas.html','Personas'],['jobs.html','Job Explorer'],['themes.html','Theme Explorer'],['study.html','Job Study']];
  H.nav = current => {
    const el=document.createElement('div'); el.className='site';
    el.innerHTML=`<div class="wrap"><a class="brand" href="index.html">PEO Outcome Benchmark</a><nav aria-label="Pages">${PAGES.map(([h,l])=>`<a href="${h}"${h===current?' aria-current="page"':''}>${l}</a>`).join('')}</nav></div>`;
    document.body.prepend(el);
  };
  H.hashGet = () => { try{ return decodeURIComponent(location.hash.slice(1)); }catch(e){ return ''; } };
  H.hashSet = v => { try{ history.replaceState(null,'','#'+v); }catch(e){} };
})();
