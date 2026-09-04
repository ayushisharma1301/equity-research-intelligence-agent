from __future__ import annotations
import html, json
from datetime import datetime
import pandas as pd
import streamlit as st

from config import get_config
from llm.gemini_client import GeminiResearchClient
from agents.company_resolver import CompanyResolver
from agents.financial_agent import FinancialAgent
from agents.industry_agent import IndustryAgent
from agents.synthesis_agent import SynthesisAgent

st.set_page_config(page_title='Equity Research Intelligence', page_icon='E', layout='wide', initial_sidebar_state='expanded')

st.markdown('''<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');
:root{--bg:#090B10;--bg2:#0D0F16;--panel:#14161F;--panel2:#0F1119;--border:#252838;--soft:#1B1E29;--text:#EDEAE2;--dim:#8B8FA3;--accent:#E08D3C;--live:#4FD1C5;--safe:#4CAF66;--watch:#E0B23D;--flag:#D14F3D;}
.stApp{background:radial-gradient(ellipse 900px 500px at 15% -10%,rgba(224,141,60,.08),transparent 60%),var(--bg);color:var(--text);font-family:'IBM Plex Sans',sans-serif}.block-container{max-width:1240px;padding-top:1.6rem;padding-bottom:4rem}section[data-testid="stSidebar"]{background:var(--bg2);border-right:1px solid var(--border)}
h1,h2,h3,h4,h5{font-family:'Fraunces',Georgia,serif!important;color:var(--text)!important}.brand{display:flex;gap:14px;align-items:center;border-bottom:1px solid var(--border);padding-bottom:20px;margin-bottom:18px}.mark{width:40px;height:40px;border-radius:6px;background:linear-gradient(135deg,var(--accent),#8A5A26);display:flex;align-items:center;justify-content:center;color:#0D0F16;font-family:'Fraunces',Georgia,serif;font-size:21px;font-weight:700}.eyebrow{font-family:'IBM Plex Mono',monospace;font-size:10px;letter-spacing:.16em;text-transform:uppercase;color:var(--accent)}.brand h1{font-size:30px;margin:0}.tagline{color:var(--dim);font-size:13px;margin-top:5px;max-width:900px}
.ticker{display:flex;overflow-x:auto;background:var(--panel2);border:1px solid var(--border);border-radius:4px;margin:8px 0 24px}.tick{padding:10px 17px;border-right:1px solid var(--soft);white-space:nowrap;font-family:'IBM Plex Mono',monospace;font-size:10.5px}.tick span{color:var(--dim);margin-right:7px}.tick b{color:var(--text)}.live{color:var(--live)!important}.up{color:var(--safe)!important}.down{color:var(--flag)!important}
.section{margin:26px 0 12px}.section h2{font-size:23px;margin-bottom:4px}.section p{color:var(--dim);font-size:12.5px;margin:0}.panel{background:var(--panel);border:1px solid var(--border);border-radius:5px;padding:18px 20px;margin-bottom:16px}.panel-head{font-family:'IBM Plex Mono',monospace;font-size:10px;letter-spacing:.09em;text-transform:uppercase;color:var(--accent);margin-bottom:12px}
.kpi-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin:14px 0 18px}.kpi{background:var(--panel);border:1px solid var(--border);border-radius:5px;padding:14px}.klabel{font-family:'IBM Plex Mono',monospace;font-size:9px;text-transform:uppercase;color:var(--dim)}.kvalue{font-family:'Fraunces',Georgia,serif;font-size:22px;font-weight:600;margin-top:5px}.kdelta{font-family:'IBM Plex Mono',monospace;font-size:9.5px;margin-top:4px;color:var(--dim)}
.action{border:1px solid var(--border);border-left:3px solid var(--watch);background:var(--panel2);border-radius:4px;padding:14px 16px;margin-bottom:9px}.action.read{border-left-color:var(--flag)}.action.review{border-left-color:var(--accent)}.action.monitor{border-left-color:var(--watch)}.action.ignore{border-left-color:#5d6375}.action-top{display:flex;justify-content:space-between;gap:12px}.priority{font-family:'IBM Plex Mono',monospace;font-size:9.5px;letter-spacing:.08em}.confidence{font-family:'IBM Plex Mono',monospace;font-size:9px;color:var(--dim)}.action-title{font-family:'Fraunces',Georgia,serif;font-size:15px;margin:6px 0}.action-body{font-size:12px;color:var(--dim);line-height:1.6}.action-body b{color:var(--text)}
.badge{display:inline-block;font-family:'IBM Plex Mono',monospace;font-size:9px;letter-spacing:.06em;padding:3px 7px;border-radius:3px;background:rgba(79,209,197,.12);color:var(--live);border:1px solid rgba(79,209,197,.25)}.source{font-family:'IBM Plex Mono',monospace;font-size:9.5px;color:var(--dim);padding:8px 0;border-bottom:1px solid var(--soft)}.source a{color:var(--live);text-decoration:none}.small{font-size:10.5px;color:var(--dim)}.empty{padding:55px 24px;text-align:center;background:var(--panel);border:1px dashed var(--border);border-radius:5px;color:var(--dim)}.identity{display:flex;gap:18px;align-items:center}.identity-symbol{font-family:'IBM Plex Mono',monospace;color:var(--accent);font-size:12px}.identity-name{font-family:'Fraunces',Georgia,serif;font-size:25px}.identity-meta{font-family:'IBM Plex Mono',monospace;font-size:10px;color:var(--dim);margin-top:3px}.statusline{font-family:'IBM Plex Mono',monospace;font-size:10px;color:var(--dim)}
.stButton>button{font-family:'IBM Plex Mono',monospace!important;font-size:10.5px!important;letter-spacing:.04em;background:var(--accent)!important;color:#0D0F16!important;border:0!important;border-radius:4px!important;font-weight:600!important}.stTabs [data-baseweb="tab"]{font-family:'IBM Plex Mono',monospace;font-size:10.5px;color:var(--dim)}.stTabs [aria-selected="true"]{color:var(--accent)}hr{border-color:var(--border)!important}
@media(max-width:1000px){.kpi-grid{grid-template-columns:repeat(2,1fr)}}
</style>''', unsafe_allow_html=True)

