from __future__ import annotations

import html
import json
from datetime import datetime

import streamlit as st

from agents.financial_agent import FinancialAgent
from agents.industry_agent import IndustryAgent
from agents.synthesis_agent import SynthesisAgent
from config import get_config
from llm.gemini_client import GeminiResearchClient
from data.demo_data import DEMO

st.set_page_config(page_title="Equity Research Intelligence", page_icon="◈", layout="wide", initial_sidebar_state="expanded")

# ----------------------------- STYLE -----------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');
:root{--bg:#090B10;--panel:#14161F;--panel2:#0F1119;--border:#252838;--soft:#1B1E29;--text:#EDEAE2;--dim:#8B8FA3;--accent:#E08D3C;--live:#4FD1C5;--safe:#4CAF66;--watch:#E0B23D;--flag:#D14F3D;}
.stApp{background:radial-gradient(ellipse 900px 500px at 15% -10%,rgba(224,141,60,.08),transparent 60%),var(--bg);color:var(--text);font-family:'IBM Plex Sans',sans-serif;}
.block-container{max-width:1220px;padding-top:2.2rem;padding-bottom:4rem;}
section[data-testid="stSidebar"]{background:#0D0F16;border-right:1px solid var(--border);}
section[data-testid="stSidebar"] *{font-family:'IBM Plex Sans',sans-serif;}
h1,h2,h3,h4{font-family:'Fraunces',Georgia,serif!important;color:var(--text)!important;}
.mono{font-family:'IBM Plex Mono',monospace!important;}
.brand{display:flex;gap:14px;align-items:center;border-bottom:1px solid var(--border);padding:0 0 20px;margin-bottom:18px;}
.mark{width:40px;height:40px;border-radius:6px;background:linear-gradient(135deg,var(--accent),#8A5A26);display:flex;align-items:center;justify-content:center;color:#0D0F16;font-family:'Fraunces',Georgia,serif;font-size:20px;font-weight:700;}
.eyebrow{font-family:'IBM Plex Mono',monospace;font-size:10px;letter-spacing:.16em;text-transform:uppercase;color:var(--accent);}
.brand h1{font-size:30px;margin:0;line-height:1.05;}
.tagline{color:var(--dim);font-size:13px;margin-top:4px;max-width:800px;}
.ticker{display:flex;overflow:hidden;background:var(--panel2);border:1px solid var(--border);border-radius:4px;margin:8px 0 22px;}
.tick{padding:10px 17px;border-right:1px solid var(--soft);white-space:nowrap;font-family:'IBM Plex Mono',monospace;font-size:11px;}
.tick span{color:var(--dim);margin-right:8px}.tick b{color:var(--text)}
.live{color:var(--live)!important}.up{color:var(--safe)!important}.down{color:var(--flag)!important}
.card{background:var(--panel);border:1px solid var(--border);border-radius:5px;padding:18px 19px;min-height:118px;}
.card .label{font-family:'IBM Plex Mono',monospace;font-size:9.5px;letter-spacing:.08em;text-transform:uppercase;color:var(--dim);}
.card .value{font-family:'Fraunces',Georgia,serif;font-size:27px;font-weight:600;margin:7px 0 2px;}
.card .sub{font-size:11.5px;color:var(--dim);}
.section{margin-top:26px;margin-bottom:10px;}.section h2{font-size:22px;margin-bottom:3px}.section p{color:var(--dim);font-size:12.5px;margin:0}
.panel{background:var(--panel);border:1px solid var(--border);border-radius:5px;padding:18px 20px;margin-bottom:16px;}
.panel-head{font-family:'IBM Plex Mono',monospace;font-size:10px;letter-spacing:.09em;text-transform:uppercase;color:var(--accent);margin-bottom:12px;}
.action{border:1px solid var(--border);border-left:3px solid var(--watch);background:var(--panel2);border-radius:4px;padding:13px 15px;margin-bottom:9px;}
.action.read{border-left-color:var(--flag)}.action.monitor{border-left-color:var(--watch)}.action.ignore{border-left-color:#5d6375}.action.review{border-left-color:var(--accent)}
.action-top{display:flex;justify-content:space-between;gap:12px;align-items:center}.priority{font-family:'IBM Plex Mono',monospace;font-size:9.5px;letter-spacing:.08em}.confidence{font-family:'IBM Plex Mono',monospace;font-size:9.5px;color:var(--dim)}
.action-title{font-family:'Fraunces',Georgia,serif;font-size:15px;margin:5px 0}.action-body{font-size:12px;color:var(--dim);line-height:1.55}.action-body b{color:var(--text)}
.kpi{background:var(--panel2);border:1px solid var(--border);border-radius:4px;padding:13px 14px;}.kpi-label{font-family:'IBM Plex Mono',monospace;font-size:9px;text-transform:uppercase;color:var(--dim);}.kpi-value{font-family:'Fraunces',Georgia,serif;font-size:20px;font-weight:600;margin-top:4px}.kpi-delta{font-family:'IBM Plex Mono',monospace;font-size:10px;margin-top:3px}
.source{font-family:'IBM Plex Mono',monospace;font-size:9.5px;color:var(--dim);padding:7px 0;border-bottom:1px solid var(--soft)}.source a{color:var(--live);text-decoration:none}.source:last-child{border-bottom:none}
.note{padding:12px 14px;background:var(--panel2);border-left:2px solid var(--accent);font-size:12px;color:var(--dim);line-height:1.55;border-radius:0 4px 4px 0;}
div.stButton>button{font-family:'IBM Plex Mono',monospace;font-size:10.5px;letter-spacing:.04em;background:var(--accent);color:#0D0F16;border:0;border-radius:4px;font-weight:600;padding:.55rem .9rem;}
div.stButton>button:hover{background:#eea05a;color:#0D0F16;}
.stTabs [data-baseweb="tab-list"]{gap:2px;border-bottom:1px solid var(--border);}.stTabs [data-baseweb="tab"]{font-family:'IBM Plex Mono',monospace;font-size:10.5px;color:var(--dim);padding:10px 13px;}.stTabs [aria-selected="true"]{color:var(--accent);}
[data-testid="stMetric"]{background:var(--panel2);border:1px solid var(--border);padding:12px;border-radius:4px;}.stMetricLabel{font-family:'IBM Plex Mono',monospace!important;font-size:9px!important;color:var(--dim)!important;text-transform:uppercase}.stMetricValue{font-family:'Fraunces',Georgia,serif!important;font-size:23px!important;color:var(--text)!important}.stMetricDelta{font-family:'IBM Plex Mono',monospace!important;font-size:10px!important}
hr{border-color:var(--border)!important;}
.small{font-size:11px;color:var(--dim)}
</style>
""", unsafe_allow_html=True)


def esc(x):
    return html.escape(str(x))


def money(x, currency=""):
    if x is None or x == "":
        return "—"
    try:
        v = float(x)
    except Exception:
        return str(x)
    a = abs(v)
    if a >= 1_000_000_000:
        s = f"{v/1e9:,.2f}B"
    elif a >= 1_000_000:
        s = f"{v/1e6:,.1f}M"
    elif a >= 1_000:
        s = f"{v/1e3:,.1f}K"
    else:
        s = f"{v:,.2f}"
    return f"{currency} {s}".strip()


def pct(x):
    if x is None:
        return "—"
    try:
        return f"{float(x):+.1f}%"
    except Exception:
        return str(x)


def render_sources(sources):
    if not sources:
        st.markdown('<div class="small">No source list returned.</div>', unsafe_allow_html=True)
        return
    for s in sources[:12]:
        url = s.get("url") or s.get("link") or ""
        title = s.get("title") or s.get("publisher") or "Source"
        date = s.get("publication_date") or s.get("date") or s.get("as_of") or ""
        if url:
            st.markdown(f'<div class="source">{esc(title)} · {esc(date)} · <a href="{esc(url)}" target="_blank">open source ↗</a></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="source">{esc(title)} · {esc(date)}</div>', unsafe_allow_html=True)


def action_html(a):
    priority = str(a.get("priority", "MONITOR")).upper()
    cls = {"READ NOW":"read","REVIEW":"review","MONITOR":"monitor","IGNORE":"ignore"}.get(priority,"monitor")
    conf = a.get("confidence", "—")
    return f'''<div class="action {cls}">
      <div class="action-top"><span class="priority">{esc(priority)} · {esc(a.get('company_or_sector',''))}</span><span class="confidence">CONF {esc(conf)}/100</span></div>
      <div class="action-title">{esc(a.get('development',''))}</div>
      <div class="action-body"><b>Why it matters:</b> {esc(a.get('why_it_matters',''))}<br><b>Next:</b> {esc(a.get('action',''))}</div>
    </div>'''


cfg = get_config()

if "financial" not in st.session_state:
    st.session_state.financial = {}
if "industry" not in st.session_state:
    st.session_state.industry = None
if "synthesis" not in st.session_state:
    st.session_state.synthesis = None
if "errors" not in st.session_state:
    st.session_state.errors = []

# ----------------------------- SIDEBAR -----------------------------
st.sidebar.markdown("### COVERAGE")
st.sidebar.caption("Companies the agent will research")
watch_text = st.sidebar.text_area("Watchlist", ", ".join(cfg["watchlist"]), height=90, help="Comma-separated tickers. Use exchange suffixes where useful, e.g. RELIANCE.NS.")
watchlist = [x.strip().upper() for x in watch_text.split(",") if x.strip()]
watchlist = watchlist[: cfg["max_companies_per_run"]]
selected = st.sidebar.selectbox("Company detail", watchlist if watchlist else cfg["watchlist"])

st.sidebar.markdown("---")
st.sidebar.markdown("### RUN CONTROL")
st.sidebar.caption("Gemini is the only external intelligence/data interface. Google Search grounding supplies current public web evidence; calculations happen locally in Python.")
run_fin = st.sidebar.button("Run Financial Intelligence", use_container_width=True)
run_ind = st.sidebar.button("Run Industry Intelligence", use_container_width=True)
run_all = st.sidebar.button("Run Full Research Cycle", use_container_width=True)

if not cfg["gemini_api_key"]:
    st.sidebar.error("GEMINI_API_KEY is not configured.")
    st.sidebar.caption("Add it under Streamlit → Manage app → Settings → Secrets.")

client = None
if cfg["gemini_api_key"]:
    try:
        client = GeminiResearchClient(cfg["gemini_api_key"], cfg["gemini_model"])
    except Exception as e:
        st.session_state.errors.append(str(e))

# ----------------------------- RUNS -----------------------------
def run_financial_cycle():
    if not client:
        st.error("Gemini API key is missing. Configure Streamlit Secrets first.")
        return
    agent = FinancialAgent(client)
    progress = st.progress(0, text="Starting financial intelligence…")
    for i, ticker in enumerate(watchlist):
        try:
            progress.progress(i / max(1, len(watchlist)), text=f"Researching {ticker} financial statements…")
            st.session_state.financial[ticker] = agent.run(ticker)
        except Exception as e:
            st.session_state.errors.append(f"{ticker}: {e}")
    progress.progress(1.0, text="Financial intelligence complete")


def run_industry_cycle():
    if not client:
        st.error("Gemini API key is missing. Configure Streamlit Secrets first.")
        return
    with st.spinner("Scanning competitors, sector news and macro drivers…"):
        try:
            st.session_state.industry = IndustryAgent(client).run(watchlist)
        except Exception as e:
            st.session_state.errors.append(f"Industry: {e}")


def run_full_cycle():
    run_financial_cycle()
    if client:
        try:
            st.session_state.industry = IndustryAgent(client).run(watchlist)
        except Exception as e:
            st.session_state.errors.append(f"Industry: {e}")
        if st.session_state.financial and st.session_state.industry:
            try:
                st.session_state.synthesis = SynthesisAgent(client).run(st.session_state.financial, st.session_state.industry)
            except Exception as e:
                st.session_state.errors.append(f"Synthesis: {e}")

if run_fin:
    run_financial_cycle()
if run_ind:
    run_industry_cycle()
if run_all:
    run_full_cycle()

# ----------------------------- HEADER -----------------------------
st.markdown('''<div class="brand"><div class="mark">E</div><div><div class="eyebrow">Equity Research · Intelligence Console</div><h1>EQUITY RESEARCH INTELLIGENCE</h1><div class="tagline">An autonomous research layer that turns financial statements, industry moves and market context into a prioritized analyst work queue.</div></div></div>''', unsafe_allow_html=True)

updated = datetime.now().strftime("%d %b %Y · %H:%M")
ticker_items = [
    ("STATUS", "LIVE SESSION", "live"),
    ("COVERAGE", f"{len(watchlist)} names", ""),
    ("FINANCIAL", f"{len(st.session_state.financial)}/{len(watchlist)} analyzed", ""),
    ("INDUSTRY", "READY" if st.session_state.industry else "PENDING", ""),
    ("UPDATED", updated, ""),
]
st.markdown('<div class="ticker">' + ''.join([f'<div class="tick"><span>{esc(a)}</span><b class="{c}">{esc(b)}</b></div>' for a,b,c in ticker_items]) + '</div>', unsafe_allow_html=True)

# ----------------------------- ACTION CENTER -----------------------------
syn = st.session_state.synthesis
actions = (syn or {}).get("actions", [])
if not actions:
    actions = DEMO["actions"]
    demo_mode = True
else:
    demo_mode = False

st.markdown('<div class="section"><h2>ANALYST ACTION CENTER</h2><p>What deserves your time today? The agent ranks changes by materiality, novelty, confidence and research relevance.</p></div>', unsafe_allow_html=True)
cols = st.columns(4)
counts = {k: sum(1 for a in actions if str(a.get("priority","")).upper()==k) for k in ["READ NOW","REVIEW","MONITOR","IGNORE"]}
for col, key in zip(cols, ["READ NOW","REVIEW","MONITOR","IGNORE"]):
    col.markdown(f'<div class="card"><div class="label">{key}</div><div class="value">{counts[key]}</div><div class="sub">research items</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
for a in actions[:8]:
    st.markdown(action_html(a), unsafe_allow_html=True)
if demo_mode:
    st.info("Demo shell shown. Click **Run Full Research Cycle** in the sidebar to replace it with live, source-grounded research.")

# ----------------------------- TABS -----------------------------
tab1, tab2, tab3, tab4 = st.tabs(["COMPANY INTELLIGENCE", "INDUSTRY MONITOR", "DAILY RESEARCH BRIEF", "METHODOLOGY"])

with tab1:
    d = st.session_state.financial.get(selected)
    st.markdown(f'<div class="section"><h2>{esc(selected)} · Financial Intelligence</h2><p>Real reported statement data + local calculations + Gemini evidence synthesis. No generic company summary.</p></div>', unsafe_allow_html=True)
    if not d:
        st.markdown('<div class="panel"><div class="note">No live company dataset yet. Run Financial Intelligence or the Full Research Cycle.</div></div>', unsafe_allow_html=True)
    else:
        latest = d.get("latest", {})
        health = d.get("financial_health", {})
        periods = d.get("periods", [])
        currency = d.get("currency", "")
        k = st.columns(5)
        metrics = [
            ("Revenue", latest.get("revenue"), None),
            ("Operating margin", latest.get("operating_margin"), "%"),
            ("Net margin", latest.get("net_margin"), "%"),
            ("CFO", latest.get("cash_from_operations"), None),
            ("Net debt", latest.get("net_debt"), None),
        ]
        for col,(lab,val,unit) in zip(k,metrics):
            display = "—" if val is None else (f"{val:.1f}%" if unit=="%" else money(val,currency))
            col.markdown(f'<div class="kpi"><div class="kpi-label">{lab}</div><div class="kpi-value">{esc(display)}</div></div>', unsafe_allow_html=True)

        st.markdown('<div class="section"><h2>Financial Health</h2></div>', unsafe_allow_html=True)
        hc = st.columns(3)
        hs = health.get("score", health.get("financial_health_score", "—"))
        read = health.get("read", health.get("summary", ""))
        hc[0].metric("HEALTH SCORE", f"{hs}/100" if hs != "—" else "—")
        hc[1].metric("LATEST PERIOD", str(d.get("as_of", "—")))
        hc[2].metric("HISTORICAL PERIODS", len(periods))
        if read:
            st.markdown(f'<div class="note">{esc(read)}</div>', unsafe_allow_html=True)

        # Historical charts: built from returned real numbers.
        if periods:
            labels = [str(p.get("period", p.get("date", i+1))) for i,p in enumerate(periods)]
            rev = {labels[i]: periods[i].get("revenue") for i in range(len(periods)) if periods[i].get("revenue") is not None}
            margin_series = {labels[i]: periods[i].get("operating_margin") for i in range(len(periods)) if periods[i].get("operating_margin") is not None}
            c1,c2 = st.columns(2)
            with c1:
                st.markdown('<div class="panel"><div class="panel-head">Revenue trajectory</div>', unsafe_allow_html=True)
                if rev: st.line_chart(rev, height=230)
                st.markdown('</div>', unsafe_allow_html=True)
            with c2:
                st.markdown('<div class="panel"><div class="panel-head">Operating margin trajectory</div>', unsafe_allow_html=True)
                if margin_series: st.line_chart(margin_series, height=230)
                st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="section"><h2>Statement Movements</h2><p>Latest-period changes the agent believes deserve analyst attention.</p></div>', unsafe_allow_html=True)
        moves = d.get("movements", [])
        if moves:
            for m in moves[:10]:
                st.markdown(action_html({
                    "priority": m.get("priority", "REVIEW"),
                    "company_or_sector": selected,
                    "development": m.get("metric", m.get("change", "Financial movement")),
                    "why_it_matters": m.get("interpretation", m.get("why_it_matters", "")),
                    "action": m.get("analyst_action", m.get("action", "Investigate")),
                    "confidence": m.get("confidence", "—"),
                }), unsafe_allow_html=True)
        else:
            st.caption("No structured movement list returned.")

        c1,c2 = st.columns(2)
        with c1:
            st.markdown('<div class="panel"><div class="panel-head">Anomalies / breaks from history</div>', unsafe_allow_html=True)
            for a in d.get("anomalies", [])[:8]:
                st.markdown(f'<div class="fact"><b>{esc(a.get("metric", a.get("title", "Anomaly")))}</b><br><span class="small">{esc(a.get("explanation", a.get("description", "")))}</span></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="panel"><div class="panel-head">Capital allocation</div>', unsafe_allow_html=True)
            for a in d.get("capital_allocation", [])[:8]:
                st.markdown(f'<div class="fact"><b>{esc(a.get("decision", a.get("type", "Decision")))}</b><br><span class="small">{esc(a.get("implication", a.get("why_it_matters", "")))}</span></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="panel"><div class="panel-head">Research actions</div>', unsafe_allow_html=True)
        for q in d.get("research_actions", [])[:10]:
            st.markdown(f"- {esc(q)}")
        st.markdown('</div>', unsafe_allow_html=True)

        with st.expander("Evidence & sources"):
            render_sources(d.get("sources", []))

with tab2:
    ind = st.session_state.industry
    st.markdown('<div class="section"><h2>Industry Monitor</h2><p>Competitor moves, sector news and macro drivers are deduplicated into impact-oriented developments.</p></div>', unsafe_allow_html=True)
    if not ind:
        st.markdown('<div class="panel"><div class="note">No live industry scan yet. Run Industry Intelligence or the Full Research Cycle.</div></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="note"><b>{esc(ind.get("industry","Relevant industries"))}</b><br>{esc(ind.get("industry_read",""))}</div>', unsafe_allow_html=True)
        st.markdown('<div class="section"><h2>Competitor Moves</h2></div>', unsafe_allow_html=True)
        for item in ind.get("competitor_moves", [])[:10]:
            st.markdown(action_html({
                "priority": item.get("priority", "REVIEW"),
                "company_or_sector": item.get("company", item.get("affected_companies", "Industry")),
                "development": item.get("development", item.get("move", "")),
                "why_it_matters": item.get("impact", item.get("why_it_matters", "")),
                "action": item.get("analyst_action", item.get("action", "")),
                "confidence": item.get("confidence", "—"),
            }), unsafe_allow_html=True)
        st.markdown('<div class="section"><h2>Sector News & Macro</h2></div>', unsafe_allow_html=True)
        c1,c2=st.columns(2)
        with c1:
            st.markdown('<div class="panel"><div class="panel-head">Sector developments</div>', unsafe_allow_html=True)
            for item in ind.get("sector_news", [])[:10]:
                st.markdown(f'<div class="fact"><b>{esc(item.get("headline", item.get("development", "News")))}</b><br><span class="small">{esc(item.get("why_it_matters", item.get("impact", "")))}</span></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="panel"><div class="panel-head">Macro snapshot</div>', unsafe_allow_html=True)
            for item in ind.get("macro_snapshot", [])[:10]:
                st.markdown(f'<div class="fact"><b>{esc(item.get("metric", item.get("indicator", "Macro")))}</b> · {esc(item.get("direction", ""))}<br><span class="small">{esc(item.get("why_it_matters", item.get("impact", "")))}</span></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with st.expander("Industry sources"):
            render_sources(ind.get("sources", []))

with tab3:
    st.markdown('<div class="section"><h2>Daily Equity Research Brief</h2><p>The synthesis layer answers one question: what should an analyst spend time on next?</p></div>', unsafe_allow_html=True)
    if not syn:
        st.markdown('<div class="panel"><div class="note">Run the Full Research Cycle to generate the cross-company daily brief.</div></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="panel"><div class="panel-head">Senior research read</div><div style="font-size:14px;line-height:1.65">{esc(syn.get("daily_read",""))}</div></div>', unsafe_allow_html=True)
        c1,c2=st.columns(2)
        with c1:
            st.markdown('<div class="panel"><div class="panel-head">Top three</div>', unsafe_allow_html=True)
            for i,x in enumerate(syn.get("top_three", [])[:3],1): st.markdown(f"**0{i}** · {esc(x)}")
            st.markdown('</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="panel"><div class="panel-head">Watch next</div>', unsafe_allow_html=True)
            for x in syn.get("watch_next", [])[:5]: st.markdown(f"- {esc(x)}")
            st.markdown('</div>', unsafe_allow_html=True)

with tab4:
    st.markdown('<div class="section"><h2>How the Agent Works</h2><p>Designed to automate repetitive equity-research triage while keeping evidence and calculations visible.</p></div>', unsafe_allow_html=True)
    stages = [
        ("01", "COLLECT", "Gemini + Google Search grounding finds current public filings, company disclosures, financial data, competitor announcements, macro releases and sector news."),
        ("02", "NORMALIZE", "Gemini returns structured statement periods and event records. Python performs transparent local calculations such as margins, FCF, net debt and percentage movements."),
        ("03", "DETECT", "Historical periods are used to surface breaks in margins, cash conversion, working capital, leverage, capex and capital allocation."),
        ("04", "IMPACT", "Industry events are translated from headline → affected company → transmission mechanism → research question."),
        ("05", "TRIAGE", "The synthesis layer ranks what deserves analyst time as READ NOW, REVIEW, MONITOR or IGNORE."),
    ]
    for num,title,desc in stages:
        st.markdown(f'<div class="panel"><span class="eyebrow">{num} · {title}</span><div style="font-family:Fraunces,Georgia,serif;font-size:16px;margin:5px 0">{esc(desc)}</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="note"><b>Important:</b> This is a research-assistance system, not an autonomous trading or investment-advice engine. It is deliberately designed to show source evidence and formulate questions for an analyst to investigate.</div>', unsafe_allow_html=True)

if st.session_state.errors:
    with st.expander(f"Run diagnostics ({len(st.session_state.errors)})"):
        for e in st.session_state.errors[-10:]: st.error(e)
