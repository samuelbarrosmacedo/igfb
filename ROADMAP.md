# ROADMAP — IGFB

Atualizado em 2026-11-24 (segunda ampliação de pistas históricas). Fonte de verdade: código, configuração e evidências versionadas neste repositório. **Não confundir cobertura documental com conclusão do projeto.**

## Painel de métricas

| Indicador | Estado atual | Cálculo e interpretação |
|---|---:|---|
| Recorte brasileiro Série A | 55 temporadas | 1971–2025, inclusive |
| Temporadas com pistas cadastradas | 55/55 = **100%** | Anos distintos em `config/historical_source_leads.json`; não comprova resultados |
| Temporadas sem pistas | **0** | 55 menos 55 |
| Registros de fontes institucionais cadastrados | **26** | Registros de `sources` no arquivo de pistas |
| Afirmações candidatas | **58** | Soma de `claim_years`; não são registros aprovados |
| Resultados homologados | **0** | Sem evidências aprovadas |
| Estimativa histórica de conclusão | **38% (não auditada)** | Valor legado, **não utilizar como progresso real** |
| Progresso global auditado | **indisponível** | Não há denominador nem pesos aprovados para todos os pilares |

Os números documentais devem ser **recalculados** executando `python -m igfb_agent.project_audit` e `python -m igfb_agent.research_backlog`. Nunca aumentar o percentual só porque houve commits. O campo `measured_progress` mede apenas a cobertura de pistas.

## Metas verificáveis

Uma tarefa só é marcada concluída quando o artefato correspondente existe e foi conferido. Marcar teste como aprovado exige execução comprovada, não apenas código de teste.

| ID | Prioridade | Meta / critério de aceite | Situação |
|---|---|---|---|
| M01 | P0 | Recorte 1971–2025 e exclusões expressas no calendário e nas regras | Implementado; validação CI pendente |
| M02 | P0 | Auditoria distingue cobertura medida, progresso legado e homologação | Implementado; validação CI pendente |
| M03 | P0 | Exportação JSON conservadora com manifesto SHA-256 e fila de pesquisa | Implementado; validação CI pendente |
| M04 | P0 | Suíte de testes completa com execução bem-sucedida documentada | **Pendente** |
| M05 | P0 | Fonte oficial localizada para cada uma das 55 temporadas | **55/55 com pistas; localização completa, revisão documental pendente** |
| M06 | P0 | Evidências originais arquivadas com SHA-256 e procedência auditável | Validador implementado; **0 arquivos reais arquivados** |
| M07 | P0 | Resultados esportivos homologados por edição, sem duplicidade e com revisão | **0 homologados** |
| M08 | P1 | Modelo de pesos calibrado e análise de sensibilidade com dados homologados | **Pendente** |
| M09 | P1 | Site responsivo com metodologia, pesquisa, cobertura e estado de homologação | **Pendente** |
| M10 | P1 | Build e publicação verificáveis, acessibilidade e testes de ponta a ponta | **Pendente** |

**Contagem de metas integralmente concluídas e validadas: 0/10.** Isso não significa que o trabalho executado seja zero: três metas estão implementadas, mas dependem de confirmação da CI. O percentual `0/10` é apenas um controle de aceite estrito e **não** é o percentual global do IGFB.

## Entrega incremental recente

- 2026-11-24: `86d9a0f2ac09aefe5669820f1f5fabfadfb9b0ce` sinaliza a referência cbf-santos-2004 como não verificada e de baixa confiança por apontar para notícia de outro clube/ano. Mantida para rastreabilidade, sem valor probatório; existe pista alternativa cbf-santos-112. Releitura confirmou 55 anos, 26 registros e 58 afirmações. Clone local bloqueado por resolução DNS; conector GitHub operacional. Testes Python e arquivamento original não realizados.


- 2026-11-24: commits `65d07d0f7d313a391147a220b346d412f648ace5` e `098a9c9416daf380862c6c813800761c3ca39b9f` integram a reconciliação de evidências à fila de pesquisa e auditoria padrão; relatórios Markdown/CSV passam a consumir a fila reconciliada. Candidatos explicitamente injetados permanecem isolados. Testes Python e CI ainda não comprovados; nenhuma evidência histórica real adicionada. Cobertura 55/55, homologações 0, metas validadas 0/10.


- 2026-11-24: `8eb7ad8fcf5feafe3091ffc68c61461f0ad7aba4` permite injetar inventário e raiz de evidências na exportação pública, preservando os padrões de produção; `7e9edf96b8e46a3cebc16d69d00f5ac890c9c8bb` isola fixtures e acrescenta teste de exportação com arquivo sintético e hash real, sem homologação. Suíte não executada nesta etapa; cobertura de pistas 55/55, arquivos históricos reais 0, homologações 0. Próxima prioridade permanece arquivamento real e execução da CI.


