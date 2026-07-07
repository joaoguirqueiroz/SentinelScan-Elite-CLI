# Changelog

Todas as mudancas relevantes do SentinelScan Elite CLI serao registradas neste arquivo.

## [Nao lancado] - 2026-07-06

### Adicionado

- Interface CLI mais organizada com paineis, ajuda integrada, menu interativo ampliado, barra de progresso e mensagens coloridas quando suportado pelo terminal.
- Dashboard inicial em estilo cyber/hacker com logo ASCII, slogan, autor, status, usuario, sistema operacional, IP local, CPU, RAM e aviso etico.
- Integracao do Nmap como modulo interno `nmap_scan`, com perfis `quick`, `basic`, `services`, `ports` e `custom`.
- Integracao do Nuclei como modulo interno `nuclei_scan`, com perfis `basic`, `technologies`, `exposure`, `low-medium`, `high` e `custom`.
- Comandos `scan nmap` e `scan nuclei` com confirmacao obrigatoria de autorizacao e confirmacao extra para perfis avancados/personalizados.
- Modulo `smart_scan` para correlacionar descoberta Nmap, endpoints web selecionados e achados Nuclei.
- Comando `scan smart` com perfis `basic`, `intermediate`, `advanced` e `custom`.
- Servico `SmartScanService` para selecao inteligente de endpoints web, decisoes rastreaveis, correlacao e score de risco.
- Servico `BaselineService` e comandos `baseline create` / `baseline compare` para baseline defensivo de exposicoes.
- Configuracao YAML segura em `config/sentinelscan.yaml` e exemplo em `config/sentinelscan.example.yaml`.
- Suporte controlado a NSE do Nmap com perfis/scripts permitidos.
- Filtros adicionais de Nuclei por tags, severidades, templates e diretorios de templates.
- Exportacao de relatorios nos formatos Markdown, TXT, JSON, CSV e HTML.
- Organizacao automatica de relatorios por projeto, data, sessao e ferramenta (`nmap`/`nuclei`).
- Historico interno enriquecido com funcao executada, data/hora, resultado e erro tecnico quando houver.
- Relatorio final da sessao no encerramento do modo interativo, incluindo tempo total, modulos usados, relatorios criados e erros encontrados.
- Servico e comando de limpeza segura de temporarios, com simulacao por padrao e confirmacao explicita via `--yes`.
- Instalador assistido com verificacao de Python, pip, Git, dependencias, estrutura de pastas, arquivos obrigatorios, permissoes, Nmap e Nuclei.
- Scripts auxiliares `scripts/setup_wizard.py`, `scripts/check_tools.py`, `scripts/install_dependencies.py`, `scripts/setup_report.py` e `scripts/__init__.py`.
- Comandos `setup check`, `setup tools` e `setup wizard` para verificar ambiente, ferramentas e abrir o assistente pela CLI.
- Relatorios de setup em `reports/setup/setup_report.txt` e `reports/setup/setup_report.json`.
- Submenu de configuracoes com `Verificar ambiente`, `Instalador assistido` e `Verificar Nmap/Nuclei`.
- Documento `docs/FUNCTIONAL_AUDIT.md` com matriz funcional opcao por opcao.
- Suite ampliada para 208 testes automatizados, cobrindo os novos fluxos de CLI, YAML, relatorios, configuracao, historico, limpeza, Nmap, Nuclei, smart scan, baseline, instalador assistido, scripts e resumo de sessao.
- Arquivo `requirements.txt` raiz apontando para as dependencias de execucao.
- Dependencia `rich` para experiencia visual profissional em terminais compativeis, com fallback ASCII.

### Melhorado

