"use client";
import { useState, useRef, useEffect } from "react";

const AGENTS = {
  director: {
    id: "director", name: "ZARA", title: "Creative Director",
    burmese: "ဖန်တီးမှုဦးဆောင်သူ", avatar: "Z", color: "#FF2D55", bg: "#1a0008",
    systemPrompt: `You are ZARA, Creative Director at ZYNTH — sharp marketing agency for Singapore and Myanmar.

PERSONALITY: Confident, direct, sharp. Like a brilliant boss. Mix Burmese + English naturally.

PROACTIVE MODE: If user says "good morning", "what's next", "update me", "briefing" or anything open-ended — give a proactive daily briefing:
- What ZYNTH should be working on
- What campaigns need attention
- What to propose to clients
- Strategic recommendation for the day

OUTPUT FORMAT (max 250 words):
**STRATEGIC TAKE:** [2-3 sentences]
**DECISION:** [clear action]
**AGENT CHAIN:**
CALI_BRIEF: [brief]
SOMI_BRIEF: [brief]
KAI_BRIEF: [brief]

HOW TO USE ZYNTH BRAIN (teach users when they ask):
- Give ZARA a client brief → hit AUTO-CHAIN → all agents run automatically
- Each agent specializes: BRIX=brand, CALI=campaigns, KAI=copy, SOMI=social, ANA=analytics
- After AUTO-CHAIN, click each agent to see their output
- Use Export panel to download results as PDF, CSV, or copy
- Ask any agent follow-up questions directly
- Voice input: click 🎤 to speak your brief`
  },
  brand: {
    id: "brand", name: "BRIX", title: "Brand Strategist",
    burmese: "အမှတ်တံဆိပ်မဟာဗျူဟာပညာရှင်", avatar: "B", color: "#FF9500", bg: "#1a0d00",
    systemPrompt: `You are BRIX, Senior Brand Strategist at ZYNTH.
Max 300 words. Use headers: ## POSITIONING, ## VOICE (SG/Myanmar), ## KEY MESSAGES, ## RECOMMENDATION
Burmese: conversational, like texting a smart colleague. Mix English naturally. Never formal essay style.
Proactive: If asked for ideas, propose brand concepts unprompted.`
  },
  campaign: {
    id: "campaign", name: "CALI", title: "Campaign Planner",
    burmese: "ကမ်ပိန်းစီမံသူ", avatar: "C", color: "#30D158", bg: "#001a08",
    systemPrompt: `You are CALI, Campaign Planner at ZYNTH.
ALWAYS respond in tables. Max 300 words + tables.
Campaign table: | Month | Theme | FB Posts | LinkedIn | IG | Budget | Focus |
Calendar table: | Week | Day | Platform | Format | Topic | Caption Hook |
Max 8 posts/month per platform request. Phases: Awareness→Trust→Conversion.
Proactive: Suggest campaign ideas if brief is open-ended.`
  },
  copy: {
    id: "copy", name: "KAI", title: "Copywriter",
    burmese: "မိတ္တူရေးဆွဲသူ", avatar: "K", color: "#0A84FF", bg: "#00081a",
    systemPrompt: `You are KAI, Senior Copywriter at ZYNTH.
Max 2 versions per post. Max 300 words total.
Format: **[POST TYPE] — Version A** then **Version B**
BURMESE RULES: Write like smart Myanmar friend on Facebook. Short punchy sentences. Mix English naturally. Think in Burmese, never translate. Max 120 words per post.
Proactive: After writing copy, rate each version (1-10) and explain which to use and why.`
  },
  social: {
    id: "social", name: "SOMI", title: "Social Media Manager",
    burmese: "လူမှုကွန်ရက်မန်နေဂျာ", avatar: "S", color: "#BF5AF2", bg: "#0d001a",
    systemPrompt: `You are SOMI, Social Media Manager at ZYNTH.
ALWAYS tables only. Max 8 posts/month.
Calendar: | Week | Day | Platform | Format | Topic | Caption Hook | Best Time |
FB 50%, IG 30%, LinkedIn 20%. Myanmar FB: conversational Burmese, punchy.
Post times: FB Myanmar: 7-9am, 12-1pm, 7-10pm MMT. LinkedIn: 8-10am SGT.
Proactive: Flag which posts need visuals, which need boosting budget.`
  },
  analytics: {
    id: "analytics", name: "ANA", title: "Analytics Specialist",
    burmese: "ဒေတာခွဲခြမ်းစိတ်ဖြာသူ", avatar: "A", color: "#FF375F", bg: "#1a0005",
    systemPrompt: `You are ANA, Analytics Specialist at ZYNTH.
Tables only. Max 200 words + tables.
KPI table: | Metric | Target | Platform | How to Track | Alert if |
Weekly review: | Week | Check | Green = | Red = | Action |
End with: **WATCH:** [most important metric] and **REPORT:** [what to tell client]
Myanmar: CPM $0.50-2, ER 3-6%. Singapore: CPM $8-20, ER 1-3%.`
  }
};

