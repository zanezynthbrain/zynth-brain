import React, { useRef, useEffect, useState, useCallback } from "react";
import { Brain, Activity, Rocket, FileText, Box, FolderOpen, X, Layers, RotateCcw, Star, ChevronRight, ExternalLink, Circle } from "lucide-react";

// ============================================================================
// ZYNTH COMMAND — one connected, vault-linked command dashboard
// Page 1: SECOND BRAIN SPHERE (live from repo) · then Ongoing / To-Execute /
// Proposals / 3D Studio / Outputs. Proposals open as FULLY COMPOSED documents.
// ============================================================================

const C={ bg:"#050708",panel:"#0a1013",teal:"#22D3EE",violet:"#A78BFA",blue:"#60A5FA",gold:"#D4AF37",tealSoft:"#2DD4BF",text:"#EAF0F2",dim:"#8A97A0" };
const hx=(c,a)=>{const n=Math.round(a*255).toString(16).padStart(2,"0");return c+n;};

// ---------- REAL inventory (github.com/zanezynthbrain/zynth-brain) ----------
const HUBS=[{id:"creative",label:"CREATIVE STUDIO"},{id:"events",label:"EVENTS & EXPERIENTIAL"},{id:"growth",label:"GROWTH & MEDIA"},{id:"bd",label:"BUSINESS DEV"},{id:"ops",label:"FINANCE & OPS"},{id:"research",label:"RESEARCH & KNOWLEDGE"},{id:"outputs",label:"OUTPUTS & PROPOSALS"}];
const AGENTS={brand_strategist:"creative",copywriter:"creative",content_creator:"creative",design_director:"creative",designer:"creative",motion_designer:"creative",myanmar_copy_chief:"creative",portfolio:"creative",video_master:"creative",event_concept:"events",event_designer:"events",event_manager:"events",event_ops:"events",paid_ads:"growth",research_seo:"growth",lead_gen:"bd",master_proposal:"bd",proposal_factory:"bd",ceo:"ops",coo:"ops",cfo:"ops",hr:"ops",operations:"ops",market_researcher:"research"};
const SKILLS={"zynth-3d-design-studio":"creative","zynth-3d-production":"creative","zynth-commercial-video-studio":"creative","zynth-creative-video-director":"creative","zynth-video-producer":"creative","zynth-art-director":"creative","zynth-creative-director":"creative","zynth-content-strategist":"creative","zynth-copywriter":"creative","zynth-brand-strategist":"creative","zynth-social-media-manager":"creative","zynth-master-event-planner":"events","zynth-event-manager":"events","zynth-sponsorship-value":"events","zynth-paid-media-specialist":"growth","zynth-seo-specialist":"growth","zynth-analytics-specialist":"growth","zynth-campaign-planner":"growth","zynth-master-campaign-planner":"growth","zynth-campaign-requirements":"growth","zb-icp":"bd","zb-objections":"bd","zb-offer":"bd","zb-pitch-kit":"bd","zynth-bd-researcher":"bd","zynth-bd-pitch-prep":"bd","zynth-account-manager":"bd","zynth-competitor-analyst":"bd","zynth-market-researcher":"bd","zynth-vendor-finder":"bd","zynth-pitch-packager":"bd","zynth-master-proposal-writer":"bd","yadana-finance":"ops","zynth-project-manager":"ops","graphify":"ops","zynth-tactical-prompts":"ops"};
const PROPOSALS=[
  {t:"Shwe-Pay · The New Gold Standard",sector:"Fintech",market:"MM",type:"Integrated Launch"},
  {t:"Dry-Fry · Hear The Crunch",sector:"F&B",market:"MM",type:"Product Launch"},
  {t:"The Drive · Luxury Auto Experience",sector:"Automotive",market:"MM",type:"Experiential"},
  {t:"Season of Belonging · Mall Festival",sector:"Retail",market:"MM",type:"Event"},
  {t:"In Good Hands · Healthcare Trust",sector:"Healthcare",market:"MM",type:"Brand Series"},
  {t:"Data That Moves You · Telecom",sector:"Telecom",market:"MM",type:"Youth Campaign"},
  {t:"Find Where You Belong · Property",sector:"Real Estate",market:"MM",type:"Launch"},
  {t:"Pour Culture · Beverage Activation",sector:"F&B",market:"MM",type:"Brand Activation"},
  {t:"Stay a While · Hospitality",sector:"Hospitality",market:"SG",type:"Lifestyle Campaign"},
  {t:"The New Menu Drop · F&B Social",sector:"F&B",market:"SG",type:"Social Sprint"},
  {t:"The Next Tier · Premium Fintech",sector:"Fintech",market:"SG",type:"Launch"},
  {t:"Your Future Enrolled · Education",sector:"Education",market:"MM",type:"Funnel"},
];
const DELIVERABLES=[
  {t:"IGNITE 2026 Financial Model",by:"cfo",kind:"Finance"},{t:"IGNITE 2026 Sponsor Prospectus",by:"master_proposal",kind:"Proposal"},
  {t:"Shwe-Pay Launch Build v1",by:"proposal_factory",kind:"Proposal"},{t:"Dry-Fry Launch Build v1",by:"proposal_factory",kind:"Proposal"},
  {t:"Out of Chaos · Commercial",by:"video_master",kind:"Film"},{t:"KitKat · The Break-Line (spec film)",by:"video_master",kind:"Film"},{t:"Connections Map",by:"operations",kind:"Ops"},
];
const STAGE=[
  {t:"The Living Forum",market:"MM",type:"Corporate"},{t:"The Luminous Spine",market:"MM",type:"Exhibition"},{t:"Clear Care Forum",market:"MM",type:"Healthcare"},{t:"Monsoon Arrival",market:"MM",type:"Hospitality"},
  {t:"The Reveal Spine",market:"MM",type:"Product Launch"},{t:"City Pulse Pavilion",market:"MM",type:"Public"},{t:"The Layered Forum",market:"SG",type:"Corporate"},{t:"Proof to Pipeline Lab",market:"SG",type:"Exhibition"},
];
const PROSPECTS=[
  ["KBZ Bank","Banking & Fintech",5],["AYA Bank","Banking & Fintech",5],["CB Bank","Banking & Fintech",5],["Yoma Bank","Banking & Fintech",5],
  ["Wave Money / WavePay","Fintech",5],["Ooredoo Myanmar","Telecom",5],["ATOM Myanmar","Telecom",5],["MPT","Telecom",5],
  ["Capital Diamond Star (CDSG)","FMCG",5],["City Mart Holding","Retail",5],["Loi Hein","FMCG",5],["Myanmar Brewery","FMCG",5],
  ["Shwe Taung Group","Real Estate",5],["Yoma Land","Real Estate",5],["Pun Hlaing Siloam","Healthcare",5],["Super Seven Stars","Automotive",5],["UAB Bank","Banking & Fintech",4],
];
// fully composed proposal (real, from vault) — the reader demonstrates FINAL, not draft
const COMPOSED={
  "Shwe-Pay · The New Gold Standard":{
    sub:"Banking & Finance / Fintech (digital wallet) · Myanmar (Yangon) · Integrated launch — campaign + flagship event",
    idea:"In a market of wallets that belong to the banks, Shwe Pay becomes the one that belongs to *you* — money that moves as fast as your ambition. \u201CThe New Gold Standard\u201D (Shwe = gold), carried from positioning → creative → the Launch Night → the KPI line.",
    deliverables:["Hero brand film \u201CThe New Gold Standard\u201D","#MyGoldStandard UGC challenge","\u201CLaunch Night\u201D flagship event (150–200 + creators)","Gold Moves reels · 6 KOLs incl. 1 top-tier","OOH (Yangon) · university/mall roadshow · 8-week paid"],
    kpis:["120k–180k installs","45–55% first-transaction activation","CPA ≤ MMK 650","2,000–3,500 merchants"],
    tiers:[["Essential","48M MMK",false],["Signature","98M MMK",true],["Flagship","168M MMK",false]],
    edge:"One idea carried the whole way through; competes on meaning, not a cashback war scale would win. 50% deposit · market FX.",
  },
};

