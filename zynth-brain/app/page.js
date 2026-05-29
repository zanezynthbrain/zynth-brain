"use client";
import { useState, useRef, useEffect } from "react";

const AGENTS = {
  director: {
    id: "director",
    name: "ZARA",
    title: "Creative Director",
    burmese: "ဖန်တီးမှုဦးဆောင်သူ",
    avatar: "Z",
    color: "#FF2D55",
    bg: "#1a0008",
    description: "Strategic lead. Routes tasks. Oversees all.",
    systemPrompt: `You are ZARA, Creative Director at ZYNTH — a sharp marketing agency for Singapore and Myanmar.

CRITICAL OUTPUT RULES:
- Maximum 300 words per response
- Always use this structure:
  **STRATEGIC TAKE:** (2-3 sentences max)
  **DECISION:** (what you're doing next)
  **NEXT AGENT:** (who you're handing to and exact brief)
- No long explanations. No padding.
- Burmese: Use natural conversational Burmese — like texting a colleague, not writing an essay. Mix English terms naturally (e.g. "campaign ကောင်းမှ brand က grow ဖြစ်မယ်")

When given a brief:
1. Assess in 2-3 sentences
2. State your decision
3. Hand off to next agent with a tight brief

You coordinate: BRIX (Brand), CALI (Campaign), KAI (Copy), SOMI (Social), ANA (Analytics).`
  },
  brand: {
    id: "brand",
    name: "BRIX",
    title: "Brand Strategist",
    burmese: "အမှတ်တံဆိပ်မဟာဗျူဟာပညာရှင်",
    avatar: "B",
    color: "#FF9500",
    bg: "#1a0d00",
    description: "Positioning. Identity. Tone of voice.",
    systemPrompt: `You are BRIX, Senior Brand Strategist at ZYNTH.

CRITICAL OUTPUT RULES:
- Always respond in clean structured format using headers and bullet points
- Maximum 400 words
- Structure every response as:
  ## POSITIONING
  ## VOICE (SG / Myanmar)
  ## KEY MESSAGES (3 bullets max)
  ## NEXT STEP
- Burmese writing rules: Write like a smart Myanmar friend texting — casual, confident, direct. NOT formal essay style. Mix English naturally. Example: "Brand က credible ဖြစ်ဖို့ results ပြရတယ် — fancy words မဟုတ်ဘူး။"
- No AI-sounding Burmese. No overly formal phrasing.

Myanmar market: Facebook-first, mobile, community trust, aspirational middle class.
Singapore market: Multicultural, trust signals matter, premium positioning.`
  },
  campaign: {
    id: "campaign",
    name: "CALI",
    title: "Campaign Planner",
    burmese: "ကမ်ပိန်းစီမံသူ",
    avatar: "C",
    color: "#30D158",
    bg: "#001a08",
    description: "Go-to-market. Channels. Timelines.",
    systemPrompt: `You are CALI, Campaign Planner at ZYNTH.

CRITICAL OUTPUT RULES:
- Always respond in TABLE format when giving plans
- Maximum 350 words + tables
- For campaign plans use this table:
  | Phase | Days | Platform | Content | Budget |
- For content calendars use:
  | Week | Day | Platform | Format | Topic |
- Only 16 posts per month total (4 per week)
- Burmese: Natural, conversational — "Week 1 မှာ awareness build လုပ်မယ်၊ Facebook ကနေ စမယ်" style

Platforms: LinkedIn (SG), Facebook (Myanmar-primary), Instagram (visual).
Always phase campaigns: Awareness → Credibility → Conversion.`
  },
  copy: {
    id: "copy",
    name: "KAI",
    title: "Copywriter",
    burmese: "မိတ္တူရေးဆွဲသူ",
    avatar: "K",
    color: "#0A84FF",
    bg: "#00081a",
    description: "Headlines. Scripts. Captions. Bilingual.",
    systemPrompt: `You are KAI, Senior Copywriter at ZYNTH.

CRITICAL OUTPUT RULES:
- Give maximum 2 versions of any copy (not 3-4)
- Structure: English version first, Burmese version second
- Maximum 300 words total per response
- Format:
  **[POST TYPE] — Version A**
  [copy]
  ---
  **[POST TYPE] — Version B**
  [copy]

BURMESE COPY RULES — CRITICAL:
- Write like a real Myanmar person talking to friends on Facebook
- Use everyday words: မင်း/ကျွန်တော် not ခင်ဗျား (unless formal context)
- Mix English naturally where Myanmar people actually do: "Marketing budget က waste ဖြစ်နေတယ်ဆိုတာ သိလား?"
- Short punchy sentences. No long paragraphs.
- Avoid: overly formal phrases, textbook Burmese, AI-sounding constructions
- Sound like: a smart, confident Myanmar entrepreneur talking directly to peers
- NEVER translate English directly to Burmese — think in Burmese first

For social posts: max 150 words. For manifestos: max 200 words.`
  },
  social: {
    id: "social",
    name: "SOMI",
    title: "Social Media Manager",
    burmese: "လူမှုကွန်ရက်မန်နေဂျာ",
    avatar: "S",
    color: "#BF5AF2",
    bg: "#0d001a",
    description: "Content calendar. Community. Platforms.",
    systemPrompt: `You are SOMI, Social Media Manager at ZYNTH.

CRITICAL OUTPUT RULES:
- ALWAYS respond with tables, never paragraphs
- 16 posts per month MAXIMUM (4 per week)
- Content calendar format:
  | Week | Day | Platform | Format | Topic | Caption Hook |
- Platform split: Facebook 40%, Instagram 35%, LinkedIn 25%
- No TikTok unless specifically requested
- Maximum 250 words + table

MYANMAR CONTENT RULES:
- Facebook posts in Burmese: conversational, punchy, like a friend sharing insight
- Post times: 7-9am, 12-1pm, 7-10pm Myanmar time
- Mix Burmese + English naturally in captions

SINGAPORE CONTENT RULES:
- LinkedIn: professional but human, English only
- Instagram: visual-first, English captions with 1-2 Burmese words max`
  },
  analytics: {
    id: "analytics",
    name: "ANA",
    title: "Analytics Specialist",
    burmese: "ဒေတာခွဲခြမ်းစိတ်ဖြာသူ",
    avatar: "A",
    color: "#FF375F",
    bg: "#1a0005",
    description: "Performance. KPIs. Data insights.",
    systemPrompt: `You are ANA, Analytics Specialist at ZYNTH.

CRITICAL OUTPUT RULES:
- ALWAYS respond in tables
- Maximum 200 words + tables
- KPI table format:
  | Metric | Target | Platform | How to Track |
- Weekly review format:
  | Week | What to Check | Green = | Red = |
- No long explanations — numbers and decisions only
- End every response with: "**WATCH:** [1 most important metric this week]"

Myanmar benchmarks: CPM $0.50-2, ER 3-6%, Facebook dominant
Singapore benchmarks: CPM $8-20, ER 1-3%, LinkedIn + Instagram`
  }
};

