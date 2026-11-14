# Kafka — laboratório de mensageria de rotas, fretes e simulações

Infraestrutura de desenvolvimento com Kafka/ZooKeeper e **exemplo funcional em Python 3.10+**. O código Python publica e consome eventos dos tópicos `route`, `freight` e `simulation`.

## Requisitos
Docker Compose, Python 3.10+ e acesso ao broker.

```bash
docker compose up -d
python -m pip install -r requirements.txt
python principal.py --servidor localhost:9094 publicar --topico route --tipo ROTA_CRIADA --dados '{"codigo":"R001"}'
python principal.py --servidor localhost:9094 consumir --topico route --grupo teste-local
```

O endereço externo depende de `KAFKA_ADVERTISED_LISTENERS` no Compose. Ajuste `host.docker.internal` conforme o sistema operacional. É um ambiente **PLAINTEXT somente para laboratório**.

## Estrutura
- `docker-compose.yaml`: Kafka, ZooKeeper e tópicos.
- `mensageria/eventos.py`: estrutura e validação dos eventos.
- `mensageria/servico.py`: publicação e adaptadores Kafka.
- `principal.py`: CLI para publicar/consumir.
- `tests/test_eventos.py`: testes unitários com produtor simulado.
- `docs/`: requisitos, arquitetura, UML e plano de testes.
- `AGENTS.md`: contexto para ferramentas de IA.

## Testar
```bash
python -m unittest discover -s tests -v
```

Os testes unitários validam eventos e o contrato do publicador, **não** uma conexão real com Kafka. O serviço em produção exigiria autenticação, TLS, idempotência e controle de retenção.

## Documentação técnica v1.0.0

- [Especificação de projeto](docs/projeto/ESPECIFICACAO.md)
- [Diagramas UML específicos](docs/uml/README.md)
- [Plano de testes](docs/testes/PLANO_DE_TESTES.md)
- [Controle de versões](docs/controle/VERSIONAMENTO.md)

## Integridade dos eventos (13/11/2026)

A criação do evento valida a representação JSON antes de contatar o broker: recusa números não finitos, objetos não serializáveis e mensagens maiores que **256 KiB**. A codificação permanece UTF-8 e os tópicos ficam restritos a `route`, `freight` e `simulation`. O workflow `.github/workflows/testes.yml` testa esse contrato; **não executa integração real com Kafka**, tolerância a falhas nem TLS.
