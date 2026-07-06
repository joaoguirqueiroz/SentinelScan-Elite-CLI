# SentinelScan Elite CLI

SentinelScan Elite CLI e uma plataforma modular de linha de comando para auditorias autorizadas, inventario de ativos, organizacao de projetos, sessoes, logs, auditoria, historico e relatorios.

Esta implementacao segue os documentos oficiais em `docs/MASTER_PROMPT.md` e `docs/TECHNICAL_SPECIFICATION.md`, preservando a arquitetura em camadas definida para `app`, `core`, `cli`, `services`, `modules`, `plugins`, `config`, `reports`, `logs`, `data`, `cache` e `tests`.

## Recursos implementados

- Bootstrap com validacao do ambiente, criacao de diretorios e inicializacao controlada.
- CLI com comandos para status, ajuda, configuracoes, projetos, sessoes, modulos, relatorios, plugins, logs e manutencao segura.
- Interface de terminal com estilo cyber/hacker, paineis, tabelas, mensagens coloridas, Rich quando disponivel, menu organizado, ajuda integrada e barra de progresso.
- Gerenciador de modulos com descoberta automatica, metadados, estados, execucao, eventos e isolamento de falhas.
- Modulos internos `nmap_scan` e `nuclei_scan` para analises autorizadas com confirmacao obrigatoria.
- Sistema centralizado de configuracao com valores padrao, validacao e persistencia.
- Logs rotativos, trilha de auditoria estruturada em JSONL e historico interno de acoes.
- Gerenciamento de projetos e sessoes com catalogo, historico e integridade de arquivos.
- Gerador de relatorios em Markdown, TXT, JSON, CSV e HTML com metadados padronizados.
- Organizacao automatica de relatorios por projeto, data e sessao.
- Sistema de plugins com manifestos, validacao, ciclo de vida e plugin de referencia.
- Limpeza segura de arquivos temporarios e cache sem apagar relatorios, logs ou dados persistentes.
- Testes automatizados unitarios, funcionais, de integracao, regressao e smoke.

## Exemplo visual do terminal

```text
+--------------------------------------------------------------------------------------+
| SentinelScan Elite CLI v1.0.0                                                        |
+--------------------------------------------------------------------------------------+
| Plataforma modular para auditorias autorizadas, inventario e relatorios.             |
| Use 'sentinelscan help' para ver navegacao, atalhos e comandos.                      |
+--------------------------------------------------------------------------------------+

metric    | value
----------+-----------------------
Aplicacao | SentinelScan Elite CLI
Versao    | 1.0.0
Modulos   | 3
Plugins   | 1
Projetos  | 0
```

## Instalacao rapida

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Para desenvolvimento e testes:

```bash
pip install -r requirements/dev.txt
```

## Comandos principais

```bash
python main.py status
python main.py help
python main.py interactive
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
python main.py modules run system_health --report --report-format html
python main.py modules list
python main.py scan nmap 127.0.0.1 --authorize
python main.py scan nuclei http://localhost --authorize
```

Gerar relatorio manual:

```bash
python main.py reports generate --title "Resumo" --format json --data "{\"status\":\"ok\"}"
python main.py reports generate --title "Resumo HTML" --format html --data "{\"status\":\"ok\"}"
```

Consultar auditoria:

```bash
python main.py logs audit --limit 10
```

Limpar arquivos temporarios com seguranca:

```bash
python main.py maintenance clean-temp
python main.py maintenance clean-temp --yes
```

O primeiro comando apenas mostra uma simulacao. A limpeza real exige `--yes` e remove somente conteudo descartavel do cache.

## Uso do Nmap no SentinelScan Elite CLI

O modulo `nmap_scan` integra o Nmap ao sistema de modulos do SentinelScan Elite CLI. Ele foi criado para reconhecimento de rede somente em ambientes proprios, redes internas, laboratorios ou ativos com autorizacao explicita.