def esc(x): return html.escape(str(x))
def fmt(x, suffix=''):
    if x is None or x=='': return '—'
    try:
        v=float(x); a=abs(v)
        if a>=1e12:s=f'{v/1e12:,.2f}T'
        elif a>=1e9:s=f'{v/1e9:,.2f}B'
        elif a>=1e6:s=f'{v/1e6:,.1f}M'
        elif a>=1e3:s=f'{v/1e3:,.1f}K'
        else:s=f'{v:,.2f}'
        return s+suffix
    except:return str(x)
def pct(x):
    try:return f'{float(x):+.1f}%'
    except:return '—'
def sources_block(sources, limit=20):
    if not sources: st.markdown('<div class="small">No source list returned.</div>',unsafe_allow_html=True); return
    for s in sources[:limit]:
        if not isinstance(s,dict):continue
        title=esc(s.get('title') or s.get('publisher') or 'Source'); url=s.get('url') or ''; date=esc(s.get('publication_date') or s.get('date') or s.get('as_of') or ''); typ=esc(s.get('source_type') or '')
        if url: st.markdown(f'<div class="source">{title} · {date} · {typ} · <a href="{esc(url)}" target="_blank">open ↗</a></div>',unsafe_allow_html=True)
        else: st.markdown(f'<div class="source">{title} · {date} · {typ}</div>',unsafe_allow_html=True)

def run_research(query, exchange):
    cfg=get_config(); client=GeminiResearchClient(cfg['GEMINI_API_KEY'],cfg['GEMINI_MODEL']); today=datetime.now().strftime('%d %b %Y')
    resolver=CompanyResolver(client)
    identity=resolver.resolve(query,exchange,today)
    ticker=identity.get('symbol') or query
    canonical=f"{identity.get('company_name','')} ({ticker}, {identity.get('exchange',exchange)})"
    with st.status('Researching '+canonical,expanded=True) as status:
        st.write('01 · Identifying listed security')
        st.write('02 · Fetching financial statements, reports and management commentary')
        financial=FinancialAgent(client).run(canonical,today)
        st.write('03 · Scanning industry, competitors, macro and recent news')
        industry=IndustryAgent(client).run(canonical,today)
        st.write('04 · Synthesizing analyst priorities')
        synthesis=SynthesisAgent(client).run(canonical,financial,industry)
        status.update(label='Research complete',state='complete',expanded=False)
    st.session_state.identity=identity; st.session_state.financial=financial; st.session_state.industry=industry; st.session_state.synthesis=synthesis; st.session_state.query=query; st.session_state.exchange=exchange; st.session_state.updated=datetime.now().strftime('%d %b %Y · %H:%M')

