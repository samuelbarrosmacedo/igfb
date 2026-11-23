# Auditoria inicial e decisões do frontend

Data: 23/11/2026. Base inspecionada: `358c1c1fd73ed139875dbb51160d831acda23de4`.

O repositório mudou durante a inspeção inicial: a primeira árvore consultada
precedia a introdução de `public_export.py`. O checkout utilizado incorporou esse
exportador antes de qualquer alteração. O frontend amplia essa implementação.

## Estado observado

- Não havia frontend, catálogo completo de clubes ou ledger histórico persistido.
- Existiam calendário, candidatos, revisão, catálogo em dataclasses, trilha de
  decisões revogáveis, conferência de arquivos, pontuação e robustez experimental.
- Os protocolos em `docs/` e o README foram lidos integralmente.
- A auditoria de estado retornou 55 temporadas, 20 candidatos em 20 temporadas,
  35 temporadas sem pistas, 7 referências distintas, uma página marcada como
  conferida e zero resultados aprovados.
- As seis identidades de clubes são derivadas das pistas. Não representam um
  cadastro completo. Nomes de exibição ficam em `config/public_labels.json`;
  IDs novos têm fallback tipográfico, sem editar componentes.
- 113 testes Python passaram antes das alterações.

## Preservação e fronteiras

Nenhum arquivo de fonte histórica, evento, regra ou decisão foi substituído.
O exportador v1 foi evoluído para v2. O teste de cardinalidade/versão foi
atualizado para os nove documentos do contrato. O núcleo matemático permanece
inalterado e continua sendo a referência para os pesos.

O auditor atual recusa `approved_records != 0` sem reconciliação de ledger. Esta
fronteira foi preservada: se aprovações forem inseridas sem uma integração auditada,
a publicação falha e a versão anterior permanece online. Não há interruptor no
frontend que transforme pistas em resultados.

A futura abertura do ranking histórico exige uma nova versão do contrato:
carregamento do ledger real, `materialize_approved` com arquivos verificados,
reconciliação de contagens, cobertura adequada, método composto calibrado e
aprovação expressa de publicação vinculada ao snapshot. Esta entrega não cria
essas decisões nem declara concluída a pesquisa.

## Direção de arte

Editorial esportivo: grafite, verde, dourado pontual, campo vetorial original,
Barlow Condensed nos títulos, Montserrat na interface e JetBrains Mono nos IDs.
Sem fotografias ou escudos externos. O manifesto dos assets registra autoria,
fontes e limites de licença. Não foi atribuída uma licença ao projeto inteiro.

## Reutilização

Radix fornece diálogo, foco modal, menu móvel, select e slider; TanStack Table
fornece ordenação e estrutura tabular. São os mesmos tipos de primitivas
acessíveis usados por componentes shadcn, utilizados diretamente para evitar
copiar uma camada de templates sem necessidade. ECharts é carregado somente
quando a simulação é aberta. Motion foi dispensado: o feedback necessário usa
transições CSS breves e respeita movimento reduzido.

Documentação consultada em 23/11/2026:

- https://vite.dev/guide/ e https://vite.dev/guide/static-deploy
- https://tanstack.com/query/latest/docs/framework/react/overview
- https://ui.shadcn.com/docs/components/slider
- https://tailwindcss.com/docs/installation/using-vite
- https://zod.dev/json-schema
- https://fontsource.org/fonts/barlow-condensed/about
- https://fontsource.org/fonts/montserrat/about
- https://fontsource.org/fonts/jetbrains-mono/about
- https://github.com/sportsdataverse/sdvplot
- https://github.com/JoseArroyave/football-logos

A licença de software de um repositório de logos não foi tratada como
comprovação de autorização sobre todas as marcas. O fallback utiliza texto.