Aviso obrigatorio: antes de executar qualquer analise, confirme que voce possui autorizacao para analisar o alvo. Sem essa confirmacao, o modulo cancela a operacao e nao executa o Nmap.

Instalar Nmap no Linux:

Debian, Ubuntu e Kali:

```bash
sudo apt update
sudo apt install -y nmap
```

Fedora:

```bash
sudo dnf install -y nmap
```

Arch Linux e Manjaro:

```bash
sudo pacman -S nmap
```

Verificar instalacao:

```bash
nmap --version
```

Acessar pela CLI:

```bash
python main.py scan nmap 127.0.0.1 --authorize
```

Perfis disponiveis:

- `quick`: verificacao rapida com opcoes leves.
- `basic`: perfil padrao seguro.
- `services`: identifica servicos com `-sV --version-light`.
- `ports`: permite informar portas com `--ports 80,443`.
- `custom`: permite apenas flags controladas e exige `--extra-confirm`.

Exemplos:

```bash
python main.py scan nmap 127.0.0.1 --profile quick --authorize
python main.py scan nmap 192.168.1.10 --profile ports --ports 22,80,443 --authorize
python main.py scan nmap localhost --profile custom --custom-flag -sV --authorize --extra-confirm
```

O modulo salva a saida bruta em TXT e XML, interpreta o XML e extrai host, status, portas, protocolo, estado, servico e versao quando disponivel. Os relatorios profissionais sao gerados em TXT, JSON, CSV e HTML.

Relatorios do Nmap:

```text
reports/<projeto-ou-global>/<ano>/<mes>/<dia>/<sessao-ou-sessionless>/nmap/
```

Erros comuns:

- `nmap: command not found`: instale Nmap com o gerenciador de pacotes da sua distribuicao.
- Alvo invalido: use IP, dominio, `localhost` ou faixa local privada em CIDR.
- Timeout: aumente `--timeout` com cuidado.
- Erro ao interpretar XML: verifique se a execucao gerou saida XML valida; detalhes tecnicos ficam em `logs/`.

## Uso do Nuclei no SentinelScan Elite CLI

O modulo `nuclei_scan` integra o Nuclei ao sistema de modulos do SentinelScan Elite CLI. Ele deve ser usado somente para auditoria web autorizada em ativos proprios, laboratorios, redes internas ou ambientes com permissao explicita.

Sem `--authorize`, o modulo cancela a execucao. Perfis de maior impacto, como `high` e `custom`, tambem exigem `--extra-confirm`.

Instalar Nuclei no Linux:

Debian, Ubuntu, Kali, Fedora, Arch e Manjaro podem usar o binario oficial do projeto Nuclei ou o gerenciador de pacotes quando disponivel. Uma forma comum e instalar via Go:

```bash
go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
```

Verifique se o binario esta no `PATH` e confirme:

```bash
nuclei -version
```

Acessar pela CLI:

```bash
python main.py scan nuclei http://localhost --authorize
```

Perfis disponiveis:

- `basic`: perfil padrao seguro.
- `technologies`: usa tags para identificacao de tecnologias.
- `exposure`: procura exposicoes comuns e configuracoes indevidas.
- `low-medium`: limita severidade a baixa e media.
- `high`: usa severidade alta/critica e exige confirmacao extra.
- `custom`: permite templates controlados com `--template` e exige confirmacao extra.

Exemplos:

```bash
python main.py scan nuclei http://localhost --profile basic --authorize
python main.py scan nuclei http://localhost https://127.0.0.1 --profile low-medium --authorize
python main.py scan nuclei http://localhost --profile custom --template exposures/ --authorize --extra-confirm
```

Parametros configuraveis:

```bash
python main.py scan nuclei http://localhost --authorize --timeout 45 --concurrency 3 --rate-limit 10 --max-targets 5
```

