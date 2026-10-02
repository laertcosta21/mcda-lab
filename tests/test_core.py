"""A camada de explicação (core/) só pode decompor o que os motores calculam, nunca divergir deles."""
import numpy as np
from core.explain import electre_pair, electre_tests, leaders, promethee_ranking, rank_changes
from core.rules import default_data, rebuild_matrix, validate
from engine.electre import calculate as ecalc
from engine.promethee import calculate as pcalc, sensitivity as psens

A = ['Onix', 'HB20', 'Corolla', 'Kwid']
X = np.array([[72, 14.5, 7, 2800], [74, 13.8, 7.5, 2600], [89, 13, 8.5, 3200], [58, 15.2, 5.5, 2200]], float)
C = [{'name': 'Preço', 'weight': .35, 'direction': 'MIN', 'function': 'Usual'}, {'name': 'Consumo', 'weight': .25, 'direction': 'MAX', 'function': 'Usual'},
     {'name': 'Conforto', 'weight': .25, 'direction': 'MAX', 'function': 'Usual'}, {'name': 'Manutenção', 'weight': .15, 'direction': 'MIN', 'function': 'Usual'}]


def test_electre_pair_reproduces_engine():
    r = ecalc(X, C, .7, .4)
    for a in range(4):
        for b in range(4):
            if a == b: continue
            p = electre_pair(X, C, a, b)
            assert np.isclose(r['weights'][p['agrees']].sum(), r['C'][a, b])
            assert np.isclose(p['discordance'].max(initial=0), r['D'][a, b])


def test_electre_tests_reproduce_relation():
    r = ecalc(X, C, .7, .4)
    okc, okd = electre_tests(r['C'], r['D'], .7, .4)
    R = okc & okd; np.fill_diagonal(R, False)
    assert (R == r['R']).all()


def test_promethee_ranking_follows_engine_order():
    r = pcalc(X, C)
    out = promethee_ranking(A, r)
    assert out['Alternativa'].tolist() == [A[i] for i in r['order']]
    assert out['Posição'].tolist() == [1, 2, 3, 4]


def test_rank_changes_match_sensitivity_ranks():
    sd = psens(X, C, 0, np.linspace(.05, .80, 16))
    changes = rank_changes(sd, A)
    assert [(c['up'], c['down']) for c in changes] == [('Onix', 'HB20')]
    assert .15 < changes[0]['weight'] < .20
    assert {name for _, name in leaders(sd, A)} == {'Kwid'}


def test_validate_and_rebuild_matrix():
    assert len(validate(default_data())) == 4
    data = {'alternatives': A, 'criteria': C, 'matrix': X.tolist(), 'c': .7, 'd': .4}
    assert validate(data) == []
    new = rebuild_matrix(data, ['Kwid', 'Novo'], ['Preço', 'Outro'])
    assert new.values.tolist() == [[58.0, 0.0], [0.0, 0.0]]