const AGENT_LIST = Object.values(AGENTS);

export default function ZynthBrain() {
  const [activeAgent, setActiveAgent] = useState("director");
  const [chatHistories, setChatHistories] = useState({
    director: [{
      id: 1, role: "assistant", agentId: "director",
      content: "ZYNTH Brain — Online.\n\nကျွန်တော်က ZARA။ Brief တစ်ခု ပေးပြီး ⚡ AUTO နှိပ်ရင် agents အကုန် run မယ်။\n\n**HOW TO USE:**\n1. Brief ပေး (client + goal + market)\n2. ⚡ AUTO နှိပ် — agents အကုန် အလိုလျောက် run\n3. Sidebar မှာ agent တစ်ခုချင်း click ကြည့်\n4. Export panel မှာ PDF/CSV/Copy ထုတ်\n5. 🎤 Voice input သုံးနိုင်\n\nAgents: BRIX • CALI • KAI • SOMI • ANA",
      timestamp: new Date()
    }],
    brand: [], campaign: [], copy: [], social: [], analytics: []
  });
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [chainRunning, setChainRunning] = useState(false);
  const [chainStatus, setChainStatus] = useState("");
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [showExport, setShowExport] = useState(false);
  const [exportStatus, setExportStatus] = useState("");
  const [isListening, setIsListening] = useState(false);
  const messagesEndRef = useRef(null);
  const recognitionRef = useRef(null);

  const messages = chatHistories[activeAgent] || [];
  const agent = AGENTS[activeAgent];

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  // Voice input setup
  useEffect(() => {
    if (typeof window !== 'undefined' && ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window)) {
      const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SR();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = false;
      recognitionRef.current.lang = 'en-US';
      recognitionRef.current.onresult = (e) => {
        const transcript = e.results[0][0].transcript;
        setInput(prev => prev + transcript);
        setIsListening(false);
      };
      recognitionRef.current.onend = () => setIsListening(false);
      recognitionRef.current.onerror = () => setIsListening(false);
    }
  }, []);

  const toggleVoice = () => {
    if (!recognitionRef.current) { alert("Voice not supported in this browser. Try Chrome."); return; }
    if (isListening) { recognitionRef.current.stop(); setIsListening(false); }
    else { recognitionRef.current.start(); setIsListening(true); }
  };

  const callAPI = async (agentId, msgs) => {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ systemPrompt: AGENTS[agentId].systemPrompt, messages: msgs })
    });
    const data = await res.json();
    if (data.error) throw new Error(data.error);
    return data.content;
  };

  const addMessage = (agentId, content) => {
    setChatHistories(prev => ({
      ...prev,
      [agentId]: [...(prev[agentId] || []), {
        id: Date.now() + Math.random(), role: "assistant", agentId,
        content, timestamp: new Date(), isChain: true
      }]
    }));
  };

  const sendMessage = async () => {
    if (!input.trim() || loading) return;
    const userMsg = { id: Date.now(), role: "user", content: input, timestamp: new Date() };
    const currentInput = input;
    setInput("");
    setChatHistories(prev => ({ ...prev, [activeAgent]: [...(prev[activeAgent] || []), userMsg] }));
    setLoading(true);
    try {
      const history = [...(chatHistories[activeAgent] || [])].slice(-12).map(m => ({
        role: m.role === "user" ? "user" : "assistant", content: m.content
      }));
      history.push({ role: "user", content: currentInput });
      const text = await callAPI(activeAgent, history);
      setChatHistories(prev => ({
        ...prev,
        [activeAgent]: [...(prev[activeAgent] || []), userMsg, {
          id: Date.now() + 1, role: "assistant", agentId: activeAgent, content: text, timestamp: new Date()
        }]
      }));
    } catch (e) {
      setChatHistories(prev => ({
        ...prev,
        [activeAgent]: [...(prev[activeAgent] || []), userMsg, {
          id: Date.now() + 1, role: "assistant", agentId: activeAgent,
          content: `Error: ${e.message}`, timestamp: new Date()
        }]
      }));
    }
    setLoading(false);
  };

  const runAutoChain = async () => {
    if (loading || chainRunning) return;
    const lastUserMsg = [...(chatHistories.director || [])].reverse().find(m => m.role === "user");
    if (!lastUserMsg) { alert("ZARA ကို brief တစ်ခု ပေးပြီးမှ Auto-Chain run ပါ"); return; }

    setChainRunning(true);
    setLoading(true);
    const brief = lastUserMsg.content;
    let zaraBriefs = { campaign: brief, social: brief, copy: brief };

    setChainStatus("⚡ ZARA analyzing...");
    try {
      const zaraText = await callAPI("director", [{ role: "user", content: brief }]);
      addMessage("director", zaraText);
      const caliMatch = zaraText.match(/CALI_BRIEF:\s*([^\n]+(?:\n(?!SOMI_BRIEF:|KAI_BRIEF:)[^\n]+)*)/);
      const somiMatch = zaraText.match(/SOMI_BRIEF:\s*([^\n]+(?:\n(?!CALI_BRIEF:|KAI_BRIEF:)[^\n]+)*)/);
      const kaiMatch = zaraText.match(/KAI_BRIEF:\s*([^\n]+(?:\n(?!CALI_BRIEF:|SOMI_BRIEF:)[^\n]+)*)/);
      if (caliMatch) zaraBriefs.campaign = caliMatch[1].trim();
      if (somiMatch) zaraBriefs.social = somiMatch[1].trim();
      if (kaiMatch) zaraBriefs.copy = kaiMatch[1].trim();
    } catch(e) { console.error(e); }
    await new Promise(r => setTimeout(r, 400));

    setChainStatus("📊 CALI building campaign...");
    setActiveAgent("campaign");
    let caliOutput = "";
    try {
      caliOutput = await callAPI("campaign", [{ role: "user", content: zaraBriefs.campaign }]);
      addMessage("campaign", caliOutput);
    } catch(e) { console.error(e); }
    await new Promise(r => setTimeout(r, 400));

    setChainStatus("📅 SOMI creating calendar...");
    setActiveAgent("social");
    try {
      const somiOut = await callAPI("social", [{ role: "user", content: `${zaraBriefs.social}\n\nCALI output:\n${caliOutput}` }]);
      addMessage("social", somiOut);
    } catch(e) { console.error(e); }
    await new Promise(r => setTimeout(r, 400));

    setChainStatus("✍️ KAI writing copy...");
    setActiveAgent("copy");
    try {
      const kaiOut = await callAPI("copy", [{ role: "user", content: zaraBriefs.copy }]);
      addMessage("copy", kaiOut);
    } catch(e) { console.error(e); }
    await new Promise(r => setTimeout(r, 400));

    setChainStatus("📈 ANA setting KPIs...");
    setActiveAgent("analytics");
    try {
      const anaOut = await callAPI("analytics", [{ role: "user", content: `Campaign brief: ${brief}. Set KPI dashboard.` }]);
      addMessage("analytics", anaOut);
    } catch(e) { console.error(e); }

    setActiveAgent("director");
    setChainStatus("✅ Done! Check each agent →");
    setLoading(false);
    setChainRunning(false);
    setTimeout(() => setChainStatus(""), 5000);
  };

  // Export functions
  const getAllOutput = () => {
    let output = "ZYNTH BRAIN — CAMPAIGN REPORT\n";
    output += "Generated: " + new Date().toLocaleDateString() + "\n";
    output += "=".repeat(50) + "\n\n";
    AGENT_LIST.forEach(ag => {
      const msgs = (chatHistories[ag.id] || []).filter(m => m.role === "assistant");
      if (msgs.length > 0) {
        output += `\n${"=".repeat(50)}\n${ag.name} — ${ag.title}\n${"=".repeat(50)}\n`;
        msgs.forEach(m => { output += m.content + "\n\n"; });
      }
    });
    return output;
  };

  const exportPDF = () => {
    setExportStatus("Generating PDF...");
    const content = getAllOutput();
    const printWindow = window.open('', '_blank');
    printWindow.document.write(`
      <html><head><title>ZYNTH Campaign Report</title>
      <style>
        body { font-family: 'Courier New', monospace; background: #070707; color: #e0e0e0; padding: 30px; font-size: 12px; line-height: 1.6; }
        h1 { color: #FF2D55; border-bottom: 2px solid #FF2D55; padding-bottom: 10px; }
        h2 { color: #FF9500; margin-top: 30px; border-left: 4px solid #FF9500; padding-left: 10px; }
        pre { white-space: pre-wrap; word-wrap: break-word; }
        @media print { body { background: white; color: black; } h1 { color: #d00; } h2 { color: #d60; } }
      </style></head>
      <body><h1>ZYNTH BRAIN — Campaign Report</h1><pre>${content}</pre>
      <script>window.onload = () => { window.print(); }</script>
      </body></html>
    `);
    printWindow.document.close();
    setTimeout(() => setExportStatus(""), 3000);
  };

  const exportCSV = () => {
    setExportStatus("Generating CSV...");
    const somiMsgs = (chatHistories.social || []).filter(m => m.role === "assistant");
    const caliMsgs = (chatHistories.campaign || []).filter(m => m.role === "assistant");
    
    let csv = "ZYNTH Content Calendar\n";
    csv += "Generated," + new Date().toLocaleDateString() + "\n\n";
    csv += "CAMPAIGN PLAN\n";
    csv += "Month,Theme,FB Posts,LinkedIn,Instagram,Focus\n";
    
    if (caliMsgs.length > 0) {
      const lines = caliMsgs[0].content.split('\n');
      lines.forEach(line => {
        if (line.startsWith('|') && !line.includes('---')) {
          const cells = line.split('|').filter(c => c.trim()).map(c => `"${c.trim().replace(/\*\*/g, '')}"`);
          csv += cells.join(',') + '\n';
        }
      });
    }
    
    csv += "\n\nCONTENT CALENDAR\n";
    csv += "Week,Day,Platform,Format,Topic,Caption Hook,Best Time\n";
    
    if (somiMsgs.length > 0) {
      const lines = somiMsgs[0].content.split('\n');
      lines.forEach(line => {
        if (line.startsWith('|') && !line.includes('---')) {
          const cells = line.split('|').filter(c => c.trim()).map(c => `"${c.trim().replace(/\*\*/g, '')}"`);
          csv += cells.join(',') + '\n';
        }
      });
    }

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a'); a.href = url;
    a.download = `ZYNTH_Campaign_${new Date().toISOString().split('T')[0]}.csv`;
    a.click(); URL.revokeObjectURL(url);
    setTimeout(() => setExportStatus(""), 3000);
  };

  const copyAll = () => {
    navigator.clipboard.writeText(getAllOutput());
    setExportStatus("✅ Copied to clipboard!");
    setTimeout(() => setExportStatus(""), 3000);
  };

  const copyAgent = () => {
    const msgs = (chatHistories[activeAgent] || []).filter(m => m.role === "assistant");
    const text = msgs.map(m => m.content).join('\n\n---\n\n');
    navigator.clipboard.writeText(text);
    setExportStatus(`✅ ${agent.name} output copied!`);
    setTimeout(() => setExportStatus(""), 3000);
  };

  const fmt = (d) => new Date(d).toLocaleTimeString("en-SG", { hour: "2-digit", minute: "2-digit" });

  const renderContent = (content) => {
    return content.split('\n').map((line, i) => {
      if (line.startsWith('## ')) return <div key={i} style={{ color: '#FF9500', fontWeight: 700, fontSize: 10, marginTop: 10, marginBottom: 3, letterSpacing: 1 }}>{line.replace('## ', '')}</div>;
      if (line.match(/^\*\*[A-Z ]+:\*\*$/) || line.match(/^\*\*[A-Z ]+\*\*$/)) return <div key={i} style={{ color: '#fff', fontWeight: 700, fontSize: 11, marginTop: 7, marginBottom: 2 }}>{line.replace(/\*\*/g, '')}</div>;
      if (line.startsWith('- ') || line.startsWith('• ')) return <div key={i} style={{ color: '#ccc', fontSize: 11, paddingLeft: 10, lineHeight: 1.6 }}>• {line.replace(/^[-•] /, '')}</div>;
      if (line.startsWith('| ') && line.includes('|')) {
        const cells = line.split('|').filter(c => c.trim());
        if (line.match(/^\|[-|\s]+\|$/)) return null;
        const isHeader = i < content.split('\n').length - 1 && content.split('\n')[i+1]?.match(/^\|[-|\s]+\|$/);
        return (
          <div key={i} style={{ display: 'flex', borderBottom: '1px solid #1e1e1e', padding: '2px 0' }}>
            {cells.map((cell, j) => (
              <div key={j} style={{ flex: 1, fontSize: 10, color: isHeader ? agent.color : '#bbb', fontWeight: isHeader ? 700 : 400, padding: '2px 5px', minWidth: 0, wordBreak: 'break-word', lineHeight: 1.5 }}>
                {cell.trim().replace(/\*\*/g, '')}
              </div>
            ))}
          </div>
        );
      }
      if (line.startsWith('---')) return <hr key={i} style={{ border: 'none', borderTop: '1px solid #1e1e1e', margin: '5px 0' }} />;
      if (line === '') return <div key={i} style={{ height: 4 }} />;
      return <div key={i} style={{ color: '#d5d5d5', fontSize: 11.5, lineHeight: 1.7 }}>{line.replace(/\*\*(.*?)\*\*/g, '$1')}</div>;
    });
  };

  const hasOutput = AGENT_LIST.some(ag => (chatHistories[ag.id] || []).filter(m => m.role === "assistant").length > 0);

  return (
    <div style={{ display: "flex", height: "100vh", background: "#070707", fontFamily: "'DM Mono', monospace", color: "#e0e0e0", overflow: "hidden" }}>
      
      {/* Sidebar */}
      <div style={{ width: sidebarOpen ? 215 : 0, minWidth: sidebarOpen ? 215 : 0, background: "#0c0c0c", borderRight: "1px solid #181818", display: "flex", flexDirection: "column", overflow: "hidden", transition: "all 0.2s", flexShrink: 0 }}>
        <div style={{ padding: "16px 14px 12px", borderBottom: "1px solid #181818" }}>
          <div style={{ fontSize: 16, fontWeight: 700, letterSpacing: 5, color: "#fff" }}>ZYNTH</div>
          <div style={{ fontSize: 7, color: "#333", letterSpacing: 3, marginTop: 2 }}>AI BRAIN — ONLINE</div>
        </div>

        <div style={{ flex: 1, overflowY: "auto", padding: "8px 0" }}>
          <div style={{ fontSize: 7, color: "#222", letterSpacing: 2, padding: "0 14px 5px" }}>AGENTS</div>
          {AGENT_LIST.map(ag => {
            const isActive = activeAgent === ag.id;
            const hasContent = (chatHistories[ag.id] || []).filter(m => m.role === "assistant").length > 0;
            return (
              <div key={ag.id} onClick={() => setActiveAgent(ag.id)} style={{ padding: "7px 14px", cursor: "pointer", display: "flex", alignItems: "center", gap: 8, background: isActive ? "#141414" : "transparent", borderLeft: isActive ? `2px solid ${ag.color}` : "2px solid transparent", transition: "all 0.15s" }}>
                <div style={{ width: 28, height: 28, borderRadius: 5, background: ag.bg, border: `1px solid ${ag.color}${isActive ? "66" : "22"}`, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 10, fontWeight: 700, color: ag.color, flexShrink: 0 }}>{ag.avatar}</div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
                    <span style={{ fontSize: 10, fontWeight: 700, color: isActive ? ag.color : "#bbb" }}>{ag.name}</span>
                    {hasContent && <div style={{ width: 4, height: 4, borderRadius: "50%", background: ag.color, opacity: 0.8 }} />}
                  </div>
                  <div style={{ fontSize: 7, color: "#333" }}>{ag.title}</div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Export Panel */}
        <div style={{ borderTop: "1px solid #181818", padding: "8px 12px" }}>
          <button onClick={() => setShowExport(!showExport)} style={{ width: "100%", padding: "7px 0", background: showExport ? "#111" : "#0f0f0f", border: `1px solid ${showExport ? "#FF9500" : "#222"}`, color: showExport ? "#FF9500" : "#555", fontSize: 7.5, cursor: "pointer", borderRadius: 4, letterSpacing: 2, marginBottom: 4 }}>
            📦 EXPORT
          </button>
          {showExport && (
            <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
              <button onClick={exportPDF} style={{ padding: "6px", background: "#0f0f0f", border: "1px solid #222", color: "#aaa", fontSize: 8, cursor: "pointer", borderRadius: 3, textAlign: "left" }}>📄 Print / Save as PDF</button>
              <button onClick={exportCSV} style={{ padding: "6px", background: "#0f0f0f", border: "1px solid #222", color: "#aaa", fontSize: 8, cursor: "pointer", borderRadius: 3, textAlign: "left" }}>📊 Download CSV (Excel)</button>
              <button onClick={copyAll} style={{ padding: "6px", background: "#0f0f0f", border: "1px solid #222", color: "#aaa", fontSize: 8, cursor: "pointer", borderRadius: 3, textAlign: "left" }}>📋 Copy All Output</button>
              <button onClick={copyAgent} style={{ padding: "6px", background: "#0f0f0f", border: "1px solid #222", color: "#aaa", fontSize: 8, cursor: "pointer", borderRadius: 3, textAlign: "left" }}>📝 Copy {agent.name}'s Output</button>
              {exportStatus && <div style={{ fontSize: 8, color: "#30D158", textAlign: "center", padding: "3px 0" }}>{exportStatus}</div>}
            </div>
          )}
        </div>

        {/* Auto-Chain Button */}
        <div style={{ padding: "8px 12px", borderTop: "1px solid #181818" }}>
          <button onClick={runAutoChain} disabled={loading || chainRunning}
            style={{ width: "100%", padding: "9px 0", background: chainRunning ? "#1a0d00" : "#FF9500", border: "none", color: chainRunning ? "#FF9500" : "#000", fontSize: 8, cursor: (loading || chainRunning) ? "not-allowed" : "pointer", borderRadius: 5, fontWeight: 700, letterSpacing: 2 }}>
            {chainRunning ? "⚡ RUNNING..." : "⚡ AUTO-CHAIN"}
          </button>
          <div style={{ fontSize: 7, color: "#333", textAlign: "center", marginTop: 3 }}>
            {chainRunning ? chainStatus : "Brief ZARA → all agents auto-run"}
          </div>
        </div>
      </div>

      {/* Main */}
      <div style={{ flex: 1, display: "flex", flexDirection: "column", overflow: "hidden", minWidth: 0 }}>
        {/* Header */}
        <div style={{ padding: "10px 16px", borderBottom: "1px solid #181818", display: "flex", alignItems: "center", gap: 10, background: "#090909", flexShrink: 0 }}>
          <button onClick={() => setSidebarOpen(!sidebarOpen)} style={{ background: "none", border: "none", color: "#333", cursor: "pointer", fontSize: 14 }}>☰</button>
          <div style={{ width: 30, height: 30, borderRadius: 6, background: agent.bg, border: `1px solid ${agent.color}44`, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 11, fontWeight: 700, color: agent.color, flexShrink: 0 }}>{agent.avatar}</div>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
              <span style={{ fontSize: 12, fontWeight: 700, color: agent.color }}>{agent.name}</span>
              <span style={{ fontSize: 8, color: "#333" }}>|</span>
              <span style={{ fontSize: 8.5, color: "#444" }}>{agent.title}</span>
            </div>
            <div style={{ fontSize: 7, color: "#222" }}>{agent.burmese}</div>
          </div>
          {chainRunning && (
            <div style={{ marginLeft: "auto", background: "#1a0d00", border: "1px solid #FF950044", borderRadius: 4, padding: "3px 8px" }}>
              <span style={{ fontSize: 8, color: "#FF9500" }}>{chainStatus}</span>
            </div>
          )}
          {!chainRunning && (
            <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: 10 }}>
              {hasOutput && (
                <button onClick={() => setShowExport(!showExport)} style={{ background: "#111", border: "1px solid #333", color: "#888", fontSize: 8, padding: "4px 8px", borderRadius: 3, cursor: "pointer" }}>
                  📦 Export
                </button>
              )}
              <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
                <div style={{ width: 5, height: 5, borderRadius: "50%", background: "#30D158" }} />
                <span style={{ fontSize: 7, color: "#252525", letterSpacing: 2 }}>ONLINE</span>
              </div>
            </div>
          )}
        </div>

        {/* Messages */}
        <div style={{ flex: 1, overflowY: "auto", padding: "14px 16px", display: "flex", flexDirection: "column", gap: 10 }}>
          {messages.length === 0 && activeAgent !== "director" && (
            <div style={{ textAlign: "center", padding: "50px 20px" }}>
              <div style={{ fontSize: 26, color: agent.color, fontWeight: 700, letterSpacing: 3 }}>{agent.name}</div>
              <div style={{ fontSize: 9, color: "#333", marginTop: 5 }}>{agent.title}</div>
              <div style={{ fontSize: 8, color: "#222", marginTop: 15 }}>Run AUTO-CHAIN or brief this agent directly ↓</div>
            </div>
          )}
          {messages.map(msg => {
            const msgAgent = msg.agentId ? AGENTS[msg.agentId] : null;
            return (
              <div key={msg.id} style={{ display: "flex", gap: 8, flexDirection: msg.role === "user" ? "row-reverse" : "row", alignItems: "flex-start" }}>
                {msg.role === "assistant" && msgAgent && (
                  <div style={{ width: 24, height: 24, borderRadius: 5, background: msgAgent.bg, border: `1px solid ${msgAgent.color}33`, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 8, fontWeight: 700, color: msgAgent.color, flexShrink: 0, marginTop: 2 }}>{msgAgent.avatar}</div>
                )}
                <div style={{ maxWidth: "80%", display: "flex", flexDirection: "column", gap: 2, alignItems: msg.role === "user" ? "flex-end" : "flex-start" }}>
                  {msg.role === "assistant" && msgAgent && (
                    <div style={{ display: "flex", alignItems: "center", gap: 5 }}>
                      <span style={{ fontSize: 7.5, color: msgAgent.color, fontWeight: 700 }}>{msgAgent.name}</span>
                      {msg.isChain && <span style={{ fontSize: 6, color: "#FF9500", background: "#1a0d00", padding: "1px 3px", borderRadius: 2 }}>AUTO</span>}
                      <span style={{ fontSize: 6.5, color: "#1a1a1a" }}>{fmt(msg.timestamp)}</span>
                    </div>
                  )}
                  <div style={{ padding: "9px 12px", borderRadius: msg.role === "user" ? "10px 2px 10px 10px" : "2px 10px 10px 10px", background: msg.role === "user" ? "#161616" : "#0f0f0f", border: msg.role === "user" ? "1px solid #222" : `1px solid ${msgAgent?.color}15` }}>
                    {msg.role === "user"
                      ? <div style={{ fontSize: 12, lineHeight: 1.7, color: "#bbb" }}>{msg.content}</div>
                      : renderContent(msg.content)
                    }
                  </div>
                </div>
              </div>
            );
          })}
          {loading && !chainRunning && (
            <div style={{ display: "flex", gap: 8, alignItems: "flex-start" }}>
              <div style={{ width: 24, height: 24, borderRadius: 5, background: agent.bg, border: `1px solid ${agent.color}33`, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 8, fontWeight: 700, color: agent.color, flexShrink: 0 }}>{agent.avatar}</div>
              <div style={{ padding: "9px 12px", borderRadius: "2px 10px 10px 10px", background: "#0f0f0f", border: `1px solid ${agent.color}15`, display: "flex", gap: 4 }}>
                {[0,1,2].map(i => <div key={i} style={{ width: 4, height: 4, borderRadius: "50%", background: agent.color, animation: "blink 1.2s ease-in-out infinite", animationDelay: `${i*0.2}s` }} />)}
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div style={{ padding: "10px 16px", borderTop: "1px solid #181818", background: "#090909", flexShrink: 0 }}>
          <div style={{ display: "flex", gap: 6, alignItems: "flex-end" }}>
            <button onClick={toggleVoice} style={{ padding: "9px 10px", background: isListening ? "#FF2D55" : "#111", border: `1px solid ${isListening ? "#FF2D55" : "#222"}`, borderRadius: 5, color: isListening ? "#fff" : "#444", fontSize: 14, cursor: "pointer", flexShrink: 0, animation: isListening ? "blink 1s infinite" : "none" }}>
              🎤
            </button>
            <textarea
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(); }}}
              placeholder={activeAgent === "director" ? "Brief ZARA → ⚡ AUTO for full report | or say 'good morning' for daily briefing..." : `Ask ${agent.name} directly...`}
              disabled={loading}
              rows={2}
              style={{ flex: 1, background: "#0e0e0e", border: `1px solid ${isListening ? "#FF2D55" : "#1e1e1e"}`, borderRadius: 6, padding: "8px 11px", color: "#ddd", fontSize: 12, lineHeight: 1.6, resize: "none", outline: "none", fontFamily: "inherit", transition: "border-color 0.15s" }}
              onFocus={e => e.target.style.borderColor = agent.color + "55"}
              onBlur={e => e.target.style.borderColor = isListening ? "#FF2D55" : "#1e1e1e"}
            />
            <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
              <button onClick={sendMessage} disabled={loading || !input.trim()} style={{ padding: "7px 12px", background: (!loading && input.trim()) ? agent.color : "#111", border: "none", borderRadius: 5, color: (!loading && input.trim()) ? "#000" : "#2a2a2a", fontSize: 8, fontWeight: 700, cursor: (!loading && input.trim()) ? "pointer" : "not-allowed", letterSpacing: 1 }}>SEND</button>
              {activeAgent === "director" && (
                <button onClick={runAutoChain} disabled={loading || chainRunning} style={{ padding: "7px 12px", background: chainRunning ? "#1a0d00" : "#FF9500", border: "none", borderRadius: 5, color: chainRunning ? "#FF9500" : "#000", fontSize: 8, fontWeight: 700, cursor: (loading || chainRunning) ? "not-allowed" : "pointer", letterSpacing: 1 }}>⚡ AUTO</button>
              )}
            </div>
          </div>
          <div style={{ fontSize: 7, color: "#1a1a1a", marginTop: 4, letterSpacing: 1 }}>
            🎤 Voice · ENTER to send · ⚡ AUTO = all agents · 📦 Export results
          </div>
        </div>
      </div>

      <style>{`
        @keyframes blink { 0%,100%{opacity:.2;transform:scale(.8)} 50%{opacity:1;transform:scale(1.1)} }
        * { box-sizing: border-box; }
        ::-webkit-scrollbar { width: 3px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #1e1e1e; border-radius: 2px; }
      `}</style>
    </div>
  );
}
