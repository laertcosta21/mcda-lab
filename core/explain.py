"""Leituras derivadas dos resultados dos motores, usadas só para explicar e ilustrar.

Nenhuma função aqui altera ou substitui o cálculo de engine/: os totais exibidos
na interface continuam vindo de engine.promethee e engine.electre.
"""
import numpy as np
import pandas as pd

from engine.electre import EPS


def promethee_ranking(names, result):
    """Tabela de fluxos ordenada por posição (empates recebem a mesma posição)."""
    out = pd.DataFrame({'Alternativa': names, 'φ+': result['phi_plus'], 'φ−': result['phi_minus'], 'φ': result['phi']})
    out['Posição'] = out['φ'].rank(method='min', ascending=False).astype(int)
    return out.sort_values(['Posição', 'Alternativa'])


def electre_pair(X, criteria, a, b):
    """Decomposição por critério de C(a,b) e D(a,b), espelhando engine.electre.calculate."""
    X = np.asarray(X, float)
    signs = np.array([1 if c.get('direction', 'MAX').upper() == 'MAX' else -1 for c in criteria])
    Y = X * signs
    ranges = np.ptp(Y, axis=0)
    agrees = Y[a] >= Y[b] - EPS
    worse = Y[b] - Y[a]
    disc = np.where((worse > EPS) & (ranges > EPS), worse / np.where(ranges > EPS, ranges, 1), 0)
    return {'agrees': agrees, 'discordance': disc}


def electre_tests(C, D, c_threshold, d_threshold):
    """Quais pares atendem a cada limiar, com a mesma tolerância do motor."""
    return np.asarray(C) >= c_threshold - EPS, np.asarray(D) <= d_threshold + EPS


def rank_changes(sd, names):
    """Trocas de posição entre pesos consecutivos de uma análise de sensibilidade PROMETHEE.

    sd: DataFrame de engine.promethee.sensitivity (weight, alternative, phi, rank).
    Devolve uma lista de dicts {'weight', 'up', 'down'}: perto de `weight`, a
    alternativa `up` passa à frente de `down`. φ é linear no peso testado, então
    o ponto de cruzamento é obtido por interpolação entre os dois pesos vizinhos.
    """
    weights = sorted(sd['weight'].unique())
    phi = sd.pivot(index='weight', columns='alternative', values='phi')
    rank = sd.pivot(index='weight', columns='alternative', values='rank')
    alts = list(phi.columns)
    changes = []
    for w0, w1 in zip(weights, weights[1:]):
        for x, i in enumerate(alts):
            for k in alts[x + 1:]:
                before = rank.loc[w0, i] - rank.loc[w0, k]
                after = rank.loc[w1, i] - rank.loc[w1, k]
                if before * after >= 0: continue
                d0 = phi.loc[w0, i] - phi.loc[w0, k]; d1 = phi.loc[w1, i] - phi.loc[w1, k]
                cross = w0 + (w1 - w0) * d0 / (d0 - d1) if abs(d0 - d1) > EPS else (w0 + w1) / 2
                cross = min(max(float(cross), float(w0)), float(w1))
                up, down = (i, k) if after < 0 else (k, i)
                changes.append({'weight': cross, 'up': names[up], 'down': names[down]})
    return sorted(changes, key=lambda c: c['weight'])


def leaders(sd, names):
    """Líder (posição 1) em cada peso testado, na ordem dos pesos."""
    first = sd[sd['rank'] == 1].sort_values('weight')
    return [(float(w), names[int(a)]) for w, a in zip(first['weight'], first['alternative'])]