// ============================ APP ==========================================
export default function ZynthCommand(){
  const [tab,setTab]=useState("brain");
  const [reader,setReader]=useState(null);
  const NAV=[["brain","Second Brain",<Brain size={16}/>],["ongoing","Ongoing",<Activity size={16}/>],["execute","To Execute",<Rocket size={16}/>],["proposals","Proposals",<FileText size={16}/>],["studio","3D Studio",<Box size={16}/>],["outputs","Outputs",<FolderOpen size={16}/>]];
  return (
    <div className="w-full h-screen flex overflow-hidden" style={{background:C.bg,fontFamily:"ui-sans-serif,system-ui"}}>
      {/* sidebar */}
      <div className="w-56 shrink-0 flex flex-col border-r" style={{borderColor:"#111b1f",background:hx(C.panel,0.6)}}>
        <div className="px-5 py-5">
          <div className="flex items-center gap-2"><div className="w-5 h-5 rotate-45 border-2" style={{borderColor:C.teal,boxShadow:`0 0 12px ${C.teal}`}}/><span className="tracking-[0.3em] text-xs font-semibold" style={{color:C.text}}>ZYNTH</span></div>
          <div className="text-[8px] tracking-[0.25em] mt-1" style={{color:C.dim}}>COMMAND · THE INTELLIGENCE OF CREATIVITY</div>
        </div>
        <nav className="flex-1 px-3 space-y-1">
          {NAV.map(([id,label,icon])=>(
            <button key={id} onClick={()=>setTab(id)} className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors"
              style={{background:tab===id?hx(C.teal,0.1):"transparent",color:tab===id?C.teal:C.dim,border:`1px solid ${tab===id?hx(C.teal,0.25):"transparent"}`}}>
              {icon}<span className="tracking-wide">{label}</span>
            </button>))}
        </nav>
        <div className="px-5 py-4 text-[9px] leading-relaxed" style={{color:hx(C.dim,0.6)}}>
          <div className="flex items-center gap-1.5 mb-1"><Circle size={7} fill={C.tealSoft} color={C.tealSoft}/> vault linked</div>
          github.com/zanezynthbrain<br/>/zynth-brain
        </div>
      </div>

      {/* content */}
      <div className="flex-1 relative overflow-hidden">
        {tab==="brain" && <BrainSphere/>}
        {tab!=="brain" && (
          <div className="absolute inset-0 overflow-y-auto px-8 py-7" style={{background:`radial-gradient(1000px 500px at 60% -10%, #0a1216, ${C.bg})`}}>
            {tab==="ongoing" && <Ongoing/>}
            {tab==="execute" && <ToExecute/>}
            {tab==="proposals" && <Proposals open={setReader}/>}
            {tab==="studio" && <Studio/>}
            {tab==="outputs" && <Outputs open={setReader}/>}
          </div>
        )}
      </div>

      {reader && <Reader item={reader} close={()=>setReader(null)}/>}
    </div>
  );
}

// ---------- helpers ----------
const Head=({t,s})=>(<div className="mb-6"><h1 className="text-xl font-light tracking-wide" style={{color:C.text}}>{t}</h1><p className="text-xs mt-1" style={{color:C.dim}}>{s}</p></div>);
const Stars=({n})=>(<span className="inline-flex">{Array.from({length:5},(_,i)=><Star key={i} size={10} fill={i<n?C.gold:"none"} color={i<n?C.gold:"#2a3a40"}/>)}</span>);
const Chip=({children,c=C.teal})=><span className="text-[9px] tracking-wider px-2 py-0.5 rounded" style={{background:hx(c,0.12),color:c}}>{children}</span>;

