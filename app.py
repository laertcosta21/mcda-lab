import json
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
from engine import storage
from engine.promethee import calculate as pcalc, sensitivity as psens
from engine.electre import calculate as ecalc, sensitivity as esens
from ui.theme import apply_theme
from ui.components import page_header, badge, metric_card, section, callout, formula, footer

storage.init()
st.set_page_config(page_title='MCDA Lab', layout='wide', initial_sidebar_state='expanded')
apply_theme()

DISCLAIMER = ('O MCDA Lab é uma ferramenta didática destinada ao estudo e à experimentação de métodos de Apoio Multicritério à Decisão. '
              'Os resultados dependem dos dados, pesos, parâmetros, limiares e preferências definidos pelo usuário e não devem ser interpretados como recomendações automáticas de decisão. '
              'O sistema apoia a análise; a decisão permanece sob responsabilidade do decisor.')

def default_data():
    return {'alternatives': [], 'criteria': [], 'matrix': [], 'c': .70, 'd': .40}

def auth():
    if st.session_state.get('user'): return True
    st.markdown('<div class="mcda-login-wrap"></div>', unsafe_allow_html=True)
    left, gap, right = st.columns([1.08,.12,.8], vertical_alignment='center')
    with left:
        st.markdown('<div class="mcda-hero"><div class="mcda-eyebrow">Laboratório acadêmico</div><h1>Decisão multicritério, explicada passo a passo.</h1><div class="mcda-lead">Construa problemas, compare alternativas e compreenda visualmente PROMETHEE II e ELECTRE I — do dado bruto à análise de sensibilidade.</div><div class="mcda-flow">PROBLEMA → CRITÉRIOS → PREFERÊNCIAS<br>COMPARAÇÕES → FLUXOS / SOBRECLASSIFICAÇÃO → ANÁLISE</div></div>', unsafe_allow_html=True)
    with right:
        st.markdown('<div class="mcda-eyebrow">MCDA LAB</div>', unsafe_allow_html=True)
        tabs=st.tabs(['Entrar','Criar conta'])
        with tabs[0]:
            with st.form('login'):
                e=st.text_input('E-mail', placeholder='nome@exemplo.com')
                p=st.text_input('Senha', type='password')
                if st.form_submit_button('Entrar', type='primary', use_container_width=True):
                    u=storage.login(e,p)
                    if u:
                        st.session_state.user=dict(u); st.session_state.section='Problema'; st.rerun()
                    else: st.error('E-mail ou senha inválidos.')
        with tabs[1]:
            with st.form('reg'):
                n=st.text_input('Nome')
                e=st.text_input('E-mail', key='reg_email')
                p=st.text_input('Senha', type='password', key='reg_pass')
                if st.form_submit_button('Criar conta', type='primary', use_container_width=True):
                    ok,msg=storage.register(n,e,p)
                    if ok: st.success('Conta criada. Agora você pode entrar.')
                    else: st.error(msg)
        st.caption('Ao acessar, você reconhece o caráter didático do laboratório. Os resultados apoiam a análise e não substituem o julgamento do decisor.')
    footer(); return False

