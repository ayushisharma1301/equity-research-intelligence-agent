from __future__ import annotations
import html
from datetime import datetime
import pandas as pd
import streamlit as st

from config import get_config
from llm.gemini_client import GeminiResearchClient
from llm.tavily_client import TavilyResearchClient
from agents.company_resolver import CompanyResolver
from agents.financial_agent import FinancialAgent
from agents.industry_agent import IndustryAgent
from agents.synthesis_agent import SynthesisAgent

st.set_page_config(page_title="Equity Research Intelligence", page_icon="E", layout="wide", initial_sidebar_state="expanded")

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');
:root{--bg:#090B10;--bg2:#0D0F16;--panel:#14161F;--panel2:#0F1119;--border:#252838;--soft:#1B1E29;--text:#EDEAE2;--dim:#8B8FA3;--accent:#E08D3C;--live:#4FD1C5;--safe:#4CAF66;--watch:#E0B23D;--flag:#D14F3D;}
.stApp{background:radial-gradient(ellipse 900px 500px at 15% -10%,rgba(224,141,60,.08),transparent 60%),var(--bg);color:var(--text);font-family:'IBM Plex Sans',sans-serif}.block-container{max-width:1240px;padding-top:1.6rem;padding-bottom:4rem}section[data-testid="stSidebar"]{background:var(--bg2);border-right:1px solid var(--border)}
h1,h2,h3,h4,h5{font-family:'Fraunces',Georgia,serif!important;color:var(--text)!important}.brand{display:flex;gap:14px;align-items:center;border-bottom:1px solid var(--border);padding-bottom:20px;margin-bottom:18px}.mark{width:40px;height:40px;border-radius:6px;background:linear-gradient(135deg,var(--accent),#8A5A26);display:flex;align-items:center;justify-content:center;color:#0D0F16;font-family:'Fraunces',Georgia,serif;font-size:21px;font-weight:700}.eyebrow{font-family:'IBM Plex Mono',monospace;font-size:10px;letter-spacing:.16em;text-transform:uppercase;color:var(--accent)}.brand h1{font-size:30px;margin:0}.tagline{color:var(--dim);font-size:13px;margin-top:5px;max-width:900px}
.ticker{display:flex;overflow-x:auto;background:var(--panel2);border:1px solid var(--border);border-radius:4px;margin:8px 0 24px}.tick{padding:10px 17px;border-right:1px solid var(--soft);white-space:nowrap;font-family:'IBM Plex Mono',monospace;font-size:10.5px}.tick span{color:var(--dim);margin-right:7px}.tick b{color:var(--text)}.live{color:var(--live)!important}.up{color:var(--safe)!important}.down{color:var(--flag)!important}
.section{margin:26px 0 12px}.section h2{font-size:23px;margin-bottom:4px}.section p{color:var(--dim);font-size:12.5px;margin:0}.panel{background:var(--panel);border:1px solid var(--border);border-radius:5px;padding:18px 20px;margin-bottom:16px}.panel-head{font-family:'IBM Plex Mono',monospace;font-size:10px;letter-spacing:.09em;text-transform:uppercase;color:var(--accent);margin-bottom:12px}
.kpi-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin:14px 0 18px}.kpi{background:var(--panel);border:1px solid var(--border);border-radius:5px;padding:14px}.klabel{font-family:'IBM Plex Mono',monospace;font-size:9px;text-transform:uppercase;color:var(--dim)}.kvalue{font-family:'Fraunces',Georgia,serif;font-size:22px;font-weight:600;margin-top:5px}.kdelta{font-family:'IBM Plex Mono',monospace;font-size:9.5px;margin-top:4px;color:var(--dim)}
.action{border:1px solid var(--border);border-left:3px solid var(--watch);background:var(--panel2);border-radius:4px;padding:14px 16px;margin-bottom:9px}.action.readnow{border-left-color:var(--flag)}.action.review{border-left-color:var(--accent)}.action.monitor{border-left-color:var(--watch)}.action.ignore{border-left-color:#5d6375}.action-top{display:flex;justify-content:space-between;gap:12px}.priority{font-family:'IBM Plex Mono',monospace;font-size:9.5px;letter-spacing:.08em}.confidence{font-family:'IBM Plex Mono',monospace;font-size:9px;color:var(--dim)}.action-title{font-family:'Fraunces',Georgia,serif;font-size:15px;margin:6px 0}.action-body{font-size:12px;color:var(--dim);line-height:1.6}.action-body b{color:var(--text)}
.badge{display:inline-block;font-family:'IBM Plex Mono',monospace;font-size:9px;letter-spacing:.06em;padding:3px 7px;border-radius:3px;background:rgba(79,209,197,.12);color:var(--live);border:1px solid rgba(79,209,197,.25)}.source{font-family:'IBM Plex Mono',monospace;font-size:9.5px;color:var(--dim);padding:8px 0;border-bottom:1px solid var(--soft)}.source a{color:var(--live);text-decoration:none}.small{font-size:10.5px;color:var(--dim)}.empty{padding:55px 24px;text-align:center;background:var(--panel);border:1px dashed var(--border);border-radius:5px;color:var(--dim)}.identity{display:flex;gap:18px;align-items:center}.identity-symbol{font-family:'IBM Plex Mono',monospace;color:var(--accent);font-size:12px}.identity-name{font-family:'Fraunces',Georgia,serif;font-size:25px}.identity-meta{font-family:'IBM Plex Mono',monospace;font-size:10px;color:var(--dim);margin-top:3px}
.stButton>button{font-family:'IBM Plex Mono',monospace!important;font-size:10.5px!important;letter-spacing:.04em;background:var(--accent)!important;color:#0D0F16!important;border:0!important;border-radius:4px!important;font-weight:600!important}.stTabs [data-baseweb="tab"]{font-family:'IBM Plex Mono',monospace;font-size:10.5px;color:var(--dim)}.stTabs [aria-selected="true"]{color:var(--accent)}hr{border-color:var(--border)!important}
@media(max-width:1000px){.kpi-grid{grid-template-columns:repeat(2,1fr)}}
</style>""", unsafe_allow_html=True)


def esc(x):
    return html.escape(str(x))


def fmt(x, suffix=""):
    if x is None or x == "":
        return "—"
    try:
        v = float(x)
        a = abs(v)
        if a >= 1e12: s = f"{v/1e12:,.2f}T"
        elif a >= 1e9: s = f"{v/1e9:,.2f}B"
        elif a >= 1e6: s = f"{v/1e6:,.1f}M"
        elif a >= 1e3: s = f"{v/1e3:,.1f}K"
        else: s = f"{v:,.2f}"
        return s + suffix
    except Exception:
        return str(x)


def pct(x):
    try:
        return f"{float(x):+.1f}%"
    except Exception:
        return "—"


def sources_block(sources, limit=30):
    if not sources:
        st.markdown('<div class="small">No source list returned.</div>', unsafe_allow_html=True)
        return
    seen = set()
    for s in sources[:limit]:
        if not isinstance(s, dict):
            continue
        url = s.get("url") or ""
        if url in seen:
            continue
        seen.add(url)
        title = esc(s.get("title") or s.get("publisher") or "Source")
        date = esc(s.get("publication_date") or s.get("date") or s.get("as_of") or "")
        typ = esc(s.get("source_type") or "")
        if url:
            st.markdown(f'<div class="source">{title} · {date} · {typ} · <a href="{esc(url)}" target="_blank">open ↗</a></div>', unsafe_allow_html=True)


def run_research(query, exchange):
    cfg = get_config()
    gemini = GeminiResearchClient(cfg["GEMINI_API_KEY"], cfg["GEMINI_MODEL"])
    tavily = TavilyResearchClient(cfg["TAVILY_API_KEY"])
    today = datetime.now().strftime("%d %b %Y")

    with st.status("Running live research", expanded=True) as status:
        st.write("01 · Resolving the requested NSE/BSE security from live web data")
        identity = CompanyResolver(tavily).resolve(query, exchange, today)
        company = identity.get("company_name") or query
        symbol = identity.get("symbol") or query.upper()
        st.write(f"Resolved → {company} · {exchange}:{symbol}")

        st.write("02 · Financial Agent: statements, cash flow, balance sheet, management commentary")
        financial = FinancialAgent(gemini, tavily).run(company, exchange, symbol, today)

        st.write("03 · Industry Agent: competitors, sector news, reports and macro signals")
        industry = IndustryAgent(gemini, tavily).run(company, exchange, symbol, today)

        st.write("04 · Synthesis Agent: prioritizing the analyst work queue")
        synthesis = SynthesisAgent(gemini).run(f"{company} ({exchange}:{symbol})", financial, industry)
        status.update(label="Live research complete", state="complete", expanded=False)

    identity["sector"] = identity.get("sector") or financial.get("sector") or ""
    identity["industry"] = identity.get("industry") or financial.get("industry") or industry.get("industry") or ""
    st.session_state.identity = identity
    st.session_state.financial = financial
    st.session_state.industry = industry
    st.session_state.synthesis = synthesis
    st.session_state.query = query
    st.session_state.exchange = exchange
    st.session_state.updated = datetime.now().strftime("%d %b %Y · %H:%M")


# Dynamic company search — no fixed universe.
with st.sidebar:
    st.markdown('<div class="brand"><div class="mark">E</div><div><div class="eyebrow">LIVE RESEARCH</div><div style="font-family:Fraunces,Georgia,serif;font-size:19px">Equity Intelligence</div></div></div>', unsafe_allow_html=True)
    st.markdown("### COMPANY SEARCH")
    st.caption("Search any listed company. Nothing is preloaded or hard-coded.")
    exchange = st.selectbox("Exchange", ["NSE", "BSE"], index=0)
    query = st.text_input("Company / symbol / scrip", placeholder="e.g. Tata Motors, TCS, HDFCBANK")
    if st.button("RUN LIVE RESEARCH", use_container_width=True):
        try:
            if not query.strip():
                st.error("Enter a company name, symbol or scrip first.")
            else:
                run_research(query, exchange)
        except Exception as exc:
            st.error(f"Research failed: {exc}")
    if st.button("CLEAR CURRENT COMPANY", use_container_width=True):
        for k in ["identity", "financial", "industry", "synthesis", "query", "exchange", "updated"]:
            st.session_state.pop(k, None)
        st.rerun()
    st.markdown("---")
    st.markdown("**Required Streamlit Secrets**")
    st.code('GEMINI_API_KEY = "..."\nTAVILY_API_KEY = "..."\nGEMINI_MODEL = "gemini-2.5-flash-lite"', language="toml")
    st.caption("Live web retrieval: Tavily. AI analysis: Gemini. No company universe is stored in the app.")

identity = st.session_state.get("identity")
financial = st.session_state.get("financial")
industry = st.session_state.get("industry")
synthesis = st.session_state.get("synthesis")

st.markdown('<div class="brand"><div class="mark">E</div><div><div class="eyebrow">EQUITY RESEARCH INTELLIGENCE AGENT</div><h1>Research what matters next.</h1><div class="tagline">Choose any NSE/BSE security. The system resolves it, retrieves current public information, runs financial and industry agents, and turns the evidence into an analyst work queue.</div></div></div>', unsafe_allow_html=True)

if not identity or not financial or not industry or not synthesis:
    st.markdown('<div class="empty"><div style="font-family:Fraunces,Georgia,serif;font-size:26px;color:#EDEAE2;margin-bottom:8px">No company selected</div>Enter any NSE or BSE company in the sidebar and click <b>RUN LIVE RESEARCH</b>.<br><br>The dashboard fetches fresh web evidence only when you run a company.</div>', unsafe_allow_html=True)
    st.stop()

symbol = identity.get("symbol") or financial.get("ticker") or st.session_state.get("query", "—")
ex = identity.get("exchange") or st.session_state.get("exchange", "—")
name = identity.get("company_name") or financial.get("company") or "—"
sector = identity.get("sector") or ""
ind = identity.get("industry") or industry.get("industry") or ""
ms = financial.get("market_snapshot") or {}
latest = financial.get("latest") or {}
periods = financial.get("periods") or []
fh = financial.get("financial_health") or {}

change = ms.get("daily_change_pct")
change_class = "up" if isinstance(change, (int, float)) and change >= 0 else "down"

st.markdown(f'<div class="ticker"><div class="tick"><span>STATUS</span><b class="live">LIVE WEB RESEARCH</b></div><div class="tick"><span>SECURITY</span><b>{esc(symbol)} · {esc(ex)}</b></div><div class="tick"><span>PRICE</span><b>{esc(fmt(ms.get("price")))}</b></div><div class="tick"><span>DAY</span><b class="{change_class}">{esc(pct(change))}</b></div><div class="tick"><span>MARKET CAP</span><b>{esc(fmt(ms.get("market_cap")))}</b></div><div class="tick"><span>UPDATED</span><b>{esc(st.session_state.get("updated","—"))}</b></div></div>', unsafe_allow_html=True)

st.markdown(f'<div class="panel"><div class="identity"><div><div class="identity-symbol">{esc(symbol)} · {esc(ex)}</div><div class="identity-name">{esc(name)}</div><div class="identity-meta">{esc(sector)}{(" · " + esc(ind)) if ind else ""} · Current live research session</div></div><div style="margin-left:auto"><span class="badge">LIVE · TAVILY + GEMINI</span></div></div></div>', unsafe_allow_html=True)

# Analyst action center
st.markdown('<div class="section"><h2>ANALYST ACTION CENTER</h2><p>What deserves the analyst\'s time after the agents have researched the company and its surrounding industry?</p></div>', unsafe_allow_html=True)
actions = synthesis.get("actions") or []
counts = {p: sum(1 for a in actions if str(a.get("priority", "")).upper() == p) for p in ["READ NOW", "REVIEW", "MONITOR", "IGNORE"]}
cols = st.columns(4)
for c, p in zip(cols, ["READ NOW", "REVIEW", "MONITOR", "IGNORE"]):
    c.metric(p, counts[p])
for a in actions:
    p = str(a.get("priority", "MONITOR")).upper()
    cls = p.lower().replace(" ", "")
    st.markdown(f'<div class="action {cls}"><div class="action-top"><span class="priority">{esc(p)} · {esc(symbol)}</span><span class="confidence">CONF {esc(a.get("confidence",0))}/100</span></div><div class="action-title">{esc(a.get("title","Untitled"))}</div><div class="action-body"><b>Evidence:</b> {esc(a.get("evidence","—"))}<br><b>Why it matters:</b> {esc(a.get("why_it_matters","—"))}<br><b>Next:</b> {esc(a.get("analyst_question","—"))}</div></div>', unsafe_allow_html=True)
if not actions:
    st.info("No prioritized research actions returned.")

# Financial intelligence
st.markdown('<div class="section"><h2>COMPANY INTELLIGENCE</h2><p>Fresh financial statements, historical movement, cash-flow quality, balance-sheet risk and capital allocation.</p></div>', unsafe_allow_html=True)
vals = [
    ("Revenue", latest.get("revenue"), latest.get("revenue_growth")),
    ("Operating margin", latest.get("operating_margin"), latest.get("operating_margin_yoy") or latest.get("operating_margin_change")),
    ("Net income", latest.get("net_income"), latest.get("net_income_yoy") or latest.get("net_income_growth")),
    ("CFO", latest.get("cfo"), latest.get("cfo_yoy") or latest.get("cfo_growth")),
    ("FCF", latest.get("fcf"), latest.get("fcf_yoy") or latest.get("fcf_growth")),
]
html_cards = []
for label, value, delta in vals:
    suffix = "%" if "margin" in label.lower() and isinstance(value, (int, float)) else ""
    html_cards.append(f'<div class="kpi"><div class="klabel">{esc(label)}</div><div class="kvalue">{esc(fmt(value, suffix))}</div><div class="kdelta">Movement {esc(pct(delta) if isinstance(delta,(int,float)) else delta or "—")}</div></div>')
st.markdown('<div class="kpi-grid">' + "".join(html_cards) + "</div>", unsafe_allow_html=True)

c1, c2 = st.columns([1.25, 1])
with c1:
    st.markdown('<div class="panel"><div class="panel-head">Financial movement history</div>', unsafe_allow_html=True)
    if periods:
        df = pd.DataFrame(periods)
        show = [x for x in ["period","revenue","operating_income","net_income","cfo","capex","fcf","total_debt","cash","net_debt"] if x in df.columns]
        if show:
            st.dataframe(df[show], use_container_width=True, hide_index=True)
        chart_cols = [x for x in ["revenue","net_income","cfo","fcf"] if x in df.columns]
        if chart_cols and "period" in df.columns:
            st.line_chart(df[["period"] + chart_cols].copy().set_index("period"), use_container_width=True)
    else:
        st.caption("No historical table returned from the live evidence.")
    st.markdown('</div>', unsafe_allow_html=True)
with c2:
    st.markdown('<div class="panel"><div class="panel-head">Financial health</div>', unsafe_allow_html=True)
    st.metric("Analytical score", f"{fh.get('score','—')}/100")
    for d in (fh.get("drivers") or [])[:8]:
        st.markdown(f"• {esc(d)}")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="panel"><div class="panel-head">Capital allocation & strategic decisions</div>', unsafe_allow_html=True)
    for x in (financial.get("capital_allocation") or [])[:8]:
        st.markdown(f'**{esc(x.get("type","Decision"))}** — {esc(x.get("description", x.get("decision","—")))}')
    st.markdown('</div>', unsafe_allow_html=True)

with st.expander("Financial movement interpretation"):
    for m in (financial.get("movements") or [])[:12]:
        st.markdown(f'**{esc(m.get("metric", m.get("title","Movement")))}** · {esc(m.get("movement",""))}  \n{esc(m.get("why_it_matters", m.get("explanation","")))}')

with st.expander("Management commentary"):
    mc = financial.get("management_commentary") or []
    if isinstance(mc, list):
        for x in mc[:10]:
            if isinstance(x, dict):
                st.markdown(f'**{esc(x.get("topic","Commentary"))}** — {esc(x.get("comment", x.get("summary","—")))}')
            else:
                st.markdown(f"• {esc(x)}")
    else:
        st.write(mc)

# Industry intelligence
st.markdown('<div class="section"><h2>INDUSTRY INTELLIGENCE</h2><p>Competitor moves, current sector news, industry reports and macro transmission channels — filtered for economic relevance.</p></div>', unsafe_allow_html=True)
ci, cj = st.columns(2)
with ci:
    st.markdown('<div class="panel"><div class="panel-head">Industry snapshot</div>', unsafe_allow_html=True)
    st.write(industry.get("industry_snapshot", "—"))
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="panel"><div class="panel-head">Competitor moves</div>', unsafe_allow_html=True)
    for x in (industry.get("competitors") or [])[:8]:
        st.markdown(f'**{esc(x.get("company", x.get("name","Competitor")))}** — {esc(x.get("development", x.get("move","—")))}')
    st.markdown('</div>', unsafe_allow_html=True)
with cj:
    st.markdown('<div class="panel"><div class="panel-head">Recent material news</div>', unsafe_allow_html=True)
    for x in (industry.get("news") or [])[:10]:
        st.markdown(f'**{esc(x.get("title", x.get("headline","News")))}**  \n{esc(x.get("why_it_matters", x.get("implication","—")))}')
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="panel"><div class="panel-head">Macro / industry signals</div>', unsafe_allow_html=True)
    for x in (industry.get("macro_signals") or [])[:8]:
        st.markdown(f'**{esc(x.get("signal", x.get("name","Signal")))}** — {esc(x.get("implication", x.get("why_it_matters","—")))}')
    st.markdown('</div>', unsafe_allow_html=True)

with st.expander("Industry reports & research"):
    for x in (industry.get("industry_reports") or [])[:12]:
        st.markdown(f'**{esc(x.get("title","Report"))}** — {esc(x.get("finding", x.get("summary","—")))}')

# Final brief + sources
st.markdown('<div class="section"><h2>DAILY EQUITY RESEARCH BRIEF</h2><p>The synthesis agent converts the live evidence into the few things an analyst should investigate next.</p></div>', unsafe_allow_html=True)
st.markdown(f'<div class="panel"><div class="panel-head">Executive synthesis</div><div style="font-size:14px;line-height:1.7">{esc(synthesis.get("executive_summary","—"))}</div></div>', unsafe_allow_html=True)
b1, b2 = st.columns(2)
with b1:
    st.markdown('<div class="panel"><div class="panel-head">Top 3 things to know</div>', unsafe_allow_html=True)
    for i, x in enumerate((synthesis.get("top_three") or [])[:3], 1):
        st.markdown(f"**0{i}** · {esc(x)}")
    st.markdown('</div>', unsafe_allow_html=True)
with b2:
    st.markdown('<div class="panel"><div class="panel-head">Watch next</div>', unsafe_allow_html=True)
    for x in (synthesis.get("watch_next") or [])[:8]:
        st.markdown(f"• {esc(x)}")
    st.markdown('</div>', unsafe_allow_html=True)

with st.expander("SOURCE ROOM · live web evidence used"):
    allsrc = []
    allsrc += identity.get("sources") or []
    allsrc += financial.get("sources") or []
    allsrc += industry.get("sources") or []
    sources_block(allsrc)

st.markdown('<div class="small">Research-intelligence and prioritization only — not investment advice. Every run retrieves fresh public web evidence through Tavily and uses Gemini for analysis. No fixed company universe is embedded.</div>', unsafe_allow_html=True)
