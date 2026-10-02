"""Design tokens e CSS global do MCDA Lab.

Toda cor, medida e fonte usada pela interface (HTML, CSS e gráficos) sai daqui.
As cores de base também estão em .streamlit/config.toml, que é de onde o
Streamlit tira o tema dos widgets nativos; mantenha os dois em sincronia.
"""
import streamlit as st

COLORS = {
    'canvas': '#F4F6F6',
    'surface': '#FFFFFF',
    'sunken': '#EDF1F2',
    'ink': '#18242A',
    'ink-2': '#44535A',
    'muted': '#5D6C73',
    'faint': '#93A0A6',
    'line': '#DDE4E6',
    'line-strong': '#C5D0D4',
    'primary': '#1B5A72',
    'primary-strong': '#134556',
    'primary-soft': '#E6F0F3',
    'primary-line': '#B9D0D8',
    'secondary': '#5B7785',
    'secondary-soft': '#EDF1F3',
    # diferenciação sutil entre métodos: mesma família de azuis, matiz deslocado
    'promethee': '#1B5A72',
    'promethee-soft': '#E6F0F3',
    'electre': '#41587A',
    'electre-soft': '#EAEEF5',
    'success': '#1F6B55',
    'success-soft': '#E8F4EF',
    'success-line': '#B7DACC',
    'warning': '#8A5A10',
    'warning-soft': '#FBF3E1',
    'warning-line': '#E8D3A2',
    'danger': '#A33B3B',
    'danger-soft': '#FBECEC',
    'danger-line': '#E6BFBF',
}

FONTS = {
    'sans': "'Inter', system-ui, -apple-system, 'Segoe UI', sans-serif",
    'serif': "'Source Serif 4', Georgia, 'Times New Roman', serif",
    'mono': "'JetBrains Mono', ui-monospace, 'SFMono-Regular', Consolas, monospace",
}

# tamanhos em px
TYPE = {'2xs': 10, 'xs': 11, 'sm': 12, 'base': 14, 'md': 15, 'lg': 18, 'xl': 22, '2xl': 30, '3xl': 44}
SPACE = {1: 4, 2: 8, 3: 12, 4: 16, 5: 24, 6: 32, 7: 48, 8: 64}
RADIUS = {'sm': 4, 'md': 6, 'lg': 8}
SHADOWS = {
    'sm': '0 1px 2px rgba(24,36,42,.05)',
    'md': '0 6px 20px rgba(24,36,42,.06)',
    'focus': '0 0 0 3px rgba(27,90,114,.16)',
}
WIDTHS = {'content': 1200, 'login': 1080, 'sidebar': 248, 'prose': 720}
HEIGHTS = {'control': 40, 'nav': 36, 'chart': 360, 'chart-lg': 420}
ICONS = {'sm': 16, 'md': 18, 'lg': 20}

# séries categóricas dos gráficos: matizes dessaturados, primeiro o primário
CHART_SERIES = ['#1B5A72', '#B0752A', '#5E7F4E', '#84506C', '#41587A', '#B5573C', '#2F8A86', '#7A8A91']


def _root():
    v = {f'c-{k}': x for k, x in COLORS.items()}
    v.update({f'f-{k}': x for k, x in FONTS.items()})
    v.update({f't-{k}': f'{x}px' for k, x in TYPE.items()})
    v.update({f's-{k}': f'{x}px' for k, x in SPACE.items()})
    v.update({f'r-{k}': f'{x}px' for k, x in RADIUS.items()})
    v.update({f'sh-{k}': x for k, x in SHADOWS.items()})
    v.update({f'w-{k}': f'{x}px' for k, x in WIDTHS.items()})
    v.update({f'h-{k}': f'{x}px' for k, x in HEIGHTS.items()})
    v.update({f'i-{k}': f'{x}px' for k, x in ICONS.items()})
    return ':root{' + ''.join(f'--{k}:{x};' for k, x in v.items()) + '}'


