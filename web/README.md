# IGFB — Observatório da grandeza

Frontend editorial conectado ao exportador Python do repositório. O site tem
home, ranking bloqueado por homologação, explorador e perfis, comparação de
cobertura, laboratório sintético, almanaque, metodologia e central de pesquisa.

## Executar

Requer Python 3.12+ e Node 24 LTS (mínimo declarado: 22.12).
A partir da raiz do repositório:

```sh
python -m unittest discover -s tests -v
python -m igfb_agent.project_audit
python -m igfb_agent.public_export --output web/public/data
cd web
npm ci
npm run schemas
npm run data:validate
npm test
npm run dev
```

Abra o endereço emitido pelo Vite, com `/igfb/` no caminho. Para produção:

```sh
npm run build
npm run preview
```

O resultado completo fica em `web/dist/`, incluindo `index.html`, fontes locais,
chunks JavaScript, CSS, manifesto de assets, schemas e JSONs. Sirva a pasta em
`/igfb/`. Abrir o HTML via `file://` não reproduz um servidor de produção.
Não existe dependência de `raw.githubusercontent.com` nem de tokens no navegador.

## Testes

```sh
npm test
npm run data:validate
npm run build
npx playwright install --with-deps chromium
npm run test:e2e
```

Playwright verifica desktop e Pixel 7 emulado, estados de rede, filtros,
comparação, sliders por teclado, restauração e acessibilidade via axe. Screenshots
e relatório ficam em `test-results/`. Em ambiente gerenciado de prévia, o servidor
é fornecido pelo host; o runner não deve tentar iniciá-lo novamente. Teste móvel
emulado não substitui medição em um aparelho físico.

## Contrato e atualização

`src/lib/contracts.ts` centraliza os schemas Zod e tipos TypeScript. `npm run
schemas` deriva JSON Schema; não mantenha cópias manuais divergentes.

O exportador v2 produz:

- `manifest.json`: schema, commit, geração UTC, recorte, auditoria, disponibilidade,
  digest do conjunto e paths/hashes de cada dataset.
- `project-status.json`, `coverage.json`, `methodology.json`, `review-queue.json`,
  `ranking.json`, `clubs.json`, `editions.json`, `sources.json`, `research-backlog.json`.

Os mesmos documentos são gravados sob `snapshots/<sha256>/`. O manifesto só é
substituído após escrever o snapshot. O frontend busca apenas esses caminhos
relativos, confere cada SHA-256, valida schemas e relações e mantém o snapshot
atual até o visitante aceitar uma atualização. O manifesto é consultado a cada
cinco minutos e ao recuperar foco. Não há API do GitHub por interação.

A geração UTC não representa publicação. `data_published_at` permanece `null`;
a execução de deploy do GitHub é a evidência de publicação. O horário de build
é gerado separadamente pelo Vite. O rodapé distingue as duas informações.

`null` em títulos, participações, quedas e pontos significa indisponível, jamais
zero. A estimativa legada de 38% não alimenta barra de progresso atual.
As contagens de pistas têm denominador explícito de 55 temporadas da Série A.

## Publicação, desligada por padrão

O workflow `igfb-web.yml` valida Python, auditoria, exportação, schemas, relações,
testes de frontend, build e Playwright. Só então disponibiliza os artefatos
`igfb-web-dist` e `igfb-web-test-results`. O deploy fica condicionado à variável
`IGFB_PAGES_ENABLED=true`, em eventos da `main`, nunca em pull requests.

Após revisar e autorizar expressamente a publicação:

1. Fazer merge da branch revisada.
2. Em Settings → Pages, escolher GitHub Actions como origem.
3. Configurar proteção/revisor no environment `github-pages`, se desejado.
4. Definir a variável de repositório `IGFB_PAGES_ENABLED` como `true`.
5. Executar o workflow manualmente na `main` para a primeira publicação.

URL preparada: `https://samuelbarrosmacedo.github.io/igfb/`.
HashRouter preserva refresh e links internos sem exigir fallback de servidor.

Alterações relevantes disparam nova compilação. `workflow_run` também observa a
coleta experimental: commits feitos com `GITHUB_TOKEN` não disparam `push` em
outro workflow. Apenas execuções bem-sucedidas da coleta na `main` podem iniciar
esse caminho. O workflow de coleta original não foi modificado.

Falhas deixam a última versão do Pages intacta. Para rollback, reverter o commit
na `main` e executar o workflow com validações; desativar a variável bloqueia
novas publicações sem remover a versão existente.

## Laboratório e limites históricos

O laboratório usa três equipes fictícias isoladas dos IDs reais, contagens
sintéticas visíveis e pesos exportados do Python. O usuário pode ajustar todos
os pesos, ver contribuição por critério, guardar um cenário em memória e
restaurar o modelo. Fechar a página elimina os ajustes. Empates usam ranking por
competição (1, 1, 3), sem desempate histórico inventado.

Os exemplos de Jain, padronização e logística são didáticos, independentes e
não representam o índice composto final. O comparador real compara cobertura,
nunca transforma quantidade de notícias em grandeza.

A versão atual mantém o ranking real bloqueado por design. O repositório ainda
não possui ledger histórico homologado, população final/calibração do índice ou
autorização expressa para classificação. Novos aprovados exigem reconciliação e
uma evolução auditada do contrato; o exportador falha fechado até isso ocorrer.
Ver `docs/WEB_AUDIT.md` e `docs/WEB_VALIDATION.md`.

## Bibliotecas efetivamente usadas

| Biblioteca | Uso |
|---|---|
| React, TypeScript, Vite | Componentes tipados e produção estática |
| Tailwind CSS | Base CSS e tokens de design; estética editorial em CSS próprio |
| Radix Dialog, Select, Slider | Foco, teclado, overlays e controles acessíveis |
| Lucide React | Ícones funcionais |
| TanStack Query | Snapshot, cache, falhas e atualização opcional |
| TanStack Table 8 | Tabelas ordenáveis e células acessíveis |
| Zod 4 | Validação em build/runtime e geração de JSON Schema |
| React Router | Rotas por hash compatíveis com Pages |
| Apache ECharts | Gráfico de contribuições sintéticas, carregado sob demanda |
| React Markdown, remark-gfm | Protocolos reais sem permitir HTML bruto |
| Fontsource | Fontes locais OFL; licenças em `public/assets/licenses/` |
| Vitest, Testing Library | Contrato, simulação e bloqueio de ranking |
| Playwright, axe-core | Testes de interface e acessibilidade |
| tsx, Prettier | Scripts TypeScript e formatação do código |

Versões exatas e integridade de instalação: `package.json` e `package-lock.json`.
Sem Recharts duplicado, sem Motion desnecessário e sem biblioteca de escudos.


## Catálogos e contrato v3

Consulte [cadastro, estados, migração e reversão](../docs/OBSERVATORY_CATALOG.md) e [auditoria desta evolução](../docs/WEB_EVOLUTION_AUDIT.md). Nenhuma dependência de runtime nova foi necessária: as páginas reutilizam React, Zod, Radix, TanStack Table/Query e React Router já instalados. O novo catálogo não depende de APIs esportivas pagas.