# Sidebar: dynamic, no universe
with st.sidebar:
    st.markdown('''<div class="brand"><div class="mark">E</div><div><div class="eyebrow">LIVE RESEARCH</div><div style="font-family:Fraunces,Georgia,serif;font-size:19px">Equity Intelligence</div></div></div>''',unsafe_allow_html=True)
    st.markdown('### COMPANY SEARCH')
    st.caption('Choose any currently listed company. Nothing is preloaded.')
    exchange=st.selectbox('Exchange',['NSE','BSE'],index=0)
    query=st.text_input('Company / symbol / scrip',placeholder='e.g. Tata Motors, TCS, HDFCBANK')
    st.caption('Examples are only input hints — the agent resolves the actual NSE/BSE security live.')
    if st.button('RUN LIVE RESEARCH',use_container_width=True,disabled=not query.strip()):
        try: run_research(query.strip(),exchange)
        except Exception as e: st.error(f'Research failed: {e}')
    if st.button('CLEAR CURRENT COMPANY',use_container_width=True):
        for k in ['identity','financial','industry','synthesis','query','exchange','updated']:
            st.session_state.pop(k,None)
        st.rerun()
    st.markdown('---')
    st.markdown('### RESEARCH PIPELINE')
    st.caption('Gemini + Google Search grounding is the only external research interface. No fixed company universe and no static financial dataset.')

identity=st.session_state.get('identity'); financial=st.session_state.get('financial'); industry=st.session_state.get('industry'); synthesis=st.session_state.get('synthesis')

st.markdown('<div class="brand"><div class="mark">E</div><div><div class="eyebrow">Equity Research · Intelligence Console</div><h1>EQUITY RESEARCH INTELLIGENCE</h1><div class="tagline">Select any NSE or BSE company, let the agent collect current public evidence, reconstruct the financial picture, scan the industry and return a prioritized research queue.</div></div></div>',unsafe_allow_html=True)

if not identity:
    st.markdown('<div class="ticker"><div class="tick"><span>STATUS</span><b class="live">READY</b></div><div class="tick"><span>UNIVERSE</span><b>ANY NSE / BSE LISTED COMPANY</b></div><div class="tick"><span>DATA</span><b>NOT FETCHED</b></div><div class="tick"><span>MODE</span><b>LIVE RESEARCH</b></div></div>',unsafe_allow_html=True)
    st.markdown('<div class="empty"><h2>Choose a company to begin</h2><p>Use the left panel to select NSE or BSE and type any company name, symbol or scrip. The agent will resolve the security and then research its financial statements, reports, earnings-call commentary, industry, competitors and recent news.</p></div>',unsafe_allow_html=True)
    st.stop()

name=identity.get('company_name','Unknown'); symbol=identity.get('symbol','—'); ex=identity.get('exchange',st.session_state.get('exchange','—')); sector=identity.get('sector','—'); ind=identity.get('industry','—')
ms=(financial or {}).get('market_snapshot') or {}; latest=(financial or {}).get('latest') or {}; periods=(financial or {}).get('periods') or []
price=ms.get('price'); change=ms.get('daily_change_pct'); mcap=ms.get('market_cap'); fh=(financial or {}).get('financial_health') or {}

st.markdown(f'<div class="ticker"><div class="tick"><span>STATUS</span><b class="live">LIVE RESEARCH</b></div><div class="tick"><span>SECURITY</span><b>{esc(symbol)} · {esc(ex)}</b></div><div class="tick"><span>PRICE</span><b>{fmt(price)}</b></div><div class="tick"><span>DAY</span><b class="{"up" if isinstance(change,(int,float)) and change>=0 else "down"}">{pct(change)}</b></div><div class="tick"><span>UPDATED</span><b>{esc(st.session_state.get("updated","—"))}</b></div></div>',unsafe_allow_html=True)

