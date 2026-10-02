"""Design tokens e CSS global do MCDA Lab.

Toda cor, medida e fonte usada pela interface (HTML, CSS e gráficos) sai daqui.
As cores de base também estão em .streamlit/config.toml, que é de onde o
Streamlit tira o tema dos widgets nativos; mantenha os dois em sincronia.
"""
import streamlit as st

COLORS = {
    'canvas': '#FFFFFF',
    'surface': '#FFFFFF',
    'sunken': '#F8FAFC',
    'sunken-2': '#F1F5F9',
    'ink': '#262730',
    'ink-2': '#31333F',
    'muted': '#5F6672',
    'faint': '#9AA1AD',
    'line': '#E4E7EC',
    'line-strong': '#D5D9E0',
    'primary': '#0068C9',
    'primary-strong': '#0054A3',
    'primary-soft': '#E8F2FC',
    'primary-line': '#B3D4F5',
    'secondary': '#83C9FF',
    # sidebar escura
    'side': '#1E293B',
    'side-2': '#334155',
    'side-text': '#F1F5F9',
    'side-muted': '#94A3B8',
    'side-hover': 'rgba(197,206,221,.12)',
    'side-active': 'rgba(197,206,221,.25)',
    # métodos: dois matizes da mesma paleta de gráficos
    'promethee': '#0068C9',
    'promethee-soft': '#E8F2FC',
    'promethee-ink': '#0054A3',
    'electre': '#29B09D',
    'electre-soft': '#E3F6F2',
    'electre-ink': '#0B6B5D',
    'success': '#158237',
    'success-soft': '#E6F6EA',
    'warning': '#8A5A00',
    'warning-soft': '#FFF4DC',
    'danger': '#BD2F2F',
    'danger-soft': '#FFECEC',
    'danger-line': '#F3BCBC',
}

FONTS = {
    'sans': "'Work Sans', 'Source Sans', system-ui, -apple-system, 'Segoe UI', sans-serif",
    # só para fórmulas e códigos de exercício; é a fonte de código que o Streamlit já carrega
    'mono': "'Source Code Pro', ui-monospace, 'SFMono-Regular', Consolas, monospace",
}

# tamanhos em px
TYPE = {'xs': 12, 'sm': 13, 'base': 14, 'md': 16, 'lg': 18, 'xl': 22, 'metric': 30, '2xl': 32, '3xl': 42}
SPACE = {1: 4, 2: 8, 3: 12, 4: 16, 5: 24, 6: 32, 7: 48, 8: 64}
# o raio cresce com o tamanho do elemento: controle < card < painel
RADIUS = {'sm': 6, 'md': 8, 'lg': 12, 'xl': 16, 'pill': 999}
SHADOWS = {
    'sm': '0 1px 2px rgba(15,23,42,.06)',
    'md': '0 1px 2px rgba(15,23,42,.05), 0 10px 28px rgba(15,23,42,.08)',
    'focus': '0 0 0 3px rgba(0,104,201,.22)',
}
WIDTHS = {'content': 1240, 'login': 1080, 'sidebar': 256, 'prose': 720}
HEIGHTS = {'control': 40, 'nav': 36, 'chart': 360, 'chart-lg': 420}
ICONS = {'sm': 16, 'md': 18, 'lg': 20, 'xl': 28}

# séries categóricas dos gráficos (mesma família da referência ECharts/Streamlit)
CHART_SERIES = ['#0068C9', '#FF8700', '#29B09D', '#FF2B2B', '#83C9FF', '#7DEFA1', '#FFABAB', '#6D3FC0']
CHART_POSITIVE = '#83C9FF'
CHART_NEGATIVE = '#FFABAB'
CHART_MARK = '#FF8700'


def rgb(hex_color):
    """'#0068C9' → '0,104,201', para compor rgba() em tintas proporcionais."""
    h = hex_color.lstrip('#')
    return ','.join(str(int(h[i:i + 2], 16)) for i in (0, 2, 4))


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
/* ── APP SHELL ─────────────────────────────────────────────── */
.stApp{background:var(--c-canvas);color:var(--c-ink-2)}
header[data-testid="stHeader"]{background:transparent}
[data-testid="stMainBlockContainer"]{max-width:var(--w-content);padding:56px var(--s-7) var(--s-8)}
[data-testid="InputInstructions"]{display:none}
[data-testid="stCaptionContainer"],[data-testid="stCaptionContainer"] p{color:var(--c-muted);opacity:1;font-size:var(--t-sm)}
.stMain [data-testid="stMarkdownContainer"] p{font-size:var(--t-base);line-height:1.6}

