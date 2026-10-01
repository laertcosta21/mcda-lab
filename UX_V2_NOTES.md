# MCDA Lab — UX/UI V2

Esta versão preserva os motores matemáticos de PROMETHEE II e ELECTRE I e refatora a camada de experiência.

## Principais mudanças
- Design visual adaptado do Design System fornecido (Inter, Stone, cards, superfícies e hierarquia).
- Jornada interna: Problema → Dados → Método → Análise → Sensibilidade → Sobre.
- Exercícios novos iniciam vazios, sem exemplos pré-carregados.
- Critérios exibem somente os parâmetros q/p/s exigidos pela função de preferência selecionada.
- PROMETHEE II com comparação didática, matriz S, fluxos, ranking e análise de sensibilidade.
- ELECTRE I com concordância, discordância, limiares, relação, grafo, kernel e sensibilidade.
- Disclaimer acadêmico no primeiro acesso da sessão e aviso permanente no footer/Sobre.
- Footer com MCDA Lab, UFMS, 2026, Laert Costa e Felipe Pires.
- Mensagens de validação orientadas à correção.

## Execução
```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Validação matemática
Os testes `tests/test_engines.py` permanecem inalterados e passam para os casos dourados de PROMETHEE II e ELECTRE I.
