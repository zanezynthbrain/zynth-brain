"use client";
import { useState, useRef, useEffect } from "react";

const AGENTS = {
  director: {
    id: "director", name: "ZARA", title: "Creative Director",
    burmese: "ဖန်တီးမှုဦးဆောင်သူ", avatar: "Z", color: "#FF2D55", bg: "#1a0008",
    systemPrompt: `You are ZARA, Creative Director at ZYNTH — sharp marketing agency for Singapore and Myanmar.

OUTPUT RULES:
- Max 200 words
- Always use EXACTLY this format:

**STRATEGIC TAKE:**
[2-3 sentences on the brief]

**DECISION:**
[what you're doing]

**AGENT CHAIN:**
CALI_BRIEF: [one paragraph brief for campaign planner]
SOMI_BRIEF: [one paragraph brief for social media manager]  
KAI_BRIEF: [one paragraph brief for copywriter]

- Natural Burmese mix where relevant
- No padding, no fluff`
  },
  brand: {
    id: "brand", name: "BRIX", title: "Brand Strategist",
    burmese: "အမှတ်တံဆိပ်မဟာဗျူဟာပညာရှင်", avatar: "B", color: "#FF9500", bg: "#1a0d00",
    systemPrompt: `You are BRIX, Senior Brand Strategist at ZYNTH.
OUTPUT RULES: Max 300 words. Use headers: ## POSITIONING, ## VOICE, ## KEY MESSAGES, ## NEXT STEP
Burmese: natural conversational, like texting a smart colleague. Mix English naturally.`
  },
  campaign: {
    id: "campaign", name: "CALI", title: "Campaign Planner",
    burmese: "ကမ်ပိန်းစီမံသူ", avatar: "C", color: "#30D158", bg: "#001a08",
    systemPrompt: `You are CALI, Campaign Planner at ZYNTH.
OUTPUT RULES: ALWAYS respond in tables. Max 300 words + tables.
Campaign table: | Month | Theme | FB Posts | LinkedIn Posts | IG Posts | Focus |
Content table: | Week | Platform | Format | Topic |
Max 16 posts/month. Phases: Awareness → Trust → Conversion.
Natural Burmese mix where relevant.`
  },
  copy: {
    id: "copy", name: "KAI", title: "Copywriter",
    burmese: "မိတ္တူရေးဆွဲသူ", avatar: "K", color: "#0A84FF", bg: "#00081a",
    systemPrompt: `You are KAI, Senior Copywriter at ZYNTH.
OUTPUT RULES: Max 2 versions per post type. Max 300 words total.
Format: **[POST TYPE] — Version A** then **Version B**
BURMESE RULES: Write like smart Myanmar friend on Facebook. Short punchy sentences. Mix English naturally. Never translate directly — think in Burmese first. Max 150 words per post.`
  },
  social: {
    id: "social", name: "SOMI", title: "Social Media Manager",
    burmese: "လူမှုကွန်ရက်မန်နေဂျာ", avatar: "S", color: "#BF5AF2", bg: "#0d001a",
    systemPrompt: `You are SOMI, Social Media Manager at ZYNTH.
OUTPUT RULES: ALWAYS tables only. Max 16 posts/month.
Calendar table: | Week | Day | Platform | Format | Topic | Caption Hook |
Platform split: FB 50%, IG 30%, LinkedIn 20%.
Myanmar FB: conversational Burmese, punchy. Post times: 7-9am, 12-1pm, 7-10pm MMT.`
  },
  analytics: {
    id: "analytics", name: "ANA", title: "Analytics Specialist",
    burmese: "ဒေတာခွဲခြမ်းစိတ်ဖြာသူ", avatar: "A", color: "#FF375F", bg: "#1a0005",
    systemPrompt: `You are ANA, Analytics Specialist at ZYNTH.
OUTPUT RULES: Tables only. Max 200 words.
KPI table: | Metric | Target | Platform | How to Track |
End with: **WATCH:** [1 most important metric]
Myanmar benchmarks: CPM $0.50-2, ER 3-6%. Singapore: CPM $8-20, ER 1-3%.`
  }
};

const AGENT_LIST = Object.values(AGENTS);

const CHAIN_ORDER = ["campaign", "social", "copy", "analytics"];