- 2026-11-24: commit `495144e01349496f9d33d29066dcc7321b06b806` fecha as lacunas de 1977 e 1979 com retrospectiva oficial CBF da final de 1977 e perfil de Batista (títulos do Internacional de 1975, 1976 e 1979). Releitura do JSON e validação programática: 55 anos distintos, 26 IDs únicos, 23 URLs distintas, 58 afirmações, nenhum ano fora do recorte. Cobertura de pistas 96,36% → 100%; não equivale à verificação de todos os documentos. Nenhuma homologação, arquivo original ou execução Python comprovada. M05 permanece pendente de revisão documental integral.


- 2026-11-24: commit `d0526e54d1d43fb536ef816e05c8595b3d30c364`: fontes CBF para Bahia 1988, Corinthians 1998–1999, Athletico-PR 2001 e Santos 2002; referência adicional para Santos 2004. Cobertura 48/55 → 53/55; faltam 1977 e 1979. 24 registros e 54 afirmações; sem arquivo original ou homologação. Testes Python e CI pendentes.
- Referência visual indicada pelo usuário: https://www.tiktok.com/@chilenodoscortes/video/7711333263662517522 — acesso falhou; conteúdo e conceito pendentes de inspeção antes de implementação.


- 2026-11-24: commit `c0137a492f8440566b322c88b7d948bd8ffbab09` acrescenta Coritiba 1985, Corinthians 1990 e São Paulo 1991 com textos CBF efetivamente consultados no índice. Cobertura 45/55 → 48/55 (87,27%); 20 registros, 48 afirmações, 7 lacunas: 1977, 1979, 1988, 1998, 1999, 2001 e 2002. Nenhum arquivo original arquivado ou resultado homologado; CI não comprovada.
- Localizada também a RDP 06/2011, que revoga a RDP 02/2011 e reconhece Sport como único campeão de 1987: https://www.cbf.com.br/a-cbf/por-dentro-da-cbf/juridico/a/resolucao-da-presidencia-062011 . Registrar na revisão de 1987, mantendo a convenção própria do IGFB distinta da posição institucional.


- 2026-11-24: commit `ce55a65d4939eaa9eb72283acdbd389fc6b8e4f4` acrescenta 14 temporadas com afirmações explícitas em cinco textos indexados da CBF: Flamengo (1980, 1982, 1983, 1992, 2009, 2019, 2020), Vasco (1997, 2000), Cruzeiro (2013, 2014), Botafogo (1995, 2024), Santos (2004). Excluídos anos pré-1971 e 2026.
- Recontagem JSON: 45/55 (81,82%), antes 31/55 (56,36%); 17 registros; lacunas 1977, 1979, 1985, 1988, 1990, 1991, 1998, 1999, 2001, 2002. Sem bytes originais arquivados, homologação ou execução comprovada da suíte Python.


- 2026-11-24: commit `a1bcea3551dacaac4c7d25eb039090d4a984c8c8` adiciona 11 temporadas com pistas CBF: Fluminense (1984, 2010, 2012), Vasco (1974, 1989), São Paulo (1986, 2006–2008), Guarani (1978), Cruzeiro (2003). Cinco registros novos, quatro URLs distintas novas. Conteúdo consultado via índice de pesquisa; bytes originais não arquivados.
- Recontagem programática do JSON: 31 anos distintos, 31 afirmações, 12 registros, 24 lacunas; cobertura 36,36% → 56,36%. Nenhuma homologação. Suíte Python e CI não comprovadas nesta execução.


- Inventário documental agora exige `source_id` não vazio e `retrieved_at` ISO 8601 com fuso; impede registrar documentos sem origem identificável ou data ambígua.
- Testes atualizados com três cenários negativos: fonte ausente, data inválida e data sem fuso.
- Workflow passa a publicar os relatórios Markdown, CSV e os JSON públicos verificados como artefato `igfb-audit-reports` por 14 dias **apenas após sucesso**.
- **Validação pendente:** commits confirmados, mas sem execução de CI comprovada nesta etapa; não atribuir aceite às metas M01–M04.
- Indicadores de conteúdo permanecem **20/55 (36,36%)**, 35 temporadas sem pistas, 0 arquivos reais e 0 homologações. O progresso global segue sem métrica auditada.


- Implementada reconciliação `igfb_agent/evidence_reconciliation.py` entre documentos SHA-256 verificados e pistas por `source_id`, edição e URL. Documentos não correspondentes são rejeitados.
- `public_export.py` passou a refletir a reconciliação em `coverage.json` e na fila pública de pesquisa, com `verified_archives` e `archived_candidate_count` separados de homologações.
- Cinco testes sintéticos novos e execução do reconciliador adicionada à CI. A execução real da CI ainda precisa ser confirmada.
- Métricas conferidas contra inventário vazio e 20 anos distintos de pistas: **20/55 (36,36%) → 20/55 (36,36%)**; **0 documentos arquivados**; **0 resultados homologados**. Progresso global permanece indisponível.


