# ZYNTH Brain — AI Marketing Intelligence

Multi-agent AI system for ZYNTH marketing firm. 6 AI agents, bilingual (English + Burmese), built for Singapore & Myanmar markets.

## Agents
- **ZARA** — Creative Director (strategic lead, routes tasks)
- **BRIX** — Brand Strategist (positioning, identity, SG+MM markets)
- **CALI** — Campaign Planner (go-to-market, channels, KPIs)
- **KAI** — Copywriter (headlines, scripts, bilingual copy)
- **SOMI** — Social Media Manager (content, community, platforms)
- **ANA** — Analytics Specialist (performance, ROAS, data insights)

## Setup

### 1. Clone & install
```bash
git clone https://github.com/YOUR_USERNAME/zynth-brain.git
cd zynth-brain
npm install
```

### 2. Add API key
Create `.env.local` file:
```
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxx
```

### 3. Run locally
```bash
npm run dev
```
Visit http://localhost:3000

## Deploy to Vercel
1. Push to GitHub
2. Go to vercel.com → Import project
3. Add `ANTHROPIC_API_KEY` in Environment Variables
4. Deploy — get your live URL

## Usage
- Click any agent in sidebar to talk to them directly
- Type in English, Burmese, or both
- Hit ⚡ AGENT ROUNDTABLE to make all agents discuss your brief together
