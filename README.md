# MCDA Lab

Laboratório didático em Streamlit para PROMETHEE II e ELECTRE I.

## Executar

```bash
pip install -r requirements.txt
python -m streamlit run app.py
```

Antes de executar, rode `supabase_schema.sql` no SQL Editor do Supabase e informe as credenciais:

- local: `SUPABASE_URL` e `SUPABASE_KEY` no arquivo `.env`;
- Streamlit Cloud: as mesmas chaves em *Settings → Secrets*.

O app usa `st.secrets` quando as chaves estão lá e, na falta, as variáveis de ambiente. A chave é a secreta (`service_role` / `sb_secret_…`): as tabelas têm RLS ligado sem policies.

## Testes

```bash
python -m pytest -q
```

- `tests/test_engines.py`: casos dourados dos motores. Não ajustar os valores esperados.
- `tests/test_core.py`: garante que a camada de explicação reproduz os totais dos motores.
- `tests/test_storage.py`: sessão persistente e operações de edição e remoção, contra um Supabase falso em memória (`tests/fake_supabase.py`).

## Estrutura

| Camada | Onde | Responsabilidade |
| --- | --- | --- |
| Roteamento | `app.py` | Decide qual tela mostrar. |
| Matemática | `engine/promethee.py`, `engine/electre.py` | Motores validados. Não alterar sem revalidação. |
| Persistência | `engine/storage.py` | Supabase (PostgreSQL) via `supabase-py`. Esquema em `supabase_schema.sql`. |
| Regras | `core/rules.py` | Estrutura do exercício, validação do modelo, parâmetros por função de preferência. |
| Explicação | `core/explain.py` | Decomposições e leituras derivadas dos resultados dos motores. |
| Design system | `ui/theme.py` | Tokens (cores, tipografia, espaçamento, raios, sombras, larguras, alturas, ícones) e todo o CSS. |
| Componentes | `ui/components.py` | Cabeçalhos, faixa de métricas, tabelas, matrizes, callouts, fórmulas, rodapé. |
| Shell | `ui/layout.py`, `ui/navigation.py` | Configuração da página, barra de contexto e sidebar. |
| Gráficos | `ui/charts.py` | ECharts no padrão do design system. |
| Telas | `ui/views/` | Login, Meus exercícios e as seis seções do workspace. |
| Sessão | `ui/session.py` | Mantém o login após recarregar a página (cookie + tabela `sessions`) e a tela atual na URL. |
| Diálogos | `ui/dialogs.py` | Criar, editar e excluir exercícios; sair de exercício; perfil, senha e exclusão de conta. |

As cores de base também ficam em `.streamlit/config.toml`, de onde o Streamlit tira o tema dos widgets nativos. Ao mudar a paleta, altere os dois arquivos.

## Convenções de interface

- Nenhum `st.markdown("<style>…")` fora de `ui/theme.py`.
- Ícones: somente Material Symbols (`:material/nome:` nos widgets, `components.icon()` em HTML). Sem emoji.
- Botões: `type='primary'`, padrão (secundário) e `type='tertiary'` (ghost). Para perigo ou botão só de ícone, envolva em `st.container(key='danger_…')` ou `st.container(key='icon_…')`.
- Estilos específicos usam a classe `st-key-…` gerada pelo `key` do container, não seletores internos do Streamlit.
- Texto vindo do usuário passa por `components.esc()` antes de entrar em HTML.

## Jornada

Problema → Dados → Método → Análise → Sensibilidade → Sobre. Exercícios novos começam vazios.