export default function ZynthBrain() {
  const [activeAgent, setActiveAgent] = useState("director");
  const [chatHistories, setChatHistories] = useState({
    director: [{
      id: 1, role: "assistant", agentId: "director",
      content: "ZYNTH Brain — Online.\n\nကျွန်တော်က ZARA။ Brief တစ်ခု ပေးလိုက်ပါ — ⚡ AUTO-CHAIN နှိပ်ရင် agents အကုန် အလိုအလျောက် run မယ်။\n\nAgents: BRIX • CALI • KAI • SOMI • ANA",
      timestamp: new Date()
    }],
    brand: [], campaign: [], copy: [], social: [], analytics: []
  });
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [chainRunning, setChainRunning] = useState(false);
  const [chainStatus, setChainStatus] = useState("");
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const messagesEndRef = useRef(null);

  const messages = chatHistories[activeAgent] || [];
  const agent = AGENTS[activeAgent];

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading, chainStatus]);

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

  const addMessage = (agentId, content, extra = {}) => {
    setChatHistories(prev => ({
      ...prev,
      [agentId]: [...(prev[agentId] || []), {
        id: Date.now() + Math.random(), role: "assistant", agentId,
        content, timestamp: new Date(), ...extra
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
    if (!lastUserMsg) {
      alert("ZARA ကို brief တစ်ခု ပေးပြီးမှ Auto-Chain run ပါ");
      return;
    }

    setChainRunning(true);
    setLoading(true);

    const brief = lastUserMsg.content;

    // Step 1: ZARA analyzes and creates briefs
    setChainStatus("ZARA — Analyzing brief...");
    let zaraBriefs = { campaign: brief, social: brief, copy: brief, analytics: brief };

    try {
      const zaraText = await callAPI("director", [{ role: "user", content: brief }]);
      addMessage("director", zaraText);

      // Extract briefs from ZARA output
      const caliMatch = zaraText.match(/CALI_BRIEF:\s*([^\n]+(?:\n(?!SOMI_BRIEF:|KAI_BRIEF:)[^\n]+)*)/);
      const somiMatch = zaraText.match(/SOMI_BRIEF:\s*([^\n]+(?:\n(?!CALI_BRIEF:|KAI_BRIEF:)[^\n]+)*)/);
      const kaiMatch = zaraText.match(/KAI_BRIEF:\s*([^\n]+(?:\n(?!CALI_BRIEF:|SOMI_BRIEF:)[^\n]+)*)/);

      if (caliMatch) zaraBriefs.campaign = caliMatch[1].trim();
      if (somiMatch) zaraBriefs.social = somiMatch[1].trim();
      if (kaiMatch) zaraBriefs.copy = kaiMatch[1].trim();

    } catch (e) {
      console.error("ZARA error:", e);
    }

    await new Promise(r => setTimeout(r, 500));

    // Step 2: Run CALI
    setChainStatus("CALI — Building campaign plan...");
    setActiveAgent("campaign");
    let caliOutput = "";
    try {
      caliOutput = await callAPI("campaign", [{ role: "user", content: zaraBriefs.campaign }]);
      addMessage("campaign", caliOutput);
    } catch (e) { console.error("CALI error:", e); }
    await new Promise(r => setTimeout(r, 500));

    // Step 3: Run SOMI with CALI context
    setChainStatus("SOMI — Creating content calendar...");
    setActiveAgent("social");
    try {
      const somiPrompt = `${zaraBriefs.social}\n\nCALI's campaign structure:\n${caliOutput}`;
      const somiOutput = await callAPI("social", [{ role: "user", content: somiPrompt }]);
      addMessage("social", somiOutput);
    } catch (e) { console.error("SOMI error:", e); }
    await new Promise(r => setTimeout(r, 500));

    // Step 4: Run KAI
    setChainStatus("KAI — Writing copy...");
    setActiveAgent("copy");
    try {
      const kaiOutput = await callAPI("copy", [{ role: "user", content: zaraBriefs.copy }]);
      addMessage("copy", kaiOutput);
    } catch (e) { console.error("KAI error:", e); }
    await new Promise(r => setTimeout(r, 500));

    // Step 5: Run ANA
    setChainStatus("ANA — Setting KPIs...");
    setActiveAgent("analytics");
    try {
      const anaPrompt = `Client brief: ${brief}. Set up KPI dashboard for this campaign.`;
      const anaOutput = await callAPI("analytics", [{ role: "user", content: anaPrompt }]);
      addMessage("analytics", anaOutput);
    } catch (e) { console.error("ANA error:", e); }

    setChainStatus("✅ All agents done. Check each agent for their output.");
    setLoading(false);
    setChainRunning(false);
    setTimeout(() => setChainStatus(""), 4000);
  };

  const fmt = (d) => new Date(d).toLocaleTimeString("en-SG", { hour: "2-digit", minute: "2-digit" });

  const renderContent = (content) => {
    const lines = content.split('\n');
    return lines.map((line, i) => {
      if (line.startsWith('## ')) return <div key={i} style={{ color: '#FF9500', fontWeight: 700, fontSize: 10, marginTop: 10, marginBottom: 3, letterSpacing: 1, textTransform: 'uppercase' }}>{line.replace('## ', '')}</div>;
      if (line.match(/^\*\*[^*]+:\*\*$/)) return <div key={i} style={{ color: '#ffffff', fontWeight: 700, fontSize: 11, marginTop: 8, marginBottom: 2 }}>{line.replace(/\*\*/g, '')}</div>;
      if (line.startsWith('**') && line.endsWith('**')) return <div key={i} style={{ color: '#ffffff', fontWeight: 700, fontSize: 11, marginTop: 6 }}>{line.replace(/\*\*/g, '')}</div>;
      if (line.startsWith('- ') || line.startsWith('• ')) return <div key={i} style={{ color: '#cccccc', fontSize: 11.5, paddingLeft: 10, lineHeight: 1.6 }}>• {line.replace(/^[-•] /, '')}</div>;
      if (line.startsWith('| ') && line.includes('|')) {
        const cells = line.split('|').filter(c => c.trim());
        const isHeader = lines[i+1]?.startsWith('|---') || lines[i-1]?.startsWith('|---');
        const isSep = line.match(/^\|[-|\s]+\|$/);
        if (isSep) return null;
        return (
          <div key={i} style={{ display: 'flex', borderBottom: '1px solid #1e1e1e', padding: '3px 0' }}>
            {cells.map((cell, j) => (
              <div key={j} style={{
                flex: 1, fontSize: 10, color: isHeader ? agent.color : '#bbb',
                fontWeight: isHeader ? 700 : 400, padding: '2px 6px', minWidth: 0,
                wordBreak: 'break-word', lineHeight: 1.5
              }}>{cell.trim().replace(/\*\*/g, '')}</div>
            ))}
          </div>
        );
      }
      if (line.startsWith('---')) return <hr key={i} style={{ border: 'none', borderTop: '1px solid #1e1e1e', margin: '6px 0' }} />;
      if (line === '') return <div key={i} style={{ height: 5 }} />;
      return <div key={i} style={{ color: '#d5d5d5', fontSize: 11.5, lineHeight: 1.7 }}>{line.replace(/\*\*(.*?)\*\*/g, '$1')}</div>;
    });
  };

  return (
    <div style={{ display: "flex", height: "100vh", background: "#070707", fontFamily: "'DM Mono', monospace", color: "#e0e0e0", overflow: "hidden" }}>
      {/* Sidebar */}
      <div style={{ width: sidebarOpen ? 215 : 0, minWidth: sidebarOpen ? 215 : 0, background: "#0c0c0c", borderRight: "1px solid #181818", display: "flex", flexDirection: "column", overflow: "hidden", transition: "all 0.2s ease", flexShrink: 0 }}>
        <div style={{ padding: "18px 14px 14px", borderBottom: "1px solid #181818", flexShrink: 0 }}>
          <div style={{ fontSize: 17, fontWeight: 700, letterSpacing: 5, color: "#fff", fontFamily: "'Space Grotesk', sans-serif" }}>ZYNTH</div>
          <div style={{ fontSize: 7, color: "#333", letterSpacing: 3, marginTop: 2 }}>AI BRAIN — ONLINE</div>
        </div>

        <div style={{ flex: 1, overflowY: "auto", padding: "8px 0" }}>
          <div style={{ fontSize: 7, color: "#222", letterSpacing: 2, padding: "0 14px 6px" }}>AGENTS</div>
          {AGENT_LIST.map(ag => {
            const isActive = activeAgent === ag.id;
            const hasContent = (chatHistories[ag.id] || []).filter(m => m.role === "assistant").length > 0;
            return (
              <div key={ag.id} onClick={() => setActiveAgent(ag.id)} style={{ padding: "8px 14px", cursor: "pointer", display: "flex", alignItems: "center", gap: 8, background: isActive ? "#141414" : "transparent", borderLeft: isActive ? `2px solid ${ag.color}` : "2px solid transparent", transition: "all 0.15s" }}>
                <div style={{ width: 28, height: 28, borderRadius: 6, background: ag.bg, border: `1px solid ${ag.color}${isActive ? "66" : "22"}`, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 10, fontWeight: 700, color: ag.color, flexShrink: 0 }}>{ag.avatar}</div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 5 }}>
                    <span style={{ fontSize: 10, fontWeight: 700, color: isActive ? ag.color : "#bbb", fontFamily: "'Space Grotesk', sans-serif" }}>{ag.name}</span>
                    {hasContent && <div style={{ width: 4, height: 4, borderRadius: "50%", background: ag.color, opacity: 0.7 }} />}
                  </div>
                  <div style={{ fontSize: 7, color: "#333" }}>{ag.title}</div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Auto-Chain Button */}
        <div style={{ padding: "10px 12px", borderTop: "1px solid #181818", flexShrink: 0 }}>
          <button onClick={runAutoChain} disabled={loading || chainRunning}
            style={{ width: "100%", padding: "10px 0", background: chainRunning ? "#1a0d00" : "#0f0f0f", border: `1px solid ${chainRunning ? "#FF9500" : "#333"}`, color: chainRunning ? "#FF9500" : "#fff", fontSize: 8, cursor: (loading || chainRunning) ? "not-allowed" : "pointer", borderRadius: 5, letterSpacing: 2, fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700, transition: "all 0.2s" }}>
            {chainRunning ? "⚡ RUNNING..." : "⚡ AUTO-CHAIN"}
          </button>
          <div style={{ fontSize: 7, color: "#333", textAlign: "center", marginTop: 4 }}>
            {chainRunning ? chainStatus : "Brief ZARA → all agents auto-run"}
          </div>
        </div>
      </div>

      {/* Main */}
      <div style={{ flex: 1, display: "flex", flexDirection: "column", overflow: "hidden", minWidth: 0 }}>
        {/* Header */}
        <div style={{ padding: "11px 18px", borderBottom: "1px solid #181818", display: "flex", alignItems: "center", gap: 10, background: "#090909", flexShrink: 0 }}>
          <button onClick={() => setSidebarOpen(!sidebarOpen)} style={{ background: "none", border: "none", color: "#333", cursor: "pointer", fontSize: 14, padding: "0 2px" }}>☰</button>
          <div style={{ width: 30, height: 30, borderRadius: 6, background: agent.bg, border: `1px solid ${agent.color}44`, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 11, fontWeight: 700, color: agent.color, flexShrink: 0 }}>{agent.avatar}</div>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
              <span style={{ fontSize: 12, fontWeight: 700, color: agent.color, fontFamily: "'Space Grotesk', sans-serif" }}>{agent.name}</span>
              <span style={{ fontSize: 8, color: "#333" }}>|</span>
              <span style={{ fontSize: 8.5, color: "#444" }}>{agent.title}</span>
            </div>
            <div style={{ fontSize: 7, color: "#222" }}>{agent.burmese}</div>
          </div>
          {chainRunning && (
            <div style={{ marginLeft: "auto", background: "#1a0d00", border: "1px solid #FF950044", borderRadius: 4, padding: "4px 10px" }}>
              <span style={{ fontSize: 8, color: "#FF9500", letterSpacing: 1 }}>{chainStatus}</span>
            </div>
          )}
          {!chainRunning && (
            <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: 5 }}>
              <div style={{ width: 5, height: 5, borderRadius: "50%", background: "#30D158" }} />
              <span style={{ fontSize: 7, color: "#252525", letterSpacing: 2 }}>ONLINE</span>
            </div>
          )}
        </div>

        {/* Messages */}
        <div style={{ flex: 1, overflowY: "auto", padding: "14px 18px", display: "flex", flexDirection: "column", gap: 10 }}>
          {messages.length === 0 && (
            <div style={{ textAlign: "center", padding: "50px 20px" }}>
              <div style={{ fontSize: 28, color: agent.color, fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700, letterSpacing: 3 }}>{agent.name}</div>
              <div style={{ fontSize: 9, color: "#333", marginTop: 6 }}>{agent.description || agent.title}</div>
              {activeAgent === "director" && (
                <div style={{ marginTop: 20, background: "#0f0f0f", border: "1px solid #1e1e1e", borderRadius: 8, padding: "14px", maxWidth: 400, margin: "20px auto 0" }}>
                  <div style={{ fontSize: 8, color: "#FF9500", letterSpacing: 2, marginBottom: 8 }}>HOW TO USE</div>
                  <div style={{ fontSize: 9, color: "#666", lineHeight: 1.8, textAlign: "left" }}>
                    1. Brief ZARA with your client + goal<br/>
                    2. Hit ⚡ AUTO-CHAIN — all agents run automatically<br/>
                    3. Click each agent to see their output<br/>
                    4. Ask follow-up questions to any agent
                  </div>
                </div>
              )}
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
                      <span style={{ fontSize: 7.5, color: msgAgent.color, fontWeight: 700, fontFamily: "'Space Grotesk', sans-serif" }}>{msgAgent.name}</span>
                      {msg.isChain && <span style={{ fontSize: 6.5, color: "#FF9500", background: "#1a0d00", padding: "1px 4px", borderRadius: 2, letterSpacing: 1 }}>AUTO</span>}
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
              <div style={{ padding: "9px 13px", borderRadius: "2px 10px 10px 10px", background: "#0f0f0f", border: `1px solid ${agent.color}15`, display: "flex", alignItems: "center", gap: 4 }}>
                {[0,1,2].map(i => <div key={i} style={{ width: 4, height: 4, borderRadius: "50%", background: agent.color, animation: "blink 1.2s ease-in-out infinite", animationDelay: `${i * 0.2}s` }} />)}
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div style={{ padding: "11px 18px", borderTop: "1px solid #181818", background: "#090909", flexShrink: 0 }}>
          <div style={{ display: "flex", gap: 7, alignItems: "flex-end" }}>
            <textarea
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(); }}}
              placeholder={activeAgent === "director" ? "Brief ZARA — then hit ⚡ AUTO-CHAIN for full report..." : `Ask ${agent.name}...`}
              disabled={loading}
              rows={2}
              style={{ flex: 1, background: "#0e0e0e", border: "1px solid #1e1e1e", borderRadius: 6, padding: "8px 12px", color: "#ddd", fontSize: 12, lineHeight: 1.6, resize: "none", outline: "none", fontFamily: "'DM Mono', monospace", transition: "border-color 0.15s" }}
              onFocus={e => e.target.style.borderColor = agent.color + "55"}
              onBlur={e => e.target.style.borderColor = "#1e1e1e"}
            />
            <div style={{ display: "flex", flexDirection: "column", gap: 5 }}>
              <button onClick={sendMessage} disabled={loading || !input.trim()} style={{ padding: "7px 13px", background: (!loading && input.trim()) ? agent.color : "#111", border: "none", borderRadius: 5, color: (!loading && input.trim()) ? "#000" : "#2a2a2a", fontSize: 8, fontWeight: 700, cursor: (!loading && input.trim()) ? "pointer" : "not-allowed", letterSpacing: 1, fontFamily: "'Space Grotesk', sans-serif" }}>SEND</button>
              {activeAgent === "director" && (
                <button onClick={runAutoChain} disabled={loading || chainRunning} style={{ padding: "7px 13px", background: chainRunning ? "#1a0d00" : "#FF9500", border: "none", borderRadius: 5, color: chainRunning ? "#FF9500" : "#000", fontSize: 8, fontWeight: 700, cursor: (loading || chainRunning) ? "not-allowed" : "pointer", letterSpacing: 1, fontFamily: "'Space Grotesk', sans-serif" }}>⚡ AUTO</button>
              )}
            </div>
          </div>
          <div style={{ fontSize: 7, color: "#1a1a1a", marginTop: 4, letterSpacing: 1 }}>
            ENTER to send · ⚡ AUTO-CHAIN = all agents run automatically
          </div>
        </div>
      </div>

      <style>{`
        @keyframes blink { 0%, 100% { opacity: 0.2; transform: scale(0.8); } 50% { opacity: 1; transform: scale(1.1); } }
        * { box-sizing: border-box; }
        ::-webkit-scrollbar { width: 3px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #1e1e1e; border-radius: 2px; }
      `}</style>
    </div>
  );
}