def dashboard():
    u=st.session_state.user
    with st.sidebar:
        st.markdown('<div class="mcda-sidebar-kicker">Laboratório acadêmico</div><div class="mcda-sidebar-brand">MCDA Lab</div>', unsafe_allow_html=True)
        st.divider()
        st.markdown(f'<div class="mcda-sidebar-meta">Conectado como</div><div class="mcda-sidebar-title">{u.get("name") or u.get("email")}</div>', unsafe_allow_html=True)
        st.divider()
        if st.button('Sair', use_container_width=True, icon=':material/logout:'): st.session_state.clear(); st.rerun()
    page_header('Workspace','Meus exercícios','Crie um experimento multicritério ou participe de uma análise usando um código compartilhado.')
    a,b=st.columns(2)
    with a:
        with st.expander('Novo exercício', expanded=False):
            with st.form('new'):
                n=st.text_input('Nome do exercício', placeholder='Ex.: Seleção de fornecedores')
                d=st.text_area('Descrição', placeholder='Contexto e objetivo da decisão')
                m=st.radio('Método',['PROMETHEE II','ELECTRE I'],horizontal=True)
                if st.form_submit_button('Criar exercício', type='primary', use_container_width=True):
                    if not n.strip(): st.error('Informe um nome para o exercício.')
                    else:
                        st.session_state.eid=storage.create(u['id'],n,d,m,default_data()); st.session_state.section='Problema'; st.rerun()
    with b:
        with st.expander('Entrar com código', expanded=False):
            with st.form('join'):
                cd=st.text_input('Código',placeholder='MCDA-7K4P2')
                if st.form_submit_button('Entrar no exercício', use_container_width=True):
                    if storage.join(u['id'],cd): st.success('Exercício adicionado.'); st.rerun()
                    else: st.error('Código não encontrado.')
    exs=storage.list_for(u['id']); section('Exercícios recentes')
    if not exs: st.info('Nenhum exercício ainda. Crie o primeiro acima; o laboratório começa vazio.')
    for i in range(0,len(exs),2):
        cols=st.columns(2)
        for col,e in zip(cols,exs[i:i+2]):
            with col:
                role='Proprietário' if e['owner_id']==u['id'] else 'Participante'
                st.markdown(f'<div class="mcda-card"><div>{badge(e["method"],"blue")}{badge(role)}</div><div style="font-size:18px;font-weight:700;letter-spacing:-.03em;margin-top:18px">{e["name"]}</div><div class="mcda-card-note" style="min-height:38px">{e["description"] or "Sem descrição."}</div><div class="mcda-rule"></div><div class="mcda-card-note">Código <strong>{e["code"]}</strong></div></div>',unsafe_allow_html=True)
                if st.button('Abrir exercício', key=f"o{e['id']}", use_container_width=True): st.session_state.eid=e['id']; st.session_state.section='Problema'; st.rerun()
    footer()

def validate(data):
    A=data['alternatives']; C=data['criteria']; errs=[]
    try: X=np.array(data['matrix'],float)
    except Exception: X=np.array([])
    if len(A)<2: errs.append('Cadastre pelo menos 2 alternativas.')
    if len(C)<1: errs.append('Cadastre pelo menos 1 critério.')
    if X.shape!=(len(A),len(C)): errs.append('A matriz de desempenho precisa acompanhar as alternativas e os critérios cadastrados.')
    sw=sum(float(c.get('weight',0)) for c in C)
    if sw<=0: errs.append('A soma dos pesos deve ser maior que zero.')
    for c in C:
        if c.get('function') in ['Level','V-Shape with Indifference'] and float(c.get('p',0))<=float(c.get('q',0)): errs.append(f"{c['name']}: p deve ser maior que q.")
        if c.get('function')=='Gaussian' and float(c.get('s',0))<=0: errs.append(f"{c['name']}: s deve ser maior que zero.")
    return errs

def sidebar_lab(e,owner):
    with st.sidebar:
        st.markdown('<div class="mcda-sidebar-kicker">Laboratório acadêmico</div><div class="mcda-sidebar-brand">MCDA Lab</div>', unsafe_allow_html=True)
        st.divider()
        st.markdown(f'<div class="mcda-sidebar-title">{e["name"]}</div><div class="mcda-sidebar-meta">{e["method"]} · {e["code"]}<br>{"Proprietário" if owner else "Participante"}</div>', unsafe_allow_html=True)
        st.divider()
        items=[
            ('Problema','01  Problema',':material/description:'),
            ('Dados','02  Dados',':material/table_view:'),
            ('Método','03  Método',':material/function:'),
            ('Análise','04  Análise',':material/analytics:'),
            ('Sensibilidade','05  Sensibilidade',':material/tune:'),
            ('Sobre','06  Sobre',':material/info:'),
        ]
        current=st.session_state.get('section','Problema')
        for key,label,icon in items:
            if st.button(label,key='nav_'+key,use_container_width=True,icon=icon,type='primary' if current==key else 'secondary'):
                st.session_state.section=key; st.rerun()
        st.divider()
        if st.button('Meus exercícios',use_container_width=True,icon=':material/arrow_back:'):
            st.session_state.pop('eid',None); st.rerun()

