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
    systemPrompt: `You are ZARA, Creative Director at ZYNTH — a sharp, intelligent marketing agency for Singapore and Myanmar markets.

ZYNTH philosophy: Strategy before creative. Clarity before execution.

Your role:
- You are the BRAIN of ZYNTH. You receive client briefs, break them down, and coordinate agents.
- You think and respond in Burmese AND English naturally. Mix both when helpful.
- Decisive, sharp, never fluffy. You challenge weak thinking.
- You coordinate: BRIX (Brand Strategist), CALI (Campaign Planner), KAI (Copywriter), SOMI (Social Media), ANA (Analytics).

When given a task:
1. Quickly assess the work type
2. Give your strategic take (sharp, 2-3 sentences)
3. State which agents should be involved and why

Style: Like a brilliant boss who respects your time. Confident. Direct. Occasionally switches to Burmese phrases naturally.
Always end with next action or agent handoff.`
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

Expertise: Brand positioning, tone of voice, competitive mapping, audience profiling for Singapore AND Myanmar.

Myanmar market: Mobile-first, Facebook-dominant, trust through community, Burmese language essential, emerging middle class in Yangon/Mandalay — aspirational messaging works.
Singapore market: Multicultural (Chinese, Malay, Indian, Expat), trust signals matter, price-value sensitivity even premium.

You defend strategic decisions with cultural insight. Push back when creative goes off-strategy.
Speak naturally in both English and Burmese. Explain the WHY behind every decision.`
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

Expertise: Campaign briefs, channel strategy (Meta, TikTok, Google, OOH, Influencer), budget phasing, KPI frameworks, launch sequencing.

Think in phases: Awareness → Consideration → Conversion → Retention.
Myanmar: Facebook-first, mobile video, community trust, Burmese copy essential.
Singapore: Multi-channel, bilingual where needed, performance-driven.

You need Brand Strategy before planning — ask BRIX if not provided.
Brief Copywriter and Social on execution. Report results to ANA.
Respond in English and Burmese naturally.`
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

Expertise: Campaign headlines, taglines, social captions, video scripts, ad copy, bilingual copy (English + Burmese).

ZYNTH copy rules: Sharp and intelligent. Never generic. Never fluffy.
- Headlines: Punchy, unexpected, zero clichés
- Burmese copy: Think in Burmese, write in Burmese — never just translate
- Always give 2-3 variations
- Know awareness copy vs conversion copy

You challenge vague briefs. Get strategic direction from ZARA/BRIX first.
You write fluidly in full Burmese, full English, or code-switch naturally.`
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

Expertise: Content calendars, platform strategy, community management, hashtag strategy, influencer briefs, social audits.

Myanmar social: Facebook is king. Video with Burmese captions performs best. Post times: 7-9am, 12-1pm, 7-10pm Myanmar time. Community groups = powerful distribution.
Singapore social: Instagram for lifestyle/B2C, LinkedIn for B2B, TikTok growing fast under-35, consistent aesthetics > frequency.

You receive copy from KAI and format for each platform. Flag when content doesn't fit platform culture.
Respond in English and Burmese naturally.`
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

Expertise: Campaign performance reporting, KPI frameworks, Meta Ads, Google Analytics, TikTok Analytics, ROI/ROAS, A/B test recommendations, data storytelling.

You translate numbers into decisions, not just charts.
Awareness KPIs: CPM, Reach, Frequency. Engagement: ER%, CTR, Saves. Conversion: CPC, CPA, ROAS, CVR.
Myanmar benchmarks: Lower CPMs, higher engagement, Facebook dominant.
Singapore benchmarks: Higher CPMs, multi-platform, stronger conversion tracking.

