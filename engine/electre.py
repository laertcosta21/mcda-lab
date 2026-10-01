import numpy as np
import pandas as pd
import networkx as nx
EPS=1e-12

def calculate(matrix, criteria, c_threshold=.7, d_threshold=.4):
    X=np.asarray(matrix,float); n,m=X.shape
    w=np.array([float(c['weight']) for c in criteria],float); w=w/w.sum()
    signs=np.array([1 if c.get('direction','MAX').upper()=='MAX' else -1 for c in criteria])
    Y=X*signs
    ranges=np.ptp(Y,axis=0)
    C=np.zeros((n,n)); D=np.zeros((n,n))
    for a in range(n):
      for b in range(n):
        if a==b: continue
        C[a,b]=w[Y[a]>=Y[b]-EPS].sum()
        worse=Y[b]-Y[a]
        vals=np.where((worse>EPS)&(ranges>EPS),worse/np.where(ranges>EPS,ranges,1),0)
        D[a,b]=vals.max(initial=0)
    R=(C>=c_threshold-EPS)&(D<=d_threshold+EPS); np.fill_diagonal(R,False)
    return {'weights':w,'C':C,'D':D,'R':R,'kernels':kernels(R)}

def kernels(R):
    n=len(R); out=[]
    for mask in range(1,1<<n):
        K=[i for i in range(n) if mask>>i&1]
        if any(R[i,j] or R[j,i] for x,i in enumerate(K) for j in K[x+1:]): continue
        outside=[i for i in range(n) if i not in K]
        if all(any(R[k,o] for k in K) for o in outside): out.append(K)
    return out

def sensitivity(matrix, criteria, c_values, d_values):
    rows=[]
    for c in c_values:
      for d in d_values:
        r=calculate(matrix,criteria,float(c),float(d))
        rows.append({'c':float(c),'d':float(d),'arcs':int(r['R'].sum()),'kernels':' | '.join(','.join(map(str,k)) for k in r['kernels']) or 'nenhum'})
    return pd.DataFrame(rows)
