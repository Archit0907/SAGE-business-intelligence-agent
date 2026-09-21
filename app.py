import html
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

import streamlit as st


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="SAGE — Strategic Intelligence",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# OPENAI KEY (Streamlit secrets support)
# ============================================================

try:
    if "OPENAI_API_KEY" in st.secrets:
        os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
except Exception:
    pass


# ============================================================
# PATHS / CONSTANTS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
AGENT_PATH = BASE_DIR / "agent_v3.py"
REPORT_PATH = BASE_DIR / "sage_research_data.json"

STAGES = [
    ("01", "Research Design", "Framing the question"),
    ("02", "Web Research", "Gathering evidence"),
    ("03", "Business Intelligence", "Analyzing findings"),
    ("04", "Strategic Synthesis", "Building strategy"),
]

STAGE_MESSAGES = {
    1: "Designing the research plan for your business question...",
    2: "Searching the web and collecting market evidence...",
    3: "Converting evidence into business intelligence...",
    4: "Building strategic implications and recommendations...",
}

TAG_KEYS = [
    "severity", "likelihood", "impact", "priority", "potential", "magnitude",
    "timeframe", "timeline", "horizon", "effort", "confidence", "urgency", "owner",
]

MAIN_KEYS = [
    "finding", "insight", "title", "name", "pattern", "characteristic",
    "development", "trend", "point", "statement", "description", "text",
    "summary", "segment", "competitor", "opportunity", "risk", "action",
    "implication",
]

TEXT_KEYS = [
    "finding", "insight", "implication", "title", "name", "pattern",
    "development", "opportunity", "risk", "action", "recommendation",
    "description", "text", "summary",
]

BADGE_RULES = [
    ("HIGH FREQUENCY", ("frequen", "daily", "weekly", "habitual", "repeat")),
    ("PRICE SENSITIVE", ("price sensitiv", "price-sensitiv", "discount", "budget", "value-conscious", "cost-conscious", "affordab")),
    ("HIGH VALUE", ("high value", "high-value", "premium", "high spend", "high-spend", "willing to pay")),
    ("MULTI-HOMER", ("multi-hom", "multihom", "multiple apps", "multi-app", "multiple platforms", "switch between", "switching")),
    ("DISCOVERY LED", ("discover", "novelty", "trial", "explor", "recommendation")),
]

DOT_SPECS = [
    (6, 78, 3, 11, 0), (14, 62, 2, 14, -4), (24, 88, 3, 12, -7),
    (33, 70, 2, 16, -2), (45, 92, 3, 13, -9), (56, 80, 2, 10, -5),
    (64, 68, 3, 15, -11), (72, 90, 2, 12, -3), (80, 74, 3, 17, -6),
    (88, 86, 2, 11, -8), (93, 60, 3, 14, -1), (52, 58, 2, 18, -12),
]


# ============================================================
# GLOBAL CSS (rendered with st.html so it never shows as text)
# ============================================================

SAGE_CSS = r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root{
  --sg-ink:#12183a;
  --sg-text:#4a5473;
  --sg-muted:#7c86a2;
  --sg-line:#e4e7f6;
  --sg-mono: ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace;
}

/* ---------- base ---------- */
html, body, .stApp,
.stApp textarea, .stApp input, .stApp button{
  font-family:'Inter', ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}
.stApp{
  color-scheme: light;
  background:
    radial-gradient(1000px 520px at 6% -6%, rgba(99,102,241,.14), transparent 60%),
    radial-gradient(900px 520px at 100% 6%, rgba(139,92,246,.11), transparent 60%),
    radial-gradient(800px 500px at 50% 112%, rgba(34,211,238,.07), transparent 60%),
    linear-gradient(180deg,#fbfbff 0%,#f5f6fd 100%);
}
#MainMenu, footer, [data-testid="stDecoration"], [data-testid="stToolbar"]{
  display:none !important; visibility:hidden !important;
}
[data-testid="stHeader"]{ background:transparent !important; }
.block-container, [data-testid="stMainBlockContainer"]{
  max-width:1240px !important;
  padding:1.5rem 2rem 4rem !important;
}