st.markdown(f'<div class="panel"><div class="identity"><div><div class="identity-symbol">{esc(symbol)} · {esc(ex)}</div><div class="identity-name">{esc(name)}</div><div class="identity-meta">{esc(sector)} · {esc(ind)} · Current research session</div></div><div style="margin-left:auto"><span class="badge">LIVE · GEMINI GROUNDED</span></div></div></div>',unsafe_allow_html=True)

# Action center
st.markdown('<div class="section"><h2>ANALYST ACTION CENTER</h2><p>What deserves the analyst\'s time after the agent has researched the company and its surrounding industry?</p></div>',unsafe_allow_html=True)
actions=(synthesis or {}).get('actions') or []
counts={p:sum(1 for a in actions if str(a.get('priority','')).upper()==p) for p in ['READ NOW','REVIEW','MONITOR','IGNORE']}
cols=st.columns(4)
for c,p in zip(cols,['READ NOW','REVIEW','MONITOR','IGNORE']): c.metric(p,counts[p])
if actions:
    for a in actions:
        p=str(a.get('priority','MONITOR')).upper(); cls=p.lower().replace(' ','');
        st.markdown(f'<div class="action {cls}"><div class="action-top"><span class="priority">{esc(p)} · {esc(symbol)}</span><span class="confidence">CONF {esc(a.get("confidence",0))}/100</span></div><div class="action-title">{esc(a.get("title","Untitled"))}</div><div class="action-body"><b>Why it matters:</b> {esc(a.get("why_it_matters","—"))}<br><b>Next:</b> {esc(a.get("analyst_question","—"))}</div></div>',unsafe_allow_html=True)
else: st.info('No prioritized research actions returned.')

st.markdown('<div class="section"><h2>COMPANY INTELLIGENCE</h2><p>Fresh financial statements, historical movement, cash-flow quality, balance-sheet risk and capital allocation.</p></div>',unsafe_allow_html=True)

vals=[('Revenue',latest.get('revenue'),latest.get('revenue_growth')),('Operating margin',latest.get('operating_margin'),latest.get('operating_margin_change')),('Net income',latest.get('net_income'),latest.get('net_income_growth')),('CFO',latest.get('cfo'),latest.get('cfo_growth')),('FCF',latest.get('fcf'),latest.get('fcf_growth'))]
st.markdown('<div class="kpi-grid">'+''.join(f'<div class="kpi"><div class="klabel">{esc(l)}</div><div class="kvalue">{fmt(v,"%" if isinstance(v,str) and v.endswith("%") else "")}</div><div class="kdelta">Movement {esc(pct(d) if isinstance(d,(int,float)) else d or "—")}</div></div>' for l,v,d in vals)+'</div>',unsafe_allow_html=True)

c1,c2=st.columns([1.25,1])
with c1:
    st.markdown('<div class="panel"><div class="panel-head">Financial movement history</div></div>',unsafe_allow_html=True)
    if periods:
        df=pd.DataFrame(periods)
        show=[x for x in ['period','revenue','operating_income','net_income','cfo','capex','fcf','total_debt','cash','net_debt'] if x in df.columns]
        if show: st.dataframe(df[show],use_container_width=True,hide_index=True)
        chart_cols=[x for x in ['revenue','net_income','cfo','fcf'] if x in df.columns]
        if chart_cols:
            chart=df[['period']+chart_cols].copy().set_index('period'); st.line_chart(chart,use_container_width=True)
    else: st.caption('No historical table returned.')
with c2:
    st.markdown('<div class="panel"><div class="panel-head">Financial health</div>',unsafe_allow_html=True)
    st.metric('Analytical score',f"{fh.get('score','—')}/100")
    if fh.get('drivers'): 
        for d in fh.get('drivers',[]): st.markdown(f'• {esc(d)}')
    st.markdown('</div>',unsafe_allow_html=True)
    st.markdown('<div class="panel"><div class="panel-head">Capital allocation & strategic decisions</div>',unsafe_allow_html=True)
    for x in (financial or {}).get('capital_allocation',[])[:8]:
        st.markdown(f'**{esc(x.get("type","Decision"))}** — {esc(x.get("description",x.get("decision","—")))}')
    st.markdown('</div>',unsafe_allow_html=True)