def problem_page(e,data,owner,u):
    page_header('01 / Problema','Defina o problema de decisão','Comece pelo contexto. A matemática entra depois que a decisão e as alternativas estiverem claras.')
    m1,m2,m3=st.columns(3); 
    with m1: metric_card('Método',e['method'],'Método selecionado')
    with m2: metric_card('Alternativas',len(data['alternatives']),'mínimo recomendado: 2')
    with m3: metric_card('Código',e['code'],'compartilhe com participantes')
    section('Contexto e alternativas')
    if not owner:
        st.info('Modo participante: somente o proprietário pode editar o problema.'); st.write(e['description'] or 'Sem descrição.'); st.write(data['alternatives']); return
    title=st.text_input('Título do exercício',value=e['name'])
    desc=st.text_area('Descrição do problema',value=e['description'] or '',placeholder='Descreva o objetivo da decisão e seu contexto.')
    adf=st.data_editor(pd.DataFrame({'Alternativa':data['alternatives']}),num_rows='dynamic',use_container_width=True,hide_index=True,key='alts_v3',column_config={'Alternativa':st.column_config.TextColumn('Alternativa',required=True)})
    alts=[str(x).strip() for x in adf['Alternativa'].tolist() if str(x).strip() and str(x)!='nan']
    if st.button('Salvar problema',type='primary'):
        oldA=data['alternatives']; oldC=data['criteria']; old=pd.DataFrame(data['matrix'],index=oldA,columns=[c['name'] for c in oldC]) if oldA and oldC else pd.DataFrame()
        new=pd.DataFrame(0.,index=alts,columns=[c['name'] for c in oldC])
        for a in new.index:
            for c in new.columns:
                if a in old.index and c in old.columns:new.loc[a,c]=old.loc[a,c]
        data['alternatives']=alts; data['matrix']=new.values.tolist(); storage.update(e['id'],u['id'],data,title,desc); st.success('Problema salvo.'); st.rerun()

def criteria_editor(data,method):
    rows=[]
    for c in data['criteria']:
        rows.append({'Critério':c.get('name',''),'Objetivo':c.get('direction','MAX'),'Peso':c.get('weight',0),'Função':c.get('function','Usual'),'q':c.get('q',0.),'p':c.get('p',1.),'s':c.get('s',1.)})
    cfg={'Objetivo':st.column_config.SelectboxColumn('Objetivo',options=['MAX','MIN'],help='MAX = maximizar · MIN = minimizar'),'Peso':st.column_config.NumberColumn('Peso',min_value=0.,format='%.4f'),'Função':st.column_config.SelectboxColumn('Função',options=['Usual','U-Shape','V-Shape','Level','V-Shape with Indifference','Gaussian'])}
    df=st.data_editor(pd.DataFrame(rows,columns=['Critério','Objetivo','Peso','Função','q','p','s']),num_rows='dynamic',use_container_width=True,hide_index=True,key='crit_v3',column_config=cfg)
    crit=[]
    for _,r in df.iterrows():
        if str(r.get('Critério','')).strip() and str(r.get('Critério'))!='nan': crit.append({'name':str(r['Critério']).strip(),'direction':str(r.get('Objetivo','MAX')),'weight':float(r.get('Peso',0) or 0),'function':str(r.get('Função','Usual')),'q':float(r.get('q',0) or 0),'p':float(r.get('p',1) or 1),'s':float(r.get('s',1) or 1)})
    return crit