O modulo salva a saida estruturada em JSONL, interpreta os achados e extrai alvo, template, nome, severidade, descricao, endpoint e timestamp. Os resultados sao enviados ao sistema de relatorios em TXT, JSON, CSV e HTML.

Relatorios do Nuclei:

```text
reports/<projeto-ou-global>/<ano>/<mes>/<dia>/<sessao-ou-sessionless>/nuclei/
```

Erros comuns:

- `nuclei: command not found`: instale Nuclei e confirme que o binario esta no `PATH`.
- Templates ausentes: atualize ou informe um caminho/tag valido para templates.
- Alvo invalido: use URL HTTP/HTTPS, dominio, IP ou lista controlada de alvos.
- Saida vazia: pode indicar ausencia de achados; verifique o relatorio e logs.
- Erro ao interpretar saida: confirme se a saida esta em JSONL valido.

## Erros comuns adicionais

`python: command not found`:

```bash
python3 --version
sudo apt install -y python3 python3-venv python3-pip
```

`pip: command not found`:

```bash
python -m pip --version
python -m pip install -r requirements.txt
```

`ModuleNotFoundError`:

```bash
source .venv/bin/activate
pip install -r requirements.txt
python main.py status
```

Permissao negada:

```bash
ls -la
python main.py status
```

Dependencias ausentes:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Erro ao gerar relatorio:

- Verifique permissao de escrita em `reports/`.
- Confirme se o formato solicitado e `markdown`, `txt`, `json`, `csv` ou `html`.
- Consulte `logs/application.log` e `logs/audit.jsonl`.

`Listar modulos` nao aparece nada:

```bash
python main.py modules list
python main.py logs audit --limit 20
```

Se a pasta `modules/` estiver vazia, a CLI mostra uma mensagem amigavel. Se houver modulo invalido ou erro de importacao, o gerenciador isola a falha, registra nos logs e continua listando os demais modulos validos.

## Como executar no Linux

As instrucoes abaixo funcionam para Kali Linux, Ubuntu, Debian, Linux Mint, Fedora, Arch Linux, Manjaro, Pop!_OS e outras distribuicoes compativeis com Python 3.

### 1. Requisitos minimos

- Python: 3.10 ou superior.
- Git: necessario para clonar e atualizar o repositorio.
- pip: necessario para instalar dependencias.
- Espaco em disco recomendado: 200 MB livres para o projeto, ambiente virtual, logs e relatorios iniciais.
- Memoria RAM recomendada: 1 GB livre para uso basico; 2 GB ou mais para desenvolvimento e testes.
- Arquitetura suportada: x86_64/amd64 e ARM64/aarch64, desde que a distribuicao tenha Python 3.10+.

Instalar requisitos por familia de distribuicao:

