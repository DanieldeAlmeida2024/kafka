# Controle documental — kafka

Versão inicial: **1.0.0**, em 11/11/2026. Código auditado: `754092c70eeb10efb241d1e072cc05ab94931392`.

| ID | Arquivo | Versão | Motivo |
|---|---|---|---|
| MSG-KAFKA-PROJ | [Projeto](../projeto/ESPECIFICACAO.md) | 1.0.0 | Análise do domínio e código |
| MSG-KAFKA-UML | [Arquitetura/UML](../uml/README.md) | 1.0.0 | Componentes, dados, fluxos |
| MSG-KAFKA-TST | [Plano de testes](../testes/PLANO_DE_TESTES.md) | 1.0.0 | Casos existentes e lacunas |

## MSG-KAFKA 1.1.0 — 14/11/2026

- Bind de broker externo e Control Center restringido a `127.0.0.1`.
- Listener interno `kafka:9092` preservado somente na rede Docker; externo `localhost:9094`, sem `host.docker.internal` forçado.
- CI declarativa Docker Compose e testes de portas/anúncios/tópicos em `infra-tests/`.
- Mantidos Kafka Confluent 7.3.0, ZooKeeper, PLAINTEXT e replicação 1 apenas para laboratório.
- Pendência de homologação E2E, TLS/SASL, monitoramento e isolamento de rede antes de implantação.

### Regras
Versão **MAJOR** quando o contrato mudar; **MINOR** para casos/fluxos novos; **PATCH** para correções editoriais. Cada PR que alterar comportamento deve atualizar os documentos afetados e registrar o SHA testado e evidências, nunca substituir execução por proposta.