def data_page(e,data,owner,u):
    page_header('02 / Dados','Critérios, pesos e desempenho','Organize a estrutura do modelo em uma visão compacta. MAX indica que valores maiores são preferíveis; MIN, valores menores.')
    if not owner: st.info('Modo participante: os dados são definidos pelo proprietário do exercício.')
    section('Critérios')
    if owner: crit=criteria_editor(data,e['method'])
    else: crit=data['criteria']; st.dataframe(pd.DataFrame(crit),use_container_width=True,hide_index=True)
    if crit:
        sw=sum(c['weight'] for c in crit); c1,c2,c3=st.columns(3)
        with c1: metric_card('Critérios',len(crit),'estrutura de avaliação')
        with c2: metric_card('Soma dos pesos',f'{sw:.4f}','normalizados no cálculo')
        with c3: metric_card('Direções',f"{sum(c['direction']=='MAX' for c in crit)} MAX · {sum(c['direction']=='MIN' for c in crit)} MIN",'objetivos dos critérios')
    section('Matriz de desempenho')
    alts=data['alternatives']
    old=pd.DataFrame(data['matrix'],index=data['alternatives'],columns=[c['name'] for c in data['criteria']]) if data['alternatives'] and data['criteria'] else pd.DataFrame()
    new=pd.DataFrame(0.,index=alts,columns=[c['name'] for c in crit])
    for a in new.index:
        for c in new.columns:
            if a in old.index and c in old.columns:new.loc[a,c]=old.loc[a,c]
    labels={c['name']:c['name']+(' ↑' if c['direction']=='MAX' else ' ↓') for c in crit}
    display=new.rename(columns=labels)
    if owner: edited=st.data_editor(display,use_container_width=True,key='matrix_v3')
    else: edited=display; st.dataframe(display,use_container_width=True)
    st.caption('↑ maior é preferível · ↓ menor é preferível. q, p e s só afetam funções de preferência que utilizam esses parâmetros.')
    if e['method']=='ELECTRE I':
        c1,c2=st.columns(2); data['c']=c1.slider("Concordância mínima c′",0.,1.,float(data.get('c',.7)),.01,disabled=not owner); data['d']=c2.slider("Discordância máxima d′",0.,1.,float(data.get('d',.4)),.01,disabled=not owner)
    if owner and st.button('Salvar dados',type='primary'):
        data['criteria']=crit; data['matrix']=edited.rename(columns={v:k for k,v in labels.items()}).astype(float).values.tolist(); storage.update(e['id'],u['id'],data); st.success('Dados salvos.'); st.rerun()

def matrix_view(M,names,title):
    st.markdown(f'**{title}**'); st.dataframe(pd.DataFrame(M,index=names,columns=names).style.format('{:.4f}'),use_container_width=True)

def promethee_method(data):
    A=data['alternatives']; C=data['criteria']; X=np.array(data['matrix']); r=pcalc(X,C)
    page_header('03 / Método','Como o PROMETHEE II constrói a preferência','Explore uma comparação par a par e veja como cada critério contribui para a preferência agregada.')
    formula(['S(a,b) = Σⱼ wⱼ · Fⱼ(a,b)','φ⁺(a) = Σ S(a,b) / (n−1)','φ⁻(a) = Σ S(b,a) / (n−1)','φ(a) = φ⁺(a) − φ⁻(a)'])
    section('Comparação didática')
    c1,c2=st.columns(2); a=c1.selectbox('Alternativa a',range(len(A)),format_func=lambda i:A[i]); b=c2.selectbox('Alternativa b',range(len(A)),index=min(1,len(A)-1),format_func=lambda i:A[i])
    if a==b: st.warning('Escolha duas alternativas diferentes para visualizar a comparação.'); return
    rows=[]
    for j,c in enumerate(C): rows.append({'Critério':c['name'],'Direção':'↑ MAX' if c['direction']=='MAX' else '↓ MIN',A[a]:X[a,j],A[b]:X[b,j],'Peso':r['weights'][j],'Fj':r['preferences'][a,b,j],'w × Fj':r['weights'][j]*r['preferences'][a,b,j]})
    st.dataframe(pd.DataFrame(rows).style.format({'Peso':'{:.4f}','Fj':'{:.4f}','w × Fj':'{:.4f}'}),use_container_width=True,hide_index=True)
    c1,c2=st.columns([1,2]);
    with c1: metric_card(f'S({A[a]}, {A[b]})',f'{r["S"][a,b]:.4f}','preferência agregada')
    with c2: callout('Leia a tabela da esquerda para a direita: desempenho das alternativas → preferência por critério Fj → peso normalizado → contribuição w × Fj. A soma das contribuições produz S(a,b).')