- Criado `igfb_agent/evidence_inventory.py`: valida arquivo local existente, SHA-256 dos bytes, URL HTTPS, ano e edição canônicos, data de coleta, IDs únicos e impede homologação automática.
- Criado `config/evidence_inventory.json` com inventário **vazio**: não representa evidências existentes.
- Adicionados sete testes de integridade e segurança e etapa de CI para conferir inventário.
- Cobertura de pistas **36,36% → 36,36%**, evidências arquivadas **0 → 0**, homologações **0 → 0**. Meta M06 continua pendente de evidências reais e de execução comprovada dos testes.


- Exportação CSV da fila de pesquisa (`python -m igfb_agent.research_report --format csv --output /tmp/igfb-research-plan.csv`), com 55 linhas, IDs das fontes e prioridades, útil para revisão em planilhas.
- Corrigido teste que exigia 36,36% fixos: agora compara com o valor recalculado e não quebra quando novas fontes forem cadastradas.
- Dois testes para CSV e geração de ambos os formatos no workflow; commits confirmados, mas execução da suíte e CI **ainda não comprovadas**.
- GitHub retornou listas vazias para status e execuções associadas ao commit anterior; isso **não comprova sucesso nem falha** da CI.


- Adicionado `igfb_agent/research_report.py`: transforma a fila de 55 temporadas em relatório Markdown ordenado por prioridade, sem inventar fontes nem aprovações.
- Adicionados testes de formato e recorte; CI configurada para gerar `/tmp/igfb-research-plan.md`.
- Pesquisa externa nesta etapa não encontrou evidência institucional nova suficientemente identificada para cadastro. **Cobertura permanece 20/55 (36,36%)**; nenhuma meta recebeu aceite sem testes executados.

## Próxima fila de execução

1. **P0 — Confirmar CI:** executar `python -m unittest discover -s tests -v`, `python -m igfb_agent.public_export --output /tmp/igfb-public-data` e `verify_public_data`; corrigir qualquer falha antes de declarar verde.
2. **P0 — Pesquisa histórica:** usar `python -m igfb_agent.research_report --output /tmp/igfb-research-plan.md` para priorizar as fontes cadastradas para conferência e arquivamento. Adicionar somente fontes efetivamente identificadas; nunca inventar URLs ou campeões.
3. **P0 — Arquivamento:** guardar bytes da evidência, SHA-256, data, URL e vínculo com a edição, antes de homologar.
4. **P1 — Experiência pública:** iniciar frontend de pesquisa/metodologia com indicação explícita de ranking indisponível.
5. **P1 — Metodologia:** definir denominadores, pesos e critérios de aceite do progresso global, sem misturar métricas incomparáveis.

## Regras permanentes de continuidade

- Inspecionar o repositório e este roadmap antes de mudar código.
- Entregar pelo menos uma melhoria verificável por etapa; preferir pesquisa histórica e produto útil a microcorreções repetitivas.
- Preservar as regras de 1971–2025, a exclusão de 1937/Taça Brasil/Robertão e a convenção metodológica explícita de 1987.
- Não converter pistas em resultados homologados automaticamente.
- Atualizar tarefas, contagens e evidências após cada etapa; registrar commit e resultados dos testes.
- Não afirmar sucesso de testes, deploy ou CI sem observar a execução.


## Conferência documental — 24/11/2026

Commit `9d6868cd1aad7ee3a38717f2f39d6a8fd8db22da`: conferidos os textos indexados da CBF relativos ao Santos em 2002 e 2004; substituída a URL de baixa confiança de 2004 por retrospectiva específica de 15/08/2020. Contagem de temporadas com fonte marcada conferida: 1 → 3 de 55 (a marca anterior de 2025 não foi reconferida). Cobertura de pistas permanece 55/55. Conferência textual não equivale a arquivamento original nem homologação. Próximo lote: conferir fontes restantes e arquivar originais com hashes. Testes Python não executados nesta etapa.

### Palmeiras — conferência de 24/11/2026
Fonte CBF de 26/08/2024 conferida: 1972, 1973, 1993, 1994, 2016, 2018, 2022 e 2023. Registro textual 3/55 → 11/55; pistas 55/55. Commit 36e5a84ea3654feb3672f7e5c808304d5b073915. Sem arquivamento ou homologação; testes Python não executados.

### Flamengo — conferência de 24/11/2026
Texto CBF de 25/02/2021 conferido: 1980, 1982, 1983, 1992, 2009, 2019, 2020; 1987 identificado separadamente como Copa União, sem homologação nesta etapa. Conferência registrada 11/55 → 18/55. Commit 97a2f83a3f9de222955200a77051e1b207f373e3. Sem arquivamento original nem testes Python. Próximo lote: fontes dos campeões restantes, preservando recorte 1971–2025.