// ---------- ONGOING ----------
function Ongoing(){
  return (<div className="max-w-5xl">
    <Head t="Ongoing" s="Live projects and the always-on workforce."/>
    <div className="rounded-2xl p-6 mb-5" style={{background:hx(C.panel,0.7),border:`1px solid ${hx(C.gold,0.25)}`}}>
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-2 mb-1"><h2 className="text-lg" style={{color:C.text}}>IGNITE Myanmar Business Summit 2026</h2><Chip c={C.gold}>OWNED IP</Chip><Chip c={C.gold}>PROPOSAL</Chip></div>
          <p className="text-xs" style={{color:C.dim}}>ZYNTH flagship · Yangon · 14 Nov 2026 · 300 delegates</p>
        </div>
        <div className="text-right"><div className="text-lg" style={{color:C.tealSoft}}>198M MMK</div><div className="text-[10px]" style={{color:C.dim}}>inventory</div></div>
      </div>
      <p className="text-xs mt-3 leading-relaxed" style={{color:"#9fb0b6"}}>Sponsorship-funded. Lean build clears the 35% margin floor at 43% sell-through. Financial model + sponsor prospectus already produced.</p>
      <div className="mt-4 h-1.5 rounded" style={{background:"#121a1e"}}><div className="h-1.5 rounded" style={{width:"55%",background:C.gold,boxShadow:`0 0 8px ${C.gold}`}}/></div>
    </div>
    <div className="grid grid-cols-2 gap-4">
      <div className="rounded-xl p-5" style={{background:hx(C.panel,0.6),border:"1px solid #14201f"}}>
        <div className="text-[10px] tracking-[0.2em] mb-3" style={{color:C.teal}}>ALWAYS-ON WORKFORCE (YANGON TIME)</div>
        {[["06:30","Market research sweep"],["07:00","FX refresh"],["08:00","Founder morning brief"],["18:00","End-of-day roll-up"],["21:00","Consolidation + learning"]].map(([t,d])=>(
          <div key={t} className="flex items-center gap-3 py-1.5 text-xs" style={{color:"#c9d3d8"}}><span className="w-12" style={{color:C.tealSoft}}>{t}</span>{d}</div>))}
      </div>
      <div className="rounded-xl p-5" style={{background:hx(C.panel,0.6),border:"1px solid #14201f"}}>
        <div className="text-[10px] tracking-[0.2em] mb-3" style={{color:C.teal}}>READY TO DEPLOY</div>
        {["Shwe-Pay launch — client-ready","Dry-Fry launch — client-ready","12 proposals in library","8 × 3D stage concepts rendered"].map((x,i)=>(
          <div key={i} className="flex items-center gap-2 py-1.5 text-xs" style={{color:"#c9d3d8"}}><ChevronRight size={12} color={C.tealSoft}/>{x}</div>))}
      </div>
    </div>
  </div>);
}

// ---------- TO EXECUTE ----------
function ToExecute(){
  return (<div className="max-w-5xl">
    <Head t="To Execute" s="The pipeline still to pursue — 52 prospects, 42 hot."/>
    <div className="grid grid-cols-4 gap-3 mb-6">
      {[["PROSPECTS",52,C.teal],["HOT (★★★★+)",42,C.gold],["SUPPLIERS",17,C.tealSoft],["VENUES",14,C.blue]].map(([l,v,c])=>(
        <div key={l} className="rounded-xl p-4" style={{background:hx(C.panel,0.7),border:`1px solid ${hx(c,0.2)}`}}><div className="text-[9px] tracking-[0.2em]" style={{color:C.dim}}>{l}</div><div className="text-3xl font-extralight mt-1" style={{color:c}}>{v}</div></div>))}
    </div>
    <div className="text-[10px] tracking-[0.2em] mb-3" style={{color:C.teal}}>HOT PROSPECTS — READY FOR OUTREACH</div>
    <div className="grid grid-cols-2 gap-2.5">
      {PROSPECTS.map(([name,sector,fit])=>(
        <div key={name} className="rounded-xl px-4 py-3 flex items-center justify-between group" style={{background:hx(C.panel,0.6),border:"1px solid #14201f"}}>
          <div><div className="text-sm" style={{color:C.text}}>{name}</div><div className="text-[10px]" style={{color:C.dim}}>{sector}</div></div>
          <div className="flex items-center gap-3"><Stars n={fit}/><span className="text-[9px] tracking-wider px-2 py-1 rounded" style={{background:hx(C.teal,0.1),color:C.teal}}>DRAFT PITCH</span></div>
        </div>))}
    </div>
  </div>);
}

// ---------- PROPOSALS ----------
function Proposals({open}){
  return (<div className="max-w-5xl">
    <Head t="Proposals & Suggestions" s="12 client-ready proposals. Tap to open the fully composed document."/>
    <div className="grid grid-cols-2 gap-3">
      {PROPOSALS.map(p=>(
        <button key={p.t} onClick={()=>open({...p,kind:"proposal"})} className="text-left rounded-xl p-5 transition-colors hover:border-current group" style={{background:hx(C.panel,0.6),border:`1px solid ${hx(C.gold,0.18)}`}}>
          <div className="flex items-start justify-between mb-2"><Star size={14} fill={C.gold} color={C.gold}/><ExternalLink size={13} color={C.dim}/></div>
          <div className="text-sm mb-2" style={{color:C.text}}>{p.t}</div>
          <div className="flex gap-1.5"><Chip c={C.gold}>{p.sector}</Chip><Chip>{p.market}</Chip><Chip c={C.dim}>{p.type}</Chip></div>
          {COMPOSED[p.t] && <div className="text-[9px] mt-3 tracking-wider" style={{color:C.tealSoft}}>● FULLY COMPOSED</div>}
        </button>))}
    </div>
  </div>);
}

// ---------- 3D STUDIO ----------
function Studio(){
  return (<div className="max-w-5xl">
    <Head t="3D Studio" s="8 rendered stage & exhibition concepts."/>
    <div className="grid grid-cols-4 gap-3">
      {STAGE.map((s,i)=>(
        <div key={s.t} className="rounded-xl overflow-hidden" style={{background:hx(C.panel,0.6),border:"1px solid #14201f"}}>
          <div className="h-24 relative" style={{background:`linear-gradient(135deg, ${hx(C.teal,0.25)}, ${hx(C.violet,0.15)} 60%, ${hx(C.gold,0.2)})`}}>
            <div className="absolute inset-0" style={{background:`radial-gradient(60px 40px at ${30+i*8}% 60%, ${hx(C.teal,0.5)}, transparent)`}}/>
            <Box size={20} color={hx(C.text,0.5)} className="absolute bottom-2 right-2"/>
          </div>
          <div className="p-3"><div className="text-xs" style={{color:C.text}}>{s.t}</div><div className="flex gap-1.5 mt-1.5"><Chip>{s.market}</Chip><Chip c={C.dim}>{s.type}</Chip></div></div>
        </div>))}
    </div>
    <p className="text-[10px] mt-4" style={{color:hx(C.dim,0.6)}}>Live build loads each concept's rendered hero previews from outputs/3d_stage_exhibition_library/.</p>
  </div>);
}