def promethee_analysis(data):
    A=data['alternatives']; C=data['criteria']; X=np.array(data['matrix']); r=pcalc(X,C)
    page_header('04 / Análise','Resultado PROMETHEE II','Fluxos positivos e negativos sintetizam as comparações par a par; o fluxo líquido φ organiza o ranking final.')
    out=pd.DataFrame({'Alternativa':A,'φ+':r['phi_plus'],'φ−':r['phi_minus'],'φ':r['phi']}); out['Posição']=out['φ'].rank(method='min',ascending=False).astype(int); out=out.sort_values(['Posição','Alternativa'])
    winner=out.iloc[0]; cols=st.columns(4)
    vals=[('1ª posição',winner['Alternativa'],'maior fluxo líquido'),('φ+',f"{winner['φ+']:.4f}",'força de saída'),('φ−',f"{winner['φ−']:.4f}",'pressão recebida'),('φ',f"{winner['φ']:+.4f}",'saldo líquido')]
    for col,(l,v,n) in zip(cols,vals):
        with col: metric_card(l,v,n)
    section('Visão analítica')
    left,right=st.columns([1.55,.75])
    with left:
        fig=px.bar(out.sort_values('φ'),x='φ',y='Alternativa',orientation='h'); fig.update_layout(title='Fluxo líquido φ',height=360,margin=dict(l=20,r=20,t=55,b=25),plot_bgcolor='white',paper_bgcolor='white',showlegend=False); fig.add_vline(x=0,line_width=1,line_color='#a8a29e'); st.plotly_chart(fig,use_container_width=True)
    with right:
        st.markdown('<div class="mcda-card-flat"><div class="mcda-card-label">Ranking</div>',unsafe_allow_html=True)
        for _,row in out.iterrows(): st.markdown(f'<div class="mcda-rank"><span class="mcda-rank-n">{int(row["Posição"]):02d}</span><span class="mcda-rank-name">{row["Alternativa"]}</span><span class="mcda-rank-val">{row["φ"]:+.4f}</span></div>',unsafe_allow_html=True)
        st.markdown('</div>',unsafe_allow_html=True)
    c1,c2=st.columns([1,1])
    with c1: matrix_view(r['S'],A,'Matriz de preferências S(a,b)')
    with c2: st.markdown('**Fluxos por alternativa**'); st.dataframe(out[['Posição','Alternativa','φ+','φ−','φ']].style.format({'φ+':'{:.4f}','φ−':'{:.4f}','φ':'{:+.4f}'}),use_container_width=True,hide_index=True)

def promethee_sensitivity(data):
    A=data['alternatives']; C=data['criteria']; X=np.array(data['matrix'])
    page_header('05 / Sensibilidade','O ranking permanece estável quando os pesos mudam?','Varie um critério e observe como os fluxos líquidos e as posições respondem. Os demais pesos são reajustados proporcionalmente.')
    c1,c2=st.columns([1,2]); idx=c1.selectbox('Critério a variar',range(len(C)),format_func=lambda i:C[i]['name']); lo,hi=c2.slider('Faixa do peso',0.,1.,(0.05,0.80),.05); vals=np.linspace(lo,hi,16); sd=psens(X,C,idx,vals); sd['Alternativa']=sd['alternative'].map(dict(enumerate(A)))
    original=float(C[idx]['weight']); metric_card('Peso original',f'{original:.2f}',f'critério: {C[idx]["name"]}')
    fig=px.line(sd,x='weight',y='phi',color='Alternativa',markers=True); fig.add_vline(x=original,line_dash='dash',line_color='#57534e'); fig.update_layout(title=f'Evolução de φ · {C[idx]["name"]}',height=410,plot_bgcolor='white',paper_bgcolor='white',legend_title_text='Alternativa'); st.plotly_chart(fig,use_container_width=True)
    st.markdown('**Posição por peso testado**'); st.dataframe(sd.pivot(index='weight',columns='Alternativa',values='rank'),use_container_width=True)