Debian, Ubuntu, Kali, Linux Mint e Pop!_OS:

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git
python3 --version
git --version
python3 -m pip --version
```

Fedora:

```bash
sudo dnf install -y python3 python3-pip git
python3 --version
git --version
python3 -m pip --version
```

Arch Linux e Manjaro:

```bash
sudo pacman -Syu --needed python python-pip git
python --version
git --version
python -m pip --version
```

### 2. Instalacao

Clone o repositorio:

```bash
git clone https://github.com/joaoguirqueiroz/SentinelScan-Elite-CLI.git
```

Entre na pasta do projeto:

```bash
cd SentinelScan-Elite-CLI
```

Crie e ative um ambiente virtual.

Debian, Ubuntu, Kali, Linux Mint, Fedora, Pop!_OS e outras distribuicoes com `python3`:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Arch Linux e Manjaro:

```bash
python -m venv .venv
source .venv/bin/activate
```

Atualize o pip e instale as dependencias:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Verifique se a instalacao foi concluida:

```bash
python main.py status
python main.py help
```

Se os comandos mostrarem o nome `SentinelScan Elite CLI`, os modulos carregados e a tela de ajuda, a instalacao basica esta correta.

### 3. Primeira execucao

Inicie o sistema pelo menu principal:

```bash
python main.py interactive
```

No menu principal:

- Digite o numero da opcao e pressione Enter.
- Use `1` para ver o status.
- Use `2` para listar modulos.
- Use `3` para listar projetos.
- Use `4` para abrir a ajuda de navegacao.
- Use `5` para simular limpeza de temporarios.
- Use `0` para sair corretamente e visualizar o relatorio final da sessao.

Atalhos e comportamento:

- `0`: voltar/sair no menu interativo.
- `Ctrl+C`: cancelar uma entrada ou interromper a acao atual.
- `python main.py help`: abrir a ajuda sem entrar no menu interativo.
- `python main.py modules list`: listar modulos antes de executar.
- `python main.py reports list`: consultar relatorios gerados.

### 4. Atualizacao do projeto

Dentro da pasta do projeto, atualize o codigo:

```bash
git pull
```

Atualize as dependencias novamente:

```bash
pip install -r requirements.txt
```

Para ambiente de desenvolvimento:

```bash
pip install -r requirements/dev.txt
```

Verifique a saude depois da atualizacao:

```bash
python main.py status
python -B -m pytest -p no:cacheprovider
```

### 5. Estrutura do projeto

- `app/`: inicializacao, contexto e ciclo de vida da aplicacao.
- `core/`: contratos, eventos, validadores, seguranca, recursos, modulos e plugins.
- `cli/`: parser, comandos, mensagens, tabelas e componentes visuais do terminal.
- `services/`: configuracao, logs, auditoria, historico, relatorios, projetos, sessoes, armazenamento e limpeza.
- `modules/`: modulos internos carregados pelo gerenciador.
- `plugins/`: plugins e manifestos de extensao.
- `config/`: configuracao padrao.
- `reports/`: relatorios gerados, organizados por projeto, data e sessao.
- `logs/`: logs operacionais e auditoria.
- `data/`: dados persistentes de configuracao, projetos, sessoes e historico.
- `cache/`: arquivos temporarios e descartaveis.
- `tests/`: suite automatizada com testes unitarios, funcionais, integracao, regressao e smoke.
- `docs/`: documentacao oficial e guias tecnicos.
- `examples/`: arquivos e fluxos de exemplo.
- `requirements/`: dependencias de execucao e desenvolvimento.
- `scripts/`: scripts auxiliares.

### 6. Solucao de problemas

Python nao encontrado:

Debian, Ubuntu, Kali, Linux Mint e Pop!_OS:

```bash
sudo apt update
sudo apt install -y python3 python3-venv
python3 --version
```

Fedora:

```bash
sudo dnf install -y python3
python3 --version
```

Arch Linux e Manjaro:

```bash
sudo pacman -Syu --needed python
python --version
```

pip nao encontrado:

Debian, Ubuntu, Kali, Linux Mint e Pop!_OS:

```bash
sudo apt install -y python3-pip
python3 -m pip --version
```

Fedora:

```bash
sudo dnf install -y python3-pip
python3 -m pip --version
```

Arch Linux e Manjaro:

```bash
sudo pacman -Syu --needed python-pip
python -m pip --version
```

Git nao instalado:

```bash
# Debian, Ubuntu, Kali, Linux Mint e Pop!_OS
sudo apt install -y git

# Fedora
sudo dnf install -y git

