# SentinelScan Elite CLI

SentinelScan Elite CLI e uma plataforma modular de linha de comando para auditorias autorizadas, inventario de ativos, organizacao de projetos, sessoes, logs, auditoria, historico e relatorios.

Esta implementacao segue os documentos oficiais em `docs/MASTER_PROMPT.md` e `docs/TECHNICAL_SPECIFICATION.md`, preservando a arquitetura em camadas definida para `app`, `core`, `cli`, `services`, `modules`, `plugins`, `config`, `reports`, `logs`, `data`, `cache` e `tests`.

## Recursos implementados

- Bootstrap com validacao do ambiente, criacao de diretorios e inicializacao controlada.
- CLI com comandos para status, ajuda, configuracoes, projetos, sessoes, modulos, relatorios, plugins, logs e manutencao segura.
- Interface de terminal com estilo cyber/hacker, paineis, tabelas, mensagens coloridas, Rich quando disponivel, menu organizado, ajuda integrada e barra de progresso.
- Instalador assistido para verificar Python, pip, Git, dependencias, estrutura do projeto, Nmap, Nuclei, permissoes e capacidade de execucao.
- Gerenciador de modulos com descoberta automatica, metadados, estados, execucao, eventos e isolamento de falhas.
- Modulos internos `nmap_scan` e `nuclei_scan` para analises autorizadas com confirmacao obrigatoria.
- Modulo `smart_scan` para correlacionar Nmap + Nuclei, selecionar endpoints web relevantes e priorizar risco.
- Baseline defensivo para comparar exposicoes antes/depois, novas portas, servicos removidos, mudancas de versao e achados persistentes.
- Sistema centralizado de configuracao com valores padrao, validacao e persistencia.
- Configuracao YAML segura em `config/sentinelscan.yaml`, com exemplo em `config/sentinelscan.example.yaml`.
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
Modulos   | 5
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
python main.py setup check
python main.py setup tools
python main.py setup wizard
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
python main.py scan smart 127.0.0.1 --authorize
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

## Smart Scan Nmap + Nuclei

O `smart_scan` executa um fluxo autorizado e correlacionado:

1. Valida o alvo ou lista de alvos.
2. Exige confirmacao explicita com `--authorize`.
3. Executa Nmap com perfil seguro.
4. Extrai host, IP, hostnames, status, portas, protocolo, servico, versao, tecnologias e sistema operacional quando disponivel.
5. Seleciona apenas portas e servicos com caracteristica web.
6. Monta endpoints HTTP/HTTPS automaticamente.
7. Executa Nuclei somente nesses endpoints, se o Nuclei estiver instalado.
8. Correlaciona achados com host, porta, servico, tecnologia, template, severidade, evidencia e recomendacao.
9. Gera score de risco priorizado: `Critico`, `Alto`, `Medio`, `Baixo` ou `Informativo`.

Exemplos:

```bash
python main.py scan smart 127.0.0.1 --authorize
python main.py scan smart 192.168.1.10 --profile intermediate --authorize
python main.py scan smart 192.168.1.10 --profile advanced --authorize --extra-confirm
python main.py scan smart 192.168.1.10 --profile custom --ports 80,443 --template exposures/ --authorize --extra-confirm
```

Filtros controlados do Nuclei:

```bash
python main.py scan smart 127.0.0.1 --authorize --tag tech --severity medium --severity high
```

NSE controlado do Nmap:

```bash
python main.py scan smart 127.0.0.1 --profile advanced --nse-profile safe --authorize --extra-confirm
```

Regras de seguranca:

- Nao existe modo stealth, evasao, exploit automatico ou brute force.
- Advanced/custom exigem `--extra-confirm`.
- Nuclei nao roda se nao houver endpoint web relevante.
- Se Nuclei nao estiver instalado, o smart scan continua com Nmap e registra a decisao.
- Todos os subprocessos usam lista de argumentos e `shell=False`.

Relatorios:

```text
reports/<projeto-ou-global>/<ano>/<mes>/<dia>/<sessao-ou-sessionless>/smart-scan/
```

## Baseline Defensivo

O baseline salva um estado conhecido de hosts, portas, servicos, versoes e achados. Depois, compara uma nova execucao para destacar:

- novos servicos;
- servicos removidos;
- mudancas de versao;
- novos achados;
- achados resolvidos;
- achados persistentes.

Criar baseline a partir de um JSON de scan ou relatorio:

```bash
python main.py baseline create lab-interno --data resultado-smart.json
```

Comparar uma nova execucao:

```bash
python main.py baseline compare lab-interno --data resultado-smart-novo.json
```

Os baselines ficam em:

```text
data/baselines/
```

## Configuracao YAML

O SentinelScan carrega `config/default_config.json`, depois aplica uma sobreposicao segura de `config/sentinelscan.yaml` quando o arquivo existir. Se o YAML estiver corrompido, a aplicacao usa padroes seguros e expõe um aviso em `runtime.yaml_warning`.

Arquivos:

```text
config/sentinelscan.yaml
config/sentinelscan.example.yaml
```

A configuracao YAML permite ajustar:

