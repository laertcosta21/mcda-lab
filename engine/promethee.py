import numpy as np
import pandas as pd

EPS=1e-12

def _pref(d, kind='Usual', q=0.0, p=0.0, s=1.0):
    d=np.asarray(d,dtype=float)
    k=kind.lower()
    if k=='usual': return (d>EPS).astype(float)
    if k in ('u-shape','u_shape'): return (d>q).astype(float)
    if k in ('v-shape','v_shape'):
        if p<=0: raise ValueError('p deve ser > 0')
        return np.where(d<=0,0,np.where(d>=p,1,d/p))
    if k=='level':
        if p<=q: raise ValueError('p deve ser maior que q')
        return np.where(d<=q,0,np.where(d<=p,0.5,1))
    if k in ('v-shape with indifference','v_shape_indifference','v-shape-indifference'):
        if p<=q: raise ValueError('p deve ser maior que q')
        return np.where(d<=q,0,np.where(d>=p,1,(d-q)/(p-q)))
    if k=='gaussian':
        if s<=0: raise ValueError('s deve ser > 0')
        return np.where(d<=0,0,1-np.exp(-(d*d)/(2*s*s)))
    raise ValueError(f'Função desconhecida: {kind}')

def calculate(matrix, criteria):
    X=np.asarray(matrix,dtype=float)
    n,m=X.shape
    if n<2 or m<1: raise ValueError('Use ao menos 2 alternativas e 1 critério')
    w=np.array([float(c['weight']) for c in criteria],dtype=float)
    if np.any(w<0) or w.sum()<=0: raise ValueError('Pesos inválidos')
    w=w/w.sum()
    P=np.zeros((n,n,m)); S=np.zeros((n,n))
    for j,c in enumerate(criteria):
        sign=1 if c.get('direction','MAX').upper()=='MAX' else -1
        d=sign*(X[:,j,None]-X[None,:,j])
        P[:,:,j]=_pref(d,c.get('function','Usual'),float(c.get('q',0) or 0),float(c.get('p',0) or 0),float(c.get('s',1) or 1))
        S += w[j]*P[:,:,j]
    np.fill_diagonal(S,0)
    phi_plus=S.sum(axis=1)/(n-1)
    phi_minus=S.sum(axis=0)/(n-1)
    phi=phi_plus-phi_minus
    order=np.argsort(-phi,kind='stable')
    return {'weights':w,'preferences':P,'S':S,'phi_plus':phi_plus,'phi_minus':phi_minus,'phi':phi,'order':order}

def sensitivity(matrix, criteria, criterion_index, values):
    rows=[]; base=np.array([c['weight'] for c in criteria],float); idx=criterion_index
    for target in values:
        target=float(target); other=base.sum()-base[idx]
        if target<0 or target>1: continue
        nw=base.copy()
        if other<=EPS: nw[:]=(1-target)/(len(base)-1); nw[idx]=target
        else:
            factor=(1-target)/other
            for j in range(len(nw)):
                if j!=idx: nw[j]=base[j]*factor
            nw[idx]=target
        cs=[dict(c,weight=float(nw[j])) for j,c in enumerate(criteria)]
        r=calculate(matrix,cs)
        for a,v in enumerate(r['phi']): rows.append({'weight':target,'alternative':a,'phi':float(v),'rank':int(np.where(r['order']==a)[0][0])+1})
    return pd.DataFrame(rows)
