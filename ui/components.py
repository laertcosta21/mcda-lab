import html
import streamlit as st

def esc(x): return html.escape(str(x))
def page_header(kicker,title,lead=''):
 st.markdown(f'<div class="mcda-eyebrow">{esc(kicker)}</div><div class="mcda-title">{esc(title)}</div>'+ (f'<div class="mcda-lead">{esc(lead)}</div>' if lead else ''),unsafe_allow_html=True)
def badge(text,tone=''): return f'<span class="mcda-badge {tone}">{esc(text)}</span>'
def metric_card(label,value,note=''):
 st.markdown(f'<div class="mcda-card-flat"><div class="mcda-card-label">{esc(label)}</div><div class="mcda-card-value">{esc(value)}</div><div class="mcda-card-note">{esc(note)}</div></div>',unsafe_allow_html=True)
def section(label): st.markdown(f'<div class="mcda-section">{esc(label)}</div>',unsafe_allow_html=True)
def callout(text): st.markdown(f'<div class="mcda-callout">{esc(text)}</div>',unsafe_allow_html=True)
def formula(lines): st.markdown('<div class="mcda-formula">'+'<br>'.join(lines)+'</div>',unsafe_allow_html=True)
def footer():
 st.markdown('<div class="mcda-footer"><strong>MCDA Lab</strong> · Laboratório didático de Apoio Multicritério à Decisão<br>UFMS · 2026 · Laert Costa · Felipe Pires &nbsp;&nbsp;·&nbsp;&nbsp; PROMETHEE II · ELECTRE I &nbsp;&nbsp;·&nbsp;&nbsp; Uso acadêmico<br>Os resultados apoiam a análise e não substituem o julgamento do decisor.</div>',unsafe_allow_html=True)