CSS = r'''
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,500;8..60,600&display=swap');

/* ── APP SHELL ─────────────────────────────────────────────── */
.stApp{background:var(--c-canvas);color:var(--c-ink)}
header[data-testid="stHeader"]{background:transparent}
[data-testid="stMainBlockContainer"]{max-width:var(--w-content);padding:56px var(--s-6) var(--s-8)}
[data-testid="InputInstructions"]{display:none}
.stMain h1,.stMain h2,.stMain h3{color:var(--c-ink);letter-spacing:-.02em}
.stMain h3{font-size:var(--t-md);font-weight:600;padding:0 0 var(--s-2)}
[data-testid="stCaptionContainer"],[data-testid="stCaptionContainer"] p{color:var(--c-muted);opacity:1;font-size:var(--t-sm)}
.stMain [data-testid="stMarkdownContainer"] p{font-size:var(--t-base);line-height:1.6}

/* ── SIDEBAR ───────────────────────────────────────────────── */
[data-testid="stSidebar"]{border-right:1px solid var(--c-line)}
[data-testid="stSidebar"][aria-expanded="true"]{width:var(--w-sidebar)!important;min-width:var(--w-sidebar)!important}
[data-testid="stSidebarContent"]{padding:0}
[data-testid="stSidebarUserContent"]{padding:0 var(--s-3) var(--s-5)}
[data-testid="stSidebar"] hr{margin:var(--s-2) 0;border-color:var(--c-line)}
.mcda-brand{padding:0 var(--s-3)}
.mcda-brand-kicker{font-size:var(--t-2xs);letter-spacing:.14em;text-transform:uppercase;font-weight:600;color:var(--c-muted)}
.mcda-brand-name{font-family:var(--f-serif);font-size:var(--t-xl);font-weight:600;letter-spacing:-.02em;color:var(--c-ink);line-height:1.2;margin-top:2px}
.mcda-side-block{padding:0 var(--s-3)}
.mcda-side-label{font-size:var(--t-2xs);letter-spacing:.12em;text-transform:uppercase;font-weight:600;color:var(--c-muted);margin-bottom:var(--s-1)}
.mcda-side-title{font-size:var(--t-base);font-weight:600;color:var(--c-ink);line-height:1.35;overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical}
.mcda-side-meta{font-size:var(--t-sm);color:var(--c-muted);line-height:1.6;margin-top:var(--s-1)}
.mcda-side-meta .mono{font-family:var(--f-mono);font-size:var(--t-xs)}

/* navegação: [ícone] [número] [label], tudo no mesmo eixo */
.st-key-nav,.st-key-nav_foot{gap:2px}
.st-key-nav button,.st-key-nav_foot button{height:var(--h-nav);min-height:var(--h-nav);padding:0 var(--s-3);border:0;border-radius:var(--r-md);background:transparent;box-shadow:none;justify-content:flex-start;color:var(--c-ink-2);font-weight:500}
.st-key-nav button>div,.st-key-nav_foot button>div{justify-content:flex-start;align-items:center;gap:var(--s-3);width:100%}
.st-key-nav button [data-testid="stIconMaterial"],.st-key-nav_foot button [data-testid="stIconMaterial"]{font-size:var(--i-md);width:var(--i-md);color:var(--c-muted);margin:0;flex:none}
.st-key-nav button [data-testid="stMarkdownContainer"],.st-key-nav_foot button [data-testid="stMarkdownContainer"]{flex:1;min-width:0}
.st-key-nav button p,.st-key-nav_foot button p{display:flex;align-items:center;gap:var(--s-3);margin:0;font-size:var(--t-base);line-height:1;text-align:left;font-weight:inherit}
.st-key-nav button code{flex:none;width:18px;padding:0;background:none;border:0;font-family:var(--f-mono);font-size:var(--t-xs);font-weight:500;color:var(--c-faint);font-variant-numeric:tabular-nums}
.st-key-nav button:hover,.st-key-nav_foot button:hover{background:var(--c-sunken);color:var(--c-ink)}
.st-key-nav button:hover [data-testid="stIconMaterial"],.st-key-nav_foot button:hover [data-testid="stIconMaterial"]{color:var(--c-ink-2)}
.st-key-nav button[kind="primary"]{background:var(--c-primary-soft);color:var(--c-primary-strong);font-weight:600;box-shadow:inset 2px 0 0 var(--c-primary)}
.st-key-nav button[kind="primary"] [data-testid="stIconMaterial"],.st-key-nav button[kind="primary"] code{color:var(--c-primary)}
.st-key-nav button:focus-visible,.st-key-nav_foot button:focus-visible{box-shadow:var(--sh-focus);outline:0}

/* ── BOTÕES: primary · secondary · ghost (tertiary) · danger · icon ── */
[data-testid="stBaseButton-primary"],[data-testid="stBaseButton-secondary"],[data-testid="stBaseButton-tertiary"],
[data-testid="stBaseButton-primaryFormSubmit"],[data-testid="stBaseButton-secondaryFormSubmit"]{
  height:var(--h-control);min-height:var(--h-control);padding:0 var(--s-4);border-radius:var(--r-md);
  font-size:var(--t-base);font-weight:600;box-shadow:none;transition:background .12s ease,border-color .12s ease,color .12s ease}
[data-testid^="stBaseButton-"] p{font-size:var(--t-base);font-weight:inherit}
[data-testid="stBaseButton-primary"]:hover,[data-testid="stBaseButton-primaryFormSubmit"]:hover{background:var(--c-primary-strong);border-color:var(--c-primary-strong)}
[data-testid="stBaseButton-secondary"],[data-testid="stBaseButton-secondaryFormSubmit"]{background:var(--c-surface);border:1px solid var(--c-line-strong);color:var(--c-ink)}
[data-testid="stBaseButton-secondary"]:hover,[data-testid="stBaseButton-secondaryFormSubmit"]:hover{background:var(--c-surface);border-color:var(--c-primary);color:var(--c-primary-strong)}
[data-testid="stBaseButton-tertiary"]{color:var(--c-primary);padding:0 var(--s-3)}
[data-testid="stBaseButton-tertiary"]:hover{background:var(--c-primary-soft);color:var(--c-primary-strong)}
[data-testid^="stBaseButton-"]:focus-visible{box-shadow:var(--sh-focus);outline:0}
[data-testid^="stBaseButton-"]:disabled{opacity:.5;cursor:not-allowed}
[class*="st-key-danger_"] button{background:var(--c-surface);border:1px solid var(--c-danger-line);color:var(--c-danger)}
[class*="st-key-danger_"] button:hover{background:var(--c-danger-soft);border-color:var(--c-danger);color:var(--c-danger)}
[class*="st-key-icon_"] button{width:var(--h-control);padding:0}

/* ── FORMULÁRIOS ───────────────────────────────────────────── */
[data-testid="stWidgetLabel"] p{font-size:var(--t-sm);font-weight:600;color:var(--c-ink-2);letter-spacing:0}
[data-testid="stWidgetLabel"]{margin-bottom:2px}
[data-testid="stTextInput"] [data-baseweb="input"],[data-testid="stNumberInput"] [data-baseweb="input"],[data-testid="stNumberInputContainer"]{min-height:var(--h-control)}
[data-testid="stSelectbox"] [data-baseweb="select"]>div{min-height:var(--h-control)}
[data-testid="stTextInput"] input,[data-testid="stNumberInput"] input,[data-testid="stTextArea"] textarea,[data-baseweb="select"]{font-size:var(--t-base)}
[data-testid="stNumberInput"] input{font-family:var(--f-mono);font-variant-numeric:tabular-nums}
[data-testid="stTextInputRootElement"]:focus-within,[data-testid="stNumberInputContainer"]:focus-within,[data-testid="stTextArea"] [data-baseweb="textarea"]:focus-within,[data-baseweb="select"]>div:focus-within{box-shadow:var(--sh-focus)}
[data-testid="stForm"]{border-radius:var(--r-lg)}
[data-baseweb="tab-list"]{gap:var(--s-5)}
[data-baseweb="tab"]{height:var(--h-control);padding:0;font-weight:600}
[data-baseweb="tab"] p{font-size:var(--t-base);font-weight:600}
[data-testid="stAlert"]{border-radius:var(--r-md)}
[data-testid="stAlert"] p{font-size:var(--t-base)}
[data-testid="stExpander"] details{border-radius:var(--r-md);border-color:var(--c-line);background:var(--c-surface)}
[data-testid="stDataFrame"]{border-radius:var(--r-md)}
[data-testid="stVerticalBlockBorderWrapper"]{border-radius:var(--r-lg)}

/* painéis: superfícies brancas para gráficos e grupos */
[class*="st-key-panel_"]{background:var(--c-surface);border-color:var(--c-line);border-radius:var(--r-lg);padding:var(--s-4)}
.mcda-panel-title{font-size:var(--t-sm);font-weight:600;color:var(--c-ink)}
.mcda-panel-hint{font-size:var(--t-sm);color:var(--c-muted);margin-top:2px}

/* ── TIPOGRAFIA DE PÁGINA ──────────────────────────────────── */
.mcda-ico{font-family:'Material Symbols Rounded';font-weight:400;font-style:normal;font-size:var(--i-sm);line-height:1;letter-spacing:normal;text-transform:none;display:inline-block;white-space:nowrap;direction:ltr;-webkit-font-feature-settings:'liga';font-feature-settings:'liga';-webkit-font-smoothing:antialiased;vertical-align:-3px;color:var(--c-muted)}
.mcda-eyebrow{font-size:var(--t-xs);letter-spacing:.14em;text-transform:uppercase;font-weight:600;color:var(--c-muted)}
.mcda-eyebrow .num{font-family:var(--f-mono);color:var(--c-primary);letter-spacing:.04em}
.mcda-title{font-family:var(--f-serif);font-size:var(--t-2xl);line-height:1.15;letter-spacing:-.02em;font-weight:600;color:var(--c-ink);margin:var(--s-2) 0 0;text-wrap:balance}
.mcda-lead{font-size:var(--t-md);line-height:1.6;color:var(--c-ink-2);max-width:var(--w-prose);margin-top:var(--s-2)}
.mcda-pagehead{padding-bottom:var(--s-2)}
.mcda-section{display:flex;align-items:baseline;flex-wrap:wrap;gap:0 var(--s-3);min-height:28px;margin:var(--s-4) 0 0;padding-bottom:var(--s-2);border-bottom:1px solid var(--c-line)}
.mcda-section-label{font-size:var(--t-xs);text-transform:uppercase;letter-spacing:.12em;font-weight:600;color:var(--c-ink)}
.mcda-section-step{font-family:var(--f-mono);font-size:var(--t-xs);color:var(--c-primary);font-weight:600}
.mcda-section-hint{font-size:var(--t-sm);color:var(--c-muted)}

/* barra de contexto do workspace */
.mcda-context{display:flex;align-items:center;flex-wrap:wrap;gap:var(--s-2) var(--s-3);padding-bottom:var(--s-4);margin-bottom:var(--s-2);border-bottom:1px solid var(--c-line)}
.mcda-context-name{font-size:var(--t-base);font-weight:600;color:var(--c-ink);margin-right:var(--s-2)}

/* ── BADGES ────────────────────────────────────────────────── */
.mcda-badges{display:inline-flex;flex-wrap:wrap;gap:var(--s-2)}
.mcda-badge{display:inline-flex;align-items:center;height:22px;padding:0 var(--s-2);border:1px solid var(--c-line-strong);border-radius:var(--r-sm);font-size:var(--t-xs);font-weight:600;letter-spacing:.02em;background:var(--c-surface);color:var(--c-ink-2);white-space:nowrap}
.mcda-badge.mono{font-family:var(--f-mono);font-weight:500;letter-spacing:0}
.mcda-badge.promethee{background:var(--c-promethee-soft);border-color:var(--c-primary-line);color:var(--c-primary-strong)}
.mcda-badge.electre{background:var(--c-electre-soft);border-color:#C3CEDF;color:#2F4160}
.mcda-badge.success{background:var(--c-success-soft);border-color:var(--c-success-line);color:var(--c-success)}
.mcda-badge.warning{background:var(--c-warning-soft);border-color:var(--c-warning-line);color:var(--c-warning)}
.mcda-badge.danger{background:var(--c-danger-soft);border-color:var(--c-danger-line);color:var(--c-danger)}

/* ── FAIXA DE MÉTRICAS ─────────────────────────────────────── */
.mcda-metrics{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));background:var(--c-surface);border:1px solid var(--c-line);border-radius:var(--r-lg);overflow:hidden}
.mcda-metric{padding:var(--s-3) var(--s-4);box-shadow:-1px 0 0 var(--c-line),0 -1px 0 var(--c-line);min-width:0}
.mcda-metric-label{font-size:var(--t-2xs);text-transform:uppercase;letter-spacing:.12em;font-weight:600;color:var(--c-muted)}
.mcda-metric-label.plain{text-transform:none;letter-spacing:.02em;font-size:var(--t-xs)}
.mcda-metric-value{font-size:var(--t-xl);line-height:1.25;letter-spacing:-.02em;font-weight:600;color:var(--c-ink);margin-top:var(--s-1);font-variant-numeric:tabular-nums;overflow-wrap:anywhere}
.mcda-metric-value.mono{font-family:var(--f-mono);font-size:var(--t-lg);letter-spacing:-.01em;line-height:1.5}
.mcda-metric-note{font-size:var(--t-sm);color:var(--c-muted);margin-top:2px;line-height:1.4}
.mcda-metric.success .mcda-metric-note{color:var(--c-success);font-weight:600}
.mcda-metric.neutral .mcda-metric-note{color:var(--c-ink-2);font-weight:600}

/* ── TABELAS ───────────────────────────────────────────────── */
.mcda-table-wrap{background:var(--c-surface);border:1px solid var(--c-line);border-radius:var(--r-lg);overflow-x:auto}
.mcda-table{width:100%;border-collapse:collapse;font-size:var(--t-sm);margin:0}
.mcda-table th,.mcda-table td{padding:var(--s-2) var(--s-3);border:0;border-bottom:1px solid var(--c-line);text-align:left;white-space:nowrap;line-height:1.4}
.mcda-table thead th{font-size:var(--t-xs);letter-spacing:.02em;font-weight:600;color:var(--c-muted);background:var(--c-canvas);border-bottom:1px solid var(--c-line-strong)}
.mcda-table tbody th{font-weight:600;color:var(--c-ink)}
.mcda-table tbody tr:last-child th,.mcda-table tbody tr:last-child td{border-bottom:0}
.mcda-table .r{text-align:right}.mcda-table .c{text-align:center}
.mcda-table .num{font-family:var(--f-mono);font-variant-numeric:tabular-nums;font-size:var(--t-sm)}
.mcda-table .dim{color:var(--c-faint)}
.mcda-table .strong{font-weight:600;color:var(--c-ink)}
.mcda-table .hit{color:var(--c-primary-strong);font-weight:600}
.mcda-table tr.total th,.mcda-table tr.total td{background:var(--c-canvas);border-top:1px solid var(--c-line-strong);font-weight:600}
.mcda-table tr.lead th,.mcda-table tr.lead td,.mcda-table .col-lead{background:var(--c-primary-soft)}
.mcda-table.matrix thead th:first-child{font-family:var(--f-mono);letter-spacing:0}
.mcda-table.matrix td{text-align:right}
.mcda-table-note{font-size:var(--t-sm);color:var(--c-muted);margin-top:var(--s-2);line-height:1.5}

/* ── CALLOUT · FÓRMULA · PASSOS ────────────────────────────── */
.mcda-callout{background:var(--c-surface);border:1px solid var(--c-line);border-left:3px solid var(--c-primary);border-radius:var(--r-md);padding:var(--s-3) var(--s-4);color:var(--c-ink-2);font-size:var(--t-base);line-height:1.6}
.mcda-callout-title{font-size:var(--t-2xs);text-transform:uppercase;letter-spacing:.12em;font-weight:600;color:var(--c-primary);margin-bottom:var(--s-1)}
.mcda-callout ul{margin:var(--s-1) 0 0;padding-left:var(--s-4)}
.mcda-callout strong{color:var(--c-ink);font-weight:600}
.mcda-callout.warning{border-left-color:var(--c-warning)}.mcda-callout.warning .mcda-callout-title{color:var(--c-warning)}
.mcda-callout.muted{border-left-color:var(--c-line-strong)}.mcda-callout.muted .mcda-callout-title{color:var(--c-muted)}
.mcda-formula{font-family:var(--f-mono);background:var(--c-surface);color:var(--c-ink);border:1px solid var(--c-line);border-radius:var(--r-md);padding:var(--s-3) var(--s-4);font-size:var(--t-sm);line-height:2;overflow-x:auto}
.mcda-formula .res{color:var(--c-primary-strong);font-weight:600}
.mcda-steps{display:flex;flex-wrap:wrap;align-items:center;gap:var(--s-2) 0;font-size:var(--t-sm);color:var(--c-ink-2)}
.mcda-step{display:inline-flex;align-items:center;gap:var(--s-2);white-space:nowrap}
.mcda-step-n{font-family:var(--f-mono);font-size:var(--t-xs);color:var(--c-primary);font-weight:600}
.mcda-step-sep{width:var(--s-5);height:1px;background:var(--c-line-strong);margin:0 var(--s-3)}

/* ── RANKING ───────────────────────────────────────────────── */
.mcda-rank{display:grid;grid-template-columns:28px 1fr auto;align-items:center;gap:var(--s-3);padding:var(--s-2) 0;border-bottom:1px solid var(--c-line);font-size:var(--t-base)}
.mcda-rank:last-child{border-bottom:0}
.mcda-rank-n{font-family:var(--f-mono);font-size:var(--t-xs);color:var(--c-faint)}
.mcda-rank-name{font-weight:500;color:var(--c-ink);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.mcda-rank-val{font-family:var(--f-mono);font-size:var(--t-sm);color:var(--c-ink-2);font-variant-numeric:tabular-nums}
.mcda-rank.first .mcda-rank-n,.mcda-rank.first .mcda-rank-val{color:var(--c-primary);font-weight:600}
.mcda-rank.first .mcda-rank-name{font-weight:600}
.mcda-list{margin:0;padding:0!important;list-style:none;font-size:var(--t-base);color:var(--c-ink-2)}
.mcda-list li{padding:var(--s-2) 0;border-bottom:1px solid var(--c-line);line-height:1.5}
.mcda-list li:last-child{border-bottom:0}
.mcda-list .num{font-family:var(--f-mono);font-size:var(--t-sm);color:var(--c-primary-strong);font-weight:600}
.mcda-empty{font-size:var(--t-base);color:var(--c-muted);padding:var(--s-2) 0;line-height:1.6}
.mcda-prose{font-size:var(--t-base);line-height:1.65;color:var(--c-ink-2);max-width:var(--w-prose)}
.mcda-prose strong{color:var(--c-ink);font-weight:600}
.mcda-param-head{font-size:var(--t-xs);letter-spacing:.02em;font-weight:600;color:var(--c-muted)}
.mcda-param-cell{font-size:var(--t-base);color:var(--c-ink);font-weight:500}
.mcda-param-cell.dim{color:var(--c-faint);font-family:var(--f-mono)}

/* ── CARDS DE EXERCÍCIO ────────────────────────────────────── */
[class*="st-key-excard_"]{background:var(--c-surface);border-color:var(--c-line);border-radius:var(--r-lg);padding:0;gap:0;overflow:hidden;transition:border-color .12s ease}
[class*="st-key-excard_"]:hover{border-color:var(--c-line-strong)}
[class*="st-key-excard_"] .stButton{padding:0 var(--s-4) var(--s-4)}
.mcda-ex-head{display:flex;align-items:center;justify-content:space-between;gap:var(--s-2);padding:var(--s-2) var(--s-4);border-bottom:1px solid var(--c-line);font-size:var(--t-xs);font-weight:600;letter-spacing:.04em}
.mcda-ex-head.promethee{background:var(--c-promethee-soft);color:var(--c-primary-strong)}
.mcda-ex-head.electre{background:var(--c-electre-soft);color:#2F4160}
.mcda-ex-role{font-weight:500;letter-spacing:0;opacity:.85}
.mcda-ex-body{padding:var(--s-3) var(--s-4) var(--s-3)}
.mcda-ex-title{font-size:var(--t-md);font-weight:600;letter-spacing:-.01em;color:var(--c-ink);line-height:1.35;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.mcda-ex-desc{font-size:var(--t-sm);color:var(--c-muted);line-height:1.5;margin-top:2px;height:36px;overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical}
.mcda-ex-stats{display:grid;grid-template-columns:1fr 1fr;margin-top:var(--s-3);border-top:1px solid var(--c-line);border-bottom:1px solid var(--c-line)}
.mcda-ex-stat{padding:var(--s-2) 0;display:flex;align-items:baseline;gap:var(--s-2)}
.mcda-ex-stat b{font-family:var(--f-mono);font-size:var(--t-lg);font-weight:600;color:var(--c-ink);font-variant-numeric:tabular-nums}
.mcda-ex-stat span{font-size:var(--t-xs);color:var(--c-muted)}
.mcda-ex-meta{display:flex;justify-content:space-between;gap:var(--s-2);margin-top:var(--s-2);font-size:var(--t-xs);color:var(--c-muted)}
.mcda-ex-meta .mono{font-family:var(--f-mono);color:var(--c-ink-2)}

/* ── LOGIN ─────────────────────────────────────────────────── */
.st-key-login{max-width:var(--w-login);margin:0 auto;padding-top:6vh}
.mcda-hero h1{font-family:var(--f-serif);font-size:var(--t-3xl);line-height:1.08;letter-spacing:-.025em;font-weight:600;color:var(--c-ink);max-width:540px;margin:var(--s-3) 0 0;padding:0;text-wrap:balance}
.mcda-hero .mcda-lead{max-width:500px;margin-top:var(--s-4)}
.mcda-hero .mcda-steps{margin-top:var(--s-6);padding-top:var(--s-4);border-top:1px solid var(--c-line);max-width:540px;font-size:var(--t-xs)}
.mcda-hero .mcda-steps{display:grid;grid-template-columns:repeat(3,max-content);gap:var(--s-2) var(--s-5)}
.mcda-hero .mcda-step-sep{display:none}
.st-key-login_card{background:var(--c-surface);border-color:var(--c-line);border-radius:var(--r-lg);padding:var(--s-5);box-shadow:var(--sh-md)}
.st-key-login_card [data-testid="stForm"]{border:0;padding:0}
.mcda-login-note{font-size:var(--t-xs);color:var(--c-muted);line-height:1.6;margin-top:var(--s-2)}

/* ── FOOTER ────────────────────────────────────────────────── */
.mcda-footer{border-top:1px solid var(--c-line);margin-top:var(--s-7);padding-top:var(--s-4);color:var(--c-muted);font-size:var(--t-xs);line-height:1.8;display:flex;flex-wrap:wrap;justify-content:space-between;gap:var(--s-2) var(--s-5)}
.mcda-footer strong{color:var(--c-ink-2);font-weight:600}
.mcda-footer-note{flex-basis:100%;color:var(--c-muted)}

/* ── RESPONSIVO ────────────────────────────────────────────── */
@media(max-width:1100px){
  [data-testid="stMainBlockContainer"]{padding-left:var(--s-5);padding-right:var(--s-5)}
  .stMain [data-testid="stHorizontalBlock"]{flex-wrap:wrap}
  .stMain [data-testid="stColumn"]{min-width:min(100%,280px)}
  .mcda-hero h1{font-size:34px}
}
@media(max-width:640px){
  [data-testid="stMainBlockContainer"]{padding:56px var(--s-4) var(--s-7)}
  .mcda-title{font-size:24px}
  .st-key-login{padding-top:0}
}
@media(prefers-reduced-motion:reduce){*{transition:none!important}}
'''


def apply_theme():
    st.html(f'<style>{_root()}{CSS}</style>')