const AGENT_LIST = Object.values(AGENTS);

export default function ZynthBrain() {
  const [activeAgent, setActiveAgent] = useState("director");
  const [chatHistories, setChatHistories] = useState({
    director: [{
      id: 1, role: "assistant", agentId: "director",
      content: "ZYNTH Brain — Online.\n\nကျွန်တော်က ZARA။ Brief ပေးလိုက် — market, client, goal။ တစ်ကြောင်းနှစ်ကြောင်းနဲ့ ရပြီ။\n\nAgents ready: BRIX • CALI • KAI • SOMI • ANA",
      timestamp: new Date()
    }],
    brand: [], campaign: [], copy: [], social: [], analytics: []
  });
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [roundtableActive, setRoundtableActive] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const messagesEndRef = useRef(null);

  const messages = chatHistories[activeAgent] || [];
  const agent = AGENTS[activeAgent];

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const callAPI = async (agentId, msgs) => {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        systemPrompt: AGENTS[agentId].systemPrompt,
        messages: msgs
      })
    });
    const data = await res.json();
    if (data.error) throw new Error(data.error);
    return data.content;
  };

  const sendMessage = async () => {
    if (!input.trim() || loading) return;
    const userMsg = { id: Date.now(), role: "user", content: input, timestamp: new Date() };
    const currentInput = input;
    setInput("");

    setChatHistories(prev => ({
      ...prev,
      [activeAgent]: [...(prev[activeAgent] || []), userMsg]
    }));
    setLoading(true);

    try {
      const history = [...(chatHistories[activeAgent] || [])].slice(-12).map(m => ({
        role: m.role === "user" ? "user" : "assistant",
        content: m.content
      }));
      history.push({ role: "user", content: currentInput });

      const text = await callAPI(activeAgent, history);
      setChatHistories(prev => ({
        ...prev,
        [activeAgent]: [...(prev[activeAgent] || []), userMsg, {
          id: Date.now() + 1, role: "assistant", agentId: activeAgent,
          content: text, timestamp: new Date()
        }]
      }));
    } catch (e) {
      setChatHistories(prev => ({
        ...prev,
        [activeAgent]: [...(prev[activeAgent] || []), userMsg, {
          id: Date.now() + 1, role: "assistant", agentId: activeAgent,
          content: `Error: ${e.message}`,
          timestamp: new Date()
        }]
      }));
    }
    setLoading(false);
  };

  const runRoundtable = async () => {
    if (loading || roundtableActive) return;
    const lastUserMsg = [...messages].reverse().find(m => m.role === "user");
    if (!lastUserMsg) return;

    setRoundtableActive(true);
    setLoading(true);

    const topic = lastUserMsg.content;
    const roundAgents = [AGENTS.director, AGENTS.brand, AGENTS.campaign, AGENTS.copy, AGENTS.social];
    const discussionLog = [];

    for (let i = 0; i < roundAgents.length; i++) {
      const ag = roundAgents[i];
      const context = discussionLog.map(d => `[${d.name}]: ${d.content}`).join("\n\n");

      try {
        const prompt = context
          ? `ROUNDTABLE — Topic: "${topic}"\n\nPrevious:\n${context}\n\nYou are ${ag.name}. Respond in max 100 words. Your role only. Be direct.`
          : `ROUNDTABLE — Topic: "${topic}"\n\nYou are ${ag.name}. Start the discussion. Max 100 words. Be direct.`;

        const text = await callAPI(ag.id, [{ role: "user", content: prompt }]);
        discussionLog.push({ name: ag.name, content: text });

        setChatHistories(prev => ({
          ...prev,
          [activeAgent]: [...(prev[activeAgent] || []), {
            id: Date.now() + i + Math.random(),
            role: "assistant",
            agentId: ag.id,
            content: text,
            isRoundtable: true,
            timestamp: new Date()
          }]
        }));

        await new Promise(r => setTimeout(r, 300));
      } catch (e) {
        console.error(`${ag.name} error:`, e);
      }
    }

    setLoading(false);
    setRoundtableActive(false);
  };

  const fmt = (d) => new Date(d).toLocaleTimeString("en-SG", { hour: "2-digit", minute: "2-digit" });

  // Render message content with basic markdown
  const renderContent = (content) => {
    const lines = content.split('\n');
    return lines.map((line, i) => {
      if (line.startsWith('## ')) return <div key={i} style={{ color: '#FF9500', fontWeight: 700, fontSize: 11, marginTop: 10, marginBottom: 4, letterSpacing: 1 }}>{line.replace('## ', '')}</div>;
      if (line.startsWith('**') && line.endsWith('**')) return <div key={i} style={{ color: '#ffffff', fontWeight: 700, fontSize: 12, marginTop: 6 }}>{line.replace(/\*\*/g, '')}</div>;
      if (line.startsWith('- ') || line.startsWith('• ')) return <div key={i} style={{ color: '#cccccc', fontSize: 12, paddingLeft: 12, lineHeight: 1.6 }}>• {line.replace(/^[-•] /, '')}</div>;
      if (line.startsWith('| ')) return <div key={i} style={{ color: '#aaaaaa', fontSize: 11, fontFamily: 'monospace', lineHeight: 1.8, borderBottom: '1px solid #1e1e1e', padding: '2px 0' }}>{line}</div>;
      if (line.startsWith('---')) return <hr key={i} style={{ border: 'none', borderTop: '1px solid #1e1e1e', margin: '8px 0' }} />;
      if (line === '') return <div key={i} style={{ height: 6 }} />;
      return <div key={i} style={{ color: '#d5d5d5', fontSize: 12.5, lineHeight: 1.7 }}>{line.replace(/\*\*(.*?)\*\*/g, '$1')}</div>;
    });
  };

  return (
    <div style={{
      display: "flex", height: "100vh", background: "#070707",
      fontFamily: "'DM Mono', monospace", color: "#e0e0e0", overflow: "hidden"
    }}>
      {/* Sidebar */}
      <div style={{
        width: sidebarOpen ? 220 : 0, minWidth: sidebarOpen ? 220 : 0,
        background: "#0c0c0c", borderRight: "1px solid #181818",
        display: "flex", flexDirection: "column", overflow: "hidden",
        transition: "all 0.2s ease", flexShrink: 0
      }}>
        <div style={{ padding: "20px 16px 16px", borderBottom: "1px solid #181818", flexShrink: 0 }}>
          <div style={{ fontSize: 18, fontWeight: 700, letterSpacing: 5, color: "#fff", fontFamily: "'Space Grotesk', sans-serif" }}>ZYNTH</div>
          <div style={{ fontSize: 7, color: "#333", letterSpacing: 3, marginTop: 3 }}>AI BRAIN — ONLINE</div>
        </div>

        <div style={{ flex: 1, overflowY: "auto", padding: "10px 0" }}>
          <div style={{ fontSize: 7, color: "#252525", letterSpacing: 2, padding: "0 16px 8px", fontFamily: "'Space Grotesk', sans-serif" }}>AGENTS</div>
          {AGENT_LIST.map(ag => {
            const isActive = activeAgent === ag.id;
            const hasMessages = (chatHistories[ag.id] || []).length > 0;
            return (
              <div key={ag.id} onClick={() => setActiveAgent(ag.id)} style={{
                padding: "9px 16px", cursor: "pointer", display: "flex", alignItems: "center", gap: 9,
                background: isActive ? "#141414" : "transparent",
                borderLeft: isActive ? `2px solid ${ag.color}` : "2px solid transparent",
                transition: "all 0.15s"
              }}>
                <div style={{
                  width: 30, height: 30, borderRadius: 6, background: ag.bg,
                  border: `1px solid ${ag.color}${isActive ? "66" : "22"}`,
                  display: "flex", alignItems: "center", justifyContent: "center",
                  fontSize: 11, fontWeight: 700, color: ag.color, flexShrink: 0
                }}>{ag.avatar}</div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: 10, fontWeight: 700, color: isActive ? ag.color : "#bbb", fontFamily: "'Space Grotesk', sans-serif" }}>{ag.name}</div>
                  <div style={{ fontSize: 7.5, color: "#333", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{ag.title}</div>
                </div>
                {hasMessages && !isActive && <div style={{ width: 4, height: 4, borderRadius: "50%", background: ag.color, opacity: 0.5, flexShrink: 0 }} />}
              </div>
            );
          })}
        </div>

        <div style={{ padding: "10px 12px", borderTop: "1px solid #181818", flexShrink: 0 }}>
          <button onClick={runRoundtable} disabled={loading}
            style={{
              width: "100%", padding: "8px 0", background: roundtableActive ? "#111" : "#0f0f0f",
              border: `1px solid ${roundtableActive ? "#333" : "#1e1e1e"}`,
              color: roundtableActive ? "#FF9500" : "#444", fontSize: 7.5,
              cursor: loading ? "not-allowed" : "pointer", borderRadius: 4,
              letterSpacing: 2, fontFamily: "'Space Grotesk', sans-serif", fontWeight: 600
            }}>
            {roundtableActive ? "⚡ DISCUSSING..." : "⚡ ROUNDTABLE"}
          </button>
        </div>
      </div>

      {/* Main */}
      <div style={{ flex: 1, display: "flex", flexDirection: "column", overflow: "hidden", minWidth: 0 }}>
        {/* Header */}
        <div style={{
          padding: "12px 20px", borderBottom: "1px solid #181818",
          display: "flex", alignItems: "center", gap: 10, background: "#090909", flexShrink: 0
        }}>
          <button onClick={() => setSidebarOpen(!sidebarOpen)} style={{
            background: "none", border: "none", color: "#333", cursor: "pointer", fontSize: 14, padding: "0 2px"
          }}>☰</button>
          <div style={{
            width: 32, height: 32, borderRadius: 6, background: agent.bg,
            border: `1px solid ${agent.color}44`, display: "flex", alignItems: "center",
            justifyContent: "center", fontSize: 12, fontWeight: 700, color: agent.color, flexShrink: 0
          }}>{agent.avatar}</div>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
              <span style={{ fontSize: 13, fontWeight: 700, color: agent.color, fontFamily: "'Space Grotesk', sans-serif" }}>{agent.name}</span>
              <span style={{ fontSize: 9, color: "#333" }}>|</span>
              <span style={{ fontSize: 9, color: "#444" }}>{agent.title}</span>
            </div>
            <div style={{ fontSize: 7.5, color: "#252525" }}>{agent.burmese}</div>
          </div>
          <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: 5 }}>
            <div style={{ width: 5, height: 5, borderRadius: "50%", background: "#30D158" }} />
            <span style={{ fontSize: 7, color: "#252525", letterSpacing: 2 }}>ONLINE</span>
          </div>
        </div>

        {/* Messages */}
        <div style={{ flex: 1, overflowY: "auto", padding: "16px 20px", display: "flex", flexDirection: "column", gap: 12 }}>
          {messages.length === 0 && (
            <div style={{ textAlign: "center", padding: "60px 20px" }}>
              <div style={{ fontSize: 32, color: agent.color, fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700, letterSpacing: 3 }}>{agent.name}</div>
              <div style={{ fontSize: 10, color: "#333", marginTop: 8 }}>{agent.description}</div>
              <div style={{ fontSize: 9, color: "#1e1e1e", marginTop: 20 }}>Brief this agent ↓</div>
            </div>
          )}
          {messages.map(msg => {
            const msgAgent = msg.agentId ? AGENTS[msg.agentId] : null;
            return (
              <div key={msg.id} style={{
                display: "flex", gap: 9, flexDirection: msg.role === "user" ? "row-reverse" : "row", alignItems: "flex-start"
              }}>
                {msg.role === "assistant" && msgAgent && (
                  <div style={{
                    width: 26, height: 26, borderRadius: 5, background: msgAgent.bg,
                    border: `1px solid ${msgAgent.color}33`, display: "flex", alignItems: "center",
                    justifyContent: "center", fontSize: 9, fontWeight: 700, color: msgAgent.color, flexShrink: 0, marginTop: 2
                  }}>{msgAgent.avatar}</div>
                )}
                <div style={{ maxWidth: "78%", display: "flex", flexDirection: "column", gap: 3, alignItems: msg.role === "user" ? "flex-end" : "flex-start" }}>
                  {msg.role === "assistant" && msgAgent && (
                    <div style={{ display: "flex", alignItems: "center", gap: 5 }}>
                      <span style={{ fontSize: 8, color: msgAgent.color, fontWeight: 700, fontFamily: "'Space Grotesk', sans-serif" }}>{msgAgent.name}</span>
                      {msg.isRoundtable && <span style={{ fontSize: 6.5, color: "#FF9500", background: "#1a0d00", padding: "1px 4px", borderRadius: 2 }}>ROUNDTABLE</span>}
                      <span style={{ fontSize: 6.5, color: "#1e1e1e" }}>{fmt(msg.timestamp)}</span>
                    </div>
                  )}
                  <div style={{
                    padding: "10px 13px",
                    borderRadius: msg.role === "user" ? "10px 2px 10px 10px" : "2px 10px 10px 10px",
                    background: msg.role === "user" ? "#161616" : "#0f0f0f",
                    border: msg.role === "user" ? "1px solid #222" : `1px solid ${msgAgent?.color}15`,
                  }}>
                    {msg.role === "user"
                      ? <div style={{ fontSize: 12.5, lineHeight: 1.7, color: "#bbb" }}>{msg.content}</div>
                      : renderContent(msg.content)
                    }
                  </div>
                </div>
              </div>
            );
          })}

          {loading && (
            <div style={{ display: "flex", gap: 9, alignItems: "flex-start" }}>
              <div style={{
                width: 26, height: 26, borderRadius: 5, background: agent.bg,
                border: `1px solid ${agent.color}33`, display: "flex", alignItems: "center",
                justifyContent: "center", fontSize: 9, fontWeight: 700, color: agent.color, flexShrink: 0
              }}>{agent.avatar}</div>
              <div style={{
                padding: "10px 14px", borderRadius: "2px 10px 10px 10px",
                background: "#0f0f0f", border: `1px solid ${agent.color}15`,
                display: "flex", alignItems: "center", gap: 5
              }}>
                {[0,1,2].map(i => (
                  <div key={i} style={{
                    width: 4, height: 4, borderRadius: "50%", background: agent.color,
                    animation: "blink 1.2s ease-in-out infinite",
                    animationDelay: `${i * 0.2}s`
                  }} />
                ))}
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div style={{ padding: "12px 20px", borderTop: "1px solid #181818", background: "#090909", flexShrink: 0 }}>
          <div style={{ display: "flex", gap: 8, alignItems: "flex-end" }}>
            <textarea
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(); }}}
              placeholder={`Brief ${agent.name}... (English or မြန်မာဘာသာ)`}
              disabled={loading}
              rows={2}
              style={{
                flex: 1, background: "#0e0e0e", border: "1px solid #1e1e1e", borderRadius: 6,
                padding: "9px 13px", color: "#ddd", fontSize: 12.5, lineHeight: 1.6,
                resize: "none", outline: "none", fontFamily: "'DM Mono', monospace",
                transition: "border-color 0.15s"
              }}
              onFocus={e => e.target.style.borderColor = agent.color + "55"}
              onBlur={e => e.target.style.borderColor = "#1e1e1e"}
            />
            <button onClick={sendMessage} disabled={loading || !input.trim()} style={{
              padding: "9px 15px", background: (!loading && input.trim()) ? agent.color : "#111",
              border: "none", borderRadius: 6,
              color: (!loading && input.trim()) ? "#000" : "#2a2a2a",
              fontSize: 9, fontWeight: 700, cursor: (!loading && input.trim()) ? "pointer" : "not-allowed",
              letterSpacing: 1.5, transition: "all 0.15s", flexShrink: 0,
              fontFamily: "'Space Grotesk', sans-serif"
            }}>SEND</button>
          </div>
          <div style={{ fontSize: 7.5, color: "#1a1a1a", marginTop: 5, letterSpacing: 1 }}>
            ENTER to send · SHIFT+ENTER new line · Switch agents in sidebar
          </div>
        </div>
      </div>

      <style>{`
        @keyframes blink {
          0%, 100% { opacity: 0.2; transform: scale(0.8); }
          50% { opacity: 1; transform: scale(1.1); }
        }
        * { box-sizing: border-box; }
        ::-webkit-scrollbar { width: 3px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #1e1e1e; border-radius: 2px; }
      `}</style>
    </div>
  );
}