// ---------- OUTPUTS ----------
function Outputs({open}){
  const all=[...DELIVERABLES.map(d=>({...d,cat:"Deliverable"})),...PROPOSALS.map(p=>({t:p.t,kind:"proposal",cat:"Proposal"})),...STAGE.map(s=>({t:s.t,kind:"3D",cat:"3D Stage"}))];
  const col=c=>c==="Deliverable"?C.tealSoft:c==="Proposal"?C.gold:C.violet;
  return (<div className="max-w-5xl">
    <Head t="All Outputs" s={`Everything ZYNTH has produced — ${all.length} finished pieces, final composed versions.`}/>
    <div className="rounded-xl overflow-hidden" style={{background:hx(C.panel,0.6),border:"1px solid #14201f"}}>
      {all.map((o,i)=>(
        <button key={i} onClick={()=>open(o)} className="w-full flex items-center gap-3 px-5 py-3 text-left" style={{borderTop:i?"1px solid #101a1e":"none"}}>
          <FileText size={14} color={col(o.cat)}/>
          <span className="flex-1 text-sm" style={{color:"#c9d3d8"}}>{o.t}</span>
          <Chip c={col(o.cat)}>{o.cat}</Chip>
          <ChevronRight size={14} color={C.dim}/>
        </button>))}
    </div>
  </div>);
}

// ---------- READER (fully composed) ----------
function Reader({item,close}){
  const d=COMPOSED[item.t];
  return (
    <div className="absolute inset-0 z-40 flex justify-center" style={{background:"rgba(3,5,6,0.7)",backdropFilter:"blur(6px)"}} onClick={close}>
      <div className="w-full max-w-2xl h-full overflow-y-auto" style={{background:C.bg,borderLeft:"1px solid #14201f",borderRight:"1px solid #14201f"}} onClick={e=>e.stopPropagation()}>
        <div className="sticky top-0 flex items-center justify-between px-8 py-4" style={{background:hx(C.bg,0.9),borderBottom:"1px solid #14201f",backdropFilter:"blur(8px)"}}>
          <span className="text-[10px] tracking-[0.25em]" style={{color:C.gold}}>{d?"FULLY COMPOSED · CLIENT-READY":"COMPOSED DOCUMENT"}</span>
          <button onClick={close} style={{color:C.text}}><X size={18}/></button>
        </div>
        <div className="px-8 py-8">
          <h1 className="text-2xl font-light mb-2" style={{color:C.text}}>{item.t}</h1>
          {d?(<>
            <p className="text-xs mb-8" style={{color:C.dim}}>{d.sub}</p>
            <Block label="THE BIG IDEA"><p className="text-sm leading-relaxed" style={{color:"#c9d3d8"}}>{d.idea}</p></Block>
            <Block label="KEY DELIVERABLES"><ul className="space-y-1.5">{d.deliverables.map((x,i)=><li key={i} className="text-sm flex gap-2" style={{color:"#c9d3d8"}}><span style={{color:C.gold}}>◆</span>{x}</li>)}</ul></Block>
            <Block label="KPIs"><div className="flex flex-wrap gap-2">{d.kpis.map((k,i)=><span key={i} className="text-xs px-3 py-1.5 rounded" style={{background:hx(C.teal,0.08),color:C.tealSoft,border:`1px solid ${hx(C.teal,0.2)}`}}>{k}</span>)}</div></Block>
            <Block label="INVESTMENT — 3 TIERS"><div className="grid grid-cols-3 gap-3">{d.tiers.map(([n,v,rec])=>(
              <div key={n} className="rounded-xl p-4 text-center" style={{background:rec?hx(C.gold,0.1):hx(C.panel,0.7),border:`1px solid ${rec?C.gold:"#14201f"}`}}>
                <div className="text-[10px] tracking-wider" style={{color:rec?C.gold:C.dim}}>{n}{rec?" ★":""}</div><div className="text-lg mt-1" style={{color:C.text}}>{v}</div></div>))}</div></Block>
            <Block label="THE ZYNTH EDGE"><p className="text-sm leading-relaxed" style={{color:"#c9d3d8"}}>{d.edge}</p></Block>
          </>):(
            <div className="mt-6 rounded-xl p-6 text-sm leading-relaxed" style={{background:hx(C.panel,0.6),border:"1px solid #14201f",color:"#9fb0b6"}}>
              This piece is stored in your Obsidian vault. In the live build the reader loads the full composed document straight from <span style={{color:C.tealSoft}}>vault/ZYNTH-OS/</span> — final version, formatted, client-ready.
            </div>)}
          <div className="mt-8 pt-6 flex gap-3" style={{borderTop:"1px solid #14201f"}}>
            <button className="flex-1 py-2.5 rounded-lg text-xs tracking-wider" style={{background:C.gold,color:"#0A0A0A"}}>EXPORT PDF</button>
            <button className="flex-1 py-2.5 rounded-lg text-xs tracking-wider border" style={{borderColor:"#2a3a40",color:C.dim}}>OPEN IN VAULT</button>
          </div>
        </div>
      </div>
    </div>);
}
const Block=({label,children})=>(<div className="mb-7"><div className="text-[10px] tracking-[0.22em] mb-3" style={{color:C.teal}}>{label}</div>{children}</div>);


// ============================ SPHERE (page 1) ==============================
// v2 — cinematic pass. Changes vs v1:
//   · true perspective projection (was orthographic — the main cause of "flat")
//   · nodes occupy a SHELL with thickness, not a single surface (volume, not decal)
//   · depth now reads on four agreeing channels: scale, alpha, fog, focus blur
//   · cached glow sprites + half-res bloom pass instead of ~95 gradients per frame
//   · deep-space plate: starfield, nebula, equator ring, vignette
//   · calm motion — 4x slower drift, and it RESUMES after you stop (v1 froze forever)
const TYPE={agent:{c:C.teal},skill:{c:C.violet},research:{c:C.blue},knowledge:{c:C.blue},project:{c:C.gold},proposal:{c:C.gold},deliverable:{c:C.gold},hub:{c:C.tealSoft}};
// shell radius per type — this is what turns a decal into a volume
const RAD={hub:1.0,agent:0.87,skill:0.79,proposal:0.95,deliverable:0.95,project:0.66,research:0.73,knowledge:0.73};
const FOV=2.7;                 // camera distance in sphere radii
const AUTO=0.00055;            // rad/frame drift — a full turn takes ~3 minutes
const IDLE_MS=3500;            // how long after your last touch the drift returns

