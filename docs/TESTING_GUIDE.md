# Testing Guide

## Executar testes

```bash
pytest
```

ou:

```bash
python -m pytest
```

## Cobertura

```bash
pytest --cov=. --cov-report=term-missing
```

## Estrutura

- `tests/test_core.py`: eventos, permissoes, contratos, validadores e recursos.
- `tests/test_cli.py`: comandos reais da CLI e parsing de parametros.
- `tests/test_config.py`: configuracoes validas, invalidas, padrao e corrompidas.
- `tests/test_logger.py`: logs, auditoria e historico.
- `tests/test_reports.py`: relatorios Markdown/JSON e erros esperados.
- `tests/test_projects.py`: catalogo, arquivamento, historico e estatisticas.
- `tests/test_sessions.py`: abertura, fechamento, retomada e persistencia.
- `tests/test_modules.py`: descoberta, registro, execucao, modulos internos e falhas controladas.
- `tests/test_plugins.py`: plugins validos, invalidos, desativados e incompativeis.
- `tests/test_utils.py`: persistencia auxiliar, tabelas e mensagens.
- `tests/test_errors.py`: hierarquia de erros e tratamento pela CLI.
- `tests/test_integration.py`: fluxos completos entre servicos.
- `tests/test_smoke.py`: inicializacao e comandos basicos.

Os testes usam fixtures em `tests/conftest.py` para criar uma copia temporaria do projeto, evitando que logs, relatorios e dados de execucao sujem o repositorio.

## Criterios

Uma alteracao deve:

- passar nos testes existentes;
- adicionar testes quando alterar comportamento;
- preservar a estrutura documentada;
- atualizar documentacao e changelog quando criar funcionalidade.
