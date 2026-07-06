# Changelog

Todas as mudancas relevantes do SentinelScan Elite CLI serao registradas neste arquivo.

## [Nao lancado] - 2026-07-06

### Adicionado

- Interface CLI mais organizada com paineis, ajuda integrada, menu interativo ampliado, barra de progresso e mensagens coloridas quando suportado pelo terminal.
- Exportacao de relatorios nos formatos Markdown, TXT, JSON, CSV e HTML.
- Organizacao automatica de relatorios por projeto, data e sessao.
- Historico interno enriquecido com funcao executada, data/hora, resultado e erro tecnico quando houver.
- Relatorio final da sessao no encerramento do modo interativo, incluindo tempo total, modulos usados, relatorios criados e erros encontrados.
- Servico e comando de limpeza segura de temporarios, com simulacao por padrao e confirmacao explicita via `--yes`.
- Suite ampliada para 153 testes automatizados, cobrindo os novos fluxos de CLI, relatorios, configuracao, historico, limpeza e resumo de sessao.
- Arquivo `requirements.txt` raiz apontando para as dependencias de execucao.

### Melhorado

- Tratamento de erros da CLI com mensagens amigaveis ao usuario e detalhes tecnicos persistidos em logs e historico.
- README com secao completa "Como executar no Linux", comandos por distribuicao, primeira execucao, atualizacao, solucao de problemas, FAQ, desenvolvimento e licenca.
- Guia de testes atualizado com a cobertura dos novos componentes.

### Corrigido

- Saida de status preserva o caminho completo do projeto mesmo quando o painel visual quebra linhas longas.
- Validacao de configuracao agora aceita todos os formatos de relatorio suportados.

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
