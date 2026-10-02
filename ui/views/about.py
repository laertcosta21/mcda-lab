import streamlit as st

from core.rules import DISCLAIMER
from ui.components import callout, cell, data_table, esc, page_header, section

_NOTATION = [
    ('a, b', 'alternativas comparadas'),
    ('j', 'critério'),
    ('wⱼ', 'peso normalizado do critério j'),
    ('Fⱼ(a,b)', 'preferência de a sobre b no critério j, entre 0 e 1'),
    ('S(a,b)', 'preferência agregada de a sobre b'),
    ('φ⁺ · φ⁻ · φ', 'fluxos positivo, negativo e líquido'),
    ('q · p · s', 'limiares de indiferença, de preferência e parâmetro gaussiano'),
    ('C(a,b) · D(a,b)', 'índices de concordância e de discordância'),
    ('c′ · d′', 'limiares de concordância e de discordância'),
    ('aSb', 'a sobreclassifica b'),
]


def render(e):
    page_header('06 / Sobre', 'Sobre o laboratório', 'Referência rápida para compreender o propósito, os métodos e os limites de uso do MCDA Lab.')
    section('Uso acadêmico')
    callout(esc(DISCLAIMER), 'Aviso')

    section('Métodos')
    c1, c2 = st.columns(2, gap='medium')
    with c1:
        st.html('<div class="mcda-prose"><strong>PROMETHEE II</strong><br>Compara alternativas par a par por critérios ponderados, calcula fluxos '
                'positivo e negativo e utiliza o fluxo líquido para produzir uma ordenação completa, admitindo empates.</div>')
    with c2:
        st.html('<div class="mcda-prose"><strong>ELECTRE I</strong><br>Constrói uma relação de sobreclassificação a partir de concordância, '
                'discordância e limiares. O resultado é uma relação, um grafo e um kernel, não um ranking artificial.</div>')

    section('Notação essencial')
    data_table([('Símbolo', ''), ('Significado', '')], [[cell(s, 'num strong'), d] for s, d in _NOTATION])

    section('Créditos')
    st.html('<div class="mcda-prose">MCDA Lab · Laboratório didático de Apoio Multicritério à Decisão · UFMS · 2026<br>'
            'Laert Costa · Felipe Pires</div>')
