import numpy as np
from engine.promethee import calculate as pcalc
from engine.electre import calculate as ecalc
X=np.array([[72,14.5,7,2800],[74,13.8,7.5,2600],[89,13,8.5,3200],[58,15.2,5.5,2200]],float)
C=[{'weight':.35,'direction':'MIN','function':'Usual'},{'weight':.25,'direction':'MAX','function':'Usual'},{'weight':.25,'direction':'MAX','function':'Usual'},{'weight':.15,'direction':'MIN','function':'Usual'}]
def test_promethee_golden():
 r=pcalc(X,C)
 assert np.allclose(r['S'],[[0,.6,.75,.25],[.4,0,.75,.25],[.25,.25,0,.25],[.75,.75,.75,0]])
 assert np.allclose(r['phi'],[.0666666667,-.0666666667,-.5,.5])
 assert list(r['order'])==[3,0,1,2]
def test_electre_golden():
 r=ecalc(X,C,.7,.4)
 assert r['R'].sum()==1 and r['R'][1,2]
 assert [0,1,3] in r['kernels']
