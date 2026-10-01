import streamlit as st

CSS = r'''
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500;600&display=swap');
:root{
 --bg:#f5f7f7;--surface:#ffffff;--surface-2:#eef3f4;--ink:#172126;--muted:#66747b;--line:#dce4e6;
 --primary:#1f5f78;--primary-strong:#17495d;--primary-soft:#e9f2f5;--primary-line:#bfd4dc;
 --good:#28755f;--good-soft:#edf7f3;--bad:#a84444;--warn:#9a6b24;
 --sidebar:#1d292e;--sidebar-2:#25353b;--sidebar-line:#34464d;--sidebar-text:#dce7ea;--sidebar-muted:#91a4ab;
 --radius:10px;--shadow:0 8px 24px rgba(23,33,38,.045)
}
html,body,[class*="css"]{font-family:'Inter',sans-serif}.stApp{background:var(--bg);color:var(--ink)}
#MainMenu,header[data-testid="stHeader"],footer{visibility:hidden}.block-container{max-width:1240px;padding:2.15rem 2.6rem 4rem}.stDeployButton{display:none}
[data-testid="InputInstructions"],div[data-testid="InputInstructions"]{display:none!important}
h1,h2,h3{letter-spacing:-.035em;color:var(--ink)}h1{font-size:2rem!important;line-height:1.15!important}h2{font-size:1.45rem!important}h3{font-size:1.05rem!important}.stCaption,small{color:var(--muted)!important}

/* SIDEBAR */
[data-testid="stSidebar"]{background:var(--sidebar);border-right:1px solid var(--sidebar-line);width:238px!important}
[data-testid="stSidebar"]>div:first-child{width:238px!important;padding:1.35rem 1rem 1.2rem}
[data-testid="stSidebar"] *{color:var(--sidebar-text)}
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p{color:var(--sidebar-muted)!important;line-height:1.45}
[data-testid="stSidebar"] hr{border-color:var(--sidebar-line);margin:1rem .1rem}
[data-testid="stSidebar"] .stButton{margin:.12rem 0}
[data-testid="stSidebar"] .stButton>button{background:transparent;border:1px solid transparent;color:var(--sidebar-text);text-align:left;justify-content:flex-start;width:100%;box-shadow:none;padding:.58rem .68rem;border-radius:8px;font-weight:500;min-height:40px;gap:.65rem}
[data-testid="stSidebar"] .stButton>button p{width:auto;text-align:left;margin:0;font-size:.88rem;line-height:1.1}
[data-testid="stSidebar"] .stButton>button [data-testid="stIconMaterial"]{color:var(--sidebar-muted)!important;font-size:19px!important}
[data-testid="stSidebar"] .stButton>button:hover{background:var(--sidebar-2);color:#fff;border-color:var(--sidebar-line)}
[data-testid="stSidebar"] .stButton>button:hover [data-testid="stIconMaterial"]{color:#fff!important}
[data-testid="stSidebar"] .stButton>button[kind="primary"]{background:#eaf3f6!important;color:#173f4f!important;border-color:#eaf3f6!important;box-shadow:none!important}
[data-testid="stSidebar"] .stButton>button[kind="primary"] p,[data-testid="stSidebar"] .stButton>button[kind="primary"] [data-testid="stIconMaterial"]{color:#173f4f!important;font-weight:650}

/* CONTROLS */
.stButton>button,.stFormSubmitButton>button{min-height:40px;border-radius:8px;border:1px solid #cfdadd;background:#fff;color:var(--ink);font-weight:600;box-shadow:0 1px 2px rgba(23,33,38,.025);transition:.15s ease}
.stButton>button:hover,.stFormSubmitButton>button:hover{border-color:#9fb4bc;background:#f9fbfb;color:var(--ink)}
button[kind="primary"]{background:var(--primary)!important;color:#fff!important;border-color:var(--primary)!important}button[kind="primary"]:hover{background:var(--primary-strong)!important;border-color:var(--primary-strong)!important}
[data-testid="stTextInput"] input,[data-testid="stNumberInput"] input,[data-testid="stTextArea"] textarea,[data-baseweb="select"]>div{border:1px solid #cfdadd!important;border-radius:8px!important;background:#fff!important;box-shadow:none!important;color:var(--ink)!important}
[data-testid="stTextInput"] input:focus,[data-testid="stNumberInput"] input:focus,[data-testid="stTextArea"] textarea:focus{border-color:var(--primary)!important;box-shadow:0 0 0 2px rgba(31,95,120,.09)!important}

/* DATA / SURFACES */
[data-testid="stMetric"]{background:#fff;border:1px solid var(--line);padding:14px 16px;border-radius:9px;box-shadow:none}[data-testid="stMetricLabel"]{font-size:.75rem;color:var(--muted)}[data-testid="stMetricValue"]{font-size:1.35rem;font-weight:650;letter-spacing:-.03em}
[data-testid="stDataFrame"],[data-testid="stDataEditor"]{border:1px solid var(--line);border-radius:9px;overflow:hidden;background:#fff}
[data-testid="stExpander"]{background:#fff;border:1px solid var(--line)!important;border-radius:9px!important;box-shadow:none}
[data-testid="stTabs"] [data-baseweb="tab-list"]{gap:1.25rem;border-bottom:1px solid var(--line)}[data-testid="stTabs"] button{padding-left:0;padding-right:0;color:var(--muted)}
[data-testid="stTabs"] button[aria-selected="true"]{color:var(--primary)!important}
[data-testid="stAlert"]{border-radius:9px;border-width:1px}
[data-testid="stPlotlyChart"]{background:#fff;border:1px solid var(--line);border-radius:9px;padding:8px}

.mcda-eyebrow{font-size:10px;letter-spacing:.17em;text-transform:uppercase;font-weight:700;color:#687980;margin-bottom:8px}.mcda-title{font-size:30px;line-height:1.12;letter-spacing:-.04em;font-weight:700;margin:0;color:var(--ink)}.mcda-lead{font-size:15px;line-height:1.65;color:#586970;max-width:760px;margin-top:10px}.mcda-rule{height:1px;background:var(--line);margin:18px 0}
.mcda-card{background:#fff;border:1px solid var(--line);border-radius:9px;padding:18px;box-shadow:var(--shadow);height:100%}.mcda-card-flat{background:#fff;border:1px solid var(--line);border-radius:9px;padding:16px;height:100%}.mcda-card-label{font-size:10px;text-transform:uppercase;letter-spacing:.1em;color:#708087;font-weight:700}.mcda-card-value{font-size:22px;letter-spacing:-.04em;font-weight:700;margin-top:7px;color:var(--ink)}.mcda-card-note{font-size:12px;color:#718087;margin-top:5px;line-height:1.5}
.mcda-badge{display:inline-flex;align-items:center;border:1px solid #cfdadd;border-radius:999px;padding:5px 9px;font-size:9px;letter-spacing:.07em;text-transform:uppercase;font-weight:700;background:#fff;color:#53636a;margin-right:6px}.mcda-badge.blue{background:var(--primary-soft);border-color:var(--primary-line);color:var(--primary-strong)}.mcda-badge.green{background:var(--good-soft);border-color:#bddfd2;color:#23644f}
.mcda-formula{font-family:'JetBrains Mono',monospace;background:#203036;color:#eef5f6;border:1px solid #31454c;border-radius:9px;padding:16px 18px;font-size:13px;line-height:1.8;overflow:auto}.mcda-callout{background:#fff;border:1px solid var(--line);border-left:3px solid var(--primary);border-radius:8px;padding:13px 15px;color:#586970;font-size:13px;line-height:1.55}.mcda-section{font-size:10px;text-transform:uppercase;letter-spacing:.15em;font-weight:700;color:#708087;margin:26px 0 10px}
.mcda-footer{border-top:1px solid var(--line);margin-top:38px;padding-top:18px;color:#718087;font-size:10px;line-height:1.75}.mcda-footer strong{color:#506168}.mcda-login-wrap{padding-top:4vh}.mcda-hero{padding:28px 18px 28px 0}.mcda-hero h1{font-size:46px!important;max-width:560px}.mcda-flow{font-family:'JetBrains Mono',monospace;font-size:11px;color:#52656d;line-height:2.1;margin-top:28px;letter-spacing:.02em}.mcda-login-card{background:#fff;border:1px solid var(--line);border-radius:10px;padding:24px;box-shadow:var(--shadow)}
.mcda-rank{display:flex;align-items:center;gap:12px;padding:10px 0;border-bottom:1px solid #edf1f2}.mcda-rank:last-child{border-bottom:0}.mcda-rank-n{font-family:'JetBrains Mono';font-size:11px;color:#93a1a6;width:28px}.mcda-rank-name{font-weight:650;flex:1}.mcda-rank-val{font-family:'JetBrains Mono';font-size:12px;color:#52656d}
.mcda-sidebar-brand{font-size:16px;font-weight:700;letter-spacing:-.025em;color:#fff;margin:.2rem 0 .2rem}.mcda-sidebar-kicker{font-size:10px;letter-spacing:.12em;text-transform:uppercase;color:var(--sidebar-muted);font-weight:700}.mcda-sidebar-title{font-size:14px;font-weight:650;color:#fff;margin:.15rem 0 .25rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.mcda-sidebar-meta{font-size:11px;line-height:1.6;color:var(--sidebar-muted)}
@media(max-width:900px){.block-container{padding:1.4rem 1rem 3rem}.mcda-hero h1{font-size:34px!important}[data-testid="stSidebar"]{width:220px!important}[data-testid="stSidebar"]>div:first-child{width:220px!important}}
</style>
'''

def apply_theme(): st.markdown(CSS, unsafe_allow_html=True)
