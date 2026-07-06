# User Guide

## Verificar status

```bash
python main.py status
```

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
python main.py modules run asset_inventory --param input_file=examples/assets.json --report
```

## Gerar relatorio manual

```bash
python main.py reports generate --title "Resumo" --data "{\"status\":\"ok\"}"
```

## Consultar auditoria

```bash
python main.py logs audit --limit 20
```

