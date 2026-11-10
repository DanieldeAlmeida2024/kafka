# Guia para agentes — Kafka

Leia README, docker-compose.yaml e docs/ARQUITETURA.md. Este é um laboratório de infraestrutura, não um serviço público.

- Preserve os tópicos existentes: route, freight, simulation.
- Não modifique listener externo sem testar comunicação no Docker.
- Escreva novos métodos Python com nomes descritivos em português.
- Separe contratos de eventos de dependências kafka-python.
- Nunca exponha credenciais; não declare Kafka funcionando com base em mock.
- Execute `python -m unittest discover -s tests -v` e teste integração com broker antes de merge.
