/* Shared helpers for the vocabulary, taxonomy and ontology explorer pages. */
(function(){
const D = window.EXPLORER_DATA;
const NODES = Object.fromEntries(D.lineage.nodes.map(n=>[n.id,n]));
const TIERS = Object.fromEntries(D.lineage.tiers.map(t=>[t.id,t]));
const ONT = D.ontologies, VOC = D.vocab;

const esc = s => String(s==null?"":s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const localName = iri => { const s=String(iri).replace(/[\/#]+$/,""); return s.split(/[\/#]/).pop(); };
const keyOf = iri => localName(iri).replace(/[^A-Za-z0-9._-]+/g,"_").replace(/^_+|_+$/g,"") || "x";
const tierOf = id => (NODES[id]||{}).tier || (id.startsWith("v-")?"vocab":id.startsWith("tax-")?"tax":"core");
const colorOf = id => `var(${(TIERS[tierOf(id)]||TIERS.core).color})`;
const label = id => {
  if(NODES[id]) return NODES[id].label;
  return id;
};

/* ---------- which views exist for a lineage node ---------- */
const ALIAS = {svc:"v-svc", dqm:"v-svc"};
const VOCAB_OF_ONT = D.vocabOf || {asset:"v-asset", req:"v-requirements", cap:"v-capability", event:"v-event", domain:"v-domain"};
const ONT_OF_VOCAB = D.ontOfVocab || Object.fromEntries(Object.entries(VOCAB_OF_ONT).map(([a,b])=>[b,a]));
function vocabFor(id){
  if(VOC[id]) return id;
  if(id.startsWith("tax-")){
    const v = id==="tax-services-technicalservices" ? "v-technicalservices" : "v-"+id.slice(4);
    return VOC[v]?v:null;
  }
  return VOCAB_OF_ONT[id] || null;
}
function hasClasses(o){ return o && Object.values(o.classes).some(c=>c.local||c.anchored); }
function treeFor(id){
  id = ALIAS[id]||id;
  if(VOC[id]){ const t = ontFor(id); return t && t.startsWith("tax-") ? t : id; }
  if(id.startsWith("tax-")) return vocabFor(id)?id:null;
  const o = ONT[id];
  if(!o) return null;
  if(hasClasses(o) || o.individuals.length || Object.values(o.props).some(p=>p.parents.length)) return id;
  return null;
}
function ontFor(id){
  id = ALIAS[id]||id;
  if(ONT[id]) return id;
  if(id.startsWith("tax-")) return id;
  if(ONT_OF_VOCAB[id]) return ONT_OF_VOCAB[id];
  if(id.startsWith("v-")){
    const t = id==="v-technicalservices" ? "tax-services-technicalservices" : "tax-"+id.slice(2);
    if(NODES[t]) return t;
  }
  return null;
}
function viewsFor(id){ return {vocabulary:vocabFor(ALIAS[id]||id), taxonomy:treeFor(id), ontology:ontFor(id)}; }
function primaryView(id){
  const t = tierOf(id);
  const v = viewsFor(id);
  if(t==="vocab" && v.vocabulary) return ["vocabulary", v.vocabulary];
  if(t==="tax") return ["taxonomy", v.taxonomy||id];
  return ["ontology", v.ontology];
}
const href = (page,id,key) => `${page}.html#${id}${key?"~"+key:""}`;
function parseHash(){
  const h = decodeURIComponent(location.hash.replace(/^#/,""));
  const i = h.indexOf("~");
  return i<0 ? {id:h, key:null} : {id:h.slice(0,i), key:h.slice(i+1)};
}

/* ---------- class / concept lookups across modules ---------- */
const classIndex = {};
for(const [mid,o] of Object.entries(ONT)) for(const [iri,c] of Object.entries(o.classes)){
  if(c.local) (classIndex[iri] ||= {mid, c});
}
for(const [mid,o] of Object.entries(ONT)) for(const [iri,c] of Object.entries(o.classes)) if(!classIndex[iri]) classIndex[iri] = {mid:c.owner||mid, c, ext:true};
const taxClass = {};
for(const [tid,refs] of Object.entries(D.taxref)) for(const [iri,e] of Object.entries(refs)) taxClass[iri] = {tid, e};

function classHref(iri){
  const tc = taxClass[iri];
  if(tc && tc.e.concept) return href("taxonomy", tc.tid, tc.e.concept);
  const ci = classIndex[iri];
  if(ci && ONT[ci.mid] && ONT[ci.mid].classes[iri] && (ONT[ci.mid].classes[iri].local)) return href("ontology", ci.mid, keyOf(iri));
  const own = ci && ci.c.owner;
  if(own && own.startsWith("tax-")) return href("ontology", own, keyOf(iri));
  if(own && ONT[own]) return href("ontology", own, keyOf(iri));
  return null;
}
function classLabel(iri){
  const ci = classIndex[iri]; if(ci) return ci.c.label;
  for(const v of Object.values(VOC)) if(iri.startsWith(v.ns)){ const k=iri.slice(v.ns.length); const c=v.concepts.find(x=>x[0]===k); if(c) return c[1]; }
  return localName(iri).replace(/_/g," ").replace(/([a-z0-9])([A-Z])/g,"$1 $2");
}
function ownerOfIri(iri){
  const ci = classIndex[iri]; if(ci) return ci.c.local?ci.mid:(ci.c.owner||null);
  if(taxClass[iri]) return taxClass[iri].tid;
  return null;
}
const conceptMap = {};
for(const [vid,v] of Object.entries(VOC)){ const m = conceptMap[vid] = {}; for(const c of v.concepts) m[c[0]] = c; }
function concept(vid,key){ return (conceptMap[vid]||{})[key]; }
function conceptIriOwner(iri){
  for(const v of Object.values(VOC)) if(iri.startsWith(v.ns)) return [v.id, iri.slice(v.ns.length)];
  return null;
}
const propIndex = {};
for(const [mid,o] of Object.entries(ONT)) for(const [iri,p] of Object.entries(o.props)) (propIndex[iri] ||= {mid,p});
function propLabel(iri){ const p=propIndex[iri]; return p?p.p.label:localName(iri); }

/* ---------- chrome ---------- */
const PAGE_NAMES = {vocabulary:"Vocabulary", taxonomy:"Hierarchy", ontology:"Ontology", graph:"Graph"};
function allowed(page){
  const ids = D.lineage.nodes.map(n=>n.id);
  const pick = page==="vocabulary" ? vocabFor : page==="taxonomy" ? treeFor : ontFor;
  const seen = new Set(), out = [];
  for(const id of ids){ const t = pick(id); if(t && !seen.has(t)){ seen.add(t); out.push(t); } }
  return out;
}
function topbar(page, id){
  const bar = document.getElementById("topbar");
  const opts = allowed(page);
  const groups = {};
  for(const o of opts){ (groups[tierOf(o)] ||= []).push(o); }
  const sel = Object.entries(groups).map(([t,list])=>`<optgroup label="${esc(TIERS[t].name)}">${list.map(o=>`<option value="${o}"${o===id?" selected":""}>${esc(label(o))}</option>`).join("")}</optgroup>`).join("");
  const v = viewsFor(id);
  const pills = ["vocabulary","taxonomy","ontology"].map(p=>{
    const tgt = v[p];
    if(p===page) return `<span class="on" aria-current="page">${PAGE_NAMES[p]}</span>`;
    return tgt ? `<a href="${href(p,tgt)}">${PAGE_NAMES[p]}</a>` : `<span class="off" title="No ${PAGE_NAMES[p].toLowerCase()} view for this module">${PAGE_NAMES[p]}</span>`;
  }).join("") + `<a href="graph.html#${id}">Graph</a>`;
  bar.innerHTML = `<div class="topbar-in">
    <nav class="crumb" aria-label="Breadcrumb"><a href="index.html"><svg width="14" height="14" viewBox="0 0 14 14" aria-hidden="true"><path d="M9 2 4 7l5 5" fill="none" stroke="currentColor" stroke-width="1.6"/></svg>Lineage map</a><span class="sep">/</span><b>${PAGE_NAMES[page]}</b></nav>
    <div class="picker"><label for="modpick">Module</label><select id="modpick">${sel}</select></div>
    <nav class="views" aria-label="Views of this module">${pills}</nav></div>`;
  document.getElementById("modpick").onchange = e => { location.hash = e.target.value; };
}
function boot(page, render){
  const go = () => {
    let {id,key} = parseHash();
    const ok = allowed(page);
    if(!ok.includes(id)){
      const alt = id && ({vocabulary:vocabFor,taxonomy:treeFor,ontology:ontFor}[page])(id);
      id = alt && ok.includes(alt) ? alt : ok[0];
    }
    topbar(page, id);
    render(id, key);
  };
  addEventListener("hashchange", go);
  go();
}
function setKey(id,key){
  const h = "#"+id+(key?"~"+key:"");
  if(location.hash!==h) history.replaceState(null,"",h);
}

window.X = {D, NODES, TIERS, ONT, VOC, esc, localName, keyOf, tierOf, colorOf, label, vocabFor, treeFor, ontFor, viewsFor, primaryView,
  href, parseHash, classIndex, taxClass, classHref, classLabel, ownerOfIri, concept, conceptIriOwner, propIndex, propLabel, boot, setKey, ALIAS};
})();
