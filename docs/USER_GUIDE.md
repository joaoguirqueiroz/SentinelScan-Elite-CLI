# User Guide

## Verificar status

```bash
python main.py status
```

## Abrir ajuda e menu interativo

```bash
python main.py help
python main.py interactive
```

No menu interativo, use `0` para sair corretamente e visualizar o relatorio final da sessao.

## Criar projeto

```bash
python main.py projects create "Meu Projeto" --description "Auditoria autorizada"
```

## Iniciar sessao

```bash
python main.py sessions start <project_id>
```

## Executar modulo

```bash
python main.py modules run system_health --report
python main.py modules run system_health --report --report-format html
python main.py modules run asset_inventory --param input_file=examples/assets.json --report --report-format csv
```

## Gerar relatorio manual

```bash
python main.py reports generate --title "Resumo" --data "{\"status\":\"ok\"}"
python main.py reports generate --title "Resumo HTML" --format html --data "{\"status\":\"ok\"}"
```

Formatos suportados: `markdown`, `txt`, `json`, `csv` e `html`.

## Consultar auditoria

```bash
python main.py logs audit --limit 20
```

## Limpar temporarios com seguranca

```bash
python main.py maintenance clean-temp
python main.py maintenance clean-temp --yes
```

O primeiro comando apenas simula a limpeza. A remocao real exige `--yes` e preserva relatorios, logs, projetos, sessoes e dados persistentes.
