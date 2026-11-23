# ROADMAP — IGFB

Atualizado em 2026-11-23 (continuidade: relatório operacional de pesquisa). Fonte de verdade: código, configuração e evidências versionadas neste repositório. **Não confundir cobertura documental com conclusão do projeto.**

## Painel de métricas

| Indicador | Estado atual | Cálculo e interpretação |
|---|---:|---|
| Recorte brasileiro Série A | 55 temporadas | 1971–2025, inclusive |
| Temporadas com pistas cadastradas | 20/55 = **36,36%** | Anos distintos em `config/historical_source_leads.json`; não comprova resultados |
| Temporadas sem pistas | **35** | 55 menos 20 |
| Fontes institucionais cadastradas | **7** | Registros de `sources` no arquivo de pistas |
| Afirmações candidatas | **20** | Soma de `claim_years`; não são registros aprovados |
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
| M05 | P0 | Fonte oficial localizada para cada uma das 55 temporadas | **20/55 com pistas; 35 pendentes** |
| M06 | P0 | Evidências originais arquivadas com SHA-256 e procedência auditável | **Pendente** |
| M07 | P0 | Resultados esportivos homologados por edição, sem duplicidade e com revisão | **0 homologados** |
| M08 | P1 | Modelo de pesos calibrado e análise de sensibilidade com dados homologados | **Pendente** |
| M09 | P1 | Site responsivo com metodologia, pesquisa, cobertura e estado de homologação | **Pendente** |
| M10 | P1 | Build e publicação verificáveis, acessibilidade e testes de ponta a ponta | **Pendente** |

**Contagem de metas integralmente concluídas e validadas: 0/10.** Isso não significa que o trabalho executado seja zero: três metas estão implementadas, mas dependem de confirmação da CI. O percentual `0/10` é apenas um controle de aceite estrito e **não** é o percentual global do IGFB.

## Entrega incremental recente

- Adicionado `igfb_agent/research_report.py`: transforma a fila de 55 temporadas em relatório Markdown ordenado por prioridade, sem inventar fontes nem aprovações.
- Adicionados testes de formato e recorte; CI configurada para gerar `/tmp/igfb-research-plan.md`.
- Pesquisa externa nesta etapa não encontrou evidência institucional nova suficientemente identificada para cadastro. **Cobertura permanece 20/55 (36,36%)**; nenhuma meta recebeu aceite sem testes executados.

## Próxima fila de execução

1. **P0 — Confirmar CI:** executar `python -m unittest discover -s tests -v`, `python -m igfb_agent.public_export --output /tmp/igfb-public-data` e `verify_public_data`; corrigir qualquer falha antes de declarar verde.
2. **P0 — Pesquisa histórica:** usar `python -m igfb_agent.research_report --output /tmp/igfb-research-plan.md` para priorizar as 35 temporadas sem pistas. Adicionar somente fontes efetivamente identificadas; nunca inventar URLs ou campeões.
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