def electre_method(data):
    A=data['alternatives']; C=data['criteria']; X=np.array(data['matrix']); r=ecalc(X,C,data['c'],data['d'])
    page_header('03 / Método','Como o ELECTRE I testa a sobreclassificação','Compare concordância e discordância com os limiares definidos para verificar se a relação aSb é aceita.')
    formula(['C(a,b) = Σ wⱼ nos critérios favoráveis','D(a,b) = max(desvantagem / amplitude)','aSb ⇔ C(a,b) ≥ c′  E  D(a,b) ≤ d′'])
    c1,c2=st.columns(2); a=c1.selectbox('Alternativa a',range(len(A)),format_func=lambda i:A[i],key='ea'); b=c2.selectbox('Alternativa b',range(len(A)),index=min(1,len(A)-1),format_func=lambda i:A[i],key='eb')
    if a==b: st.warning('Escolha duas alternativas diferentes.'); return
    cc=float(r['C'][a,b]); dd=float(r['D'][a,b]); okc=cc>=data['c']; okd=dd<=data['d']; cols=st.columns(3)
    with cols[0]: metric_card('Concordância',f'{cc:.4f}',f"limite c′ = {data['c']:.2f} · {'atende' if okc else 'não atende'}")
    with cols[1]: metric_card('Discordância',f'{dd:.4f}',f"limite d′ = {data['d']:.2f} · {'atende' if okd else 'não atende'}")
    with cols[2]: metric_card('Relação aSb','Sim' if r['R'][a,b] else 'Não',f'{A[a]} → {A[b]}')
    callout(f"{A[a]} {'sobreclassifica' if r['R'][a,b] else 'não sobreclassifica'} {A[b]}. A relação exige que concordância e discordância satisfaçam simultaneamente seus limiares.")

def electre_analysis(data):
    A=data['alternatives']; C=data['criteria']; X=np.array(data['matrix']); r=ecalc(X,C,data['c'],data['d'])
    page_header('04 / Análise','Relação de sobreclassificação ELECTRE I','Leia as matrizes, o grafo dirigido e o kernel sem forçar um ranking completo onde o método não o produz.')
    arcs=int(r['R'].sum()); ks=['{'+', '.join(A[i] for i in k)+'}' for k in r['kernels']]; cols=st.columns(3)
    with cols[0]: metric_card('Relações aSb',arcs,'arestas aceitas')
    with cols[1]: metric_card('c′ / d′',f"{data['c']:.2f} / {data['d']:.2f}",'limiares ativos')
    with cols[2]: metric_card('Kernel', ' · '.join(ks) if ks else '—','conjunto(s) encontrado(s)')
    c1,c2=st.columns(2)
    with c1: matrix_view(r['C'],A,'Concordância C(a,b)')
    with c2: matrix_view(r['D'],A,'Discordância D(a,b)')
    section('Relação e grafo')
    left,right=st.columns([.8,1.2])
    with left: st.dataframe(pd.DataFrame(r['R'].astype(int),index=A,columns=A),use_container_width=True)
    with right:
        G=nx.DiGraph(); G.add_nodes_from(range(len(A))); G.add_edges_from(zip(*np.where(r['R']))); pos=nx.circular_layout(G); fig=go.Figure()
        for u,v in G.edges(): fig.add_trace(go.Scatter(x=[pos[u][0],pos[v][0]],y=[pos[u][1],pos[v][1]],mode='lines',line=dict(width=1,color='#78716c'),hoverinfo='skip',showlegend=False))
        fig.add_trace(go.Scatter(x=[pos[i][0] for i in G],y=[pos[i][1] for i in G],mode='markers+text',text=A,textposition='top center',marker=dict(size=22,color='#1c1917'),showlegend=False)); fig.update_layout(height=360,margin=dict(l=10,r=10,t=30,b=10),xaxis=dict(visible=False),yaxis=dict(visible=False),paper_bgcolor='white',plot_bgcolor='white'); st.plotly_chart(fig,use_container_width=True)

