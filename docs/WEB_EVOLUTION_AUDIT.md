# Auditoria da evolução — 25/11/2026

## Estado inicial observado

Produção consultada no navegador: home e menus Ranking, Clubes, Comparador, Laboratório, Linha do tempo, Metodologia e Pesquisa. Busca por Flamengo, abertura do dossiê e registro documental, ativação e restauração do laboratório exercitados. Capturas da interface confirmaram a identidade editorial verde/grafite, tipografia condensada e estados de pesquisa. Não há declaração de conformidade integral WCAG por inspeção visual.

O snapshot observado inicialmente era d46bc1e; na retomada, produção já mostrava 49d3d11, enquanto a main havia avançado para 7a16493. Isso registra momentos diferentes, não prova mistura de snapshots. O carregamento funcionou nas páginas consultadas. A verificação automatizada de todos os hashes da nova publicação faz parte da entrega.

## Problemas confirmados no código

- Catálogo de clubes derivado exclusivamente das pistas; escudos forçados a null.
- Calendário público restrito a 55 edições do Brasileiro. Filtro oferecia competições sem calendário correspondente.
- Ausência de competição/edição/temporada atual como páginas próprias.
- Prefixo fixo sobre 1987 na metodologia e texto fixo na linha do tempo divergiam da nova configuração provisória.
- Marcações de conferência declaradas apresentadas como páginas conferidas; inventário de bytes vazio não comprova essa conferência.
- Workflow sem conferência HTTP posterior ao deploy e sem virada diária da temporada.

## Decisões

Preservar home, paleta, tipografia, componentes Radix/TanStack, laboratório sintético e bloqueio do ranking. Ampliar por contrato v3, catálogo independente e páginas reutilizáveis. Preservar a configuração metodológica atual do repositório; expor sua convenção provisória sem aprovar resultados. Nenhuma alteração no núcleo de pontuação, decisões ou pesos.

Não há dados esportivos atuais suficientes para fabricar tabelas ou placares. Estados vazios são parte correta da interface até o cadastro documental. A validação de extensibilidade usa fixtures isoladas e não altera a base pública.

## Validação executada

Commit de implementação `ed11a192d479cb5cde959f05b4108a7244825c01`, PR #2.
Execução [45673811691](https://github.com/samuelbarrosmacedo/igfb/actions/runs/45673811691), job `validate-build` 139415870473: concluída com sucesso em 25/11/2026. 161 testes Python, 20 testes Vitest e 16 testes Playwright (8 cenários em desktop e mobile) passaram. Schemas gerados sem divergência, dez datasets v3 validados, build concluído. A execução de CI do núcleo [45673811677](https://github.com/samuelbarrosmacedo/igfb/actions/runs/45673811677) também passou.

Os E2E incluem axe nas rotas principais, laboratório ativo e edição sintética; não houve violações nos conjuntos WCAG 2 A/AA e 2.1 AA examinados. Isso não equivale a certificação de acessibilidade ou medição em aparelho físico. Capturas desktop/mobile estão no artefato `igfb-web-test-results` da execução. O ambiente local não conseguiu instalar o Chromium do Playwright (HTTP 403); a execução completa ocorreu no runner GitHub.

| Critério de expansão | Evidência automatizada |
|---|---|
| Nova temporada e 2026 → 2027 | Python, Vitest e Playwright com relógio/dataset isolados |
| Nova competição e nova edição | Catálogo sintético; página genérica testada |
| Novo clube independente de pistas | Vitest e navegação Playwright |
| Inclusão/atualização de escudo | Vitest troca de caminho e recuperação de fallback |
| Temporada em andamento e encerramento | Fixture ongoing → finished; resultado official_final sem homologação |
| Correção de resultado | Revisão incrementada, hash alterado, UI atualizada |
| Imagem ausente ou inválida | Vitest e interceptação de imagem no Playwright |
| Dados incompletos | null preservado; interface mostra ausência de valor |
| Falha no dataset | 503, estado de erro e recuperação sem snapshot parcial |
| Nova publicação | Novo manifesto, aviso e atualização atômica |
| Estadual com identidade própria | Jurisdição/federação validadas e rota sintética |
| Rejeição de resultados inelegíveis | Testes do núcleo: pré-1971, 2026, Taça Brasil, Robertão e 1937 |

## Integração e publicação verificadas — 25/11/2026

PR #2 integrado em `90134764ad0408dfbb3baebbb441596403962ffd`, preservando as alterações concorrentes sobre 1987. A integração passou em 162 testes Python, 21 Vitest e 16 Playwright no [run 45719459436](https://github.com/samuelbarrosmacedo/igfb/actions/runs/45719459436). Build e publicação da main confirmados no [run 45719719686](https://github.com/samuelbarrosmacedo/igfb/actions/runs/45719719686).

O job de publicação conferiu os dez datasets servidos por HTTP contra o manifesto do artefato aprovado, incluindo commit, versão e SHA-256. Snapshot `f5bc91d55a39f2896fd66a3f2565875af306b18bbea7fe800ffa92aca0bbc4d3`.

Inspeção manual em navegador de produção: home, temporada 2026, edição do Carioca e suas fontes, catálogo e busca de clubes, perfil/escudo local do Flamengo, convenção de 1987, catálogo de competições e ranking bloqueado. Rodapé confirmou origem `9013476`; imagem SVG carregou com dimensões válidas. Layout desktop preservado. Desktop e mobile foram examinados automaticamente por Playwright/axe no CI; não houve teste em aparelho Android físico nem medição de Core Web Vitals.

A inspeção identificou glifos de setas ausentes nos links do catálogo: substituídos por SVG Lucide, dependência já existente. Também corrigida a concordância de uma edição cadastrada. Esses ajustes visuais seguem o mesmo pipeline.

 Pesquisa histórica, homologações, resultados esportivos atuais e demais escudos continuam dependendo de cadastro documental; não foram fabricados para completar a interface.