- Tratamento de erros da CLI com mensagens amigaveis ao usuario e detalhes tecnicos persistidos em logs e historico.
- Tratamento de erros para Nmap/Nuclei ausentes, alvos invalidos, timeout, saida vazia, parsing XML/JSONL e templates/configuracoes invalidas.
- Parser Nmap enriquecido com hostnames, IP, sistema operacional, produto, versao e tecnologias quando disponiveis no XML.
- Priorizacao de risco combinando severidade, endpoint correlacionado, servico, versao e evidencia.
- README com secao completa "Como executar no Linux", comandos por distribuicao, primeira execucao, atualizacao, solucao de problemas, FAQ, desenvolvimento e licenca.
- README com secoes dedicadas ao uso de Nmap e Nuclei no SentinelScan Elite CLI.
- README com secoes para Smart Scan, Baseline Defensivo e Configuracao YAML.
- README com secao "Instalador assistido", incluindo execucao, verificacoes, Nmap, Nuclei, relatorios e erros comuns.
- Guia de testes atualizado com a cobertura dos novos componentes.
- Navegacao interativa revisada para substituir telas marcadas como desenvolvimento por fluxos guiados defensivos.

### Corrigido

- Banner inicial removeu a linha hexadecimal de autor, mantendo a apresentacao profissional da CLI.
- Saida de status preserva o caminho completo do projeto mesmo quando o painel visual quebra linhas longas.
- Validacao de configuracao agora aceita todos os formatos de relatorio suportados.
- Opcao "Listar modulos" agora usa renderizacao dedicada, mostra Nmap/Nuclei, informa estado/categoria/versao e exibe mensagem amigavel quando nao ha modulos carregados.
- Opcoes `4`, `5`, `6`, `7`, `8` e `10` do menu interativo deixaram de cair como invalidas e agora exibem status funcional claro.
- Opcoes `3`, `4`, `5`, `6`, `7`, `8` e `10` agora exibem fluxos guiados seguros em vez de mensagens de desenvolvimento.
- Fluxo interativo de limpeza agora mostra aviso, simula, pede confirmacao e permite cancelar sem apagar arquivos.
- Fluxo interativo de relatorios agora abre o Report Center, lista relatorios e permite gerar relatorio manual com validacao JSON.

## [1.0.0] - 2026-07-06

### Adicionado

- Estrutura completa do repositorio conforme a especificacao tecnica.
- Nucleo da aplicacao com bootstrap, contexto, eventos, seguranca e ciclo de vida.
- Interface CLI com comandos para status, configuracoes, projetos, sessoes, modulos, relatorios, plugins e auditoria.
- Gerenciador de modulos com descoberta automatica, validacao, estados, execucao e isolamento de falhas.
- Sistema centralizado de configuracao com validacao e persistencia em JSON.
- Logs rotativos e auditoria estruturada em JSONL.
- Gerenciamento de projetos e sessoes com catalogo, historico e arquivos por projeto.
- Sistema de relatorios em Markdown e JSON.
- Sistema de plugins com manifestos e plugin de referencia.
- Modulos internos `asset_inventory`, `system_health` e `project_summary`.
- Testes unitarios e de integracao.
- Documentacao operacional, tecnica e de contribuicao.
- Suite ampliada com mais de 100 testes automatizados cobrindo core, CLI, configuracao, logs, relatorios, projetos, sessoes, modulos, plugins, utilitarios, erros, integracao, regressao e smoke.
- Segunda rodada de validacao da suite, removendo teste/helper redundante, cobrindo entradas principais, smoke script, lifecycle defensivo, plugins duplicados/incompativeis, metadados inconsistentes e falhas de loader.

### Observacoes

- A especificacao descreve uma plataforma expansivel; esta versao entrega a base funcional completa para evolucao incremental.
- Modulos de auditoria intrusiva nao foram adicionados nesta versao inicial; o foco e seguranca operacional, inventario informado e extensibilidade.
- Configuracoes corrompidas, niveis de log invalidos e plugins incompativeis agora possuem comportamento seguro coberto por testes de regressao.
- A validacao daquela rodada registrou 136 testes aprovados e 100% de cobertura nos pacotes da aplicacao.