/* ── SIDEBAR ───────────────────────────────────────────────── */
[data-testid="stSidebar"]{border-right:0}
[data-testid="stSidebar"][aria-expanded="true"]{width:var(--w-sidebar)!important;min-width:var(--w-sidebar)!important}
[data-testid="stSidebarUserContent"]{padding:0 var(--s-3) var(--s-5)}
[data-testid="stSidebar"] hr{margin:var(--s-2) 0;border-color:var(--c-side-2)}
.mcda-brand{display:flex;align-items:center;gap:var(--s-3);padding:0 var(--s-2)}
.mcda-brand-mark{display:grid;place-items:center;width:36px;height:36px;border-radius:var(--r-md);background:var(--c-primary);flex:none}
.mcda-brand-mark .mcda-ico{font-size:var(--i-lg);color:#fff;vertical-align:0}
.mcda-brand-name{font-size:var(--t-lg);font-weight:700;letter-spacing:-.01em;color:var(--c-side-text);line-height:1.2}
.mcda-brand-sub{font-size:var(--t-xs);color:var(--c-side-muted);line-height:1.3;white-space:nowrap}
.mcda-side-block{padding:0 var(--s-2)}
.mcda-side-label{font-size:var(--t-xs);color:var(--c-side-muted);margin-bottom:2px}
.mcda-side-title{font-size:var(--t-base);font-weight:600;color:var(--c-side-text);line-height:1.35;overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical}
.mcda-side-meta{font-size:var(--t-sm);color:var(--c-side-muted);line-height:1.6;margin-top:var(--s-1)}
.mcda-side-meta .code{font-family:var(--f-mono);font-size:var(--t-xs)}

/* navegação: [ícone] [número] [label], tudo no mesmo eixo */
.st-key-nav,:is(.st-key-nav_foot,.st-key-nav_back){gap:2px}
.st-key-nav button,:is(.st-key-nav_foot,.st-key-nav_back) button{height:var(--h-nav);min-height:var(--h-nav);padding:0 var(--s-3);border:0;border-radius:var(--r-md);background:transparent;box-shadow:none;justify-content:flex-start;color:var(--c-side-text);font-weight:400}
.st-key-nav button>div,:is(.st-key-nav_foot,.st-key-nav_back) button>div{justify-content:flex-start;align-items:center;gap:var(--s-3);width:100%}
.st-key-nav button [data-testid="stIconMaterial"],:is(.st-key-nav_foot,.st-key-nav_back) button [data-testid="stIconMaterial"]{font-size:var(--i-md);width:var(--i-md);color:var(--c-side-muted);margin:0;flex:none}
.st-key-nav button [data-testid="stMarkdownContainer"],:is(.st-key-nav_foot,.st-key-nav_back) button [data-testid="stMarkdownContainer"]{flex:1;min-width:0}
.st-key-nav button p,:is(.st-key-nav_foot,.st-key-nav_back) button p{display:flex;align-items:center;gap:var(--s-3);margin:0;font-size:var(--t-base);line-height:1;text-align:left;font-weight:inherit;color:inherit}
.st-key-nav button code{flex:none;width:18px;padding:0;background:none;border:0;font-family:var(--f-sans);font-size:var(--t-xs);font-weight:500;color:var(--c-side-muted);font-variant-numeric:tabular-nums}
.st-key-nav button:hover,:is(.st-key-nav_foot,.st-key-nav_back) button:hover{background:var(--c-side-hover);color:#fff}
.st-key-nav button[kind="primary"]{background:var(--c-side-active);color:#fff;font-weight:600}
.st-key-nav button[kind="primary"] [data-testid="stIconMaterial"],.st-key-nav button[kind="primary"] code,
.st-key-nav button:hover [data-testid="stIconMaterial"],:is(.st-key-nav_foot,.st-key-nav_back) button:hover [data-testid="stIconMaterial"]{color:#fff}
.st-key-nav button:focus-visible,:is(.st-key-nav_foot,.st-key-nav_back) button:focus-visible{box-shadow:0 0 0 2px var(--c-secondary);outline:0}

/* ── BOTÕES: primary · secondary · ghost (tertiary) · danger · icon ── */
[data-testid="stBaseButton-primary"],[data-testid="stBaseButton-secondary"],[data-testid="stBaseButton-tertiary"],
[data-testid="stBaseButton-primaryFormSubmit"],[data-testid="stBaseButton-secondaryFormSubmit"],[data-testid="stPopoverButton"]{
  height:var(--h-control);min-height:var(--h-control);padding:0 var(--s-4);border-radius:var(--r-md);
  font-size:var(--t-base);font-weight:600;transition:background-color .12s ease,border-color .12s ease,color .12s ease}
[data-testid^="stBaseButton-"] p,[data-testid="stPopoverButton"] p{font-size:var(--t-base);font-weight:inherit;white-space:nowrap}
:is(.stMain,[data-testid="stDialog"],[data-testid="stPopoverBody"]) [data-testid="stBaseButton-primary"],[data-testid="stBaseButton-primaryFormSubmit"]{background:var(--c-primary);border:1px solid var(--c-primary);color:#fff;box-shadow:var(--sh-sm)}
:is(.stMain,[data-testid="stDialog"],[data-testid="stPopoverBody"]) [data-testid="stBaseButton-primary"]:hover,[data-testid="stBaseButton-primaryFormSubmit"]:hover{background:var(--c-primary-strong);border-color:var(--c-primary-strong);color:#fff}
:is(.stMain,[data-testid="stDialog"],[data-testid="stPopoverBody"]) [data-testid="stBaseButton-secondary"],[data-testid="stBaseButton-secondaryFormSubmit"],.stMain [data-testid="stPopoverButton"]{background:var(--c-surface);border:1px solid var(--c-line-strong);color:var(--c-ink);box-shadow:var(--sh-sm)}
:is(.stMain,[data-testid="stDialog"],[data-testid="stPopoverBody"]) [data-testid="stBaseButton-secondary"]:hover,[data-testid="stBaseButton-secondaryFormSubmit"]:hover,.stMain [data-testid="stPopoverButton"]:hover{background:var(--c-sunken);border-color:var(--c-primary);color:var(--c-primary-strong)}
:is(.stMain,[data-testid="stDialog"],[data-testid="stPopoverBody"]) [data-testid="stBaseButton-tertiary"]{color:var(--c-primary);padding:0 var(--s-3)}
:is(.stMain,[data-testid="stDialog"],[data-testid="stPopoverBody"]) [data-testid="stBaseButton-tertiary"]:hover{background:var(--c-primary-soft);color:var(--c-primary-strong)}
:is(.stMain,[data-testid="stDialog"],[data-testid="stPopoverBody"]) [data-testid^="stBaseButton-"]:focus-visible,.stMain [data-testid="stPopoverButton"]:focus-visible{box-shadow:var(--sh-focus);outline:0}
[data-testid^="stBaseButton-"]:disabled{opacity:.5;cursor:not-allowed}
:is(.stMain,[data-testid="stDialog"],[data-testid="stPopoverBody"]) [class*="st-key-danger_"] button[data-testid^="stBaseButton-"]{background:var(--c-surface);border:1px solid var(--c-danger-line);color:var(--c-danger);box-shadow:none}
:is(.stMain,[data-testid="stDialog"],[data-testid="stPopoverBody"]) [class*="st-key-danger_"] button[data-testid^="stBaseButton-"]:hover{background:var(--c-danger-soft);border-color:var(--c-danger);color:var(--c-danger)}
[class*="st-key-icon_"] button,[class*="st-key-exact_"] [data-testid="stPopoverButton"]{width:var(--h-control);min-width:var(--h-control);padding:0}
[class*="st-key-exact_"] [data-testid="stPopoverButton"]>div{justify-content:center}
[class*="st-key-exact_"] [data-testid="stPopoverButton"]>div>div:last-child:not(:first-child){display:none}
/* linha de ações da página: salvar à esquerda, ação destrutiva à direita */
.st-key-page_actions{flex-wrap:wrap;gap:var(--s-3)}

/* ── FORMULÁRIOS ───────────────────────────────────────────── */
[data-testid="stWidgetLabel"] p{font-size:var(--t-sm);font-weight:500;color:var(--c-ink-2)}
[data-testid="stWidgetLabel"]{margin-bottom:2px}
[data-testid="stTextInput"] [data-baseweb="input"],[data-testid="stNumberInput"] [data-baseweb="input"],[data-testid="stNumberInputContainer"]{min-height:var(--h-control)}
[data-testid="stSelectbox"] [data-baseweb="select"]>div{min-height:var(--h-control)}
[data-testid="stTextInput"] input,[data-testid="stNumberInput"] input,[data-testid="stTextArea"] textarea,[data-baseweb="select"]{font-size:var(--t-base)}
[data-testid="stNumberInput"] input{font-variant-numeric:tabular-nums}
[data-testid="stTextInputRootElement"]:focus-within,[data-testid="stNumberInputContainer"]:focus-within,[data-testid="stTextArea"] [data-baseweb="textarea"]:focus-within,[data-baseweb="select"]>div:focus-within{box-shadow:var(--sh-focus)}
[data-baseweb="tab-list"]{gap:var(--s-5)}
[data-baseweb="tab"]{height:var(--h-control);padding:0}
[data-baseweb="tab"] p{font-size:var(--t-base);font-weight:600}
[data-testid="stAlert"]{border-radius:var(--r-md)}
[data-testid="stAlert"] p{font-size:var(--t-base)}
[data-testid="stDataFrame"]{border-radius:var(--r-md)}
[data-testid="stDialog"] [role="dialog"]{border-radius:var(--r-xl)}

/* ── CARDS ─────────────────────────────────────────────────── */
/* um só padrão: superfície branca, borda fina, raio 12, sem sombra em repouso */
[class*="st-key-panel_"]{background:var(--c-surface);border-color:var(--c-line-strong);border-radius:var(--r-lg);padding:var(--s-4) var(--s-5)}
[class*="st-key-panel_"] .mcda-table-wrap{border:0;border-radius:0}
[class*="st-key-panel_"] .mcda-table thead th{border-bottom:0}
[class*="st-key-panel_"] .mcda-table thead th:first-child{border-radius:var(--r-md) 0 0 var(--r-md)}
[class*="st-key-panel_"] .mcda-table thead th:last-child{border-radius:0 var(--r-md) var(--r-md) 0}
.mcda-panel-title{font-size:var(--t-md);font-weight:600;color:var(--c-ink);line-height:1.3}
.mcda-panel-hint{font-size:var(--t-sm);color:var(--c-muted);margin-top:2px;line-height:1.45}

/* ── HIERARQUIA DE TEXTO ───────────────────────────────────── */
.mcda-ico{font-family:'Material Symbols Rounded';font-weight:400;font-style:normal;font-size:var(--i-sm);line-height:1;letter-spacing:normal;text-transform:none;display:inline-block;white-space:nowrap;direction:ltr;-webkit-font-feature-settings:'liga';font-feature-settings:'liga';-webkit-font-smoothing:antialiased;vertical-align:-3px}
.mcda-pagehead{padding-bottom:var(--s-2)}
.mcda-title{display:flex;align-items:center;gap:var(--s-3);font-size:var(--t-2xl);line-height:1.15;letter-spacing:-.02em;font-weight:700;color:var(--c-ink);margin:0;padding:0;text-wrap:balance}
.mcda-title .mcda-ico{font-size:var(--i-xl);color:var(--c-ink);vertical-align:0;flex:none}
.mcda-lead{font-size:var(--t-md);line-height:1.55;color:var(--c-ink-2);max-width:var(--w-prose);margin-top:var(--s-3)}
.mcda-section{margin:var(--s-5) 0 0}
.mcda-section-head{display:flex;align-items:center;gap:var(--s-2)}
.mcda-section-label{font-size:var(--t-lg);font-weight:600;letter-spacing:-.01em;color:var(--c-ink);line-height:1.3;margin:0;padding:0}
.mcda-section-step{display:grid;place-items:center;width:22px;height:22px;border-radius:var(--r-pill);background:var(--c-primary);color:#fff;font-size:var(--t-xs);font-weight:600;flex:none}
.mcda-section-hint{font-size:var(--t-sm);color:var(--c-muted);margin-top:2px;line-height:1.45}

/* barra de contexto do workspace */
.mcda-context{display:flex;align-items:center;flex-wrap:wrap;gap:var(--s-2) var(--s-3);padding-bottom:var(--s-4);margin-bottom:var(--s-3);border-bottom:1px solid var(--c-line)}
.mcda-context-name{font-size:var(--t-base);font-weight:600;color:var(--c-ink);margin-right:var(--s-1)}

/* ── BADGES ────────────────────────────────────────────────── */
.mcda-badges{display:inline-flex;flex-wrap:wrap;gap:var(--s-2)}
.mcda-badge{display:inline-flex;align-items:center;gap:var(--s-1);height:24px;padding:0 10px;border-radius:var(--r-pill);font-size:var(--t-xs);font-weight:500;background:var(--c-sunken-2);color:var(--c-ink-2);white-space:nowrap}
.mcda-badge.code{font-family:var(--f-mono);letter-spacing:0}
.mcda-badge.promethee{background:var(--c-promethee-soft);color:var(--c-promethee-ink)}
.mcda-badge.electre{background:var(--c-electre-soft);color:var(--c-electre-ink)}
.mcda-badge.success{background:var(--c-success-soft);color:var(--c-success)}
.mcda-badge.warning{background:var(--c-warning-soft);color:var(--c-warning)}
.mcda-badge.danger{background:var(--c-danger-soft);color:var(--c-danger)}

/* ── CARDS DE MÉTRICA ──────────────────────────────────────── */
.mcda-metrics{margin-top:var(--s-1);display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:var(--s-4)}
.mcda-metric{background:var(--c-surface);border:1px solid var(--c-line-strong);border-radius:var(--r-lg);padding:var(--s-4) var(--s-5);min-width:0}
.mcda-metric.accent{background:var(--c-primary-soft);border-color:var(--c-primary-line)}
.mcda-metric-label{font-size:var(--t-base);color:var(--c-ink-2);line-height:1.35}
.mcda-metric-value{font-size:var(--t-metric);line-height:1.25;white-space:nowrap;letter-spacing:-.01em;font-weight:400;color:var(--c-ink);margin-top:2px;font-variant-numeric:tabular-nums;overflow-wrap:anywhere}
.mcda-metric-value.small{font-size:var(--t-xl);line-height:1.7;font-weight:500;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.mcda-metric-value.code{font-family:var(--f-mono);font-size:var(--t-xl);line-height:1.7}
.mcda-metric-note{font-size:var(--t-sm);color:var(--c-muted);margin-top:var(--s-1);line-height:1.4;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.mcda-metric.success .mcda-metric-note,.mcda-metric.neutral .mcda-metric-note{display:inline-flex;align-items:center;min-height:22px;padding:2px var(--s-2);border-radius:var(--r-pill);font-size:var(--t-xs);font-weight:500}
.mcda-metric.success .mcda-metric-note{background:var(--c-success-soft);color:var(--c-success)}
.mcda-metric.neutral .mcda-metric-note{background:var(--c-sunken-2);color:var(--c-ink-2)}

/* ── TABELAS ───────────────────────────────────────────────── */
.mcda-table-wrap{background:var(--c-surface);border:1px solid var(--c-line-strong);border-radius:var(--r-lg);overflow-x:auto}
.mcda-table{width:100%;border-collapse:collapse;font-size:var(--t-base);margin:0}
.mcda-table th,.mcda-table td{padding:10px var(--s-4);border:0;border-bottom:1px solid var(--c-line);text-align:left;white-space:nowrap;line-height:1.4;color:var(--c-ink-2);font-weight:400}
.mcda-table thead th{font-size:var(--t-sm);font-weight:600;color:var(--c-muted);background:var(--c-sunken);border-bottom:1px solid var(--c-line-strong)}
.mcda-table tbody th{font-weight:500;color:var(--c-ink)}
.mcda-table tbody tr:last-child th,.mcda-table tbody tr:last-child td{border-bottom:0}
.mcda-table.compact th,.mcda-table.compact td{padding:var(--s-2)}
.mcda-table.compact th:first-child{padding-left:var(--s-4)}
.mcda-table .r{text-align:right}.mcda-table .c{text-align:center}
.mcda-table .num{font-variant-numeric:tabular-nums}
.mcda-table .dim{color:var(--c-faint)}
.mcda-table .strong{font-weight:600;color:var(--c-ink)}
.mcda-table .hit{color:var(--c-primary-strong);font-weight:600}
.mcda-table tr.total th,.mcda-table tr.total td{background:var(--c-sunken);border-top:1px solid var(--c-line-strong);font-weight:600;color:var(--c-ink)}
.mcda-table tr.lead th,.mcda-table tr.lead td,.mcda-table .col-lead{background:var(--c-primary-soft)}
.mcda-table.matrix td{text-align:right}
.st-key-combos .mcda-table td:last-child{white-space:normal}
.mcda-table-note{font-size:var(--t-sm);color:var(--c-muted);margin-top:var(--s-2);line-height:1.5}

/* ── CALLOUT · FÓRMULA · PASSOS ────────────────────────────── */
.mcda-callout{display:grid;grid-template-columns:auto 1fr;gap:var(--s-3);background:var(--c-primary-soft);border-radius:var(--r-lg);padding:var(--s-4) var(--s-5);color:var(--c-ink-2);font-size:var(--t-base);line-height:1.6}
.mcda-callout>.mcda-ico{font-size:var(--i-lg);color:var(--c-primary);vertical-align:0;margin-top:1px}
.mcda-callout-title{font-size:var(--t-base);font-weight:600;color:var(--c-primary-strong);margin-bottom:2px}
.mcda-callout ul{margin:var(--s-1) 0 0;padding-left:var(--s-4)}
.mcda-callout strong{color:var(--c-ink);font-weight:600}
.mcda-callout.warning{background:var(--c-warning-soft)}
.mcda-callout.warning>.mcda-ico,.mcda-callout.warning .mcda-callout-title{color:var(--c-warning)}
.mcda-formula{font-family:var(--f-mono);background:var(--c-sunken);color:var(--c-ink);border:1px solid var(--c-line);border-radius:var(--r-md);padding:var(--s-3) var(--s-4);font-size:var(--t-sm);line-height:2;overflow-x:auto}
.mcda-formula .res{color:var(--c-primary-strong);font-weight:600}
.mcda-steps{display:flex;flex-wrap:wrap;align-items:center;gap:var(--s-2) 0;font-size:var(--t-sm);color:var(--c-ink-2)}
.mcda-step{display:inline-flex;align-items:center;gap:var(--s-2);white-space:nowrap}
.mcda-step-n{display:grid;place-items:center;width:20px;height:20px;border-radius:var(--r-pill);background:var(--c-sunken-2);color:var(--c-ink-2);font-size:var(--t-xs);font-weight:600;font-variant-numeric:tabular-nums}
.mcda-step-sep{width:var(--s-5);height:1px;background:var(--c-line-strong);margin:0 var(--s-3)}

/* ── RANKING · LISTAS ──────────────────────────────────────── */
.mcda-rank{display:grid;grid-template-columns:24px 1fr auto;align-items:center;gap:var(--s-3);padding:10px 0;border-bottom:1px solid var(--c-line);font-size:var(--t-base)}
.mcda-rank:last-child{border-bottom:0}
.mcda-rank-n{display:grid;place-items:center;width:24px;height:24px;border-radius:var(--r-pill);background:var(--c-sunken-2);font-size:var(--t-xs);font-weight:600;color:var(--c-ink-2);font-variant-numeric:tabular-nums}
.mcda-rank-name{color:var(--c-ink);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.mcda-rank-val{font-size:var(--t-base);color:var(--c-ink-2);font-variant-numeric:tabular-nums}
.mcda-rank.first .mcda-rank-n{background:var(--c-primary);color:#fff}
.mcda-rank.first .mcda-rank-name,.mcda-rank.first .mcda-rank-val{font-weight:600;color:var(--c-ink)}
.mcda-list{margin:0;padding:0!important;list-style:none;font-size:var(--t-base);color:var(--c-ink-2)}
.mcda-list li{padding:10px 0;border-bottom:1px solid var(--c-line);line-height:1.5}
.mcda-list li:last-child{border-bottom:0}
.mcda-list .num{color:var(--c-primary-strong);font-weight:600;font-variant-numeric:tabular-nums}
.mcda-empty{font-size:var(--t-base);color:var(--c-muted);padding:var(--s-2) 0;line-height:1.6}
.mcda-prose{font-size:var(--t-base);line-height:1.65;color:var(--c-ink-2);max-width:var(--w-prose)}
.mcda-prose strong{color:var(--c-ink);font-weight:600}
.mcda-prose h3{font-size:var(--t-md);font-weight:600;color:var(--c-ink);margin:0 0 var(--s-1);padding:0}
.mcda-person{display:flex;flex-direction:column;font-size:var(--t-base);line-height:1.4;min-width:0}
.mcda-person strong{font-weight:500;color:var(--c-ink)}
.mcda-person span{font-size:var(--t-sm);color:var(--c-muted)}
[class*="st-key-person_"]{justify-content:space-between;padding:var(--s-1) 0;border-bottom:1px solid var(--c-line)}
[class*="st-key-person_"]:last-child{border-bottom:0}
.mcda-param-head{font-size:var(--t-sm);font-weight:600;color:var(--c-muted)}
.mcda-param-cell{font-size:var(--t-base);color:var(--c-ink)}
.mcda-param-cell.dim{color:var(--c-faint)}

/* ── CARDS DE EXERCÍCIO ────────────────────────────────────── */
[class*="st-key-excard_"]{background:var(--c-surface);border-color:var(--c-line-strong);border-radius:var(--r-lg);padding:0;gap:0;overflow:hidden;transition:border-color .12s ease,box-shadow .12s ease}
[class*="st-key-excard_"]:hover{border-color:var(--c-primary-line);box-shadow:var(--sh-md)}
[class*="st-key-exact_"]{padding:0 var(--s-5) var(--s-5);gap:var(--s-2);flex-wrap:nowrap}
.mcda-ex-head{display:flex;align-items:center;justify-content:space-between;gap:var(--s-2);padding:10px var(--s-5);font-size:var(--t-sm);font-weight:600}
.mcda-ex-head.promethee{background:var(--c-promethee-soft);color:var(--c-promethee-ink)}
.mcda-ex-head.electre{background:var(--c-electre-soft);color:var(--c-electre-ink)}
.mcda-ex-role{font-weight:400}
.mcda-ex-body{padding:var(--s-4) var(--s-5)}
.mcda-ex-title{font-size:var(--t-md);font-weight:600;color:var(--c-ink);line-height:1.35;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.mcda-ex-desc{font-size:var(--t-sm);color:var(--c-muted);line-height:1.5;margin-top:2px;height:39px;overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical}
.mcda-ex-stats{display:grid;grid-template-columns:1fr 1fr;gap:var(--s-4);margin-top:var(--s-4);padding-top:var(--s-3);border-top:1px solid var(--c-line)}
.mcda-ex-stat b{display:block;font-size:var(--t-xl);font-weight:400;color:var(--c-ink);line-height:1.2;font-variant-numeric:tabular-nums}
.mcda-ex-stat span{font-size:var(--t-xs);color:var(--c-muted)}
.mcda-ex-meta{display:flex;align-items:center;justify-content:space-between;gap:var(--s-2);margin-top:var(--s-3);font-size:var(--t-xs);color:var(--c-muted)}

/* ── LOGIN ─────────────────────────────────────────────────── */
.st-key-login{padding-top:4vh}
.mcda-hero{background:var(--c-sunken);border:1px solid var(--c-line);border-radius:var(--r-xl);padding:var(--s-7)}
.mcda-hero-kicker{font-size:var(--t-base);font-weight:500;color:var(--c-primary)}
.mcda-hero h1{font-size:var(--t-3xl);line-height:1.08;letter-spacing:-.025em;font-weight:700;color:var(--c-ink);margin:var(--s-3) 0 0;padding:0;text-wrap:balance}
.mcda-hero .mcda-lead{max-width:480px;margin-top:var(--s-4)}
.mcda-hero-flow{margin-top:var(--s-6);padding-top:var(--s-5);border-top:1px solid var(--c-line-strong)}
.mcda-hero-flow-title{font-size:var(--t-sm);font-weight:600;color:var(--c-ink);margin-bottom:var(--s-3)}
.mcda-hero .mcda-steps{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:var(--s-3) var(--s-4)}
.mcda-hero .mcda-step{white-space:normal;align-items:flex-start;line-height:1.4}
.mcda-hero .mcda-step-n{background:var(--c-surface);border:1px solid var(--c-line-strong);flex:none}
.mcda-hero .mcda-step-sep{display:none}
.st-key-login_card{background:var(--c-surface);border-color:var(--c-line-strong);border-radius:var(--r-xl);padding:var(--s-6);box-shadow:var(--sh-md)}
.st-key-login_card [data-testid="stForm"]{border:0;padding:0}
.mcda-login-brand{display:flex;align-items:center;gap:var(--s-3)}
.mcda-login-brand .mcda-brand-name{color:var(--c-ink);font-size:var(--t-xl)}
.mcda-login-brand .mcda-brand-sub{color:var(--c-muted);font-size:var(--t-sm)}
.mcda-login-note{font-size:var(--t-xs);color:var(--c-muted);line-height:1.6;margin-top:var(--s-2)}

/* ── FOOTER ────────────────────────────────────────────────── */
[data-testid="stMainBlockContainer"]{min-height:100vh;display:flex;flex-direction:column;flex:0 0 auto}
[data-testid="stMainBlockContainer"]>[data-testid="stVerticalBlock"]{flex:1 1 auto}
/* o Streamlit embrulha o container; é o embrulho que precisa ser empurrado para o fim */
[data-testid="stLayoutWrapper"]:has(>.st-key-footer){margin-top:auto}
.st-key-footer{padding-top:var(--s-7)}
.mcda-footer{border-top:1px solid var(--c-line-strong);padding-top:var(--s-5);font-size:var(--t-sm);color:var(--c-muted);line-height:1.5}
.mcda-footer-grid{display:grid;grid-template-columns:minmax(0,2.4fr) repeat(3,minmax(0,1fr));gap:var(--s-5) var(--s-6);align-items:start}
.mcda-footer-brand{display:flex;align-items:center;gap:var(--s-2);font-size:var(--t-md);font-weight:700;color:var(--c-ink);letter-spacing:-.01em}
.mcda-footer-brand .mcda-brand-mark{width:28px;height:28px;border-radius:var(--r-sm)}
.mcda-footer-brand .mcda-brand-mark .mcda-ico{font-size:var(--i-sm)}
.mcda-footer-desc{margin-top:var(--s-2)}
.mcda-footer-head{font-size:var(--t-sm);font-weight:600;color:var(--c-ink);line-height:28px}
.mcda-footer ul{list-style:none;margin:var(--s-1) 0 0;padding:0!important}
.mcda-footer li{margin:0;padding:0;color:var(--c-ink-2);line-height:1.7;white-space:nowrap}
.mcda-footer-note{margin-top:var(--s-5);padding-top:var(--s-4);border-top:1px solid var(--c-line);font-size:var(--t-xs);line-height:1.6;text-wrap:pretty}

/* ── RESPONSIVO ────────────────────────────────────────────── */
@media(max-width:900px){
  .mcda-footer-grid{grid-template-columns:repeat(3,minmax(0,1fr))}
  .mcda-footer-grid>div:first-child{grid-column:1/-1}
}
@media(max-width:1100px){
  [data-testid="stMainBlockContainer"]{padding-left:var(--s-5);padding-right:var(--s-5)}
  .stMain [data-testid="stHorizontalBlock"]{flex-wrap:wrap}
  .stMain [data-testid="stColumn"]{min-width:min(100%,280px)}
  .mcda-hero{padding:var(--s-6)}
  .mcda-hero h1{font-size:var(--t-2xl)}
}
@media(max-width:640px){
  [data-testid="stMainBlockContainer"]{padding:56px var(--s-4) var(--s-7)}
  .mcda-title{font-size:26px}
  .st-key-login{padding-top:0}
  .mcda-hero{padding:var(--s-5)}
  .mcda-hero .mcda-steps{grid-template-columns:repeat(2,minmax(0,1fr))}
  .mcda-footer-grid{grid-template-columns:1fr 1fr}
}
@media(prefers-reduced-motion:reduce){*{transition:none!important}}
'''


def apply_theme():
    st.html(f'<style>{_root()}{CSS}</style>')