function mulberry(a){return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};}
function fib(n){const p=[],ga=Math.PI*(3-Math.sqrt(5));for(let i=0;i<n;i++){const y=1-(i/(n-1))*2,r=Math.sqrt(1-y*y),th=ga*i;p.push([Math.cos(th)*r,y,Math.sin(th)*r]);}return p;}
const norm=v=>{const m=Math.hypot(...v)||1;return[v[0]/m,v[1]/m,v[2]/m];};
const clamp=(v,a,b)=>v<a?a:v>b?b:v;
function nearHub(dir,seed){const rnd=mulberry(seed);const ru=norm([rnd()*2-1,rnd()*2-1,rnd()*2-1]);const k=0.72;return norm([dir[0]*k+ru[0]*(1-k),dir[1]*k+ru[1]*(1-k),dir[2]*k+ru[2]*(1-k)]);}

function buildNodes(){
  const hubDirs={};fib(7).forEach((d,i)=>hubDirs[HUBS[i].id]=d);const nodes=[];let s=1;
  HUBS.forEach(h=>nodes.push({id:h.id,label:h.label,type:"hub",hub:h.id,v:hubDirs[h.id],r:RAD.hub}));
  const add=(id,label,type,hub,by)=>{
    s+=97;const rnd=mulberry(s*7+13);
    nodes.push({id,label,type,hub,by,v:nearHub(hubDirs[hub],s),r:(RAD[type]||0.85)*(0.90+rnd()*0.19)});
  };
  Object.entries(AGENTS).forEach(([n,h])=>add("ag:"+n,n.replace(/_/g," "),"agent",h));
  Object.entries(SKILLS).forEach(([n,h])=>add("sk:"+n,n.replace(/^zynth-/,"").replace(/-/g," "),"skill",h));
  PROPOSALS.forEach((p,i)=>add("pr:"+i,p.t,"proposal","outputs","master_proposal"));
  DELIVERABLES.forEach((d,i)=>add("dl:"+i,d.t,"deliverable","outputs",d.by));
  STAGE.forEach((st,i)=>add("st:"+i,"3D · "+st.t,"deliverable","outputs","event_designer"));
  add("pj:0","IGNITE 2026 Summit","project","outputs","event_manager");
  ["MM Agency Market","SG Agency Market","MM/SG Pricing","MM Pharma Campaign","MM Video Analysis","SG Video Analysis"].forEach((r,i)=>add("re:"+i,r,"research","research"));
  add("kn:0","17 Knowledge Docs","knowledge","research");
  return nodes;
}

// one glow sprite per colour, built once — replaces ~95 createRadialGradient calls a frame
function makeSprite(col){
  const s=96,o=document.createElement("canvas");o.width=o.height=s;const g=o.getContext("2d");
  const gr=g.createRadialGradient(s/2,s/2,0,s/2,s/2,s/2);
  gr.addColorStop(0,hx(col,0.60));gr.addColorStop(0.28,hx(col,0.20));gr.addColorStop(0.6,hx(col,0.05));gr.addColorStop(1,hx(col,0));
  g.fillStyle=gr;g.fillRect(0,0,s,s);return o;
}
// the deep-space plate: drawn once per resize, parallaxed a few pixels as you orbit
function makeSky(w,h){
  const o=document.createElement("canvas");o.width=w;o.height=h;const g=o.getContext("2d");
  g.fillStyle=C.bg;g.fillRect(0,0,w,h);
  const rnd=mulberry(20260816);
  [[0.30,0.32,C.teal,0.085],[0.72,0.24,C.violet,0.070],[0.55,0.78,C.blue,0.055],[0.18,0.72,C.tealSoft,0.045]].forEach(([fx,fy,col,a])=>{
    const x=w*fx,y=h*fy,r=Math.max(w,h)*(0.30+rnd()*0.22);
    const gr=g.createRadialGradient(x,y,0,x,y,r);gr.addColorStop(0,hx(col,a));gr.addColorStop(1,hx(col,0));
    g.fillStyle=gr;g.fillRect(0,0,w,h);
  });
  for(let i=0;i<460;i++){
    const x=rnd()*w,y=rnd()*h,m=rnd(),r=m>0.97?1.5:m>0.85?1.0:0.6,a=0.10+rnd()*0.45;
    g.fillStyle=hx(m>0.93?C.tealSoft:"#FFFFFF",a*(r>1?1:0.7));
    g.beginPath();g.arc(x,y,r,0,Math.PI*2);g.fill();
  }
  return o;
}