- perfil padrao;
- timeout, concorrencia, rate limit e maximo de alvos;
- portas web usadas pelo smart scan;
- tags, severidades, templates e diretorios do Nuclei;
- perfis e scripts NSE permitidos;
- alertas e baseline.

## Instalador assistido

O instalador assistido verifica o ambiente local antes da primeira execucao ou durante manutencoes. Ele nao executa scans, nao chama Nmap contra alvos, nao chama Nuclei contra alvos e nao instala nada sem confirmacao explicita.

Executar pelo script principal do assistente:

```bash
python scripts/setup_wizard.py
```

Executar apenas em modo verificacao:

```bash
python scripts/setup_wizard.py --check-only
```

Executar pela CLI:

```bash
python main.py setup check
python main.py setup tools
python main.py setup wizard
```

O assistente verifica:

- Python instalado e versao minima do projeto.
- pip disponivel via `python -m pip --version`.
- Git disponivel via `git --version`.
- Existencia de `requirements.txt`.
- Dependencias Python instaladas e consistentes.
- Nmap via `nmap --version`.
- Nuclei via `nuclei -version`.
- Gerenciador de pacotes disponivel: `apt`, `dnf`, `pacman` ou `yay`.
- Permissao basica de escrita em `reports/setup/`.
- Estrutura de pastas do SentinelScan Elite CLI.
- Arquivos obrigatorios do projeto.
- Possibilidade de executar `python main.py --version`.

Relatorios gerados:

```text
reports/setup/setup_report.txt
reports/setup/setup_report.json
```

Verificar somente Nmap e Nuclei:

```bash
python scripts/check_tools.py
python main.py setup tools
```

Verificar templates do Nuclei sem executar scans:

```bash
python scripts/check_tools.py --templates
python main.py setup tools --templates
```

Instalacao assistida do Nmap:

- Debian, Ubuntu e Kali: `sudo apt update` e `sudo apt install -y nmap`.
- Fedora: `sudo dnf install -y nmap`.
- Arch Linux e Manjaro: `sudo pacman -S nmap`.

Instalacao assistida do Nuclei:

- Quando Go estiver disponivel, o assistente pode usar `go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest`.
- Quando nao houver metodo confiavel, ele mostra instrucao manual e continua sem quebrar.

Instalar ou atualizar dependencias Python:

```bash
python scripts/install_dependencies.py --yes
pip install -r requirements.txt
```

Erros comuns do instalador:

- `Nmap Ausente`: instale Nmap com o comando da sua distribuicao e rode `nmap --version`.
- `Nuclei Ausente`: instale Nuclei, confirme o `PATH` e rode `nuclei -version`.
- `Dependencias Python Precisa de acao manual`: rode `pip install -r requirements.txt`.
- `Permissoes basicas Erro`: revise permissao de escrita na pasta do projeto.
- `Estrutura de pastas Erro`: confira se o repositorio foi clonado completo.

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
- Use `1` para abrir Network Recon Autorizado com Nmap.
- Use `2` para abrir Web Vulnerability Audit com Nuclei.
- Use `3` a `8` para fluxos guiados defensivos de API, TLS, CVE, hardening, logs e OSINT tecnico.
- Use `9` para abrir o Report Center.
- Use `10` para ver perfis de scan e orientacoes de configuracao.
- Use `11` para consultar historico.
- Use `12` para Configuracoes, Verificar ambiente, Instalador assistido e Verificar Nmap/Nuclei.
- Use `13` para listar modulos.
- Use `14` para abrir ajuda de navegacao.
- Use `15` para simular e confirmar limpeza segura de temporarios.
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

A suite usa `pytest` e cobre nucleo, CLI, configuracao, YAML, logs, relatorios, projetos, sessoes, modulos, plugins, utilitarios, erros, integracao, regressao, limpeza segura, Nmap, Nuclei, smart scan, baseline, instalador assistido e smoke tests. A validacao atual consolidou 208 testes automatizados.

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
- `tests/test_smart_scan_service.py`
- `tests/test_baseline.py`
- `tests/test_setup_service.py`
- `tests/test_setup_scripts.py`

Todos os testes usam diretorios temporarios isolados para evitar lixo operacional no repositorio.

## Seguranca e escopo

O projeto foi implementado para fluxos autorizados. Inventario, saude do runtime, resumo de projetos, Nmap, Nuclei, smart scan e baseline foram integrados com validacao de entrada, confirmacao obrigatoria, comandos montados sem `shell=True`, relatorios e historico. Qualquer uso deve ocorrer apenas em ambientes proprios, laboratorios, redes internas ou ativos com autorizacao explicita.

## Documentacao

- `docs/ARCHITECTURE.md`
- `docs/CODING_STANDARDS.md`
- `docs/TESTING_GUIDE.md`
- `docs/ROADMAP.md`
- `docs/USER_GUIDE.md`
- `docs/DEVELOPER_GUIDE.md`
- `docs/PLUGIN_GUIDE.md`
- `docs/MODULE_GUIDE.md`
- `docs/SMART_SCAN_GUIDE.md`
