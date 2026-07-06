# SentinelScan Elite CLI

SentinelScan Elite CLI e uma plataforma modular de linha de comando para auditorias autorizadas, inventario de ativos, organizacao de projetos, sessoes, logs, auditoria e relatorios.

Esta implementacao segue os documentos oficiais em `docs/MASTER_PROMPT.md` e `docs/TECHNICAL_SPECIFICATION.md`, preservando a arquitetura em camadas definida para `app`, `core`, `cli`, `services`, `modules`, `plugins`, `config`, `reports`, `logs`, `data`, `cache` e `tests`.

## Recursos implementados

- Bootstrap com validacao do ambiente, criacao de diretorios e inicializacao controlada.
- CLI com comandos para status, configuracoes, projetos, sessoes, modulos, relatorios, plugins e logs.
- Gerenciador de modulos com descoberta automatica, metadados, estados, execucao, eventos e isolamento de falhas.
- Sistema centralizado de configuracao com valores padrao, validacao e persistencia.
- Logs rotativos e trilha de auditoria estruturada em JSONL.
- Gerenciamento de projetos e sessoes com catalogo, historico e integridade de arquivos.
- Gerador de relatorios em Markdown e JSON com metadados padronizados.
- Sistema de plugins com manifestos, validacao, ciclo de vida e plugin de referencia.
- Testes automatizados unitarios e de integracao.

## Instalação

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements/dev.txt
```

Em Linux/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements/dev.txt
```

## Comandos principais

```bash
python main.py status
python main.py modules list
python main.py plugins list
python main.py config show
```

Criar projeto e sessao:

```bash
python main.py projects create "Laboratorio autorizado" --description "Ambiente de testes"
python main.py sessions start <project_id>
```

Executar modulo com relatorio:

```bash
python main.py modules run asset_inventory --param input_file=examples/assets.json --report
python main.py modules run system_health --report
```

Consultar auditoria:

```bash
python main.py logs audit --limit 10
```

## Testes

A suíte usa `pytest` e cobre núcleo, CLI, configuração, logs, relatórios, projetos, sessões, módulos, plugins, utilitários, erros, integração e smoke tests.

```bash
pytest
```

Como alternativa equivalente:

```bash
python -m pytest
```

Com cobertura:

```bash
pytest --cov=. --cov-report=term-missing
```

Arquivos principais da suíte:

- `tests/test_core.py`
- `tests/test_cli.py`
- `tests/test_config.py`
- `tests/test_logger.py`
- `tests/test_reports.py`
- `tests/test_projects.py`
- `tests/test_sessions.py`
- `tests/test_modules.py`
- `tests/test_plugins.py`
- `tests/test_utils.py`
- `tests/test_errors.py`
- `tests/test_integration.py`
- `tests/test_smoke.py`

Todos os testes usam diretórios temporários isolados para evitar lixo operacional no repositório.

## Segurança e escopo

O projeto foi implementado para fluxos autorizados. Os modulos incluidos nesta versao inicial focam em inventario informado pelo usuario, saude do runtime e resumo de projetos, evitando operacoes intrusivas ou ofensivas.

## Documentação

- `docs/ARCHITECTURE.md`
- `docs/CODING_STANDARDS.md`
- `docs/TESTING_GUIDE.md`
- `docs/ROADMAP.md`
- `docs/USER_GUIDE.md`
- `docs/DEVELOPER_GUIDE.md`
- `docs/PLUGIN_GUIDE.md`
- `docs/MODULE_GUIDE.md`