function BrainSphere(){
  const wrap=useRef(null),cv=useRef(null),nodesRef=useRef(null);
  if(!nodesRef.current)nodesRef.current=buildNodes();          // v1 rebuilt this on every render
  const nodes=nodesRef;
  const cam=useRef({yaw:0,pitch:-0.25,zoom:1}),tgt=useRef({yaw:0,pitch:-0.25,zoom:1});
  const drag=useRef({on:false,px:0,py:0,moved:0}),pinch=useRef(0);
  const lastInput=useRef(0),focus=useRef(0),size=useRef({w:0,h:0}),proj=useRef({});
  const sky=useRef(null),bloom=useRef(null),sprites=useRef({});
  const [sel,setSel]=useState(null),[lens,setLens]=useState("ALL");
  const lensRef=useRef("ALL");useEffect(()=>{lensRef.current=lens;},[lens]);
  const selRef=useRef(null);useEffect(()=>{selRef.current=sel;},[sel]);
  const reduce=typeof window!=="undefined"&&window.matchMedia&&window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const rot=(v,yaw,pitch)=>{const cy=Math.cos(yaw),sy=Math.sin(yaw);let x=v[0]*cy+v[2]*sy,z=-v[0]*sy+v[2]*cy,y=v[1];const cp=Math.cos(pitch),sp=Math.sin(pitch);return[x,y*cp-z*sp,y*sp+z*cp];};
  const lensOn=useCallback(t=>{const L=lensRef.current;if(L==="ALL")return true;if(L==="CAPABILITY")return t==="agent"||t==="skill"||t==="hub";if(L==="OPERATIONS")return t==="agent"||t==="project"||t==="hub";if(L==="OUTPUT LINEAGE")return t==="proposal"||t==="deliverable"||t==="project"||t==="agent"||t==="hub";return true;},[]);

  useEffect(()=>{
    const c=cv.current,ctx=c.getContext("2d");let raf;
    Object.values(TYPE).forEach(({c:col})=>{if(!sprites.current[col])sprites.current[col]=makeSprite(col);});
    let dpr=1;
    const resize=()=>{
      dpr=Math.min(window.devicePixelRatio||1,2);
      const w=wrap.current.clientWidth,h=wrap.current.clientHeight;
      size.current={w,h};c.width=w*dpr;c.height=h*dpr;c.style.width=w+"px";c.style.height=h+"px";
      ctx.setTransform(dpr,0,0,dpr,0,0);
      sky.current=makeSky(w,h);
      const b=document.createElement("canvas");b.width=Math.max(1,Math.round(c.width/2));b.height=Math.max(1,Math.round(c.height/2));bloom.current=b;
    };
    resize();window.addEventListener("resize",resize);

    const draw=t=>{
      const{w,h}=size.current,cm=cam.current,tg2=tgt.current;
      cm.yaw+=(tg2.yaw-cm.yaw)*0.085;cm.pitch+=(tg2.pitch-cm.pitch)*0.085;cm.zoom+=(tg2.zoom-cm.zoom)*0.085;
      // the drift comes BACK once you stop touching it — v1 stopped forever after one drag
      if(!reduce&&t-lastInput.current>IDLE_MS){const ramp=Math.min(1,(t-lastInput.current-IDLE_MS)/2500);tg2.yaw+=AUTO*ramp;}
      const se=selRef.current;
      focus.current+=((se?1:0)-focus.current)*0.09;
      const F=focus.current;

      const cx=w/2,cy=h/2,R=Math.min(w,h)*0.38*cm.zoom;

      // ---- plate: sky, parallaxed a few px so the void feels behind the sphere
      ctx.globalCompositeOperation="source-over";ctx.globalAlpha=1;
      ctx.fillStyle=C.bg;ctx.fillRect(0,0,w,h);
      if(sky.current){const px=-Math.sin(cm.yaw)*14,py=cm.pitch*18;ctx.drawImage(sky.current,px,py,w,h);}

      // ---- project: perspective divide is what makes it a sphere and not a disc
      const P={};
      nodes.current.forEach(n=>{
        const r=rot(n.v,cm.yaw,cm.pitch),rr=n.r,z=r[2]*rr,s=FOV/(FOV-z);
        P[n.id]={x:cx+r[0]*rr*R*s,y:cy+r[1]*rr*R*s,z,s};
      });
      proj.current=P;

      const depth=z=>clamp((z+1)/2,0,1);
      const neigh=new Set();
      if(se){neigh.add(se.id);nodes.current.forEach(n=>{if(n.hub===se.hub)neigh.add(n.id);});if(se.by)neigh.add("ag:"+se.by);if(se.type==="hub")nodes.current.forEach(n=>{if(n.hub===se.id)neigh.add(n.id);});}

      // ---- containment ring + equator: cheap, and it reads as an instrument
      ctx.globalCompositeOperation="lighter";
      ctx.strokeStyle=hx(C.teal,0.05);ctx.lineWidth=1;
      ctx.beginPath();ctx.arc(cx,cy,R*1.02,0,Math.PI*2);ctx.stroke();
      ctx.strokeStyle=hx(C.tealSoft,0.07);
      ctx.beginPath();ctx.ellipse(cx,cy,R,Math.abs(Math.sin(cm.pitch))*R,0,0,Math.PI*2);ctx.stroke();

      // ---- edges
      nodes.current.forEach(n=>{
        if(n.type==="hub")return;const a=P[n.hub],b=P[n.id];if(!a)return;
        const dim=se&&!neigh.has(n.id),d=depth(b.z);
        ctx.strokeStyle=hx(C.teal,(lensOn(n.type)?0.11:0.025)*(dim?0.22:1)*(0.15+d*0.85));
        ctx.lineWidth=0.5+d*0.5;
        ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);ctx.stroke();
      });
      HUBS.forEach(h=>{const b=P[h.id],d=depth(b.z);ctx.strokeStyle=hx(C.tealSoft,0.10*(0.2+d*0.8));ctx.lineWidth=0.8+d*0.7;ctx.beginPath();ctx.moveTo(cx,cy);ctx.lineTo(b.x,b.y);ctx.stroke();});
      if(lensRef.current==="OUTPUT LINEAGE"||(se&&(se.type==="deliverable"||se.type==="proposal"||se.type==="project"))){
        nodes.current.forEach(n=>{
          if(!n.by)return;const b=P[n.id],a=P["ag:"+n.by];if(!a)return;
          if(!(lensRef.current==="OUTPUT LINEAGE"||(se&&se.id===n.id)))return;
          ctx.strokeStyle=hx(C.gold,0.45*(0.25+depth(b.z)*0.75));ctx.lineWidth=1.1;
          ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);ctx.stroke();
        });
      }

      // ---- nodes, painted back to front
      [...nodes.current].sort((a,b)=>P[a.id].z-P[b.id].z).forEach(n=>{
        const p=P[n.id],col=TYPE[n.type].c,isHub=n.type==="hub";
        const off=(se&&!neigh.has(n.id))||!lensOn(n.type);
        const d=depth(p.z);
        const base=isHub?8.5:n.type==="agent"?5:4.2;
        const r=base*p.s*(cm.zoom*0.45+0.62);
        // four agreeing depth channels: perspective scale, alpha, fog, focus
        const al=(0.14+d*0.86)*(off?0.10+(1-F)*0.08:1);
        const sp=sprites.current[col];
        if(sp){const g=r*5;ctx.globalCompositeOperation="lighter";ctx.globalAlpha=al*(0.35+d*0.65);ctx.drawImage(sp,p.x-g,p.y-g,g*2,g*2);ctx.globalAlpha=1;}
        ctx.globalCompositeOperation="lighter";
        ctx.fillStyle=hx(col,al);ctx.strokeStyle=hx(col,al);
        if(n.type==="skill"){ctx.beginPath();for(let i=0;i<6;i++){const a=Math.PI/3*i-Math.PI/6,px=p.x+Math.cos(a)*r,py=p.y+Math.sin(a)*r;i?ctx.lineTo(px,py):ctx.moveTo(px,py);}ctx.closePath();ctx.fill();}
        else if(n.type==="proposal"||n.type==="deliverable"){ctx.beginPath();for(let i=0;i<10;i++){const a=Math.PI/5*i-Math.PI/2,rr=i%2?r*0.45:r*1.1,px=p.x+Math.cos(a)*rr,py=p.y+Math.sin(a)*rr;i?ctx.lineTo(px,py):ctx.moveTo(px,py);}ctx.closePath();ctx.fill();}
        else if(n.type==="project"){ctx.lineWidth=2;ctx.beginPath();ctx.arc(p.x,p.y,r,0,Math.PI*2);ctx.stroke();}
        else if(n.type==="research"||n.type==="knowledge"){ctx.fillRect(p.x-r,p.y-r,r*2,r*2);}
        else{ctx.beginPath();ctx.arc(p.x,p.y,r,0,Math.PI*2);ctx.fill();}
        if(isHub){ctx.lineWidth=1.2;ctx.strokeStyle=hx(col,al*0.7);ctx.beginPath();ctx.arc(p.x,p.y,r+5,0,Math.PI*2);ctx.stroke();}
        if(se&&se.id===n.id){
          ctx.globalCompositeOperation="source-over";
          const pulse=1+Math.sin(t*0.003)*0.06;
          ctx.strokeStyle=hx(C.text,0.85);ctx.lineWidth=1.2;
          ctx.beginPath();ctx.arc(p.x,p.y,(r+9)*pulse,0,Math.PI*2);ctx.stroke();
          ctx.strokeStyle=hx(col,0.35);ctx.lineWidth=3;
          ctx.beginPath();ctx.arc(p.x,p.y,(r+9)*pulse,0,Math.PI*2);ctx.stroke();
          ctx.globalCompositeOperation="lighter";
        }
      });

      // ---- core
      const cr=12*(cm.zoom*0.45+0.62);
      const cs=sprites.current[C.teal];
      if(cs){ctx.globalCompositeOperation="lighter";ctx.globalAlpha=0.9;ctx.drawImage(cs,cx-cr*5,cy-cr*5,cr*10,cr*10);ctx.globalAlpha=1;}
      ctx.globalCompositeOperation="source-over";
      ctx.fillStyle="#08222a";ctx.strokeStyle=hx(C.text,0.9);ctx.lineWidth=1.3;
      ctx.beginPath();for(let i=0;i<6;i++){const a=Math.PI/3*i-Math.PI/6+t*0.00012,px=cx+Math.cos(a)*cr,py=cy+Math.sin(a)*cr;i?ctx.lineTo(px,py):ctx.moveTo(px,py);}
      ctx.closePath();ctx.fill();ctx.stroke();

      // ---- bloom: half-res copy, blurred, added back. This is the "premium" channel.
      const b=bloom.current;
      if(b&&ctx.filter!==undefined){
        const bc=b.getContext("2d");
        bc.setTransform(1,0,0,1,0,0);bc.clearRect(0,0,b.width,b.height);
        bc.drawImage(c,0,0,b.width,b.height);
        ctx.save();ctx.setTransform(1,0,0,1,0,0);
        ctx.globalCompositeOperation="lighter";ctx.globalAlpha=0.34;ctx.filter="blur(7px)";
        ctx.drawImage(b,0,0,c.width,c.height);
        ctx.restore();
      }

      // ---- vignette + labels last, so type stays crisp above the bloom
      ctx.globalCompositeOperation="source-over";ctx.globalAlpha=1;
      const vg=ctx.createRadialGradient(cx,cy,Math.min(w,h)*0.28,cx,cy,Math.max(w,h)*0.78);
      vg.addColorStop(0,"rgba(0,0,0,0)");vg.addColorStop(1,"rgba(0,0,0,0.62)");
      ctx.fillStyle=vg;ctx.fillRect(0,0,w,h);

      ctx.textAlign="center";
      nodes.current.forEach(n=>{
        const p=P[n.id];if(p.z<-0.05)return;
        const isHub=n.type==="hub";
        if(!(isHub||(se&&neigh.has(n.id))||cm.zoom>1.8))return;
        const dim=se&&!neigh.has(n.id),d=depth(p.z);
        ctx.fillStyle=isHub?hx(C.tealSoft,0.35+d*0.55):hx(C.dim,dim?0.2:0.35+d*0.5);
        ctx.font=`${isHub?"600 10":"9"}px ui-sans-serif,system-ui`;
        ctx.fillText(n.label.length>24?n.label.slice(0,23)+"…":n.label,p.x,p.y-(isHub?14:10));
      });
      ctx.fillStyle=hx(C.text,0.9);ctx.font="600 11px ui-sans-serif,system-ui";ctx.fillText("CMO",cx,cy+cr+16);

      raf=requestAnimationFrame(draw);
    };
    raf=requestAnimationFrame(draw);
    return()=>{cancelAnimationFrame(raf);window.removeEventListener("resize",resize);};
  },[reduce,lensOn]);

  useEffect(()=>{
    const c=cv.current;
    const mark=()=>{lastInput.current=performance.now();};
    const xy=e=>{const r=c.getBoundingClientRect(),t=e.touches?e.touches[0]:e;return[t.clientX-r.left,t.clientY-r.top];};
    const hit=(sx,sy)=>{let best=null,bd=24;Object.entries(proj.current).forEach(([id,p])=>{if(p.z<-0.15)return;const d=Math.hypot(sx-p.x,sy-p.y);if(d<bd){bd=d;best=id;}});return best?nodes.current.find(n=>n.id===best):null;};
    const down=e=>{const[x,y]=xy(e);drag.current={on:true,px:x,py:y,moved:0};mark();if(e.touches&&e.touches.length===2)pinch.current=Math.hypot(e.touches[0].clientX-e.touches[1].clientX,e.touches[0].clientY-e.touches[1].clientY);};
    const move=e=>{
      if(e.touches&&e.touches.length===2){const d=Math.hypot(e.touches[0].clientX-e.touches[1].clientX,e.touches[0].clientY-e.touches[1].clientY);if(pinch.current)tgt.current.zoom=clamp(tgt.current.zoom*(d/pinch.current),0.6,3.2);pinch.current=d;mark();return;}
      if(!drag.current.on)return;
      const[x,y]=xy(e);const dx=x-drag.current.px,dy=y-drag.current.py;
      drag.current.moved+=Math.abs(dx)+Math.abs(dy);
      tgt.current.yaw+=dx*0.006;tgt.current.pitch=clamp(tgt.current.pitch+dy*0.006,-1.2,1.2);
      drag.current.px=x;drag.current.py=y;mark();
    };
    const up=e=>{if(drag.current.on&&drag.current.moved<6){const t=e.changedTouches?e.changedTouches[0]:e,r=c.getBoundingClientRect(),n=hit(t.clientX-r.left,t.clientY-r.top);setSel(n||null);}drag.current.on=false;pinch.current=0;mark();};
    const wheel=e=>{e.preventDefault();mark();tgt.current.zoom=clamp(tgt.current.zoom*Math.exp(-e.deltaY*0.0015),0.6,3.2);};
    c.addEventListener("mousedown",down);window.addEventListener("mousemove",move);window.addEventListener("mouseup",up);
    c.addEventListener("wheel",wheel,{passive:false});
    c.addEventListener("touchstart",down,{passive:true});c.addEventListener("touchmove",move,{passive:true});c.addEventListener("touchend",up);
    return()=>{
      c.removeEventListener("mousedown",down);window.removeEventListener("mousemove",move);window.removeEventListener("mouseup",up);
      c.removeEventListener("wheel",wheel);
      c.removeEventListener("touchstart",down);c.removeEventListener("touchmove",move);c.removeEventListener("touchend",up);
    };
  },[]);

  const reset=()=>{tgt.current={yaw:0,pitch:-0.25,zoom:1};setSel(null);lastInput.current=0;};
  return (
    <div ref={wrap} className="absolute inset-0">
      <canvas ref={cv} className="absolute inset-0" style={{cursor:"grab"}}/>
      <div className="absolute top-5 left-6 pointer-events-none"><div className="text-sm tracking-[0.3em] font-semibold" style={{color:C.text}}>SECOND BRAIN · SPHERE</div><div className="text-[10px] tracking-[0.25em] mt-1" style={{color:C.dim}}>EVERYTHING ZYNTH HAS BUILT — LIVE FROM THE VAULT</div></div>
      <div className="absolute top-5 right-6 flex items-center gap-1 text-[9px] tracking-widest">
        <Layers size={11} color={C.dim} className="mr-1"/>
        {["ALL","CAPABILITY","OPERATIONS","OUTPUT LINEAGE"].map(v=>(<button key={v} onClick={()=>setLens(v)} className="px-2.5 py-1 rounded-full border" style={{borderColor:lens===v?C.teal:"#1a2529",color:lens===v?C.teal:C.dim,background:lens===v?hx(C.teal,0.1):"transparent"}}>{v}</button>))}
        <button onClick={reset} className="ml-1 p-1.5 rounded-full border" style={{borderColor:"#1a2529",color:C.dim}}><RotateCcw size={12}/></button>
      </div>
      <div className="absolute bottom-5 left-6 text-[9px] space-y-1" style={{color:C.dim}}>
        {[["agent",C.teal],["skill",C.violet],["research / knowledge",C.blue],["proposal / output",C.gold]].map(([l,c])=>(<div key={l} className="flex items-center gap-2"><span className="w-2 h-2 rounded-full" style={{background:c,boxShadow:`0 0 6px ${c}`}}/>{l}</div>))}
        <div className="mt-2 opacity-60">drag = orbit · scroll/pinch = zoom · tap a node</div>
      </div>
      <div className="absolute top-0 right-0 h-full transition-transform duration-500 ease-out" style={{width:340,transform:sel?"translateX(0)":"translateX(110%)",background:"rgba(6,10,12,0.88)",backdropFilter:"blur(16px)",borderLeft:`1px solid ${hx(C.teal,0.18)}`}}>
        {sel&&(<div className="h-full flex flex-col p-6 pt-16 text-sm">
          <button onClick={()=>setSel(null)} className="absolute top-4 right-4 opacity-60 hover:opacity-100" style={{color:C.text}}><X size={18}/></button>
          <div className="flex items-center gap-3 mb-1"><span className="w-3 h-3 rounded-full" style={{background:TYPE[sel.type].c,boxShadow:`0 0 12px ${TYPE[sel.type].c}`}}/><h2 className="text-lg font-semibold" style={{color:C.text}}>{sel.label}</h2></div>
          <div className="text-[11px] tracking-wider mb-5" style={{color:C.dim}}>{sel.type.toUpperCase()} · {HUBS.find(h=>h.id===sel.hub)?.label||sel.hub}</div>
          {sel.by&&<Row k="Produced by" v={sel.by.replace(/_/g," ")}/>}
          {sel.type==="hub"&&<Row k="Contains" v={`${nodes.current.filter(n=>n.hub===sel.id&&n.type!=="hub").length} nodes`}/>}
          <Row k="Source" v="vault/ZYNTH-OS/"/>
          <div className="mt-6 text-xs leading-relaxed" style={{color:"#9fb0b6"}}>{sel.type==="deliverable"||sel.type==="proposal"?"A real produced output in your vault. Opens the composed document.":sel.type==="agent"?"A specialist in the ZYNTH workforce; edges show its cluster and outputs.":"A real asset in the ZYNTH knowledge system."}</div>
        </div>)}
      </div>
    </div>);
}
const Row=({k,v})=>(<div className="flex justify-between py-2 text-xs border-b" style={{borderColor:"#14201f"}}><span style={{color:C.dim}}>{k}</span><span style={{color:"#c9d3d8"}} className="text-right ml-3">{v}</span></div>);
