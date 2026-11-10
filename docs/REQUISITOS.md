# Requisitos — laboratório Kafka

RF-01 Publicar evento JSON nos tópicos route, freight ou simulation.
RF-02 Consumir eventos por grupo de consumidores configurável.
RF-03 Rejeitar nomes de tópicos e corpos inválidos.
RF-04 Operar com endereço de broker explícito.

RNF-01 Contratos independentes da biblioteca kafka-python.
RNF-02 Execução local isolada da infraestrutura de produção.
RNF-03 Testes unitários sem conexão de rede, mais integração real separada.
RNF-04 Para produção: TLS/SASL, retries, idempotência e DLQ após desenho aprovado.