/* ---------- keyframes ---------- */
@keyframes sgGradient{0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}}
@keyframes sgOrbA{0%,100%{transform:translate3d(0,0,0) scale(1)}50%{transform:translate3d(40px,30px,0) scale(1.12)}}
@keyframes sgOrbB{0%,100%{transform:translate3d(0,0,0) scale(1)}50%{transform:translate3d(-50px,-26px,0) scale(1.08)}}
@keyframes sgGridMove{from{background-position:0 0,0 0}to{background-position:44px 44px,44px 44px}}
@keyframes sgFloat{0%{transform:translate3d(0,0,0);opacity:0}15%{opacity:.9}85%{opacity:.9}100%{transform:translate3d(14px,-130px,0);opacity:0}}
@keyframes sgPulse{0%{box-shadow:0 0 0 0 rgba(52,211,153,.6)}70%{box-shadow:0 0 0 9px rgba(52,211,153,0)}100%{box-shadow:0 0 0 0 rgba(52,211,153,0)}}
@keyframes sgRise{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
@keyframes sgSweep{0%,55%{left:-60%}100%{left:140%}}
@keyframes sgIndeterminate{0%{transform:translateX(-100%)}100%{transform:translateX(330%)}}
@keyframes sgDots{0%{content:""}25%{content:"."}50%{content:".."}75%,100%{content:"..."}}
@keyframes sgGlow{0%,100%{box-shadow:0 40px 80px -30px rgba(90,60,220,.55),0 0 0 0 rgba(167,139,250,0)}50%{box-shadow:0 40px 90px -26px rgba(110,70,240,.75),0 0 0 6px rgba(167,139,250,.10)}}
@keyframes sgStageGlow{0%,100%{box-shadow:0 0 0 1px rgba(196,181,253,.25),0 16px 40px -14px rgba(139,92,246,.55)}50%{box-shadow:0 0 0 1px rgba(196,181,253,.5),0 20px 48px -12px rgba(139,92,246,.9)}}
@keyframes sgStepGlow{0%,30%,100%{box-shadow:none;background:rgba(255,255,255,.12)}10%,20%{box-shadow:0 0 0 6px rgba(167,139,250,.22);background:rgba(167,139,250,.45)}}

.sg-rise{animation:sgRise .7s cubic-bezier(.2,.7,.2,1) backwards}
.sg-grid > *{animation:sgRise .65s cubic-bezier(.2,.7,.2,1) backwards}
.sg-grid > *:nth-child(2){animation-delay:.07s}
.sg-grid > *:nth-child(3){animation-delay:.14s}
.sg-grid > *:nth-child(4){animation-delay:.21s}
.sg-grid > *:nth-child(n+5){animation-delay:.28s}

/* ---------- inputs ---------- */
div[data-baseweb="textarea"]{
  border-radius:18px !important;
  border:1px solid #e1e4f3 !important;
  background:#ffffff !important;
  box-shadow:0 12px 30px -14px rgba(40,50,120,.22) !important;
  transition:border-color .25s ease, box-shadow .25s ease, transform .25s ease !important;
}
div[data-baseweb="textarea"]:hover{ border-color:#c9cdf0 !important; }
div[data-baseweb="textarea"]:focus-within{
  border-color:#7c6cf0 !important;
  box-shadow:0 0 0 4px rgba(124,108,240,.14), 0 18px 40px -16px rgba(79,70,229,.4) !important;
}
div[data-baseweb="textarea"] div[data-baseweb="base-input"]{
  background:transparent !important; border:none !important; box-shadow:none !important;
}
div[data-baseweb="textarea"] textarea{
  background:transparent !important;
  color:#1c2340 !important;
  font-size:15px !important;
  line-height:1.6 !important;
  padding:16px 18px !important;
  border:none !important;
}
div[data-baseweb="textarea"] textarea::placeholder{ color:#a3aac4 !important; }

/* ---------- buttons ---------- */
.stButton > button{
  position:relative; overflow:hidden; width:100%;
  min-height:64px; border:0 !important; border-radius:18px !important;
  background:linear-gradient(110deg,#4338ca 0%,#6d4aed 35%,#8b5cf6 65%,#4f46e5 100%) 0% 50% / 220% 100% no-repeat !important;
  color:#ffffff !important; font-weight:700 !important; font-size:16.5px !important; letter-spacing:.2px;
  box-shadow:0 20px 40px -14px rgba(79,70,229,.6), inset 0 1px 0 rgba(255,255,255,.28) !important;
  transition:transform .25s ease, box-shadow .25s ease, background-position .7s ease !important;
}
.stButton > button:hover{
  transform:translateY(-2px);
  background-position:100% 50% !important;
  box-shadow:0 26px 50px -14px rgba(99,70,240,.75), inset 0 1px 0 rgba(255,255,255,.35) !important;
}
.stButton > button:active{ transform:translateY(0); }
.stButton > button p, .stButton > button span{ color:#ffffff !important; font-weight:700 !important; }
.stButton > button::after{
  content:""; position:absolute; top:0; left:-60%; width:38%; height:100%;
  background:linear-gradient(100deg,transparent,rgba(255,255,255,.38),transparent);
  transform:skewX(-20deg); animation:sgSweep 5s ease-in-out infinite; pointer-events:none;
}
.stDownloadButton > button, [data-testid="stDownloadButton"] > button{
  width:100%; min-height:54px; border-radius:16px !important;
  background:#ffffff !important; color:#4338ca !important;
  border:1px solid #d5d9f7 !important; font-weight:700 !important;
  box-shadow:0 12px 28px -16px rgba(79,70,229,.4) !important;
  transition:transform .2s ease, box-shadow .2s ease, border-color .2s ease !important;
}
.stDownloadButton > button:hover, [data-testid="stDownloadButton"] > button:hover{
  transform:translateY(-2px); border-color:#8b7cf6 !important;
  box-shadow:0 18px 34px -14px rgba(79,70,229,.5) !important;
}
.stDownloadButton > button p, [data-testid="stDownloadButton"] > button p{ color:#4338ca !important; font-weight:700 !important; }

/* ---------- hero ---------- */
.sg-hero{
  position:relative; isolation:isolate; overflow:hidden;
  border-radius:32px; padding:54px 56px 50px; color:#fff;
  background:linear-gradient(125deg,#080d29 0%,#131c5c 30%,#3b23a3 62%,#5b2fc9 82%,#1a2a7a 100%);
  background-size:220% 220%;
  animation:sgGradient 24s ease-in-out infinite;
  box-shadow:0 40px 90px -30px rgba(52,44,160,.55), inset 0 1px 0 rgba(255,255,255,.14);
}
.sg-hero-gridbg{
  position:absolute; inset:0; z-index:0; opacity:.16; pointer-events:none;
  background-image:linear-gradient(rgba(255,255,255,.55) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.55) 1px,transparent 1px);
  background-size:44px 44px;
  animation:sgGridMove 14s linear infinite;
  -webkit-mask-image:radial-gradient(ellipse at 70% 30%,#000 10%,transparent 72%);
  mask-image:radial-gradient(ellipse at 70% 30%,#000 10%,transparent 72%);
}
.sg-orb{ position:absolute; border-radius:50%; filter:blur(46px); pointer-events:none; z-index:0; }
.sg-orb.a{ width:340px; height:340px; right:-60px; top:-110px; background:rgba(139,92,246,.60); animation:sgOrbA 16s ease-in-out infinite; }
.sg-orb.b{ width:280px; height:280px; left:32%; bottom:-150px; background:rgba(34,211,238,.32); animation:sgOrbB 19s ease-in-out infinite; }
.sg-orb.c{ width:240px; height:240px; left:-70px; top:30%; background:rgba(99,102,241,.45); animation:sgOrbA 22s ease-in-out infinite reverse; }
.sg-dots{ position:absolute; inset:0; z-index:1; pointer-events:none; }
.sg-dots i{
  position:absolute; border-radius:50%; background:rgba(255,255,255,.85);
  box-shadow:0 0 10px rgba(196,181,253,.9); opacity:0;
  animation:sgFloat linear infinite;
}
.sg-hero-inner{
  position:relative; z-index:2; display:grid;
  grid-template-columns:minmax(0,1.5fr) minmax(0,.8fr); gap:44px; align-items:center;
}
.sg-brand{ display:flex; align-items:center; gap:16px; flex-wrap:wrap; margin-bottom:34px; }
.sg-logo{
  position:relative; width:54px; height:54px; border-radius:16px; display:grid; place-items:center;
  background:linear-gradient(135deg,rgba(255,255,255,.24),rgba(255,255,255,.06));
  border:1px solid rgba(255,255,255,.28);
  box-shadow:0 8px 24px rgba(0,0,0,.25), inset 0 1px 0 rgba(255,255,255,.3);
}
.sg-logo i{
  position:relative; width:22px; height:22px; border:3px solid #fff; border-radius:7px;
  transform:rotate(45deg); box-shadow:0 0 18px rgba(167,139,250,.9);
}
.sg-logo i::after{
  content:""; position:absolute; inset:3px; border-radius:50%;
  background:linear-gradient(135deg,#c4b5fd,#67e8f9);
}
.sg-logo.sm{ width:38px; height:38px; border-radius:12px; background:linear-gradient(135deg,#4f46e5,#8b5cf6); border:none; box-shadow:0 10px 20px -8px rgba(99,102,241,.7); }
.sg-logo.sm i{ width:15px; height:15px; border-width:2px; border-radius:5px; }
.sg-logo.sm i::after{ inset:2px; }
.sg-brand-name{ font-size:32px; line-height:1; font-weight:800; letter-spacing:-.04em; }
.sg-brand-sub{ margin-top:6px; font-size:12.5px; font-weight:500; color:rgba(255,255,255,.7); letter-spacing:.02em; }
.sg-engine{
  margin-left:auto; display:inline-flex; align-items:center; gap:9px;
  padding:8px 14px; border-radius:999px; background:rgba(255,255,255,.09);
  border:1px solid rgba(255,255,255,.16); font-size:10.5px; font-weight:800; letter-spacing:.14em;
  color:rgba(255,255,255,.85); backdrop-filter:blur(10px); -webkit-backdrop-filter:blur(10px);
}
.sg-live-dot{ width:8px; height:8px; border-radius:50%; background:#34d399; animation:sgPulse 2s infinite; }
.sg-hero-title{
  font-size:clamp(34px,4.6vw,58px); line-height:1.02; letter-spacing:-.045em; font-weight:800;
  margin:0 0 22px; max-width:820px;
}
.sg-grad-text{
  background:linear-gradient(100deg,#e0d9ff 0%,#a5b4fc 40%,#67e8f9 100%);
  -webkit-background-clip:text; background-clip:text; color:transparent; -webkit-text-fill-color:transparent;
}
.sg-hero-desc{ max-width:640px; font-size:16.5px; line-height:1.75; color:rgba(255,255,255,.76); margin-bottom:28px; }
.sg-pills{ display:flex; flex-wrap:wrap; gap:10px; }
.sg-pill{
  padding:10px 15px; border-radius:999px; font-size:12.5px; font-weight:600; color:rgba(255,255,255,.92);
  background:rgba(255,255,255,.10); border:1px solid rgba(255,255,255,.16);
  backdrop-filter:blur(10px); -webkit-backdrop-filter:blur(10px);
  transition:transform .25s ease, background .25s ease;
}
.sg-pill:hover{ transform:translateY(-2px); background:rgba(255,255,255,.17); }
.sg-glass-panel{
  padding:26px; border-radius:26px;
  background:linear-gradient(160deg,rgba(255,255,255,.16),rgba(255,255,255,.05));
  border:1px solid rgba(255,255,255,.2);
  backdrop-filter:blur(18px); -webkit-backdrop-filter:blur(18px);
  box-shadow:0 30px 60px -30px rgba(0,0,0,.5), inset 0 1px 0 rgba(255,255,255,.25);
}
.sg-panel-kicker{ font-family:var(--sg-mono); font-size:10.5px; font-weight:700; letter-spacing:.16em; color:#c4b5fd; margin-bottom:20px; }
.sg-flow-step{ position:relative; display:flex; gap:14px; align-items:flex-start; padding-bottom:20px; }
.sg-flow-step:last-child{ padding-bottom:0; }
.sg-flow-step::before{
  content:""; position:absolute; left:15px; top:34px; bottom:2px; width:1px;
  background:linear-gradient(rgba(255,255,255,.35),rgba(255,255,255,.04));
}
.sg-flow-step:last-child::before{ display:none; }
.sg-flow-num{
  flex:0 0 31px; height:31px; border-radius:10px; display:grid; place-items:center;
  font-family:var(--sg-mono); font-size:11px; font-weight:700;
  background:rgba(255,255,255,.12); border:1px solid rgba(255,255,255,.22);
  animation:sgStepGlow 8s ease-in-out infinite;
}
.sg-flow-title{ font-size:14px; font-weight:700; color:#fff; }
.sg-flow-sub{ margin-top:2px; font-size:12px; line-height:1.5; color:rgba(255,255,255,.62); }

/* ---------- section headers ---------- */
.sg-sec{ margin:64px 0 24px; }
.sg-kicker{
  display:inline-flex; align-items:center; gap:9px; padding:7px 13px; border-radius:999px;
  background:linear-gradient(135deg,#eef0ff,#f4edff); border:1px solid #e0e3fb; color:#4f46e5;
  font-family:var(--sg-mono); font-size:10.5px; font-weight:700; letter-spacing:.14em; text-transform:uppercase;
}
.sg-kdot{ width:6px; height:6px; border-radius:50%; background:linear-gradient(135deg,#6366f1,#a855f7); box-shadow:0 0 0 3px rgba(99,102,241,.15); }
.sg-sec-title{ margin:16px 0 8px; font-size:clamp(28px,3.2vw,38px); line-height:1.1; font-weight:800; letter-spacing:-.035em; color:var(--sg-ink); }
.sg-sec-desc{ max-width:740px; color:var(--sg-muted); font-size:15px; line-height:1.65; }

/* ---------- field heads ---------- */
.sg-field{ display:flex; align-items:center; gap:12px; margin:0 0 2px; }
.sg-field-icon{
  width:40px; height:40px; border-radius:13px; display:grid; place-items:center; font-size:18px;
  background:linear-gradient(135deg,#eef0ff,#f5eeff); border:1px solid #e2e5fb;
  box-shadow:0 8px 18px -10px rgba(79,70,229,.5);
}
.sg-field-label{ font-family:var(--sg-mono); font-size:11px; font-weight:700; letter-spacing:.14em; text-transform:uppercase; color:#3b3f78; }
.sg-field-hint{ font-size:13px; color:var(--sg-muted); margin-top:3px; }
.sg-caption{ text-align:center; margin-top:4px; color:#9aa1bb; font-size:12px; line-height:1.6; }

/* ---------- notices / empty ---------- */
.sg-notice{
  display:flex; gap:14px; align-items:flex-start; padding:18px 20px; border-radius:18px;
  margin:14px 0; border:1px solid var(--sg-line); background:#fff;
}
.sg-notice.warning{ border-color:#fde3a7; background:linear-gradient(135deg,#fffaf0,#ffffff); }
.sg-notice.error{ border-color:#fbc9c9; background:linear-gradient(135deg,#fff5f5,#ffffff); }
.sg-notice-icon{ font-size:20px; line-height:1.2; }
.sg-notice-title{ font-weight:800; color:var(--sg-ink); font-size:15px; }
.sg-notice-msg{ color:var(--sg-text); font-size:13.5px; line-height:1.6; margin-top:3px; overflow-wrap:anywhere; }
.sg-empty{
  padding:26px; border-radius:20px; border:1px dashed #d6daf3; background:rgba(255,255,255,.6);
  text-align:center; color:var(--sg-muted); font-size:14px;
}
.sg-empty.small{ padding:14px; font-size:13px; border-radius:14px; }

/* ---------- grid + cards ---------- */
.sg-grid{ display:grid; gap:18px; grid-template-columns:repeat(auto-fit,minmax(min(100%,320px),1fr)); align-items:stretch; }
.sg-grid.two{ grid-template-columns:repeat(auto-fit,minmax(min(100%,460px),1fr)); }
.sg-grid.three{ grid-template-columns:repeat(auto-fit,minmax(min(100%,300px),1fr)); }
.sg-grid.metrics{ grid-template-columns:repeat(auto-fit,minmax(min(100%,230px),1fr)); }
.sg-grid.stack{ grid-template-columns:minmax(0,1fr); }
.sg-stackcol{ display:flex; flex-direction:column; gap:12px; }

.sg-card{
  position:relative; min-width:0; overflow-wrap:anywhere;
  background:rgba(255,255,255,.93); border:1px solid var(--sg-line); border-radius:22px; padding:24px 26px;
  box-shadow:0 1px 2px rgba(20,26,60,.04), 0 16px 36px -20px rgba(40,50,120,.24);
  transition:transform .28s cubic-bezier(.2,.7,.2,1), box-shadow .28s ease, border-color .28s ease;
}
.sg-card:hover{
  transform:translateY(-4px); border-color:#d3d8f7;
  box-shadow:0 1px 2px rgba(20,26,60,.05), 0 28px 50px -22px rgba(79,70,229,.32);
}
.sg-eyebrow{
  font-family:var(--sg-mono); font-size:10.5px; font-weight:700; letter-spacing:.15em;
  text-transform:uppercase; color:#6d5bf0;
}
.sg-lbl{ font-size:10.5px; font-weight:800; letter-spacing:.12em; text-transform:uppercase; color:#8a93ad; margin:16px 0 6px; }
.sg-lbl.tight{ margin:0; }
.sg-val{ font-size:14px; line-height:1.7; color:var(--sg-text); }
.sg-num{
  display:inline-grid; place-items:center; min-width:38px; height:38px; padding:0 8px; border-radius:12px;
  background:linear-gradient(135deg,#4f46e5,#8b5cf6); color:#fff;
  font-family:var(--sg-mono); font-size:13px; font-weight:700; box-shadow:0 10px 20px -8px rgba(99,102,241,.7);
}
.sg-icon{
  width:38px; height:38px; flex:0 0 38px; border-radius:12px; display:grid; place-items:center; font-size:17px;
  background:linear-gradient(135deg,#eef0ff,#f5eeff); border:1px solid #e2e5fb;
}
.sg-icon.sm{ width:32px; height:32px; flex-basis:32px; font-size:15px; border-radius:10px; }

/* key/value + lists */
.sg-kvs{ display:flex; flex-direction:column; gap:10px; }
.sg-kv-k{ font-size:10.5px; font-weight:800; letter-spacing:.11em; text-transform:uppercase; color:#8a93ad; }
.sg-kv-v{ font-size:13.5px; line-height:1.65; color:var(--sg-text); }
.sg-list{ margin:0; padding-left:18px; display:flex; flex-direction:column; gap:6px; }
.sg-list li{ font-size:14px; line-height:1.65; color:var(--sg-text); }
.sg-list li::marker{ color:#8b7cf6; }
.sg-para{ margin-top:16px; font-size:15.5px; line-height:1.85; color:#4a5473; }

/* tags / badges */
.sg-tags{ display:flex; flex-wrap:wrap; gap:6px; margin-top:12px; }
.sg-tag{
  display:inline-flex; gap:6px; align-items:center; padding:5px 10px; border-radius:999px;
  background:#f1f2fd; border:1px solid #e4e6fa; font-size:11.5px; font-weight:600; color:#3d4470;
}
.sg-tag b{ font-size:9.5px; font-weight:800; letter-spacing:.1em; text-transform:uppercase; color:#8a93ad; }
.sg-flag{
  padding:5px 10px; border-radius:8px; font-size:9.5px; font-weight:800; letter-spacing:.1em;
  color:#5b3fd6; background:linear-gradient(135deg,#efeaff,#e8f0ff); border:1px solid #ddd6fb;
}
.sg-badge{
  display:inline-flex; align-items:center; gap:8px; padding:7px 12px; border-radius:999px;
  font-size:11px; font-weight:800; letter-spacing:.08em; white-space:nowrap;
}
.sg-badge::before{ content:""; width:8px; height:8px; border-radius:50%; background:currentColor; }
.sg-badge.strong{ background:#e7faf1; color:#047857; }
.sg-badge.modstrong{ background:#e3f6fb; color:#0e7490; }
.sg-badge.moderate{ background:#fff4dc; color:#b45309; }
.sg-badge.weak{ background:#feeaea; color:#b91c1c; }
.sg-badge.neutral{ background:#eef0fb; color:#4f46e5; }
.sg-meter{ display:inline-flex; gap:2px; margin-left:2px; }
.sg-meter i{ width:10px; height:4px; border-radius:2px; background:currentColor; opacity:.22; }
.sg-meter i.on{ opacity:1; }

/* findings */
.sg-finding{ display:flex; flex-direction:column; }
.sg-finding::before{
  content:""; position:absolute; left:26px; right:26px; top:0; height:3px; border-radius:0 0 4px 4px;
  background:linear-gradient(90deg,#818cf8,#c084fc);
}
.sg-finding.strong::before{ background:linear-gradient(90deg,#10b981,#67e8f9); }
.sg-finding.modstrong::before{ background:linear-gradient(90deg,#06b6d4,#6366f1); }
.sg-finding.moderate::before{ background:linear-gradient(90deg,#f59e0b,#fbbf24); }
.sg-finding.weak::before{ background:linear-gradient(90deg,#ef4444,#fb923c); }
.sg-finding-top{ display:flex; align-items:center; gap:12px; margin-bottom:16px; }
.sg-finding-text{ font-size:17px; line-height:1.55; font-weight:700; color:var(--sg-ink); letter-spacing:-.012em; }
.sg-strength-row{ margin-top:auto; padding-top:20px; display:flex; flex-direction:column; gap:8px; align-items:flex-start; }

/* panels */
.sg-panel{ display:flex; flex-direction:column; gap:16px; }
.sg-panel-head{ display:flex; align-items:center; gap:12px; }
.sg-panel-title{ font-weight:800; color:var(--sg-ink); font-size:16px; letter-spacing:-.01em; }
.sg-count{
  margin-left:auto; font-family:var(--sg-mono); font-size:11px; font-weight:700; color:#6d5bf0;
  background:#f0f0ff; border-radius:999px; padding:4px 10px;
}
.sg-rows{ display:flex; flex-direction:column; gap:10px; }
.sg-row{ display:flex; gap:12px; padding:13px 14px; border-radius:14px; background:#f8f9ff; border:1px solid #eceefb; }
.sg-bullet{ flex:0 0 8px; width:8px; height:8px; margin-top:8px; border-radius:50%; background:linear-gradient(135deg,#6366f1,#a855f7); }
.sg-panel.cyan .sg-bullet{ background:linear-gradient(135deg,#06b6d4,#6366f1); }
.sg-panel.violet .sg-bullet{ background:linear-gradient(135deg,#8b5cf6,#ec4899); }
.sg-panel.teal .sg-bullet{ background:linear-gradient(135deg,#10b981,#06b6d4); }
.sg-row-body{ min-width:0; flex:1; }
.sg-row-main{ font-size:14px; line-height:1.65; color:#2b3454; font-weight:500; }

/* segments / competitors */
.sg-seg-top{ display:flex; align-items:center; gap:14px; margin-bottom:6px; }
.sg-avatar{
  width:48px; height:48px; flex:0 0 48px; border-radius:15px; display:grid; place-items:center;
  font-weight:800; font-size:18px; color:#fff; background:linear-gradient(135deg,#4f46e5,#a855f7);
  box-shadow:0 12px 22px -10px rgba(124,58,237,.7);
}
.sg-avatar.cyan{ background:linear-gradient(135deg,#0891b2,#6366f1); box-shadow:0 12px 22px -10px rgba(8,145,178,.7); }
.sg-seg-name{ font-size:17px; font-weight:800; color:var(--sg-ink); letter-spacing:-.015em; line-height:1.3; }
.sg-implication{
  margin-top:16px; padding:14px 16px; border-radius:16px;
  background:linear-gradient(135deg,#f1efff,#f8f2ff); border:1px solid #e3defc;
}
.sg-implication .sg-val{ color:#33306e; font-weight:500; }

/* trends */
.sg-trend{ padding:28px 30px; }
.sg-trend-top{ display:flex; align-items:center; justify-content:space-between; margin-bottom:14px; }
.sg-arrow{
  width:38px; height:38px; border-radius:12px; display:grid; place-items:center; font-size:18px; font-weight:800;
  color:#0e9f6e; background:linear-gradient(135deg,#e7faf1,#e3f6fb); border:1px solid #c8f0e2;
}
.sg-arrow.down{ color:#c2410c; background:linear-gradient(135deg,#fff3e6,#feeaea); border-color:#fbd5b0; }
.sg-arrow.flat{ color:#4f46e5; background:#eef0fb; border-color:#e0e3fb; }
.sg-trend-title{ font-size:20px; line-height:1.4; font-weight:800; color:var(--sg-ink); letter-spacing:-.02em; }

/* opportunities & risks */
.sg-duo{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:22px; align-items:start; }
.sg-col{ display:flex; flex-direction:column; gap:14px; min-width:0; }
.sg-col-head{ display:flex; align-items:center; gap:12px; margin-bottom:4px; }
.sg-col-title{ font-size:22px; font-weight:800; color:var(--sg-ink); letter-spacing:-.02em; }
.sg-signal{ padding:24px 26px; overflow:hidden; }
.sg-signal > *{ position:relative; z-index:1; }
.sg-signal.opp{ background:linear-gradient(150deg,#e6faf3 0%,#f5fffb 60%,#ffffff 100%); border-color:#bdeedd; }
.sg-signal.risk{ background:linear-gradient(150deg,#fff1e2 0%,#fff8f0 55%,#ffffff 100%); border-color:#fbd5b0; }
.sg-signal::after{
  content:""; position:absolute; right:-40px; top:-40px; width:140px; height:140px; border-radius:50%;
  filter:blur(22px); opacity:.55; pointer-events:none;
}
.sg-signal.opp::after{ background:rgba(16,185,129,.28); }
.sg-signal.risk::after{ background:rgba(249,115,22,.26); }
.sg-signal.opp .sg-eyebrow{ color:#047857; }
.sg-signal.risk .sg-eyebrow{ color:#c2410c; }
.sg-signal-head{ display:flex; align-items:center; gap:10px; margin-bottom:12px; }
.sg-signal-icon{
  width:34px; height:34px; border-radius:11px; display:grid; place-items:center; font-size:16px;
  background:rgba(255,255,255,.85); box-shadow:0 8px 16px -10px rgba(20,26,60,.35);
}
.sg-signal-title{ font-size:16.5px; line-height:1.5; font-weight:800; color:var(--sg-ink); letter-spacing:-.012em; }
.sg-signal-body{ margin-top:8px; font-size:14px; line-height:1.7; color:var(--sg-text); }

/* strategic insights (consulting brain) */
.sg-brain{
  position:relative; isolation:isolate; overflow:hidden; border-radius:30px; padding:30px; color:#fff;
  background:linear-gradient(140deg,#0a0f2c 0%,#171f63 50%,#2f1d8f 100%);
  box-shadow:0 40px 80px -34px rgba(45,40,150,.6), inset 0 1px 0 rgba(255,255,255,.12);
}
.sg-brain > .sg-grid{ position:relative; z-index:2; }
.sg-glass{
  position:relative; min-width:0; overflow-wrap:anywhere; padding:26px 28px; border-radius:22px;
  background:linear-gradient(160deg,rgba(255,255,255,.13),rgba(255,255,255,.04));
  border:1px solid rgba(255,255,255,.16);
  backdrop-filter:blur(14px); -webkit-backdrop-filter:blur(14px);
  box-shadow:inset 0 1px 0 rgba(255,255,255,.2), 0 20px 40px -24px rgba(0,0,0,.5);
  transition:transform .28s cubic-bezier(.2,.7,.2,1), border-color .28s ease, box-shadow .28s ease;
}
.sg-glass:hover{ transform:translateY(-4px); border-color:rgba(196,181,253,.5); box-shadow:inset 0 1px 0 rgba(255,255,255,.25), 0 28px 50px -22px rgba(139,92,246,.55); }
.sg-glass .sg-eyebrow{ color:#c4b5fd; }
.sg-glass-main{ margin-top:14px; font-size:18px; line-height:1.5; font-weight:700; color:#fff; letter-spacing:-.01em; }
.sg-glass .sg-lbl, .sg-glass .sg-kv-k{ color:#a5b4fc; }
.sg-glass .sg-val, .sg-glass .sg-kv-v, .sg-glass .sg-list li{ color:rgba(255,255,255,.84); }

/* actions */
.sg-action{ display:flex; gap:24px; padding:28px 30px; }
.sg-action::before{
  content:""; position:absolute; left:0; top:24px; bottom:24px; width:4px; border-radius:0 6px 6px 0;
  background:linear-gradient(180deg,#4f46e5,#c084fc);
}
.sg-action-num{
  flex:0 0 auto; font-size:54px; line-height:1; font-weight:800; letter-spacing:-.05em;
  background:linear-gradient(160deg,#4f46e5,#c084fc); -webkit-background-clip:text; background-clip:text;
  color:transparent; -webkit-text-fill-color:transparent;
}
.sg-action-body{ flex:1; min-width:0; }
.sg-action-title{ margin-top:10px; font-size:20px; line-height:1.4; font-weight:800; color:var(--sg-ink); letter-spacing:-.02em; }
.sg-action-cols{ display:grid; grid-template-columns:repeat(auto-fit,minmax(min(100%,260px),1fr)); gap:14px; margin-top:18px; }
.sg-mini{ padding:14px 16px; border-radius:16px; background:#f7f8ff; border:1px solid #eaecfb; }
.sg-mini.impact{ background:linear-gradient(135deg,#ecfbf6,#f7fffc); border-color:#c8f0e2; }
.sg-mini .sg-lbl{ margin-top:0; }

/* decision */
.sg-decision{
  position:relative; isolation:isolate; overflow:hidden; border-radius:32px; padding:50px 54px; color:#fff;
  background:linear-gradient(125deg,#0b1136 0%,#2a2a9c 45%,#7c3aed 100%);
  background-size:200% 200%;
  animation:sgGradient 20s ease-in-out infinite, sgGlow 6s ease-in-out infinite;
}
.sg-decision > *:not(.sg-orb):not(.sg-hero-gridbg){ position:relative; z-index:2; }
.sg-decision-label{ font-family:var(--sg-mono); letter-spacing:.3em; font-size:12px; font-weight:700; color:#ddd6fe; }
.sg-decision-text{ margin-top:18px; max-width:920px; font-size:26px; line-height:1.5; font-weight:700; letter-spacing:-.02em; overflow-wrap:anywhere; }
.sg-decision-text.long{ font-size:19px; font-weight:600; line-height:1.75; letter-spacing:-.01em; }
.sg-decision .sg-kv-k{ color:#c4b5fd; }
.sg-decision .sg-kv-v, .sg-decision .sg-list li{ color:rgba(255,255,255,.9); font-size:16px; }

/* executive */
.sg-exec{ display:grid; grid-template-columns:minmax(0,1.9fr) minmax(0,1fr); gap:18px; align-items:stretch; }
.sg-exec-main{
  position:relative; padding:38px 40px; border-radius:28px; min-width:0; overflow-wrap:anywhere;
  background:linear-gradient(180deg,#ffffff 0%,#fafaff 100%); border:1px solid #dfe2f8;
  box-shadow:0 40px 70px -40px rgba(79,70,229,.45), 0 1px 2px rgba(20,26,60,.05);
}
.sg-exec-main::before{
  content:""; position:absolute; left:40px; right:40px; top:0; height:4px; border-radius:0 0 6px 6px;
  background:linear-gradient(90deg,#4f46e5,#8b5cf6,#22d3ee);
}
.sg-exec-lead{ margin-top:16px; font-size:clamp(19px,2vw,24px); line-height:1.5; font-weight:700; letter-spacing:-.02em; color:var(--sg-ink); }
.sg-callout{ margin-top:26px; padding:18px 20px; border-radius:18px; background:linear-gradient(135deg,#f1efff,#f8f2ff); border:1px solid #e3defc; }
.sg-callout-text{ margin-top:8px; font-size:15px; line-height:1.65; font-weight:600; color:#33306e; }
.sg-rail{ display:grid; grid-template-columns:minmax(0,1fr); gap:14px; align-content:start; }
.sg-stat{
  padding:20px 22px; border-radius:20px; background:rgba(255,255,255,.93); border:1px solid var(--sg-line);
  box-shadow:0 16px 36px -22px rgba(40,50,120,.3);
  transition:transform .25s ease, box-shadow .25s ease;
}
.sg-stat:hover{ transform:translateY(-3px); box-shadow:0 24px 44px -22px rgba(79,70,229,.35); }
.sg-stat-value{
  margin-top:10px; font-size:34px; line-height:1; font-weight:800; letter-spacing:-.04em;
  background:linear-gradient(120deg,#4f46e5,#a855f7); -webkit-background-clip:text; background-clip:text;
  color:transparent; -webkit-text-fill-color:transparent;
}

/* metrics */
.sg-metric{ display:flex; flex-direction:column; gap:14px; padding:20px 22px; }
.sg-metric-top{ display:flex; align-items:center; gap:10px; }
.sg-metric-value{ font-size:20px; font-weight:800; color:var(--sg-ink); letter-spacing:-.02em; line-height:1.3; }
.sg-block-head{ display:flex; align-items:center; gap:12px; margin-bottom:14px; }

/* sources */
.sg-sources{ display:grid; grid-template-columns:repeat(auto-fit,minmax(min(100%,460px),1fr)); gap:12px; align-items:start; }
.sg-source{
  min-width:0; border:1px solid var(--sg-line); border-radius:18px; background:rgba(255,255,255,.94);
  box-shadow:0 12px 28px -20px rgba(40,50,120,.3);
  transition:border-color .25s ease, box-shadow .25s ease, transform .25s ease;
}
.sg-source:hover{ border-color:#cfd4f6; transform:translateY(-2px); }
.sg-source[open]{ border-color:#d3d8fa; box-shadow:0 22px 44px -24px rgba(79,70,229,.35); }
.sg-source summary{ list-style:none; cursor:pointer; display:flex; align-items:center; gap:12px; padding:15px 18px; }
.sg-source summary::-webkit-details-marker{ display:none; }
.sg-source.flat{ display:flex; align-items:center; gap:12px; padding:15px 18px; }
.sg-src-num{
  flex:0 0 auto; padding:5px 8px; border-radius:8px; background:#f0f0ff; color:#5b4be0;
  font-family:var(--sg-mono); font-size:11px; font-weight:700;
}
.sg-src-title{ flex:1; min-width:0; font-size:14px; font-weight:650; color:#242c4c; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.sg-src-domain{
  flex:0 1 auto; max-width:40%; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;
  font-size:11px; font-weight:600; color:#7c86a2; background:#f5f6fc; border-radius:999px; padding:4px 10px;
}
.sg-chevron{ flex:0 0 auto; color:#8b93b0; transition:transform .25s ease; }
.sg-source[open] .sg-chevron{ transform:rotate(180deg); }
.sg-src-body{ padding:4px 18px 18px; margin:0 18px; padding-left:0; padding-right:0; border-top:1px dashed #e4e7fa; overflow-wrap:anywhere; }
.sg-src-link{ color:#4f46e5; font-weight:600; font-size:13px; word-break:break-all; text-decoration:none; }
a.sg-src-link:hover{ text-decoration:underline; }

/* live research */
.sg-live{
  position:relative; isolation:isolate; overflow:hidden; border-radius:28px; padding:34px 36px; color:#fff; margin-top:10px;
  background:linear-gradient(135deg,#0a1030,#1b2470 55%,#3a239f);
  box-shadow:0 34px 70px -28px rgba(45,40,150,.6), inset 0 1px 0 rgba(255,255,255,.14);
}
.sg-live > *:not(.sg-orb){ position:relative; z-index:2; }
.sg-live-top{ display:flex; justify-content:space-between; align-items:center; gap:12px; flex-wrap:wrap; margin-bottom:22px; }
.sg-chip-dark{
  padding:8px 13px; border-radius:999px; background:rgba(255,255,255,.1); border:1px solid rgba(255,255,255,.18);
  font-size:10.5px; font-weight:800; letter-spacing:.16em;
}
.sg-status{ display:inline-flex; align-items:center; gap:8px; font-size:11px; font-weight:800; letter-spacing:.14em; color:#6ee7b7; }
.sg-pulse{ width:8px; height:8px; border-radius:50%; background:#34d399; animation:sgPulse 1.8s infinite; }
.sg-live-title{ font-size:clamp(28px,3.4vw,38px); font-weight:800; letter-spacing:-.035em; }
.sg-ellipsis::after{ content:"..."; animation:sgDots 1.6s steps(1,end) infinite; }
.sg-live-flow{ margin-top:8px; font-size:14px; color:rgba(255,255,255,.7); line-height:1.6; }
.sg-live-msg{
  margin-top:18px; display:inline-block; padding:10px 14px; border-radius:12px;
  background:rgba(255,255,255,.08); border:1px solid rgba(255,255,255,.14); font-size:13.5px; color:rgba(255,255,255,.9);
}
.sg-stages{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:12px; margin-top:26px; }
.sg-stage{
  position:relative; overflow:hidden; padding:16px 16px 20px; border-radius:18px;
  background:rgba(255,255,255,.06); border:1px solid rgba(255,255,255,.12); opacity:.6;
}
.sg-stage.done{ opacity:1; background:rgba(52,211,153,.10); border-color:rgba(52,211,153,.35); }
.sg-stage.active{
  opacity:1; background:linear-gradient(160deg,rgba(139,92,246,.35),rgba(99,102,241,.16));
  border-color:rgba(196,181,253,.6); animation:sgStageGlow 2.4s ease-in-out infinite;
}
.sg-stage.active::after{
  content:""; position:absolute; left:0; bottom:0; height:3px; width:40%;
  background:linear-gradient(90deg,transparent,#c4b5fd,#67e8f9,transparent);
  animation:sgIndeterminate 1.8s linear infinite;
}
.sg-stage-state{ position:absolute; right:14px; top:14px; font-size:9.5px; font-weight:800; letter-spacing:.1em; color:rgba(255,255,255,.5); }
.sg-stage.done .sg-stage-state{ color:#6ee7b7; }
.sg-stage.active .sg-stage-state{ color:#ddd6fe; }
.sg-stage-num{ font-family:var(--sg-mono); font-size:11px; font-weight:700; color:rgba(255,255,255,.65); }
.sg-stage-title{ font-size:14px; font-weight:700; margin-top:12px; }
.sg-stage-sub{ font-size:11.5px; color:rgba(255,255,255,.62); margin-top:3px; line-height:1.4; }
.sg-track{ height:3px; background:rgba(255,255,255,.1); border-radius:3px; overflow:hidden; margin-top:24px; }
.sg-track span{
  display:block; width:30%; height:100%;
  background:linear-gradient(90deg,transparent,#a78bfa,#67e8f9,transparent);
  animation:sgIndeterminate 2.2s linear infinite;
}

/* report banner */
.sg-banner{
  position:relative; isolation:isolate; overflow:hidden; margin-top:56px; padding:38px 42px; border-radius:30px; color:#fff;
  background:linear-gradient(125deg,#0a0f2c,#1a2470 55%,#4526b5); background-size:200% 200%;
  animation:sgGradient 22s ease-in-out infinite;
  box-shadow:0 34px 70px -30px rgba(45,40,150,.6), inset 0 1px 0 rgba(255,255,255,.14);
  display:grid; grid-template-columns:minmax(0,1fr) auto; gap:24px; align-items:center;
}
.sg-banner > *:not(.sg-orb):not(.sg-hero-gridbg){ position:relative; z-index:2; }
.sg-banner-kicker{ font-family:var(--sg-mono); font-size:12px; font-weight:700; letter-spacing:.2em; color:#c4b5fd; }
.sg-banner-title{ margin-top:12px; font-size:clamp(26px,3.2vw,38px); line-height:1.1; font-weight:800; letter-spacing:-.035em; }
.sg-banner-sub{ margin-top:10px; font-size:15px; color:rgba(255,255,255,.72); line-height:1.6; }
.sg-brief{ display:flex; flex-wrap:wrap; gap:10px; margin-top:22px; }
.sg-brief-chip{
  max-width:100%; padding:10px 14px; border-radius:14px; background:rgba(255,255,255,.08);
  border:1px solid rgba(255,255,255,.14); font-size:12.5px; line-height:1.45; color:rgba(255,255,255,.88);
}
.sg-brief-chip b{ display:block; font-size:9.5px; font-weight:800; letter-spacing:.14em; text-transform:uppercase; color:#a5b4fc; margin-bottom:3px; }
.sg-brief-chip span{ display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden; }
.sg-done{ display:flex; flex-direction:column; align-items:center; gap:10px; text-align:center; }
.sg-done-ring{
  width:64px; height:64px; border-radius:50%; display:grid; place-items:center; font-size:28px; color:#6ee7b7;
  background:rgba(52,211,153,.14); border:1px solid rgba(52,211,153,.45); animation:sgPulse 2.4s infinite;
}
.sg-done-label{ font-size:10.5px; font-weight:800; letter-spacing:.16em; color:#6ee7b7; }

/* footer */
.sg-footer{
  margin-top:72px; padding:30px 4px 8px; display:flex; justify-content:space-between; align-items:center; gap:20px; flex-wrap:wrap;
  border-top:1px solid transparent; border-image:linear-gradient(90deg,transparent,#c7cbf0,transparent) 1;
}
.sg-footer-brand{ display:flex; align-items:center; gap:14px; }
.sg-footer-name{ font-size:18px; font-weight:800; letter-spacing:-.03em; color:var(--sg-ink); }
.sg-footer-sub{ font-size:12px; color:var(--sg-muted); margin-top:2px; }
.sg-footer-tag{ font-size:12px; color:#9aa1bb; }

/* responsive */
@media (max-width:980px){
  .sg-hero-inner{ grid-template-columns:minmax(0,1fr); }
  .sg-glass-panel{ display:none; }
  .sg-exec{ grid-template-columns:minmax(0,1fr); }
  .sg-rail{ grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); }
  .sg-duo{ grid-template-columns:minmax(0,1fr); }
  .sg-banner{ grid-template-columns:minmax(0,1fr); }
  .sg-done{ flex-direction:row; justify-content:flex-start; }
}
@media (max-width:800px){
  .sg-stages{ grid-template-columns:repeat(2,minmax(0,1fr)); }
}
@media (max-width:640px){
  .block-container, [data-testid="stMainBlockContainer"]{ padding:1rem 1rem 3rem !important; }
  .sg-hero{ padding:34px 24px; border-radius:26px; }
  .sg-engine{ margin-left:0; }
  .sg-brain{ padding:18px; border-radius:24px; }
  .sg-decision{ padding:32px 26px; border-radius:26px; }
  .sg-decision-text{ font-size:21px; }
  .sg-exec-main{ padding:28px 24px; }
  .sg-banner{ padding:28px 24px; border-radius:24px; }
  .sg-live{ padding:26px 22px; }
  .sg-action{ flex-direction:column; gap:8px; padding:24px; }
  .sg-action-num{ font-size:40px; }
  .sg-sec{ margin-top:48px; }
  .sg-card{ padding:22px; }
}
@media (prefers-reduced-motion: reduce){
  *, *::before, *::after{ animation-duration:.001ms !important; animation-iteration-count:1 !important; transition-duration:.001ms !important; }
}
</style>
"""


# ============================================================
# SAFE DATA HELPERS
# ============================================================

def esc(value):
    """HTML-escape any value for safe injection into markup."""
    if value is None:
        return ""
    return html.escape(str(value), quote=True)


def norm(key):
    return re.sub(r"[^a-z0-9]+", "_", str(key).lower()).strip("_")


def is_empty(value):
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, (list, tuple, dict, set)):
        return len(value) == 0
    return False


def label_of(key):
    return str(key).replace("_", " ").replace("-", " ").strip().capitalize()


def title_of(key):
    return str(key).replace("_", " ").replace("-", " ").strip().title()


def one_line(text):
    return " ".join(str(text or "").split())


def to_text(value):
    """Flatten any structure into readable plain text (never a Python repr)."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, (list, tuple)):
        parts = [to_text(v) for v in value]
        return "; ".join(p for p in parts if p)
    if isinstance(value, dict):
        lookup = {}
        for k, v in value.items():
            lookup.setdefault(norm(k), v)
        for key in TEXT_KEYS:
            if not is_empty(lookup.get(key)):
                return to_text(lookup[key])
        parts = []
        for k, v in value.items():
            text = to_text(v)
            if text:
                parts.append(f"{label_of(k)}: {text}")
        return " | ".join(parts)
    return str(value)


def as_list(value):
    """Return a clean list of records from any value."""
    if is_empty(value):
        return []
    if isinstance(value, (list, tuple)):
        return [v for v in value if not is_empty(v)]
    if isinstance(value, dict):
        non_empty = [(k, v) for k, v in value.items() if not is_empty(v)]
        if len(non_empty) == 1 and isinstance(non_empty[0][1], list):
            return [v for v in non_empty[0][1] if not is_empty(v)]
        return [value]
    return [value]


def take(item, aliases, used):
    """Return the first non-empty value matching one of the (normalized) aliases."""
    if not isinstance(item, dict):
        return None
    lookup = {}
    for k, v in item.items():
        lookup.setdefault(norm(k), v)
    for alias in aliases:
        val = lookup.get(alias)
        if not is_empty(val):
            used.add(alias)
            return val
    return None


def collect_fields(container, spec):
    """spec = [(key, aliases)]. Returns ({key: value}, [(extra_key, value)])."""
    used = set()
    found = {}
    for key, aliases in spec:
        found[key] = take(container, aliases, used)
    extras = [(k, v) for k, v in container.items() if norm(k) not in used and not is_empty(v)]
    return found, extras


def split_title(text):
    t = to_text(text)
    for sep in (": ", " — ", " – ", " - "):
        if sep in t:
            head, tail = t.split(sep, 1)
            if 0 < len(head) <= 42 and len(head.split()) <= 5 and tail.strip():
                return head.strip(), tail.strip()
    return "", t


def initial_of(text):
    for ch in str(text):
        if ch.isalnum():
            return ch.upper()
    return "•"


def domain_of(url):
    try:
        return urlparse(url).netloc.replace("www.", "")
    except Exception:
        return ""


def show(markup):
    """Render trusted markup. All dynamic values inside are escaped with esc()."""
    if markup:
        st.html(markup)


# ============================================================
# MARKUP BUILDERS — generic
# ============================================================

def para_html(text):
    text = str(text or "").strip()
    if not text:
        return ""
    blocks = [b.strip() for b in re.split(r"\n\s*\n", text) if b.strip()]
    out = []
    for block in blocks:
        safe = esc(block).replace("\n", "<br>")
        out.append(f'<div class="sg-para">{safe}</div>')
    return "".join(out)


def value_html(value, depth=0, max_chars=None):
    """Turn any nested value into labeled HTML — never a raw Python structure."""
    if is_empty(value):
        return ""
    if isinstance(value, dict):
        if depth >= 4:
            return esc(to_text(value))
        rows = []
        for key, val in list(value.items())[:40]:
            inner = value_html(val, depth + 1, max_chars)
            if inner:
                rows.append(
                    f'<div class="sg-kv"><div class="sg-kv-k">{esc(label_of(key))}</div>'
                    f'<div class="sg-kv-v">{inner}</div></div>'
                )
        joined = "".join(rows)
        return f'<div class="sg-kvs">{joined}</div>' if rows else ""
    if isinstance(value, (list, tuple)):
        if depth >= 5:
            return esc(to_text(value))
        items = [v for v in value if not is_empty(v)][:60]
        lis = []
        for it in items:
            inner = value_html(it, depth + 1, max_chars)
            if inner:
                lis.append(f"<li>{inner}</li>")
        joined = "".join(lis)
        return f'<ul class="sg-list">{joined}</ul>' if lis else ""
    text = to_text(value)
    if max_chars and len(text) > max_chars:
        text = text[:max_chars].rstrip() + "…"
    return esc(text).replace("\n", "<br>")


def labeled(label, value):
    body = value_html(value)
    if not body:
        return ""
    return f'<div class="sg-lbl">{esc(label)}</div><div class="sg-val">{body}</div>'


def extras_html(item, used):
    if not isinstance(item, dict):
        return ""
    out = []
    for key, val in item.items():
        if norm(key) in used or is_empty(val):
            continue
        out.append(labeled(label_of(key), val))
    return "".join(out)


def tags_from(item, used):
    if not isinstance(item, dict):
        return ""
    tags = []
    for key, val in item.items():
        nk = norm(key)
        if (
            nk in TAG_KEYS
            and nk not in used
            and isinstance(val, (str, int, float))
            and not isinstance(val, bool)
            and not is_empty(val)
            and len(str(val)) <= 32
        ):
            used.add(nk)
            tags.append(f'<span class="sg-tag"><b>{esc(label_of(key))}</b>{esc(val)}</span>')
    if not tags:
        return ""
    return f'<div class="sg-tags">{"".join(tags)}</div>'


def strength_meta(value):
    t = to_text(value).lower()
    if not t or len(t) > 40:
        return None
    if "moderate" in t and ("strong" in t or "high" in t):
        return ("modstrong", "MODERATE-TO-STRONG", 3)
    if "weak" in t or "low" in t or "limited" in t or "poor" in t:
        return ("weak", "WEAK", 1)
    if "moderate" in t or "medium" in t or "mixed" in t or "partial" in t:
        return ("moderate", "MODERATE", 2)
    if "strong" in t or "high" in t or "robust" in t or "solid" in t:
        return ("strong", "STRONG", 4)
    return None


def meter_html(level):
    if not level:
        return ""
    bars = "".join('<i class="on"></i>' if n < level else "<i></i>" for n in range(4))
    return f'<span class="sg-meter">{bars}</span>'


def strength_badge(value, allow_neutral=False):
    text = to_text(value)
    if not text:
        return ""
    meta = strength_meta(text)
    if meta:
        cls, label, level = meta
        return f'<span class="sg-badge {cls}">{esc(label)}{meter_html(level)}</span>'
    if allow_neutral and len(text) <= 30:
        return f'<span class="sg-badge neutral">{esc(text.upper())}</span>'
    return ""


def segment_badges(text):
    t = str(text).lower()
    flags = []
    for label, tokens in BADGE_RULES:
        for tok in tokens:
            if re.search(r"\b" + re.escape(tok), t):
                flags.append(label)
                break
    if not flags:
        return ""
    chips = "".join(f'<span class="sg-flag">{esc(f)}</span>' for f in flags[:3])
    return f'<div class="sg-tags">{chips}</div>'


def trend_arrow(text):
    t = str(text).lower()
    if re.search(r"\b(declin|decreas|fall|drop|shrink|weaken)", t):
        return "↘", "down"
    if re.search(r"\b(stable|steady|flat|plateau)", t):
        return "→", "flat"
    return "↗", "up"


def find_confidence(d):
    eq = d.get("evidence_quality")
    if isinstance(eq, dict):
        for k, v in eq.items():
            nk = norm(k)
            if "confidence" in nk and not is_empty(v):
                return to_text(v)
        for k, v in eq.items():
            if norm(k) in ("overall", "overall_assessment", "overall_quality", "overall_evidence_quality") and not is_empty(v):
                return to_text(v)
    for key in ("research_confidence", "overall_confidence", "confidence"):
        if not is_empty(d.get(key)):
            return to_text(d.get(key))
    return ""


def extract_sources(value):
    if is_empty(value):
        return []
    if isinstance(value, dict):
        keys = {norm(k) for k in value}
        if keys & {"url", "link", "title", "name", "source"}:
            return [value]
        items = []
        for v in value.values():
            items.extend(as_list(v))
        return items
    return as_list(value)


# ============================================================
# MARKUP BUILDERS — components
# ============================================================

def render_section_header(number, label, title, description=""):
    desc = f'<div class="sg-sec-desc">{esc(description)}</div>' if description else ""
    return (
        '<div class="sg-sec sg-rise">'
        f'<div class="sg-kicker"><span class="sg-kdot"></span>{esc(number)} · {esc(label)}</div>'
        f'<div class="sg-sec-title">{esc(title)}</div>{desc}</div>'
    )


def show_section(number, label, title, description, body):
    show(render_section_header(number, label, title, description) + body)


def render_empty(message="No data available for this section."):
    return f'<div class="sg-empty">✦ &nbsp;{esc(message)}</div>'


def render_notice(kind, title, message):
    icon = "⚠️" if kind == "warning" else "🛑"
    return (
        f'<div class="sg-notice {esc(kind)}"><div class="sg-notice-icon">{icon}</div>'
        f'<div><div class="sg-notice-title">{esc(title)}</div>'
        f'<div class="sg-notice-msg">{esc(message)}</div></div></div>'
    )


def field_head(icon, label, hint):
    return (
        f'<div class="sg-field"><div class="sg-field-icon">{esc(icon)}</div>'
        f'<div><div class="sg-field-label">{esc(label)}</div>'
        f'<div class="sg-field-hint">{esc(hint)}</div></div></div>'
    )


def render_hero():
    dots = "".join(
        f'<i style="left:{x}%;top:{y}%;width:{s}px;height:{s}px;animation-duration:{dur}s;animation-delay:{delay}s"></i>'
        for x, y, s, dur, delay in DOT_SPECS
    )
    flow_items = [
        ("01", "Research Design", "Frames the question and the evidence needed"),
        ("02", "Web Research", "Gathers live market evidence"),
        ("03", "Business Intelligence", "Grades and analyzes what was found"),
        ("04", "Strategic Synthesis", "Builds recommendations and the decision"),
    ]
    flow = "".join(
        f'<div class="sg-flow-step"><div class="sg-flow-num" style="animation-delay:{i * 2}s">{num}</div>'
        f'<div><div class="sg-flow-title">{esc(title)}</div><div class="sg-flow-sub">{esc(sub)}</div></div></div>'
        for i, (num, title, sub) in enumerate(flow_items)
    )
    return f"""
    <div class="sg-hero sg-rise">
      <div class="sg-hero-gridbg"></div>
      <div class="sg-orb a"></div><div class="sg-orb b"></div><div class="sg-orb c"></div>
      <div class="sg-dots">{dots}</div>
      <div class="sg-hero-inner">
        <div>
          <div class="sg-brand">
            <div class="sg-logo"><i></i></div>
            <div>
              <div class="sg-brand-name">SAGE</div>
              <div class="sg-brand-sub">Strategic Analysis &amp; Guided Exploration</div>
            </div>
            <div class="sg-engine"><span class="sg-live-dot"></span>ENGINE READY</div>
          </div>
          <div class="sg-hero-title">Turn business questions into <span class="sg-grad-text">strategic intelligence.</span></div>
          <div class="sg-hero-desc">SAGE researches your business problem, gathers live market evidence, grades what it finds, and transforms complex research into structured, decision-ready strategy.</div>
          <div class="sg-pills">
            <div class="sg-pill">🌐 Web Research</div>
            <div class="sg-pill">📊 Evidence Intelligence</div>
            <div class="sg-pill">💡 Strategic Recommendations</div>
            <div class="sg-pill">🎯 Decision Support</div>
          </div>
        </div>
        <div class="sg-glass-panel">
          <div class="sg-panel-kicker">HOW SAGE THINKS</div>
          {flow}
        </div>
      </div>
    </div>
    """


def render_live_card(stage, message):
    all_done = stage > len(STAGES)
    items = []
    for i, (num, title, sub) in enumerate(STAGES, start=1):
        if all_done or i < stage:
            state, label = "done", "✓ DONE"
        elif i == stage:
            state, label = "active", "● ACTIVE"
        else:
            state, label = "", "QUEUED"
        items.append(
            f'<div class="sg-stage {state}"><div class="sg-stage-state">{label}</div>'
            f'<div class="sg-stage-num">{num}</div><div class="sg-stage-title">{esc(title)}</div>'
            f'<div class="sg-stage-sub">{esc(sub)}</div></div>'
        )
    stages_html = "".join(items)
    if all_done:
        title_html = "Research complete"
        status_html = '<span class="sg-status">✓ COMPLETE</span>'
        track_html = ""
    else:
        title_html = 'Researching<span class="sg-ellipsis"></span>'
        status_html = '<span class="sg-status"><i class="sg-pulse"></i>RESEARCHING</span>'
        track_html = '<div class="sg-track"><span></span></div>'
    return f"""
    <div class="sg-live">
      <div class="sg-orb a"></div><div class="sg-orb b"></div>
      <div class="sg-live-top">
        <span class="sg-chip-dark">SAGE INTELLIGENCE ENGINE</span>
        {status_html}
      </div>
      <div class="sg-live-title">{title_html}</div>
      <div class="sg-live-flow">Designing research → Gathering evidence → Analyzing intelligence → Building strategy</div>
      <div class="sg-live-msg">{esc(message)}</div>
      <div class="sg-stages">{stages_html}</div>
      {track_html}
    </div>
    """


def show_live(slot, stage, message):
    with slot.container():
        st.html(render_live_card(stage, message))


def render_metric_card(icon, label, value, plain=False):
    text = to_text(value)
    badge = "" if plain else strength_badge(text)
    body = badge if badge else f'<div class="sg-metric-value">{esc(text)}</div>'
    return (
        f'<div class="sg-card sg-metric"><div class="sg-metric-top"><span class="sg-icon sm">{esc(icon)}</span>'
        f'<span class="sg-lbl tight">{esc(label)}</span></div>{body}</div>'
    )


def render_quality_block(icon, label, value):
    return (
        f'<div class="sg-card"><div class="sg-block-head"><span class="sg-icon">{esc(icon)}</span>'
        f'<span class="sg-panel-title">{esc(label)}</span></div>'
        f'<div class="sg-val">{value_html(value)}</div></div>'
    )


def render_finding_card(index, item):
    used = set()
    if isinstance(item, dict):
        finding = take(item, ["finding", "key_finding", "insight", "title", "statement", "description", "text", "summary"], used)
        why = take(item, ["why_it_matters", "why_matters", "why_this_matters", "significance", "importance", "explanation", "business_meaning", "implication"], used)
        strength = take(item, ["evidence_strength", "strength", "evidence_level", "evidence_quality", "confidence"], used)
        extras = extras_html(item, used)
        main = to_text(finding)
    else:
        main, why, strength, extras = to_text(item), None, None, ""
    meta = strength_meta(strength) if strength is not None else None
    cls = meta[0] if meta else "neutral"
    badge = strength_badge(strength, allow_neutral=True) if strength is not None else ""
    if strength is not None and badge:
        strength_html = f'<div class="sg-strength-row"><div class="sg-lbl tight">Evidence strength</div>{badge}</div>'
    elif strength is not None:
        strength_html = f'<div class="sg-strength-row">{labeled("Evidence strength", strength)}</div>'
    else:
        strength_html = ""
    main_html = f'<div class="sg-finding-text">{esc(main)}</div>' if main else ""
    return (
        f'<div class="sg-card sg-finding {cls}"><div class="sg-finding-top">'
        f'<span class="sg-num">{index:02d}</span><span class="sg-eyebrow">Key finding</span></div>'
        f'{main_html}{labeled("Why it matters", why)}{extras}{strength_html}</div>'
    )


def item_row(item):
    if isinstance(item, dict):
        used = set()
        main = take(item, MAIN_KEYS, used)
        head = f'<div class="sg-row-main">{esc(to_text(main))}</div>' if main is not None else ""
        body = head + extras_html(item, used)
    else:
        inner = value_html(item)
        body = f'<div class="sg-row-main">{inner}</div>' if inner else ""
    if not body:
        return ""
    return f'<div class="sg-row"><i class="sg-bullet"></i><div class="sg-row-body">{body}</div></div>'


def render_panel(icon, title, items, tone=""):
    rows = [r for r in (item_row(x) for x in as_list(items)) if r]
    body = "".join(rows) if rows else '<div class="sg-empty small">No data returned.</div>'
    return (
        f'<div class="sg-card sg-panel {esc(tone)}"><div class="sg-panel-head"><span class="sg-icon">{esc(icon)}</span>'
        f'<span class="sg-panel-title">{esc(title)}</span><span class="sg-count">{len(rows)}</span></div>'
        f'<div class="sg-rows">{body}</div></div>'
    )


def render_segment_card(index, item):
    used = set()
    if isinstance(item, dict):
        name = to_text(take(item, ["segment", "segment_name", "customer_segment", "name", "title", "group", "persona"], used))
        behavior = take(item, ["behavior", "behaviors", "behaviour", "behaviours", "usage_pattern", "habits"], used)
        need = take(item, ["need", "needs", "pain_point", "pain_points", "jobs_to_be_done"], used)
        driver = take(item, ["value_driver", "value_drivers", "drivers", "key_driver", "motivation", "motivations"], used)
        implication = take(item, ["business_implication", "implication", "so_what"], used)
        desc = take(item, ["description", "profile", "characteristics", "summary"], used)
        tags = tags_from(item, used)
        extras = extras_html(item, used)
        blob = to_text(item)
        body = (
            labeled("Profile", desc) + labeled("Behavior", behavior) + labeled("Need", need)
            + labeled("Value driver", driver) + extras
        )
        impl_html = ""
        if implication is not None:
            impl_html = (
                f'<div class="sg-implication"><div class="sg-lbl tight">Business implication</div>'
                f'<div class="sg-val">{value_html(implication)}</div></div>'
            )
    else:
        head, tail = split_title(item)
        name = head
        blob = to_text(item)
        body = labeled("Profile", tail)
        impl_html, tags = "", ""
    name = name or "Customer segment"
    return (
        f'<div class="sg-card"><div class="sg-seg-top"><div class="sg-avatar">{esc(initial_of(name))}</div>'
        f'<div><div class="sg-eyebrow">Segment {index:02d}</div><div class="sg-seg-name">{esc(name)}</div></div></div>'
        f'{segment_badges(blob)}{tags}{body}{impl_html}</div>'
    )


def render_competitor_card(index, item):
    used = set()
    if isinstance(item, dict):
        name = to_text(take(item, ["competitor", "name", "company", "brand", "player", "title"], used))
        tags = tags_from(item, used)
        body = extras_html(item, used)
    else:
        head, tail = split_title(item)
        name = head
        tags = ""
        body = f'<div class="sg-val" style="margin-top:14px">{esc(tail)}</div>' if tail else ""
    name = name or f"Competitor {index}"
    return (
        f'<div class="sg-card"><div class="sg-seg-top"><div class="sg-avatar cyan">{esc(initial_of(name))}</div>'
        f'<div><div class="sg-eyebrow">Competitor {index:02d}</div><div class="sg-seg-name">{esc(name)}</div></div></div>'
        f'{tags}{body}</div>'
    )


def render_trend_card(index, item):
    used = set()
    if isinstance(item, dict):
        title = to_text(take(item, ["trend", "title", "name", "insight", "finding", "headline"], used))
        evidence = take(item, ["evidence", "supporting_evidence", "support", "data", "description"], used)
        implication = take(item, ["business_implication", "implication", "business_impact", "so_what"], used)
        tags = tags_from(item, used)
        extras = extras_html(item, used)
        blob = title + " " + to_text(evidence)
    else:
        title, evidence, implication, tags, extras = to_text(item), None, None, "", ""
        blob = title
    arrow, direction = trend_arrow(blob)
    impl_html = ""
    if implication is not None:
        impl_html = (
            f'<div class="sg-implication"><div class="sg-lbl tight">Business implication</div>'
            f'<div class="sg-val">{value_html(implication)}</div></div>'
        )
    title_html = f'<div class="sg-trend-title">{esc(title)}</div>' if title else ""
    return (
        f'<div class="sg-card sg-trend"><div class="sg-trend-top"><span class="sg-eyebrow">Trend {index:02d}</span>'
        f'<span class="sg-arrow {direction}">{arrow}</span></div>{title_html}{tags}'
        f'{labeled("Evidence", evidence)}{extras}{impl_html}</div>'
    )


def render_signal_card(index, item, kind):
    used = set()
    if isinstance(item, dict):
        title = to_text(take(item, ["title", "opportunity", "risk", "name", "headline", "finding", "insight"], used))
        explanation = take(item, ["explanation", "description", "why_it_matters", "rationale", "business_meaning", "implication", "details"], used)
        evidence = take(item, ["evidence", "supporting_evidence", "support", "basis", "based_on", "source_evidence"], used)
        tags = tags_from(item, used)
        extras = extras_html(item, used)
    else:
        title, explanation, evidence, tags, extras = to_text(item), None, None, "", ""
    if not title:
        title, explanation = (to_text(explanation) or "Strategic signal"), None
    is_opp = kind == "opp"
    icon = "💡" if is_opp else "⚠️"
    word = "Opportunity" if is_opp else "Risk"
    body_html = f'<div class="sg-signal-body">{value_html(explanation)}</div>' if explanation is not None else ""
    return (
        f'<div class="sg-card sg-signal {kind}"><div class="sg-signal-head"><span class="sg-signal-icon">{icon}</span>'
        f'<span class="sg-eyebrow">{word} {index:02d}</span></div>'
        f'<div class="sg-signal-title">{esc(title)}</div>{body_html}{tags}{labeled("Evidence", evidence)}{extras}</div>'
    )


def render_opportunity_card(index, item):
    return render_signal_card(index, item, "opp")


def render_risk_card(index, item):
    return render_signal_card(index, item, "risk")


def render_strategy_card(index, item):
    used = set()
    if isinstance(item, dict):
        implication = take(item, ["implication", "insight", "strategic_insight", "finding", "title", "statement"], used)
        based_on = take(item, ["based_on", "basis", "evidence", "supporting_evidence", "source_finding"], used)
        meaning = take(item, ["business_meaning", "why_it_matters", "meaning", "so_what", "business_implication"], used)
        tags = tags_from(item, used)
        extras = extras_html(item, used)
        main = to_text(implication)
    else:
        main, based_on, meaning, tags, extras = to_text(item), None, None, "", ""
    main_html = f'<div class="sg-glass-main">{esc(main)}</div>' if main else ""
    return (
        f'<div class="sg-glass"><div class="sg-eyebrow">Strategic insight {index:02d}</div>{main_html}{tags}'
        f'{labeled("Implication", None)}{labeled("Based on", based_on)}{labeled("Business meaning", meaning)}{extras}</div>'
    )


def render_action_card(index, item):
    used = set()
    if isinstance(item, dict):
        action = take(item, ["action", "recommendation", "recommended_action", "title", "step", "initiative"], used)
        based = take(item, ["based_on_finding", "based_on", "finding", "rationale", "why", "basis", "evidence"], used)
        impact = take(item, ["expected_business_impact", "expected_impact", "business_impact", "impact", "expected_outcome", "outcome", "benefit", "business_meaning"], used)
        tags = tags_from(item, used)
        extras = extras_html(item, used)
        main = to_text(action)
    else:
        main, based, impact, tags, extras = to_text(item), None, None, "", ""
    minis = ""
    if based is not None:
        minis += f'<div class="sg-mini"><div class="sg-lbl">Based on finding</div><div class="sg-val">{value_html(based)}</div></div>'
    if impact is not None:
        minis += f'<div class="sg-mini impact"><div class="sg-lbl">Expected business impact</div><div class="sg-val">{value_html(impact)}</div></div>'
    cols = f'<div class="sg-action-cols">{minis}</div>' if minis else ""
    title_html = f'<div class="sg-action-title">{esc(main)}</div>' if main else ""
    return (
        f'<div class="sg-card sg-action"><div class="sg-action-num">{index:02d}</div>'
        f'<div class="sg-action-body"><div class="sg-eyebrow">Action</div>{title_html}{tags}{cols}{extras}</div></div>'
    )


def link_html(url):
    if url.lower().startswith(("http://", "https://")):
        return f'<a class="sg-src-link" href="{esc(url)}" target="_blank" rel="noopener noreferrer">{esc(url)}</a>'
    return f'<span class="sg-src-link">{esc(url)}</span>'


def render_source_card(index, item):
    used = set()
    title, url, extras = "", "", ""
    if isinstance(item, dict):
        title = to_text(take(item, ["title", "name", "headline", "source", "site", "publication"], used))
        url = to_text(take(item, ["url", "link", "href", "source_url", "uri"], used))
        extras = extras_html(item, used)
    else:
        text = to_text(item)
        if text.lower().startswith(("http://", "https://")):
            url = text
        else:
            title = text
    if title.lower().startswith(("http://", "https://")) and not url:
        url, title = title, ""
    domain = domain_of(url) if url else ""
    display = title or domain or f"Source {index}"
    body = ""
    if url:
        body += f'<div class="sg-lbl">Link</div><div class="sg-val">{link_html(url)}</div>'
    body += extras
    num = f"{index:02d}"
    if not body:
        return (
            f'<div class="sg-source flat"><span class="sg-src-num">{num}</span>'
            f'<span class="sg-src-title" style="white-space:normal">{esc(display)}</span></div>'
        )
    chip = f'<span class="sg-src-domain">{esc(domain)}</span>' if domain else ""
    return (
        f'<details class="sg-source"><summary><span class="sg-src-num">{num}</span>'
        f'<span class="sg-src-title">{esc(display)}</span>{chip}<span class="sg-chevron">▾</span></summary>'
        f'<div class="sg-src-body">{body}</div></details>'
    )


def render_report_banner(brief, n_findings, n_sources):
    chips = ""
    for key, label in (("problem", "Problem"), ("market", "Market"), ("decision", "Decision")):
        text = (brief or {}).get(key, "")
        if text:
            chips += f'<div class="sg-brief-chip"><b>{label}</b><span>{esc(text)}</span></div>'
    brief_html = f'<div class="sg-brief">{chips}</div>' if chips else ""
    return f"""
    <div class="sg-banner sg-rise">
      <div class="sg-hero-gridbg"></div>
      <div class="sg-orb a"></div><div class="sg-orb c"></div>
      <div>
        <div class="sg-banner-kicker">✨ YOUR SAGE INTELLIGENCE REPORT</div>
        <div class="sg-banner-title">Research synthesized into structured business intelligence.</div>
        <div class="sg-banner-sub">{n_findings} key findings · {n_sources} sources · generated by the SAGE research engine</div>
        {brief_html}
      </div>
      <div class="sg-done"><div class="sg-done-ring">✓</div><div class="sg-done-label">RESEARCH COMPLETE</div></div>
    </div>
    """


def render_footer():
    return """
    <div class="sg-footer">
      <div class="sg-footer-brand">
        <div class="sg-logo sm"><i></i></div>
        <div>
          <div class="sg-footer-name">SAGE</div>
          <div class="sg-footer-sub">Strategic Analysis &amp; Guided Exploration</div>
        </div>
      </div>
      <div class="sg-footer-tag">AI-powered business research &amp; strategic intelligence</div>
    </div>
    """


# ============================================================
# REPORT SECTIONS
# ============================================================

def section_executive(d):
    summary = d.get("executive_summary")
    n_find = len(as_list(d.get("key_findings")))
    n_src = len(extract_sources(d.get("sources")))
    n_opp = len(as_list(d.get("opportunities")))
    n_risk = len(as_list(d.get("risks")))

    if isinstance(summary, str) and summary.strip():
        parts = re.split(r"(?<=[.!?])\s+", summary.strip(), maxsplit=1)
        lead = parts[0]
        rest = parts[1] if len(parts) > 1 else ""
        body = f'<div class="sg-exec-lead">{esc(lead)}</div>{para_html(rest)}'
    elif not is_empty(summary):
        body = f'<div class="sg-val" style="margin-top:16px">{value_html(summary)}</div>'
    else:
        body = render_empty("No executive summary was returned.")

    callout = ""
    takeaway = to_text(d.get("decision_takeaway"))
    if takeaway:
        first = re.split(r"(?<=[.!?])\s+", takeaway, maxsplit=1)[0]
        if len(first) > 280:
            first = first[:280].rstrip() + "…"
        callout = (
            '<div class="sg-callout"><div class="sg-eyebrow">Strategic takeaway</div>'
            f'<div class="sg-callout-text">{esc(first)}</div></div>'
        )

    stats = ""
    conf = find_confidence(d)
    if conf:
        badge = strength_badge(conf)
        value = badge if badge else f'<div class="sg-metric-value" style="font-size:16px;margin-top:10px">{esc(conf[:60])}</div>'
        stats += f'<div class="sg-stat"><div class="sg-lbl tight">Research confidence</div><div style="margin-top:10px">{value}</div></div>'
    for label, count in (("Key findings", n_find), ("Sources", n_src), ("Opportunities", n_opp), ("Risks", n_risk)):
        if count:
            stats += f'<div class="sg-stat"><div class="sg-lbl tight">{label}</div><div class="sg-stat-value">{count}</div></div>'

    main = (
        '<div class="sg-exec-main"><div class="sg-eyebrow">Executive summary</div>'
        f'{body}{callout}</div>'
    )
    rail = f'<div class="sg-rail">{stats}</div>' if stats else ""
    layout = f'<div class="sg-exec sg-rise">{main}{rail}</div>' if rail else f'<div class="sg-rise">{main}</div>'
    show_section("02", "EXECUTIVE INTELLIGENCE", "Executive Summary", "The central message from the research, at a glance.", layout)


def section_findings(d):
    items = as_list(d.get("key_findings"))
    if items:
        cards = "".join(render_finding_card(i, it) for i, it in enumerate(items, 1))
        body = f'<div class="sg-grid two">{cards}</div>'
    else:
        body = render_empty("No key findings were returned.")
    show_section("03", "WHAT WE LEARNED", "Key Findings", "The most important evidence-backed discoveries, graded by evidence strength.", body)


def section_market(d):
    mo = d.get("market_overview")
    panels = []
    if isinstance(mo, dict):
        spec = [
            ("chars", ["market_characteristics", "characteristics", "market_structure"]),
            ("demand", ["demand_patterns", "demand"]),
            ("devs", ["important_developments", "developments", "recent_developments"]),
        ]
        found, extras = collect_fields(mo, spec)
        if found["chars"] is not None:
            panels.append(render_panel("🌍", "Market Characteristics", found["chars"], "indigo"))
        if found["demand"] is not None:
            panels.append(render_panel("🛒", "Demand Patterns", found["demand"], "violet"))
        if found["devs"] is not None:
            panels.append(render_panel("⚡", "Important Developments", found["devs"], "cyan"))
        for k, v in extras:
            panels.append(render_panel("📌", title_of(k), v, "teal"))
    elif not is_empty(mo):
        panels.append(render_panel("🌍", "Market Overview", mo, "indigo"))
    body = f'<div class="sg-grid three">{"".join(panels)}</div>' if panels else render_empty("No market overview was returned.")
    show_section("04", "MARKET INTELLIGENCE", "Market Overview", "How the market is structured, how demand behaves, and what is changing.", body)


def section_customers(d):
    ci = d.get("customer_insights")
    segments, panels = [], []
    if isinstance(ci, dict):
        spec = [
            ("segments", ["segments", "customer_segments", "segment"]),
            ("behaviors", ["behaviors", "behaviours", "customer_behaviors", "customer_behaviours", "behavior"]),
            ("needs", ["needs", "customer_needs", "unmet_needs", "need"]),
        ]
        found, extras = collect_fields(ci, spec)
        segments = as_list(found["segments"])
        if found["behaviors"] is not None:
            panels.append(render_panel("🧠", "Customer Behavior", found["behaviors"], "violet"))
        if found["needs"] is not None:
            panels.append(render_panel("💬", "Customer Needs", found["needs"], "cyan"))
        for k, v in extras:
            panels.append(render_panel("📌", title_of(k), v, "teal"))
    elif isinstance(ci, (list, tuple)):
        segments = as_list(ci)
    elif not is_empty(ci):
        panels.append(render_panel("👥", "Customer Insights", ci, "indigo"))

    body = ""
    if segments:
        cards = "".join(render_segment_card(i, s) for i, s in enumerate(segments, 1))
        body += f'<div class="sg-grid">{cards}</div>'
    if panels:
        gap = ' style="margin-top:18px"' if segments else ""
        body += f'<div class="sg-grid two"{gap}>{"".join(panels)}</div>'
    if not body:
        body = render_empty("No customer insights were returned.")
    show_section("05", "CUSTOMER INTELLIGENCE", "Customer Insights", "Who the customers are, how they behave and what they need.", body)


def section_competition(d):
    cl = d.get("competitive_landscape")
    competitors, panels = [], []
    if isinstance(cl, dict):
        spec = [
            ("competitors", ["competitors", "players", "key_competitors", "competitor"]),
            ("diff", ["differentiation", "differentiation_signals", "differentiators"]),
            ("gaps", ["competitive_gaps", "gaps", "white_space", "whitespace"]),
        ]
        found, extras = collect_fields(cl, spec)
        competitors = as_list(found["competitors"])
        if found["diff"] is not None:
            panels.append(render_panel("⚔️", "Differentiation Signals", found["diff"], "violet"))
        if found["gaps"] is not None:
            panels.append(render_panel("🎯", "Competitive Gaps", found["gaps"], "teal"))
        for k, v in extras:
            panels.append(render_panel("📌", title_of(k), v, "cyan"))
    elif isinstance(cl, (list, tuple)):
        competitors = as_list(cl)
    elif not is_empty(cl):
        panels.append(render_panel("⚔️", "Competitive Landscape", cl, "indigo"))

    body = ""
    if competitors:
        cards = "".join(render_competitor_card(i, c) for i, c in enumerate(competitors, 1))
        body += f'<div class="sg-grid">{cards}</div>'
    if panels:
        gap = ' style="margin-top:18px"' if competitors else ""
        body += f'<div class="sg-grid two"{gap}>{"".join(panels)}</div>'
    if not body:
        body = render_empty("No competitive landscape was returned.")
    show_section("06", "COMPETITIVE LANDSCAPE", "Competitive Landscape", "How competitors are positioned and where differentiation is emerging.", body)


def section_trends(d):
    items = as_list(d.get("market_trends"))
    if items:
        cards = "".join(render_trend_card(i, t) for i, t in enumerate(items, 1))
        body = f'<div class="sg-grid two">{cards}</div>'
    else:
        body = render_empty("No market trends were returned.")
    show_section("07", "FUTURE SIGNALS", "Market Trends", "Emerging patterns that may influence the business decision.", body)


def section_signals(d):
    opps = as_list(d.get("opportunities"))
    risks = as_list(d.get("risks"))

    def column(icon, title, cards, count):
        inner = "".join(cards) if cards else render_empty("Nothing returned for this category.")
        return (
            f'<div class="sg-col"><div class="sg-col-head"><span class="sg-icon">{icon}</span>'
            f'<span class="sg-col-title">{title}</span><span class="sg-count">{count}</span></div>{inner}</div>'
        )

    left = column("💡", "Opportunities", [render_opportunity_card(i, o) for i, o in enumerate(opps, 1)], len(opps))
    right = column("⚠️", "Risks", [render_risk_card(i, r) for i, r in enumerate(risks, 1)], len(risks))
    show_section(
        "08", "STRATEGIC SIGNALS", "Opportunities & Risks",
        "Where the research points toward value creation — and where exposure sits.",
        f'<div class="sg-duo">{left}{right}</div>',
    )


def section_insights(d):
    items = as_list(d.get("strategic_insights"))
    if items:
        cards = "".join(render_strategy_card(i, it) for i, it in enumerate(items, 1))
        body = (
            '<div class="sg-brain"><div class="sg-orb a"></div><div class="sg-orb c"></div>'
            f'<div class="sg-grid two">{cards}</div></div>'
        )
    else:
        body = render_empty("No strategic insights were returned.")
    show_section("09", "STRATEGIC THINKING", "Strategic Insights", "What the evidence means for the business — the consulting brain of SAGE.", body)


def section_actions(d):
    items = as_list(d.get("recommended_actions"))
    if items:
        cards = "".join(render_action_card(i, it) for i, it in enumerate(items, 1))
        body = f'<div class="sg-grid stack">{cards}</div>'
    else:
        body = render_empty("No recommended actions were returned.")
    show_section("10", "ACTION PLAN", "Recommended Actions", "Practical next steps derived from the evidence and strategic insights.", body)


def section_decision(d):
    takeaway = d.get("decision_takeaway")
    if isinstance(takeaway, str) and takeaway.strip():
        text = takeaway.strip()
        cls = "sg-decision-text long" if len(text) > 320 else "sg-decision-text"
        inner = f'<div class="{cls}">{esc(text).replace(chr(10), "<br>")}</div>'
    elif not is_empty(takeaway):
        inner = f'<div class="sg-decision-text long">{value_html(takeaway)}</div>'
    else:
        inner = '<div class="sg-decision-text long">No decision takeaway was returned.</div>'
    body = (
        '<div class="sg-decision sg-rise"><div class="sg-hero-gridbg"></div>'
        '<div class="sg-orb a"></div><div class="sg-orb b"></div>'
        f'<div class="sg-decision-label">THE DECISION</div>{inner}</div>'
    )
    show_section("11", "DECISION SUPPORT", "Decision Takeaway", "The decision-oriented conclusion of the research.", body)


def q_icon(key):
    nk = norm(key)
    for frag, icon in (
        ("confidence", "🎯"), ("limit", "⚠️"), ("validat", "🔍"), ("next", "🔍"),
        ("quality", "📊"), ("source", "🔗"), ("strength", "💪"), ("gap", "🧩"),
    ):
        if frag in nk:
            return icon
    return "✓"


def section_quality(d):
    eq = d.get("evidence_quality")
    n_src = len(extract_sources(d.get("sources")))
    metrics, blocks = [], []
    if isinstance(eq, dict):
        for key, val in eq.items():
            if is_empty(val):
                continue
            if isinstance(val, (str, int, float, bool)) and len(to_text(val)) <= 40:
                metrics.append(render_metric_card(q_icon(key), title_of(key), val))
            else:
                blocks.append(render_quality_block(q_icon(key), title_of(key), val))
    elif not is_empty(eq):
        blocks.append(render_quality_block("📊", "Evidence Quality", eq))
    if n_src:
        metrics.append(render_metric_card("🔗", "Sources cited", str(n_src), plain=True))

    body = ""
    if metrics:
        body += f'<div class="sg-grid metrics">{"".join(metrics)}</div>'
    if blocks:
        gap = ' style="margin-top:18px"' if metrics else ""
        body += f'<div class="sg-grid two"{gap}>{"".join(blocks)}</div>'
    if not body:
        body = render_empty("No evidence quality assessment was returned.")
    show_section("12", "RESEARCH QUALITY", "Evidence & Confidence", "How strongly the research supports the conclusions — and what to validate next.", body)


def section_sources(d):
    sources = extract_sources(d.get("sources"))
    if sources:
        cards = "".join(render_source_card(i, s) for i, s in enumerate(sources, 1))
        body = f'<div class="sg-sources">{cards}</div>'
    else:
        body = render_empty("No source list was returned in the final report.")
    show_section("13", "EVIDENCE TRAIL", "Research Sources", "Sources used to support the findings. Expand a card for details.", body)


def section_trail(d):
    blocks = []
    for key, title in (("research_plan", "Research plan"), ("research_evidence", "Collected evidence")):
        value = d.get(key)
        if is_empty(value):
            continue
        inner = value_html(value, max_chars=900)
        if not inner:
            continue
        blocks.append(
            f'<details class="sg-source"><summary><span class="sg-src-num">↳</span>'
            f'<span class="sg-src-title">{esc(title)}</span><span class="sg-chevron">▾</span></summary>'
            f'<div class="sg-src-body">{inner}</div></details>'
        )
    if not blocks:
        return
    show_section(
        "14", "RESEARCH TRAIL", "How SAGE Researched This",
        "The research plan and evidence behind the report. The full dataset is available as JSON below.",
        f'<div class="sg-stackcol">{"".join(blocks)}</div>',
    )


REPORT_SECTIONS = [
    section_executive, section_findings, section_market, section_customers,
    section_competition, section_trends, section_signals, section_insights,
    section_actions, section_decision, section_quality, section_sources, section_trail,
]


# ============================================================
# RESEARCH RUNNER (subprocess → agent_v3.py, unchanged backend)
# ============================================================

def run_sage_research(problem, market, decision, live_slot):
    """Runs agent_v3.py exactly like before. Returns (data, error_message, log_tail)."""
    if not AGENT_PATH.exists():
        return None, "agent_v3.py was not found next to app.py.", ""

    if REPORT_PATH.exists():
        try:
            REPORT_PATH.unlink()
        except Exception:
            pass

    stage = 1
    show_live(live_slot, stage, STAGE_MESSAGES[1])

    payload = f"{problem}\n{market}\n{decision}\n"
    log = []
    process = None

    try:
        process = subprocess.Popen(
            [sys.executable, "-u", str(AGENT_PATH)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            errors="replace",
            cwd=str(BASE_DIR),
        )

        process.stdin.write(payload)
        process.stdin.flush()
        process.stdin.close()

        for raw in iter(process.stdout.readline, ""):
            line = raw.strip()
            if not line:
                continue

            log.append(line)
            if len(log) > 500:
                del log[:100]

            lower = line.lower()
            detected = 0
            if "strategic synthesis" in lower or "stage 4" in lower:
                detected = 4
            elif "business intelligence" in lower or "stage 3" in lower:
                detected = 3
            elif "web research" in lower or "stage 2" in lower:
                detected = 2
            elif "research design" in lower or "stage 1" in lower:
                detected = 1

            if detected > stage:
                stage = detected
                show_live(live_slot, stage, STAGE_MESSAGES[stage])

        try:
            process.stdout.close()
        except Exception:
            pass
        process.wait()

        if process.returncode != 0:
            tail = "\n".join(log)[-5000:]
            return None, "SAGE encountered an error while generating the research report.", tail

        for _ in range(20):
            if REPORT_PATH.exists():
                break
            time.sleep(0.2)

        if not REPORT_PATH.exists():
            return None, "Research completed, but SAGE could not find the generated report.", "\n".join(log)[-5000:]

        with open(REPORT_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        show_live(live_slot, len(STAGES) + 1, "Research complete. Building your intelligence report...")
        time.sleep(0.8)
        return data, None, ""

    except json.JSONDecodeError as e:
        return None, f"The research report could not be read (invalid JSON): {e}", "\n".join(log)[-5000:]
    except Exception as e:
        return None, f"SAGE could not complete the research: {e}", "\n".join(log)[-5000:]
    finally:
        try:
            if process is not None and process.poll() is None:
                process.terminate()
        except Exception:
            pass


# ============================================================
# PAGE: STYLES + HERO
# ============================================================

show(SAGE_CSS)
show(render_hero())


# ============================================================
# PAGE: RESEARCH BRIEF
# ============================================================

show(
    render_section_header(
        "01",
        "RESEARCH BRIEF",
        "Start with a business question.",
        "Tell SAGE what you want to understand. The sharper the question, the more useful the intelligence.",
    )
)

col1, col2, col3 = st.columns(3, gap="medium")

with col1:
    show(field_head("🔎", "Business Problem", "What should SAGE investigate?"))
    business_problem = st.text_area(
        "Business Problem",
        placeholder="Example: Should a new coffee brand target college students?",
        label_visibility="collapsed",
        key="business_problem",
        height=150,
    )

with col2:
    show(field_head("🌍", "Target Market", "Which market should SAGE focus on?"))
    target_market = st.text_area(
        "Target Market",
        placeholder="Example: India — Hyderabad",
        label_visibility="collapsed",
        key="target_market",
        height=150,
    )

with col3:
    show(field_head("🎯", "Business Decision", "What decision should this research support?"))
    business_decision = st.text_area(
        "Business Decision",
        placeholder="Example: Decide whether to launch, which segment to target and how to position.",
        label_visibility="collapsed",
        key="business_decision",
        height=150,
    )

show('<div style="height:6px"></div>')

spacer_left, mid_col, spacer_right = st.columns([1, 2, 1])
with mid_col:
    start = st.button("🚀  Start SAGE Research", key="start_sage")

show(
    '<div class="sg-caption">SAGE will research market conditions, customers, competitors, '
    "trends, opportunities and risks.</div>"
)


# ============================================================
# RUN RESEARCH
# ============================================================

if start:
    problem_clean = one_line(business_problem)
    market_clean = one_line(target_market)
    decision_clean = one_line(business_decision)

    if not problem_clean:
        show(render_notice("warning", "Business problem needed", "Please enter a business problem first."))
    elif not market_clean:
        show(render_notice("warning", "Target market needed", "Please enter a target market."))
    elif not decision_clean:
        show(render_notice("warning", "Business decision needed", "Please enter the business decision."))
    else:
        st.session_state.pop("sage_data", None)
        st.session_state.pop("sage_brief", None)

        live_slot = st.empty()
        result, error, log_tail = run_sage_research(problem_clean, market_clean, decision_clean, live_slot)
        live_slot.empty()

        if error:
            show(render_notice("error", "SAGE couldn't complete the research", error))
            if log_tail:
                with st.expander("Technical details"):
                    st.code(log_tail)
        else:
            if not isinstance(result, dict):
                result = {"executive_summary": to_text(result)}
            st.session_state["sage_data"] = result
            st.session_state["sage_brief"] = {
                "problem": problem_clean,
                "market": market_clean,
                "decision": decision_clean,
            }


# ============================================================
# REPORT
# ============================================================

data = st.session_state.get("sage_data")

if not data:
    show(render_footer())
    st.stop()

brief = st.session_state.get("sage_brief", {})
report = {norm(k): v for k, v in data.items()}

show(
    render_report_banner(
        brief,
        len(as_list(report.get("key_findings"))),
        len(extract_sources(report.get("sources"))),
    )
)

for section_fn in REPORT_SECTIONS:
    try:
        section_fn(report)
    except Exception:
        show(
            render_notice(
                "warning",
                "Section unavailable",
                "One section of the report could not be displayed. The full data is still available in the JSON download below.",
            )
        )


# ============================================================
# DOWNLOAD
# ============================================================

show('<div style="height:34px"></div>')

json_data = json.dumps(data, indent=2, ensure_ascii=False, default=str)

dl_left, dl_mid, dl_right = st.columns([1, 2, 1])
with dl_mid:
    st.download_button(
        label="⬇️  Download Full Research Data (JSON)",
        data=json_data,
        file_name="sage_research_data.json",
        mime="application/json",
        key="download_sage_json",
    )


# ============================================================
# FOOTER
# ============================================================

show(render_footer())