def electre_sensitivity(data):
    A=data['alternatives']; C=data['criteria']; X=np.array(data['matrix'])
    page_header('05 / Sensibilidade','Como os limiares alteram a relação?','Explore pequenas variações de c′ e d′ e observe quantas relações de sobreclassificação permanecem ativas.')
    cv=np.linspace(max(0,data['c']-.2),min(1,data['c']+.2),5); dv=np.linspace(max(0,data['d']-.2),min(1,data['d']+.2),5); sd=esens(X,C,cv,dv)
    fig=px.scatter(sd,x='c',y='d',size='arcs',color='arcs',labels={'c':'c′','d':'d′','arcs':'Relações'}); fig.update_layout(height=430,plot_bgcolor='white',paper_bgcolor='white'); st.plotly_chart(fig,use_container_width=True); st.dataframe(sd,use_container_width=True,hide_index=True)

def about_page(e):
    page_header('06 / Sobre','Sobre o laboratório','Referência rápida para compreender o propósito, os métodos e os limites de uso do MCDA Lab.')
    section('Uso acadêmico'); callout(DISCLAIMER)
    c1,c2=st.columns(2)
    with c1: st.markdown('### PROMETHEE II\nCompara alternativas par a par por critérios ponderados, calcula fluxos positivo e negativo e utiliza o fluxo líquido para produzir uma ordenação completa, admitindo empates.')
    with c2: st.markdown('### ELECTRE I\nConstrói uma relação de sobreclassificação a partir de concordância, discordância e limiares. O resultado é uma relação/grafo e kernel, não um ranking artificial.')
    section('Notação essencial'); st.markdown('`a, b` alternativas · `j` critério · `wⱼ` peso · `Fⱼ` preferência · `φ+` fluxo positivo · `φ−` fluxo negativo · `φ` fluxo líquido · `c′` limiar de concordância · `d′` limiar de discordância')

def lab():
    u=st.session_state.user; e=storage.get(st.session_state.eid,u['id'])
    if not e: st.session_state.pop('eid',None); st.rerun()
    data=json.loads(e['data']); owner=e['owner_id']==u['id']; sidebar_lab(e,owner)
    st.markdown(f'{badge(e["method"],"blue")}{badge(e["code"])}{badge("Proprietário" if owner else "Participante","green" if owner else "")}',unsafe_allow_html=True)
    section_name=st.session_state.get('section','Problema')
    errs=validate(data)
    if section_name=='Problema': problem_page(e,data,owner,u)
    elif section_name=='Dados': data_page(e,data,owner,u)
    elif section_name in ['Método','Análise','Sensibilidade']:
        if errs:
            page_header('Modelo incompleto','Complete os dados antes de calcular','O laboratório precisa de uma estrutura válida para executar o método.')
            for x in errs: st.error(x)
        elif e['method']=='PROMETHEE II': {'Método':promethee_method,'Análise':promethee_analysis,'Sensibilidade':promethee_sensitivity}[section_name](data)
        else: {'Método':electre_method,'Análise':electre_analysis,'Sensibilidade':electre_sensitivity}[section_name](data)
    else: about_page(e)
    footer()

if auth():
    if st.session_state.get('eid'): lab()
    else: dashboard()
