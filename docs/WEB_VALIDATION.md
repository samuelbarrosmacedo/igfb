# Validação do observatório

## Verificado localmente em 23/11/2026

- Baseline antes das mudanças: 113 testes Python.
- Após ampliar o exportador: 118 testes Python passaram.
- 12 testes Vitest/Testing Library passaram.
- TypeScript e build Vite concluídos sem erros.
- Nove schemas gerados diretamente do contrato Zod.
- Oito datasets validados por schema, SHA-256 e relações cruzadas.
- Navegação desktop e abertura da home inspecionadas na prévia real do navegador.

## Limitação local

O runner Playwright não conseguiu iniciar o servidor no executor gerenciado:
`uv_interface_addresses` retornou erro de permissão. O runner foi ajustado para
não tentar um segundo servidor nesse tipo de ambiente. A suíte completa também
está no GitHub Actions, em Ubuntu, com Chromium e emulação Pixel 7.
A configuração de testes não é tratada como prova de execução. Os resultados
remotos, quando disponíveis, são registrados abaixo.

## Métricas

Build inicial dividido por rotas: entrada JavaScript de aproximadamente 437 kB
(135 kB gzip), gráfico ECharts separado (~475 kB; 162 kB gzip), protocolos Markdown
separados (~168 kB; 51 kB gzip). Esses são tamanhos medidos do build, não Core Web
Vitals. Não há dados de campo suficientes para afirmar LCP, INP ou CLS de usuários
reais, nem teste físico em Galaxy A36. Sem pontuação Lighthouse inventada.

## Estado de entrega

Merge e deploy público não executados. Ranking histórico intencionalmente
bloqueado. A conclusão da interface não significa conclusão da pesquisa.