# Arch Linux e Manjaro
sudo pacman -Syu --needed git
```

`ModuleNotFoundError` ou erro de importacao:

```bash
cd SentinelScan-Elite-CLI
source .venv/bin/activate
pip install -r requirements.txt
python main.py status
```

Se estiver desenvolvendo:

```bash
pip install -r requirements/dev.txt
```

`Permission denied` ao executar comandos:

```bash
pwd
ls -la
chmod +x main.py
python main.py status
```

Nao use `sudo` dentro do ambiente virtual para instalar dependencias do projeto, salvo quando estiver instalando pacotes do sistema com `apt`, `dnf` ou `pacman`.

Dependencias ausentes ou incompativeis:

```bash
source .venv/bin/activate
python -m pip install --upgrade pip
pip install --upgrade -r requirements.txt
```

Problemas de PATH:

```bash
which python
which python3
which pip
python -m pip --version
```

Se `pip` apontar para outro Python, prefira sempre:

```bash
python -m pip install -r requirements.txt
```

### 7. Perguntas Frequentes (FAQ)

Posso executar no Kali Linux?

Sim. Use os comandos da familia Debian/Ubuntu/Kali e execute o sistema apenas em ambientes autorizados.

Preciso instalar dependencias externas?

A execucao principal usa biblioteca padrao do Python. Para testes, instale `requirements/dev.txt`.

Qual comando abre o menu principal?

```bash
python main.py interactive
```

Como gero relatorios?

Use `--report` ao executar um modulo ou `reports generate` para relatorios manuais.

Quais formatos de relatorio existem?

`markdown`, `txt`, `json`, `csv` e `html`.

A limpeza temporaria apaga relatorios?

Nao. A limpeza segura remove somente conteudo descartavel do cache e preserva `reports/`, `logs/`, `data/`, `backups/` e `config/`.

Como saio corretamente?

No menu interativo, digite `0`. A CLI mostra um relatorio final com tempo total, modulos usados, relatorios criados e erros encontrados.

### 8. Desenvolvimento

Prepare o ambiente:

```bash
git clone https://github.com/joaoguirqueiroz/SentinelScan-Elite-CLI.git
cd SentinelScan-Elite-CLI
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements/dev.txt
```

Execute os testes:

```bash
python -B -m pytest -p no:cacheprovider
```

Padroes para contribuir:

- Leia `docs/MASTER_PROMPT.md` e `docs/TECHNICAL_SPECIFICATION.md` antes de alterar componentes importantes.
- Preserve a arquitetura modular.
- Adicione ou atualize testes para cada mudanca relevante.
- Atualize README, guias tecnicos e CHANGELOG quando alterar comportamento.
- Nao adicione fluxos ofensivos, intrusivos ou dependentes de alvos externos sem autorizacao e isolamento adequado.
- Use mocks, fixtures, localhost ou arquivos controlados em testes.

### 9. Licenca

A licenca do projeto esta em `LICENSE`. Leia esse arquivo antes de redistribuir, modificar ou utilizar o projeto em ambientes corporativos.

## Testes

A suite usa `pytest` e cobre nucleo, CLI, configuracao, logs, relatorios, projetos, sessoes, modulos, plugins, utilitarios, erros, integracao, regressao, limpeza segura, Nmap, Nuclei e smoke tests. A validacao atual consolidou 178 testes automatizados.

```bash
pytest
```

Como alternativa equivalente:

```bash
python -m pytest
```

Para rodar sem gerar cache local:

```bash
python -B -m pytest -p no:cacheprovider
```

Com cobertura:

```bash
pytest --cov=. --cov-report=term-missing
```

Arquivos principais da suite:

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
- `tests/test_cleanup.py`
- `tests/test_scanner_service.py`
- `tests/test_scanner_modules.py`

Todos os testes usam diretorios temporarios isolados para evitar lixo operacional no repositorio.

## Seguranca e escopo

O projeto foi implementado para fluxos autorizados. Os modulos incluidos nesta versao inicial focam em inventario informado pelo usuario, saude do runtime e resumo de projetos, evitando operacoes intrusivas ou ofensivas.

## Documentacao

- `docs/ARCHITECTURE.md`
- `docs/CODING_STANDARDS.md`
- `docs/TESTING_GUIDE.md`
- `docs/ROADMAP.md`
- `docs/USER_GUIDE.md`
- `docs/DEVELOPER_GUIDE.md`
- `docs/PLUGIN_GUIDE.md`
- `docs/MODULE_GUIDE.md`
