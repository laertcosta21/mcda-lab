"""Regras de negócio do laboratório: estrutura do exercício e validação do modelo.

Nada aqui desenha tela nem faz cálculo de método; os motores ficam em engine/.
"""
import numpy as np
import pandas as pd

METHODS = ['PROMETHEE II', 'ELECTRE I']
SECTIONS = ['Problema', 'Dados', 'Método', 'Análise', 'Sensibilidade', 'Sobre']
FUNCTIONS = ['Usual', 'U-Shape', 'V-Shape', 'Level', 'V-Shape with Indifference', 'Gaussian']
# parâmetros que cada função de preferência realmente usa no motor PROMETHEE
FUNCTION_PARAMS = {
    'Usual': (),
    'U-Shape': ('q',),
    'V-Shape': ('p',),
    'Level': ('q', 'p'),
    'V-Shape with Indifference': ('q', 'p'),
    'Gaussian': ('s',),
}
PARAM_DEFAULTS = {'q': 0.0, 'p': 1.0, 's': 1.0}

DISCLAIMER = (
    'O MCDA Lab é uma ferramenta didática destinada ao estudo e à experimentação de métodos de Apoio Multicritério à Decisão. '
    'Os resultados dependem dos dados, pesos, parâmetros, limiares e preferências definidos pelo usuário e não devem ser '
    'interpretados como recomendações automáticas de decisão. '
    'O sistema apoia a análise; a decisão permanece sob responsabilidade do decisor.'
)


def default_data():
    return {'alternatives': [], 'criteria': [], 'matrix': [], 'c': .70, 'd': .40}


def validate(data):
    A = data['alternatives']; C = data['criteria']; errs = []
    try: X = np.array(data['matrix'], float)
    except Exception: X = np.array([])
    if len(A) < 2: errs.append('Cadastre pelo menos 2 alternativas.')
    if len(C) < 1: errs.append('Cadastre pelo menos 1 critério.')
    if X.shape != (len(A), len(C)): errs.append('A matriz de desempenho precisa acompanhar as alternativas e os critérios cadastrados.')
    sw = sum(float(c.get('weight', 0)) for c in C)
    if sw <= 0: errs.append('A soma dos pesos deve ser maior que zero.')
    for c in C:
        if c.get('function') in ['Level', 'V-Shape with Indifference'] and float(c.get('p', 0)) <= float(c.get('q', 0)): errs.append(f"{c['name']}: p deve ser maior que q.")
        if c.get('function') == 'Gaussian' and float(c.get('s', 0)) <= 0: errs.append(f"{c['name']}: s deve ser maior que zero.")
    return errs


def rebuild_matrix(data, alternatives, criteria_names):
    """Matriz no novo formato, preservando os valores já salvos por (alternativa, critério)."""
    old_a = data['alternatives']; old_c = [c['name'] for c in data['criteria']]
    old = pd.DataFrame(data['matrix'], index=old_a, columns=old_c) if old_a and old_c else pd.DataFrame()
    new = pd.DataFrame(0., index=alternatives, columns=criteria_names)
    for a in new.index:
        for c in new.columns:
            if a in old.index and c in old.columns: new.loc[a, c] = old.loc[a, c]
    return new


def role_label(exercise, user):
    return 'Proprietário' if exercise['owner_id'] == user['id'] else 'Participante'