You say what numbers mean and what to do next. Clear and decisive. Bilingual when needed.`
  }
};

const AGENT_LIST = Object.values(AGENTS);

export default function ZynthBrain() {
  const [activeAgent, setActiveAgent] = useState("director");
  const [chatHistories, setChatHistories] = useState({
    director: [{
      id: 1, role: "assistant", agentId: "director",
      content: "ZYNTH AI Brain — Online.\n\nကျွန်တော်က ZARA — ZYNTH ရဲ့ Creative Director ဖြစ်ပါတယ်။ မင်းရဲ့ marketing empire ကို ဒီမှာ တည်ဆောက်မယ်။\n\nClient brief ပေးလိုက်— market (SG / Myanmar / Both), ဘာလုပ်ချင်တာလဲ။ Agent team ready: BRIX, CALI, KAI, SOMI, ANA။",
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
          content: `Error: ${e.message}\n\nAPI key စစ်ကြည့်ပါ — Vercel environment variables မှာ ANTHROPIC_API_KEY ထည့်ထားရဲ့လားဆိုတာ`,
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
          ? `AGENT ROUNDTABLE — Topic: "${topic}"\n\nPrevious agents said:\n${context}\n\nNow respond as ${ag.name} (${ag.title}). Add your unique perspective. Be direct, max 120 words. Challenge or build on what others said. Use Burmese naturally.`
          : `AGENT ROUNDTABLE — Topic: "${topic}"\n\nYou go first as ${ag.name} (${ag.title}). Set the frame for the team. Sharp and strategic, max 120 words. Use Burmese naturally.`;

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

        await new Promise(r => setTimeout(r, 400));
      } catch (e) {
        console.error(`${ag.name} error:`, e);
      }
    }

    setLoading(false);
    setRoundtableActive(false);
  };

  const fmt = (d) => new Date(d).toLocaleTimeString("en-SG", { hour: "2-digit", minute: "2-digit" });

  return (
    <div style={{
      display: "flex", height: "100vh", background: "#070707",
      fontFamily: "'DM Mono', monospace", color: "#e0e0e0", overflow: "hidden"
    }}>
      {/* Sidebar */}
      <div style={{
        width: sidebarOpen ? 230 : 0, minWidth: sidebarOpen ? 230 : 0,
        background: "#0c0c0c", borderRight: "1px solid #181818",
        display: "flex", flexDirection: "column", overflow: "hidden",
        transition: "all 0.2s ease", flexShrink: 0
      }}>
        {/* Logo */}
        <div style={{ padding: "22px 18px 18px", borderBottom: "1px solid #181818", flexShrink: 0 }}>
          <div style={{ fontSize: 20, fontWeight: 700, letterSpacing: 5, color: "#fff", fontFamily: "'Space Grotesk', sans-serif" }}>ZYNTH</div>
          <div style={{ fontSize: 8, color: "#333", letterSpacing: 3, marginTop: 3 }}>AI BRAIN — ONLINE</div>
        </div>

        {/* Agents list */}
        <div style={{ flex: 1, overflowY: "auto", padding: "10px 0" }}>
          <div style={{ fontSize: 8, color: "#252525", letterSpacing: 2, padding: "0 18px 10px", fontFamily: "'Space Grotesk', sans-serif" }}>AGENTS</div>
          {AGENT_LIST.map(ag => {
            const unread = (chatHistories[ag.id] || []).filter(m => m.role === "assistant").length;
            const isActive = activeAgent === ag.id;
            return (
              <div key={ag.id} onClick={() => setActiveAgent(ag.id)} style={{
                padding: "10px 18px", cursor: "pointer", display: "flex", alignItems: "center", gap: 10,
                background: isActive ? "#141414" : "transparent",
                borderLeft: isActive ? `2px solid ${ag.color}` : "2px solid transparent",
                transition: "all 0.15s"
              }}>
                <div style={{
                  width: 32, height: 32, borderRadius: 7, background: ag.bg,
                  border: `1px solid ${ag.color}${isActive ? "66" : "22"}`,
                  display: "flex", alignItems: "center", justifyContent: "center",
                  fontSize: 12, fontWeight: 700, color: ag.color, flexShrink: 0,
                  transition: "all 0.15s"
                }}>{ag.avatar}</div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: 11, fontWeight: 700, color: isActive ? ag.color : "#bbb", fontFamily: "'Space Grotesk', sans-serif" }}>{ag.name}</div>
                  <div style={{ fontSize: 8, color: "#383838", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{ag.title}</div>
                </div>
                {unread > 0 && (
                  <div style={{ width: 5, height: 5, borderRadius: "50%", background: ag.color, opacity: 0.6, flexShrink: 0 }} />
                )}
              </div>
            );
          })}
        </div>

        {/* Roundtable button */}
        <div style={{ padding: "12px 14px", borderTop: "1px solid #181818", flexShrink: 0 }}>
          <button onClick={runRoundtable} disabled={loading}
            style={{
              width: "100%", padding: "9px 0", background: roundtableActive ? "#111" : "#0f0f0f",
              border: `1px solid ${roundtableActive ? "#333" : "#1e1e1e"}`,
              color: roundtableActive ? "#FF9500" : "#555", fontSize: 8,
              cursor: loading ? "not-allowed" : "pointer", borderRadius: 5,
              letterSpacing: 2, fontFamily: "'Space Grotesk', sans-serif", fontWeight: 600,
              transition: "all 0.2s"
            }}>
            {roundtableActive ? "⚡ DISCUSSING..." : "⚡ AGENT ROUNDTABLE"}
          </button>
          <div style={{ fontSize: 7, color: "#1e1e1e", textAlign: "center", marginTop: 5, letterSpacing: 1 }}>
            All 5 agents discuss your brief
          </div>
        </div>
      </div>

      {/* Main */}
      <div style={{ flex: 1, display: "flex", flexDirection: "column", overflow: "hidden", minWidth: 0 }}>
        {/* Header */}
        <div style={{
          padding: "14px 20px", borderBottom: "1px solid #181818",
          display: "flex", alignItems: "center", gap: 12, background: "#090909", flexShrink: 0
        }}>
          <button onClick={() => setSidebarOpen(!sidebarOpen)} style={{
            background: "none", border: "none", color: "#333", cursor: "pointer",
            fontSize: 16, padding: "0 4px", display: "flex", alignItems: "center"
          }}>☰</button>
          <div style={{
            width: 34, height: 34, borderRadius: 7, background: agent.bg,
            border: `1px solid ${agent.color}44`, display: "flex", alignItems: "center",
            justifyContent: "center", fontSize: 13, fontWeight: 700, color: agent.color, flexShrink: 0
          }}>{agent.avatar}</div>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <span style={{ fontSize: 14, fontWeight: 700, color: agent.color, fontFamily: "'Space Grotesk', sans-serif" }}>{agent.name}</span>
              <span style={{ fontSize: 9, color: "#2a2a2a" }}>|</span>
              <span style={{ fontSize: 10, color: "#444" }}>{agent.title}</span>
            </div>
            <div style={{ fontSize: 8, color: "#252525" }}>{agent.burmese}</div>
          </div>
          <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: 6 }}>
            <div style={{ width: 5, height: 5, borderRadius: "50%", background: "#30D158", boxShadow: "0 0 6px #30D15866" }} />
            <span style={{ fontSize: 7, color: "#252525", letterSpacing: 2 }}>ONLINE</span>
          </div>
        </div>

        {/* Messages */}
        <div style={{ flex: 1, overflowY: "auto", padding: "20px", display: "flex", flexDirection: "column", gap: 14 }}>
          {messages.length === 0 && (
            <div style={{ textAlign: "center", padding: "40px 20px" }}>
              <div style={{ fontSize: 28, color: agent.color, fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700, letterSpacing: 3 }}>{agent.name}</div>
              <div style={{ fontSize: 11, color: "#333", marginTop: 8 }}>{agent.description}</div>
              <div style={{ fontSize: 10, color: "#222", marginTop: 4 }}>{agent.burmese}</div>
              <div style={{ marginTop: 20, fontSize: 10, color: "#2a2a2a" }}>Brief this agent below ↓</div>
            </div>
          )}
          {messages.map(msg => {
            const msgAgent = msg.agentId ? AGENTS[msg.agentId] : null;
            return (
              <div key={msg.id} style={{
                display: "flex", gap: 10, flexDirection: msg.role === "user" ? "row-reverse" : "row", alignItems: "flex-start"
              }}>
                {msg.role === "assistant" && msgAgent && (
                  <div style={{
                    width: 28, height: 28, borderRadius: 6, background: msgAgent.bg,
                    border: `1px solid ${msgAgent.color}33`, display: "flex", alignItems: "center",
                    justifyContent: "center", fontSize: 10, fontWeight: 700, color: msgAgent.color, flexShrink: 0, marginTop: 2
                  }}>{msgAgent.avatar}</div>
                )}
                <div style={{ maxWidth: "75%", display: "flex", flexDirection: "column", gap: 3, alignItems: msg.role === "user" ? "flex-end" : "flex-start" }}>
                  {msg.role === "assistant" && msgAgent && (
                    <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                      <span style={{ fontSize: 9, color: msgAgent.color, fontWeight: 700, fontFamily: "'Space Grotesk', sans-serif" }}>{msgAgent.name}</span>
                      {msg.isRoundtable && (
                        <span style={{ fontSize: 7, color: "#FF9500", background: "#1a0d00", padding: "1px 5px", borderRadius: 2, letterSpacing: 1 }}>ROUNDTABLE</span>
                      )}
                      <span style={{ fontSize: 7, color: "#1e1e1e" }}>{fmt(msg.timestamp)}</span>
                    </div>
                  )}
                  <div style={{
                    padding: "10px 14px",
                    borderRadius: msg.role === "user" ? "10px 2px 10px 10px" : "2px 10px 10px 10px",
                    background: msg.role === "user" ? "#161616" : "#0f0f0f",
                    border: msg.role === "user" ? "1px solid #222" : `1px solid ${msgAgent?.color}15`,
                    fontSize: 12.5, lineHeight: 1.7, color: msg.role === "user" ? "#bbb" : "#d5d5d5",
                    whiteSpace: "pre-wrap", wordBreak: "break-word"
                  }}>{msg.content}</div>
                </div>
              </div>
            );
          })}

          {loading && (
            <div style={{ display: "flex", gap: 10, alignItems: "flex-start" }}>
              <div style={{
                width: 28, height: 28, borderRadius: 6, background: agent.bg,
                border: `1px solid ${agent.color}33`, display: "flex", alignItems: "center",
                justifyContent: "center", fontSize: 10, fontWeight: 700, color: agent.color, flexShrink: 0
              }}>{agent.avatar}</div>
              <div style={{
                padding: "12px 16px", borderRadius: "2px 10px 10px 10px",
                background: "#0f0f0f", border: `1px solid ${agent.color}15`,
                display: "flex", alignItems: "center", gap: 5
              }}>
                {[0,1,2].map(i => (
                  <div key={i} style={{
                    width: 5, height: 5, borderRadius: "50%", background: agent.color,
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
        <div style={{ padding: "14px 20px", borderTop: "1px solid #181818", background: "#090909", flexShrink: 0 }}>
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
                padding: "10px 14px", color: "#ddd", fontSize: 13, lineHeight: 1.6,
                resize: "none", outline: "none", fontFamily: "'DM Mono', monospace",
                transition: "border-color 0.15s"
              }}
              onFocus={e => e.target.style.borderColor = agent.color + "55"}
              onBlur={e => e.target.style.borderColor = "#1e1e1e"}
            />
            <button onClick={sendMessage} disabled={loading || !input.trim()} style={{
              padding: "10px 16px", background: (!loading && input.trim()) ? agent.color : "#111",
              border: "none", borderRadius: 6,
              color: (!loading && input.trim()) ? "#000" : "#2a2a2a",
              fontSize: 10, fontWeight: 700, cursor: (!loading && input.trim()) ? "pointer" : "not-allowed",
              letterSpacing: 1.5, transition: "all 0.15s", flexShrink: 0,
              fontFamily: "'Space Grotesk', sans-serif"
            }}>SEND</button>
          </div>
          <div style={{ fontSize: 8, color: "#1c1c1c", marginTop: 6, letterSpacing: 1 }}>
            ENTER to send · SHIFT+ENTER new line · Switch agents in sidebar · ⚡ Roundtable = all agents discuss
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
