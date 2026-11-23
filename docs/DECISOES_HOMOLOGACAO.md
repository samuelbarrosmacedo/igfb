# Protocolo de decisões de homologação (v1)

O módulo `igfb_agent.decisions` separa três coisas:

1. **Pista**: notícia ou afirmação sobre resultado, ainda não examinada.
2. **Evidência arquivada**: documento identificado por URL HTTPS e hash SHA-256 dos bytes arquivados. Um hash preenchido manualmente não prova que o documento foi realmente coletado: é necessário preservar e conferir o arquivo original.
3. **Decisão**: registro explícito de revisor, data com fuso horário, justificativa, edição, clube, resultado e evidência.

Uma decisão `approved` só pode produzir um `Result(approved=True)` quando o catálogo e a evidência existirem e os resultados não forem conflitantes. Uma decisão `revoked` referencia uma aprovação anterior, conserva o histórico e retira o resultado da saída ativa. A função `materialize_approved` não lê automaticamente o arquivo de pistas e não aprova por heurística.

**Exceção de 1987:** a convenção IGFB para o Flamengo é uma decisão metodológica do projeto, não uma declaração de consenso institucional. Quando houver decisão formal, a justificativa deve explicitar a convenção, o documento de apoio e as posições institucionais divergentes. Nenhuma decisão foi criada automaticamente para 1987.

**Limitação atual:** a implementação valida a estrutura e a integridade referencial das decisões, mas não comprova identidade real do revisor, autenticidade de documentos, independência das fontes nem assinatura criptográfica. A validação de hash contra bytes arquivados e a revisão humana continuam obrigatórias.

Para executar os testes: `python -m unittest discover -s tests -v`. Os exemplos em `tests/test_decisions.py` são **sintéticos** e não constituem resultados históricos.