### Conferência documental — Corinthians, Cruzeiro e São Paulo (24/11/2026)
Dois textos indexados da CBF efetivamente consultados: 15/11/2017 (Corinthians e São Paulo) e 02/01/2025 (Cruzeiro). Dez temporadas adicionais, 18/55 → 28/55 marcadas conferidas. Commit cffc884245460b42d10fa761d5651f0b78630dfb. Releitura JSON confirmada; registros anteriores não revalidados, testes Python não executados, originais não arquivados. Próximo: 27 temporadas restantes.

### Conferência documental — Grêmio e Fluminense (24/11/2026)
Textos indexados da CBF consultados: Grêmio 15/09/2024 (1981, 1996), Fluminense 21/07/2025 (1984, 2010, 2012). URLs corrigidas para as versões retornadas pela busca. Marcadas 28/55 → 33/55 temporadas; originais não arquivados, registros anteriores não revalidados. Commit 8e4c0caeede38a3d08160e180a5d1060adbd37c0. A RDP 06/2011 também foi localizada e lida: https://www.cbf.com.br/a-cbf/noticias/juridico/a/resolucao-da-presidencia-062011 revoga a RDP 02/2011 e reconhece Sport como único campeão oficial de 1987; manter divergência explícita e não homologar a convenção IGFB como fato oficial. Testes Python pendentes.

### Conferência Atlético-MG e integração web — 24/11/2026
CBF 02/12/2021, texto recuperado e lido, confirma 1971 e 2021. Commit 34539f3dbef22de778b2da6d46a698fc2d5e84a7; contagem registrada 33/55 → 35/55. Originais não arquivados; registros anteriores não revalidados. Frontend já incorporado à main (comparação anterior à alteração: branch feat/observatorio-web 0 commits à frente, 3 atrás). docs/WEB_VALIDATION.md registra 150 testes Python e 14 frontend locais e oito E2E em execução anterior. A URL pública não pôde ser acessada nesta verificação; configuração IGFB_PAGES_ENABLED e deploy atual não confirmados. Próximo: verificar os checks da main, confirmar configuração Pages e terminar as 20 temporadas restantes. Testes da alteração atual não executados.

### Conferência documental — 24/11/2026
CBF: Vasco 127 anos (21/08/2025), Vasco e São Paulo já decidiram o Brasileirão de 89, e Presidente da CBF parabeniza Botafogo (08/12/2024). Textos recuperados e lidos nesta execução. Oito temporadas adicionais: 1974, 1989, 1990, 1991, 1995, 1997, 2000, 2024. Cobertura marcada 35/55 → 43/55. Commit 4ed008e0254ce2c64d9fb142623e0590845848a7. Releitura JSON confirmada; testes Python e arquivamento pendentes. Registros anteriores não reconferidos. Próximo: 12 temporadas restantes.

### Conferência documental 24/11/2026 — Internacional, Guarani, São Paulo e Corinthians
Textos indexados CBF efetivamente consultados: Batista (26/10/2016), Internacional (02/02/2016), Conselho de Craques (09/04/2019), Edílson (17/09/2024). Cobertura marcada 43/55 → 50/55; commit 6ceecf308dc4abe89a2616ed795c5a581cab7097. Releitura JSON confirmada. Originais e testes Python pendentes. Restam 1977, 1985, 1987, 1988, 2001; registros anteriores não revalidados.

### Conferência documental — 24/11/2026
Textos CBF consultados nesta execução confirmam Coritiba 1985, Bahia 1988 e Athletico-PR 2001. Cobertura registrada 50/55 → 53/55. Resoluções conflitantes de 1987 consultadas; reconhecimento conjunto revogado pela RDP 06/2011, Sport único campeão oficial; reivindicação Flamengo permanece pendente. Restam 1977 e 1987. Commit 5d6a5d25bcde782a52d28c34207c37a05a7826fc. JSON conferido por releitura; testes Python e arquivos originais pendentes; registros anteriores não revalidados.

### 25/11/2026 — revisão jurídica e critério de encerramento
RDP 06/2011 e notícia de 21/02/2011 reconsultadas: Sport único campeão oficial, reconhecimento conjunto revogado. Registro de Flamengo permanece pendente de decisão metodológica, sem promover a homologado. 1977: busca realizada, sem confirmação explícita suficiente nos resultados desta execução. Cobertura registrada permanece 53/55; não equivale à auditoria independente de todas as fontes. Encerrar conferência somente com evidência explícita de 1977 e tratamento separado de fato oficial e convenção em 1987. Próxima fase: arquivamento com hashes, homologação, calibração, deploy e auditoria final. Testes Python não executados.
