# Alimentar o observatório

O catálogo canônico é `config/observatory.json` (versão 1). O contrato público é v3, gerado pelo Python. Não edite JSONs de `web/public/data` manualmente. Nenhum componente React específico é necessário para um novo registro compatível.

## Como cadastrar

1. **Fonte:** adicione em `sources` um ID estável, URL HTTPS, editor, nota e data da consulta (ou `null`, se ainda não conferida). A fonte é uma referência, não uma homologação.
2. **Clube:** adicione em `clubs` um ID, nome popular e campos de identidade. Nome oficial, sigla, cidade, estado e escudo desconhecidos são `null`; cores desconhecidas são `[]`. Associe `identity_source_ids`. O clube aparece em Clubes, ganha dossiê e pode ser comparado mesmo sem pistas de campeões.
3. **Competição:** adicione identidade independente em `competitions`. `scoring_category` referencia uma categoria existente do modelo, ou `null` para torneios ainda sem regra. Não crie uma categoria fictícia para conseguir pontuar. Estaduais exigem estado e federação. Copa CONMEBOL e Mercosul têm IDs distintos apesar de compartilharem categoria experimental.
4. **Edição:** adicione em `editions` ID único, `competition_id`, ano, rótulo, formato, estado, participantes e fontes. Não gere edições anuais automaticamente: periodicidade irregular, cancelamentos e mudanças de formato impedem essa inferência. O ano atual é obtido em America/Sao_Paulo pelo exportador, não em constantes React. A atualização diária mantém a virada do calendário.
5. **Informação esportiva:** adicione em `records` um registro `result`, `match`, `standing` ou `statistic`. Campos não aplicáveis são `null`. Informe clubes, edição, fontes, rótulo, fase/grupo se houver, valor/unidade ou placar, atualização com fuso, revisão e justificativa. Um registro de classificação representa uma métrica por clube/grupo; não presume regras universais de desempate. Partidas eliminatórias usam `phase` para identificar fase e confronto. IDs permanecem estáveis nas correções; incremente `revision`, explique em `revision_note` e preserve o histórico no Git.
6. **Escudo:** obtenha arquivo com procedência e condições de uso verificáveis. Salve em `web/public/assets/identities/`, preferencialmente com hash no nome. No campo `crest`, informe caminho relativo a `web/public`, SHA-256, URL da origem, licença/classificação, atribuição e nota de uso. Calcule o hash dos bytes reais, por exemplo `sha256sum web/public/assets/identities/arquivo.svg`. SVGs ativos ou com referências externas são recusados. Use `null` quando não houver recurso apropriado. A mesma estrutura atende competições. O componente comum troca imagens inválidas por identificação tipográfica.

O schema completo, incluindo todos os campos obrigatórios, fica em `web/public/schemas/catalog-input.json`, gerado de `web/src/lib/observatory-contract.ts`. Copie a estrutura de um registro do mesmo tipo e preserve campos desconhecidos como `null`. Exemplos sintéticos completos ficam apenas nos testes, nunca no catálogo público.

## Estados distintos

| Edição | Significado |
|---|---|
| research | Estado esportivo ainda não confirmado no cadastro |
| scheduled | Programação documentada |
| ongoing | Em andamento, com fonte |
| finished | Encerramento documentado |
| cancelled | Cancelamento documentado |

| Registro | Significado |
|---|---|
| collected | Informação coletada |
| in_review | Candidato em revisão |
| disputed | Informação contestada |
| provisional | Resultado provisório |
| official_final | Resultado oficial encerrado; ainda não é homologação IGFB |

`homologated` não é um estado aceito no catálogo editorial. A aprovação usa a trilha existente de `decisions.materialize_approved`, com revisor, justificativa, evidência e verificação dos bytes. A incorporação ao cálculo exige essa etapa, o catálogo de edições do núcleo e decisão explícita sobre recorte/metodologia; um campo booleano no JSON público nunca concede aprovação. O ranking continua bloqueado e vazio nesta fase. A expansão do observatório **não** amplia silenciosamente o recorte matemático de 1971–2025.

## Validar e publicar

```bash
python -m unittest discover -s tests -q
python -m igfb_agent.public_export
cd web
npm ci
npm run schemas
npm run data:validate
npm test
npm run build
npx playwright install chromium
npm run test:e2e
```

O workflow publica somente após os testes e validações. O deploy confere a origem e os hashes do snapshot servido. Publicação automática não coleta placares e não homologa resultados. Falhas anteriores ao deploy preservam o site anterior; falhas posteriores são registradas na execução.

## Migração v2 → v3 e recuperação

A migração é explícita: `schema_version` passa para 3; `clubs.json` ganha identidade independente; `observatory.json` acrescenta catálogo de competições, edições esportivas, fontes e registros. Os datasets históricos continuam com sua semântica e recorte anteriores. Novos IDs não alteram o schema; novos tipos/campos incompatíveis exigem uma nova versão, migração e testes.

Frontend e datasets viajam no mesmo artefato. Cada manifesto referencia arquivos por hash em um diretório de snapshot. O navegador só aceita todos os datasets validados e com relações íntegras; não mistura publicações. Uma sessão antiga pode continuar com o snapshot já carregado; recarregar é necessário após migração incompatível de contrato. Dentro da mesma versão, a interface consulta o manifesto a cada cinco minutos e oferece atualização.

Para reverter, use um commit de reversão do PR e execute novamente o workflow. O artefato `igfb-web-dist` é preservado por 30 dias; relatórios de teste, por 14 dias. Não redefina `main` nem apague o histórico para reverter.

## Conteúdo disponível nesta evolução

As pistas históricas existentes são exibidas como afirmações candidatas. O Carioca tem identidade estadual e edição de 2026 em pesquisa, a partir de anúncio da FERJ; o anúncio não foi usado para presumir campeão, classificação atual ou encerramento. Madureira comprova o cadastro de um clube fora da lista de campeões das pistas. Flamengo e Botafogo têm arquivos SVG com classificação PD-textlogo declarada pelo Wikimedia Commons, hashes e atribuição; demais clubes conservam fallback até cadastro de recursos apropriados. Os símbolos continuam pertencendo aos respectivos clubes, sem endosso ao IGFB.
