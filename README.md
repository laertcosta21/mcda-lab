# MCDA Lab V3

Laboratório didático em Streamlit para PROMETHEE II e ELECTRE I.

## Executar

```bash
pip install -r requirements.txt
python -m streamlit run app.py
```

## Estrutura
- `app.py`: navegação e telas.
- `ui/theme.py`: design tokens e CSS global.
- `ui/components.py`: componentes visuais reutilizáveis.
- `engine/`: motores matemáticos e persistência. Não alterar sem revalidação.
- `tests/`: golden tests dos motores.

## Princípios da V3
- layout analítico e compacto;
- login diagramado;
- navegação Problema → Dados → Método → Análise → Sensibilidade → Sobre;
- exercícios novos começam vazios;
- disclaimer/footer acadêmico;
- motores matemáticos preservados.
