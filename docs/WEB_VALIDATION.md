# Validação do observatório

## Verificado localmente em 24/11/2026

- Baseline antes das mudanças: 113 testes Python.
- Após ampliar o exportador e incorporar a pesquisa da main: 149 testes Python passaram.
- 14 testes Vitest/Testing Library passaram.
- TypeScript e build Vite concluídos sem erros.
- Dez schemas gerados diretamente do contrato Zod.
- Nove datasets validados por schema, SHA-256 e relações cruzadas.
- Navegação desktop, perfil, fonte documental e simulação (teclado, guardar e restaurar) inspecionados no navegador.
- Capturas de desktop e Pixel 7 emulado inspecionadas: home, comparação e almanaque.

## Limitação local

O runner Playwright não conseguiu iniciar o servidor no executor gerenciado:
`uv_interface_addresses` retornou erro de permissão. O runner foi ajustado para
não tentar um segundo servidor nesse tipo de ambiente. A suíte completa também
está no GitHub Actions, em Ubuntu, com Chromium e emulação Pixel 7.
No executor atual, o Chromium de teste não está instalado e seu download retornou
HTTP 403. A inspeção interativa usa o navegador disponibilizado pelo ambiente.
O Chromium do sistema também não pôde ser iniciado (`socket: Operation not permitted`).
Essas limitações não foram contornadas. Os testes foram executados no runner do GitHub.

## Validação remota confirmada

Execução [45407003901](https://github.com/samuelbarrosmacedo/igfb/actions/runs/45407003901),
24/11/2026, cabeça `93fe42f4e67c1c1aa95cbf034408cfc7f5da480e`:

- 149 testes Python, auditoria, reconciliação, geração e validação dos nove datasets: sucesso.
- 14 testes frontend, TypeScript e build: sucesso.
- 8 testes Playwright: sucesso em Chromium, desktop e Pixel 7 emulado.
- Rotas, filtros, comparador, falha de rede, laboratório e análise axe WCAG A/AA: sucesso.
- Artefatos `igfb-web-dist`, `igfb-web-test-results` e `github-pages` gerados.
- Job de deploy: **skipped**, como previsto; nenhum site foi publicado.

A primeira execução detectou uma ambiguidade no seletor de status do teste do
laboratório. O seletor passou a usar o nome acessível específico. A inspeção manual
também detectou que a descrição automática do gráfico vinha em inglês e incluía
valores internos NaN; agora é uma descrição explícita em português, acompanhada da
tabela completa. Nenhuma regra axe foi desabilitada.

O Actions testa a combinação do PR com a main. Nesse snapshot, novas pistas já
haviam elevado a cobertura para 45/55 temporadas; a interface acompanhou a base
sem alteração manual de contagens. A documentação registra resultados por execução;
consulte os checks do PR para o estado da cabeça mais recente.

## Métricas

Build inicial dividido por rotas: entrada JavaScript de aproximadamente 439 kB
(136 kB gzip), gráfico ECharts separado (~475 kB; 162 kB gzip), protocolos Markdown
separados (~168 kB; 51 kB gzip). Esses são tamanhos medidos do build, não Core Web
Vitals. Não há dados de campo suficientes para afirmar LCP, INP ou CLS de usuários
reais, nem teste físico em Galaxy A36. Sem pontuação Lighthouse inventada.

## Estado de entrega

Merge e deploy público não executados. Ranking histórico intencionalmente
bloqueado. A conclusão da interface não significa conclusão da pesquisa.
