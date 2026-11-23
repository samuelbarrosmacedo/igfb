# Protocolo de homologação e robustez — IGFB

## 1. Estados de evidência
1. **Descoberta:** URL encontrada, sem alegação de resultado.
2. **Coletada:** conteúdo identificado por SHA-256 e metadados, sem aprovação.
3. **Extraída:** candidato a resultado com clube, edição, posição e trecho verificável.
4. **Confrontada:** fonte independente ou documento primário sustenta a afirmação; divergências preservadas.
5. **Homologada:** decisão explícita com evidência, convenção e responsável.
6. **Revogada:** decisão substituída, sem apagar o histórico anterior.

O campo `approved=True` só é válido no estado homologado. Uma página coletada ou um resumo de modelo de linguagem **não** aprova resultados.

## 2. Chaves canônicas
- **Clube:** ID estável separado do nome exibido; aliases e mudanças de nome versionados.
- **Competição:** categoria de pesos do IGFB, que não é necessariamente a identidade do torneio.
- **Edição:** identificador único com organizador, jurisdição quando aplicável, temporada e torneio.
- **Resultado:** (clube canônico, edição, resultado), com evidências associadas.
- **Evidência:** ID único, URL HTTPS, hash do conteúdo, tipo da fonte e data de captura.

Registros antigos sem `edition_id` permanecem legíveis, mas **não podem ser homologados** pelo validador referencial. Uma edição explicitamente cadastrada não pode divergir do ano ou da categoria do resultado.

## 3. Invariantes históricas
- Brasileirão: **somente 1971–2025** no primeiro recorte.
- Taça Brasil, Robertão e torneio de 1937: **fora de todos os critérios e pontuações**.
- 1987: Flamengo campeão por **convenção metodológica do IGFB**, identificada como tal; não confundir com consenso oficial.
- Rebaixamentos: somente quedas esportivas comprovadas; não inferir automaticamente de uma classificação.
- Competições estaduais: não presumir campeão único por ano em âmbito nacional.
- Formatos especiais e títulos compartilhados: exigem regra específica de edição, nunca ajuste silencioso.

## 4. Matemática e interpretação

### Pontuação-base
`S_c(θ)=Σ_i w_{k_i,o_i}(θ)`, para resultados homologados, deduplicados por edição.

### Consistência temporal
`J_c=(Σ_t p_ct)^2/(T Σ_t p_ct²)`, somente para pontuações anuais não negativas. Valores negativos de penalidades não entram diretamente nessa fórmula.

### Padronização sazonal
`z_ct=(p_ct-μ_t)/σ_t`; a população de referência deve ser declarada, e σ=0 exige tratamento explícito.

### Robustez de cenários
Para cenários metodológicos finitos `Θ`, calcular mínimos e máximos de pontuação, melhor e pior posição, média de posição e fração dos cenários em primeiro lugar. Essa fração **não é probabilidade de vitória** e o envelope **não é intervalo de confiança**. Não atribuir probabilidades aos cenários sem distribuição justificada.

### Índice composto
Nenhum índice composto ou ranking definitivo pode ser publicado antes de:
1. Definir população de comparação, coeficientes e escalas.
2. Testar estabilidade de posições sob variações plausíveis de pesos.
3. Auditar duplicidades, títulos controversos e evidências por edição.
4. Medir cobertura de temporadas e competições, incluindo dados ausentes.

## 5. Segurança do cálculo
O fluxo recomendado é `registry.score_verified`: valida referências, aprovações e conflitos antes de chamar a soma ponderada. `scoring.score_results` é uma função matemática de baixo nível, **não** uma porta de homologação histórica.

## 6. Situação
Ainda não há resultados homologados no repositório. Os cenários dos testes são sintéticos e nunca devem ser apresentados como pontuação real de clubes.