with st.expander('Financial movement interpretation'):
    for m in (financial or {}).get('movements',[])[:12]: st.markdown(f'**{esc(m.get("metric",m.get("title","Movement")))}** · {esc(m.get("movement",""))}  \n{esc(m.get("why_it_matters",m.get("explanation","")))}')

# Industry
st.markdown('<div class="section"><h2>INDUSTRY INTELLIGENCE</h2><p>Competitor moves, industry reports, macro transmission channels and recent news — filtered for economic relevance.</p></div>',unsafe_allow_html=True)
ci,cj=st.columns(2)
with ci:
    st.markdown('<div class="panel"><div class="panel-head">Industry snapshot</div>',unsafe_allow_html=True)
    st.write((industry or {}).get('industry_snapshot','—')); st.markdown('</div>',unsafe_allow_html=True)
    st.markdown('<div class="panel"><div class="panel-head">Competitor moves</div>',unsafe_allow_html=True)
    for x in (industry or {}).get('competitors',[])[:8]: st.markdown(f'**{esc(x.get("company",x.get("name","Competitor")))}** — {esc(x.get("development",x.get("move","—")))}')
    st.markdown('</div>',unsafe_allow_html=True)
with cj:
    st.markdown('<div class="panel"><div class="panel-head">Recent material news</div>',unsafe_allow_html=True)
    for x in (industry or {}).get('news',[])[:10]:
        st.markdown(f'**{esc(x.get("title",x.get("headline","News")))}**  \n{esc(x.get("why_it_matters",x.get("implication","—")))}')
    st.markdown('</div>',unsafe_allow_html=True)
    st.markdown('<div class="panel"><div class="panel-head">Macro / industry signals</div>',unsafe_allow_html=True)
    for x in (industry or {}).get('macro_signals',[])[:8]: st.markdown(f'**{esc(x.get("signal",x.get("name","Signal")))}** — {esc(x.get("implication",x.get("why_it_matters","—")))}')
    st.markdown('</div>',unsafe_allow_html=True)

with st.expander('Industry reports & research'):
    for x in (industry or {}).get('industry_reports',[])[:12]: st.markdown(f'**{esc(x.get("title","Report"))}** — {esc(x.get("finding",x.get("summary","—")))}')

# Brief + sources
st.markdown('<div class="section"><h2>DAILY EQUITY RESEARCH BRIEF</h2><p>The final synthesis: what changed, why it matters and what to investigate next.</p></div>',unsafe_allow_html=True)
st.markdown(f'<div class="panel"><div class="panel-head">Executive synthesis</div><div style="font-size:14px;line-height:1.7">{esc((synthesis or {}).get("executive_summary","—"))}</div></div>',unsafe_allow_html=True)
b1,b2=st.columns(2)
with b1:
    st.markdown('<div class="panel"><div class="panel-head">Top 3 things to know</div>',unsafe_allow_html=True)
    for i,x in enumerate((synthesis or {}).get('top_three',[])[:3],1): st.markdown(f'**0{i}** · {esc(x)}')
    st.markdown('</div>',unsafe_allow_html=True)
with b2:
    st.markdown('<div class="panel"><div class="panel-head">Watch next</div>',unsafe_allow_html=True)
    for x in (synthesis or {}).get('watch_next',[])[:8]: st.markdown(f'• {esc(x)}')
    st.markdown('</div>',unsafe_allow_html=True)

with st.expander('SOURCE ROOM · every research source used'):
    allsrc=[]
    for pack in [financial,industry]: allsrc += (pack or {}).get('sources',[])
    sources_block(allsrc)

st.markdown('<div class="small">The system is a research-intelligence and prioritization tool, not investment advice. Current information depends on Gemini web-search grounding and source availability at run time.</div>',unsafe_allow_html=True)
