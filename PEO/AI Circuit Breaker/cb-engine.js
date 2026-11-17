/* Sales Advisor Circuit Breaker — shared model, evaluation and simulation engine.
   State is kept in this viewer's browser so every dashboard page shows the same run. */
(function(){
const DIMS=['who','what','when','where','why'];
const DL={who:'WHO',what:'WHAT',when:'WHEN',where:'WHERE',why:'WHY'};
const PERSONAS=[
 {id:'owner',name:'Business Owner / CEO',short:'Owner',col:'#8b5cf6',w:[1.0,0.8,0.7,0.6,1.9],tau:1.00,hr:'hr:PersonaOwner',role:'Economic buyer',lens:'Judges every recommendation by WHY: does it help grow the business without exposure the owner doesn’t know about?'},
 {id:'finance',name:'Finance Leader',short:'Finance',col:'#0e9f8e',w:[0.8,1.8,1.6,0.7,0.6],tau:0.85,hr:'hr:PersonaFinance',role:'Gatekeeper on total cost',lens:'Most sensitive to WHAT (fees, deposits, the numbers) and WHEN (pay dates, renewal timing). Tightest tolerance.'},
 {id:'hr',name:'HR Leader',short:'HR',col:'#e0567a',w:[1.0,1.5,0.9,1.6,0.9],tau:0.90,hr:'hr:PersonaHR',role:'Primary evaluator',lens:'Weighs WHAT and WHERE: is the guidance right for every state where employees work?'},
 {id:'ops',name:'Operations & Safety Leader',short:'Ops & Safety',col:'#d97706',w:[0.7,1.3,0.8,1.9,0.9],tau:0.95,hr:'hr:PersonaOpsSafety',role:'Influencer on risk',lens:'WHERE dominates: worksites, hazard exposure, class codes and state injury rules.'},
 {id:'mgr',name:'People Manager',short:'Manager',col:'#3b82f6',w:[1.6,0.9,1.2,0.6,0.8],tau:1.10,hr:'hr:PersonaManager',role:'User and influencer',lens:'WHO and WHEN: is this about my team, and does it land in the right part of the pay and review cycle?'},
 {id:'emp',name:'Worksite Employee',short:'Employee',col:'#65a30d',w:[1.8,1.2,1.0,0.6,0.6],tau:1.15,hr:'hr:PersonaEmployee',role:'End user',lens:'WHO first: is this about my pay, my coverage, and is my data treated with care? Loosest tolerance, highest WHO weight.'},
 {id:'it',name:'IT & Systems Administrator',short:'IT',col:'#64748b',w:[0.9,1.7,0.6,1.4,0.5],tau:0.90,hr:'hr:PersonaIT',role:'Technical veto',lens:'WHAT and WHERE: systems, data flows, where employee data lives and who can reach it.'}
];
const PM=Object.fromEntries(PERSONAS.map(p=>[p.id,p]));
const AGENTS=[
 {id:'A1',name:'Prospect Qualification',short:'Qualification',when:'Pre-engagement · lead triage'},
 {id:'A2',name:'Needs Discovery',short:'Discovery',when:'Discovery-call window'},
 {id:'A3',name:'Solution Configuration',short:'Configuration',when:'Pre-proposal design'},
 {id:'A4',name:'Pricing & Quote',short:'Pricing',when:'Quote validity · renewal cycle'},
 {id:'A5',name:'Compliance & Disclosure',short:'Compliance',when:'Before any written claim'},
 {id:'A6',name:'Proposal & Outreach',short:'Outreach',when:'Proposal and close'}
];
const AM=Object.fromEntries(AGENTS.map(a=>[a.id,a]));
const OUT={
 O195:'Minimize the time required to decide which HR responsibilities to keep in-house and which to hand off',
 O196:'Minimize the time required to compare providers on total cost, e.g., fees, benefits, insurance, taxes',
 O197:'Minimize the likelihood of hidden or unexpected fees after signing',
 O198:'Minimize the time required to understand which employer responsibilities and liabilities are shared and which the company keeps',
 O199:'Minimize the likelihood of choosing a provider that is not financially sound or properly certified, e.g., IRS CPEO status',
 O200:'Minimize the time required to negotiate and sign the service agreement',
 O201:'Minimize the likelihood of committing to contract terms that are difficult to exit',
 O202:'Minimize the likelihood that employees react negatively to a change in how they are paid and covered',
 O203:'Minimize the time required to gather the employee census and payroll history needed for setup',
 O207:'Minimize the likelihood of a gap or disruption in employees’ benefits coverage during the move',
 O071:'Minimize the time required to determine which federal, state and local employment laws apply to the company',
 O036:'Minimize the time required to determine which benefits matter most to current and prospective employees',
 O040:'Minimize the employer cost per covered employee for an equivalent level of coverage',
 O039:'Increase the likelihood of offering coverage comparable to large employers, e.g., plan choice, network breadth',
 O043:'Minimize the likelihood of losing a candidate or employee because benefits are not competitive',
 O092:'Minimize the likelihood of employees being assigned to the wrong workers’ compensation class code',
 O097:'Minimize the cost of workers’ compensation coverage, e.g., premium per payroll dollar, experience modifier',
 O054:'Minimize the time required to determine which retirement plan design fits the company’s budget and goals',
 O059:'Minimize the fiduciary liability the business owner carries for the plan',
 O011:'Minimize the time required to determine tax registration and withholding requirements when an employee starts working in a new state or locality',
 O072:'Minimize the likelihood of an employee policy being out of date with state requirements',
 O220:'Minimize the time required to determine the return the company gets from its HR provider',
 O221:'Minimize the likelihood of a large cost increase at renewal without advance notice',
 O016:'Minimize the likelihood of losing tax credits or paying wage-base taxes twice when the employer-of-record arrangement changes',
 O164:'Minimize the likelihood of people data being used for a purpose other than the one it was collected for',
 O167:'Minimize the likelihood that employee data is accessed by someone without a need to know'
};
const DECS=[
 {id:'D01',ag:'A1',name:'Score ICP fit and assign segment',act:'Fit 0.82 · professional services · 64 WSEs',pp:'owner',svc:'ProspectQualificationRFPService',out:['O195'],ex:[.4,.6,.3,.5,.7],wc:.3},
 {id:'D02',ag:'A1',name:'Map buying committee and economic buyer',act:'Economic buyer = Owner · evaluator = HR Leader',pp:'owner',svc:'ProspectQualificationRFPService',out:['O198'],ex:[1,.3,.4,.2,.5],wc:.4},
 {id:'D03',ag:'A1',name:'Route to full PEO vs payroll-only offer',act:'Route → full co-employment PEO',pp:'finance',svc:'ProspectQualificationRFPService',out:['O195','O196'],ex:[.5,.7,.3,.4,.8],wc:.5},
 {id:'D04',ag:'A2',name:'Map stated pains to jobs to be done',act:'Pains → J09 compliance · J05 benefits · J01 payroll',pp:'hr',svc:'ProspectQualificationRFPService',out:['O071','O036'],ex:[.6,.8,.3,.6,.6],wc:.4},
 {id:'D05',ag:'A2',name:'Rank desired outcomes for the engaged persona',act:'Top 3 → O040 · O197 · O221',pp:'finance',svc:'ProspectQualificationRFPService',out:['O040','O197'],ex:[1,.6,.4,.3,.8],wc:.45},
 {id:'D06',ag:'A2',name:'Capture employee census and work locations',act:'64 WSEs · IL 41 · TX 12 · CA 7 · NY 4',pp:'finance',svc:'ClientImplementationDataMigrationService',out:['O203','O164'],ex:[.8,.6,.3,.9,.3],wc:.7,g:'G5'},
 {id:'D07',ag:'A3',name:'Recommend medical plan tier',act:'Master health plan · Gold PPO + HSA option',pp:'owner',svc:'PEOMasterHealthPlanService',out:['O039','O040'],ex:[.5,.7,.6,.8,.6],wc:.7},
 {id:'D08',ag:'A3',name:'Assign workers’ comp class codes',act:'8810 clerical ×52 · 5403 carpentry ×12',pp:'ops',svc:'WorkersCompMasterPolicyService',out:['O092','O097'],ex:[.3,.9,.3,1,.4],wc:.9,g:'G3'},
 {id:'D09',ag:'A3',name:'Recommend retirement plan design',act:'MEP 401(k) · 4% safe-harbor match',pp:'owner',svc:'MultipleEmployerPlan401kService',out:['O054','O059'],ex:[.6,.6,.5,.3,.8],wc:.6},
 {id:'D10',ag:'A3',name:'Set up multi-state tax and handbook policy',act:'Register CA EDD, NY DOL · CA handbook addendum',pp:'hr',svc:'MultiStateTaxFilingService',out:['O011','O072'],ex:[.3,.8,.5,1,.4],wc:.8},
 {id:'D11',ag:'A4',name:'Build total-cost comparison vs current spend',act:'Projected savings $41,800/yr (−6.2%)',pp:'finance',svc:'ClientInvoicingBillingService',out:['O196','O220'],ex:[.4,1,.8,.6,.9],wc:.85,g:'G1'},
 {id:'D12',ag:'A4',name:'Quote per-employee admin fee',act:'$128 PEPM × 64 WSEs',pp:'finance',svc:'MasterServiceAgreementContractingService',out:['O197'],ex:[.3,1,.7,.5,.7],wc:.8},
 {id:'D13',ag:'A4',name:'Disclose expected renewal increase',act:'Renewal band +4–7% at month 12',pp:'finance',svc:'ClientRenewalRenegotiationService',out:['O221'],ex:[.3,.8,1,.4,.6],wc:.75},
 {id:'D14',ag:'A5',name:'State the shared-liability split',act:'Co-employment allocation table v3 attached',pp:'owner',svc:'MasterServiceAgreementContractingService',out:['O198'],ex:[.6,.8,.3,.7,.5],wc:.85},
 {id:'D15',ag:'A5',name:'Assert certification and tax-credit continuity',act:'IRS CPEO certified · wage base preserved',pp:'finance',svc:'CPEOComplianceMonitoringService',out:['O199','O016'],ex:[.3,.8,.5,1,.5],wc:.95,g:'G2'},
 {id:'D16',ag:'A5',name:'Apply employee-data handling and consent',act:'Census for quoting only · 90-day retention',pp:'it',svc:'DataPrivacySecurityGovernanceService',out:['O164','O167'],ex:[.7,.7,.4,.7,.6],wc:.8},
 {id:'D17',ag:'A6',name:'Draft persona-tailored value narrative',act:'Lead with benefits parity + compliance coverage',pp:'owner',svc:'ProspectQualificationRFPService',out:['O043','O039'],ex:[1,.6,.5,.4,1],wc:.6,g:'G4'},
 {id:'D18',ag:'A6',name:'Propose next step and follow-up timing',act:'Benefits review call · Thu 10:00 CT',pp:'owner',svc:'ProspectQualificationRFPService',out:['O200'],ex:[.7,.3,1,.4,.6],wc:.3},
 {id:'D19',ag:'A6',name:'Recommend contract term and exit clause',act:'12-month term · 30-day termination for convenience',pp:'owner',svc:'MasterServiceAgreementContractingService',out:['O201'],ex:[.5,.8,.6,.4,.8],wc:.8},
 {id:'D20',ag:'A6',name:'Plan the employee transition message',act:'All-hands + FAQ two weeks before first payroll',pp:'emp',svc:'ClientOnboardingKickoffService',out:['O202','O207'],ex:[1,.6,.8,.5,.5],wc:.6}
];
const DM=Object.fromEntries(DECS.map(d=>[d.id,d]));
const GUARDS={
 G1:{label:'Total-cost comparison may not show savings that fall below the admin-fee cost floor',dec:'D11',kind:'Deontic · prohibition',test:s=>s.drift.A4.why>0.5||s.drift.A4.ds>0.10},
 G2:{label:'No certification or tax-credit claim for a state the PEO is not registered in',dec:'D15',kind:'Deontic · prohibition',test:s=>s.drift.A5.where>0.55},
 G3:{label:'Workers’ comp class code must match the NAICS hazard profile of the worksite',dec:'D08',kind:'Impossible state',test:s=>s.on.hazard&&s.drift.A3.what>0.45},
 G4:{label:'No guaranteed savings and no legal advice in outbound messaging',dec:'D17',kind:'Deontic · prohibition',test:s=>s.drift.A6.why>0.55},
 G5:{label:'Census data may be used only for the consented quoting purpose (O164)',dec:'D06',kind:'Purpose limitation',test:s=>s.drift.A2.who>0.6}
};
const SCEN=[
 {id:'expand',name:'Prospect adds CA, NY and WA worksites',dims:'WHERE',inc:{A2:{where:.02},A3:{where:.045},A4:{where:.02},A5:{where:.05}}},
 {id:'renew',name:'Open enrollment and renewal window',dims:'WHEN',inc:{A3:{when:.025},A4:{when:.05},A6:{when:.04}}},
 {id:'buyer',name:'CFO replaces Owner as decision-maker',dims:'WHO',inc:{A1:{who:.05},A2:{who:.045},A6:{who:.045}}},
 {id:'rate',name:'Rate card changed outside the knowledge graph',dims:'WHAT · D_s',inc:{A4:{what:.05,ds:.006},A3:{what:.025,ds:.003}}},
 {id:'model',name:'Underlying model version changed',dims:'D_b',inc:{A1:{db:.004},A2:{db:.004},A3:{db:.004},A4:{db:.004},A5:{db:.004},A6:{db:.004}}},
 {id:'obj',name:'Objective drift: optimizing close rate',dims:'WHY',inc:{A2:{why:.025},A4:{why:.04},A6:{why:.05}}},
 {id:'hazard',name:'High-hazard prospect: roofing crews added',dims:'WHAT · WHERE',inc:{A3:{what:.05,where:.03}}}
];
const RANK={PASS:0,COMPLY:1,FREEZE:2,HALT:3};
const KEY='sacb-state-v2';
let S;
const clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
function rnd(){let a=S.rs=(S.rs+0x6D2B79F5)|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;}
function f2(x){return x.toFixed(2)} function f3(x){return x.toFixed(3)}

function fresh(){
  S={rs:20261020};
  const drift={},ag={};
  AGENTS.forEach(a=>{drift[a.id]={who:0,what:0,when:0,where:0,why:0,ds:0,db:0};ag[a.id]={k:.9,trips:0};});
  const nz={}; DECS.forEach(d=>nz[d.id]=DIMS.map(()=>rnd()*.02));
  const dropAt={}; PERSONAS.forEach(p=>dropAt[p.id]={});
  Object.assign(S,{tick:0,persona:'finance',sens:1,on:{},drift,ag,nz,dropAt,prevStat:{},prevV:{},queue:[],done:{approved:0,cond:0,rejected:0,escalated:0,recal:0},resolved:[],log:[],hist:[],sel:'D11',auto:true});
}
function evalDec(d,pid){
  const a=S.drift[d.ag],P=PM[pid],n=S.nz[d.id];
  const match={},miss={},wm={}; let dr=0;
  DIMS.forEach((k,i)=>{match[k]=clamp(.975-d.ex[i]*a[k]*.8-n[i],0,1);miss[k]=1-match[k];wm[k]=P.w[i]*miss[k]/5;dr+=wm[k];});
  const ds=.035+a.ds+.12*d.ex[1]*a.what+n[1]*.4;
  const db=.03+a.db+.07*d.ex[4]*a.why+n[4]*.4;
  const tau={s:.20-.10*d.wc,m:.15-.06*d.wc,r:(.16-.06*d.wc)*P.tau/S.sens};
  const guard=!!(d.g&&GUARDS[d.g].test(S));
  let v;
  if(guard) v='HALT';
  else if(ds>=1.5*tau.s||db>=1.5*tau.m||dr>=1.5*tau.r) v='FREEZE';
  else if(ds>tau.s||db>tau.m||dr>tau.r) v='COMPLY';
  else v='PASS';
  const phi=guard?.05:clamp(1-(.3*ds+.25*db+.3*dr),.05,.99);
  return {d,pid,match,miss,wm,ds,db,dr,tau,guard,v,phi};
}
function evalAll(){const E={};PERSONAS.forEach(p=>{E[p.id]={};DECS.forEach(d=>E[p.id][d.id]=evalDec(d,p.id));});return E;}
function agentStatus(aid,ev){
  const vs=DECS.filter(d=>d.ag===aid).map(d=>ev[d.id].v);
  const fr=vs.filter(v=>v==='FREEZE').length,co=vs.filter(v=>v==='COMPLY').length,ha=vs.includes('HALT');
  let st='ONLINE';
  if(ha||fr>=2||S.ag[aid].k<.5) st='DROPPED'; else if(fr===1||co>=2) st='RESTRICTED';
  const phi=DECS.filter(d=>d.ag===aid).reduce((p,d)=>p*ev[d.id].phi,1);
  return {st,phi};
}
function reason(e){
  if(e.guard) return 'Guardrail '+e.d.g+' breached · '+GUARDS[e.d.g].label;
  const r=[['D_s',e.ds,e.tau.s],['D_b',e.db,e.tau.m],['D_r',e.dr,e.tau.r]].sort((x,y)=>y[1]/y[2]-x[1]/x[2])[0];
  let s=r[0]+' '+f3(r[1])+' vs τ '+f3(r[2])+' ('+f2(r[1]/r[2])+'×)';
  if(r[0]==='D_r'){const k=DIMS.slice().sort((x,y)=>e.wm[y]-e.wm[x])[0];s+=' · '+DL[k]+' match '+f2(e.match[k])+' × weight '+PM[e.pid].w[DIMS.indexOf(k)].toFixed(1);}
  return s;
}
function addLog(cls,msg){S.log.unshift({t:S.tick,cls,msg});if(S.log.length>200)S.log.pop();}
function enqueue(e,why){
  if(S.queue.find(q=>q.did===e.d.id)) return;
  S.queue.unshift({qid:Math.random().toString(36).slice(2,8),did:e.d.id,v:e.v,pid:e.pid,t:S.tick,r:reason(e),why});
  if(S.queue.length>40) S.queue.pop();
}
function primePrev(){const E=evalAll();DECS.forEach(d=>S.prevV[d.id]=E[S.persona][d.id].v);}
function tick(){
  S.tick++;
  SCEN.forEach(sc=>{if(!S.on[sc.id])return;
    Object.entries(sc.inc).forEach(([aid,o])=>Object.entries(o).forEach(([k,v])=>{S.drift[aid][k]=Math.min(k==='ds'||k==='db'?.3:1,S.drift[aid][k]+v*(.7+.6*rnd()));}));});
  DECS.forEach(d=>{S.nz[d.id]=S.nz[d.id].map(x=>clamp(x+(rnd()-.5)*.012,0,.05));});
  const E=evalAll(), chain={};
  PERSONAS.forEach(p=>{let c=1;
    AGENTS.forEach(a=>{const st=agentStatus(a.id,E[p.id]);c*=st.phi;const key=p.id+a.id,prev=S.prevStat[key];
      if(st.st==='DROPPED'&&prev!=='DROPPED'){
        if(S.dropAt[p.id][a.id]==null) S.dropAt[p.id][a.id]=S.tick;
        if(p.id===S.persona) addLog('HALT','prov:Activity cb:CircuitOpen · '+a.id+' '+a.name+' dropped under '+PM[p.id].hr+' · decisions routed to human fallback');
      }
      S.prevStat[key]=st.st;});
    chain[p.id]=c;});
  DECS.forEach(d=>{const e=E[S.persona][d.id],prev=S.prevV[d.id]||'PASS';
    if(RANK[e.v]>RANK[prev]){
      if(e.v==='FREEZE'||e.v==='HALT'){
        S.ag[d.ag].trips++;
        if(e.v==='HALT') S.ag[d.ag].k=Math.max(0,S.ag[d.ag].k-.04);
        addLog(e.v,'cb:Evaluation '+d.id+' → '+e.v+' · '+PM[S.persona].hr+' · '+reason(e));
        enqueue(e,'trip');
      } else if(S.auto&&rnd()<.45) enqueue(e,'sample');
    }
    S.prevV[d.id]=e.v;});
  S.hist.push({t:S.tick,chain,persona:S.persona});
  if(S.hist.length>120) S.hist.shift();
}
function loadSample(){
  fresh();
  S.on.expand=true;S.on.renew=true;primePrev();
  for(let i=0;i<14;i++) tick();
  S.on.obj=true;
  for(let i=0;i<4;i++) tick();
  addLog('HUMAN','Sample session loaded · conditions: worksite expansion, renewal window, then objective drift from t+15');
}
function dispose(qid,action){
  const q=S.queue.find(x=>x.qid===qid); if(!q) return;
  const d=DM[q.did],A=S.ag[d.ag],dr=S.drift[d.ag];
  const who='prov:wasAttributedTo :salesAdvisorTrustee';
  let label='';
  if(action==='approve'){ if(q.v==='HALT') return;
    if(q.v==='FREEZE') A.k=Math.max(0,A.k-.02);
    S.done.approved++; label='Approved'; addLog('HUMAN',who+' · Approved '+d.id+' ('+q.v+')'+(q.v==='FREEZE'?' · override recorded, K −0.02':''));
  } else if(action==='cond'){ if(q.v==='HALT') return;
    S.done.cond++; label='Approved with conditions'; addLog('HUMAN',who+' · Approved '+d.id+' with conditions · reviewer edits attached to proposal');
  } else if(action==='reject'){
    A.k=Math.max(0,A.k-.05);
    const ks=DIMS.slice().sort((x,y)=>(d.ex[DIMS.indexOf(y)]*dr[y])-(d.ex[DIMS.indexOf(x)]*dr[x]));
    dr[ks[0]]*=.6;dr.ds*=.8;dr.db*=.8;S.nz[d.id]=S.nz[d.id].map(()=>0);
    S.done.rejected++; label='Rejected & corrected'; addLog('HUMAN',who+' · Rejected & corrected '+d.id+' · correction passed SHACL gate, '+DL[ks[0]]+' drift on '+d.ag+' reduced 40% · K −0.05');
  } else if(action==='escalate'){
    S.done.escalated++; label='Escalated'; addLog('HUMAN',who+' · Escalated '+d.id+' to Compliance counsel · decision held');
  } else if(action==='recal'){
    Object.keys(dr).forEach(k=>dr[k]*=.25); A.k=Math.min(.95,A.k+.05);
    PERSONAS.forEach(p=>{delete S.dropAt[p.id][d.ag];});
    const gone=S.queue.filter(x=>DM[x.did].ag===d.ag);
    gone.forEach(x=>S.resolved.unshift({...x,disp:'Superseded by recalibration',at:S.tick}));
    S.queue=S.queue.filter(x=>DM[x.did].ag!==d.ag);
    S.done.recal++; addLog('HUMAN',who+' · Recalibrated '+d.ag+' '+AM[d.ag].name+' against Layer-1 reference standards · drift ×0.25 · K +0.05 · '+gone.length+' queued item(s) superseded');
    S.resolved=S.resolved.slice(0,40); primePrev(); save(); return;
  }
  S.resolved.unshift({...q,disp:label,at:S.tick}); S.resolved=S.resolved.slice(0,40);
  S.queue=S.queue.filter(x=>x.qid!==qid);
  primePrev(); save();
}
function save(){try{localStorage.setItem(KEY,JSON.stringify(S));}catch(e){}}
function load(){try{const j=localStorage.getItem(KEY);if(j){const o=JSON.parse(j);if(o&&o.drift&&o.hist){S=o;return true;}}}catch(e){}return false;}
function init(){ if(!load()){loadSample();save();} }
function reset(){ loadSample(); save(); }

window.CB={DIMS,DL,PERSONAS,PM,AGENTS,AM,OUT,DECS,DM,GUARDS,SCEN,RANK,KEY,
  get S(){return S;},init,reset,load,save,tick,evalAll,evalDec,agentStatus,reason,enqueue,addLog,primePrev,dispose,clamp,f2,f3};
})();
