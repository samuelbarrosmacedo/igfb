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
