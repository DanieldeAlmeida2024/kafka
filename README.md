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

O endereço externo é **`localhost:9094`** no Windows, Linux e macOS. O listener interno é `kafka:9092` somente entre contêineres. O painel Control Center é `http://localhost:9021` e ambos os acessos externos ficam limitados a `127.0.0.1` do host. É um ambiente **PLAINTEXT somente para laboratório**; não publicar em redes públicas.

## Estrutura
- `docker-compose.yaml`: Kafka, ZooKeeper e tópicos.
- `mensageria/eventos.py`: estrutura e validação dos eventos.
- `mensageria/servico.py`: publicação e adaptadores Kafka.
- `principal.py`: CLI para publicar/consumir.
- `tests/test_eventos.py`: testes unitários com produtor simulado.
- `docs/`: requisitos, arquitetura, UML e plano de testes.
- `AGENTS.md`: contexto para ferramentas de IA.

## Validar infraestrutura (sem iniciar contêineres)
```bash
docker compose -f docker-compose.yaml config --quiet
python -m unittest discover -s infra-tests -p 'test_compose.py' -v
```

A validação CI também verifica os binds locais, o par de listeners anunciado e os tópicos da configuração. Ela não sobe Kafka e **não é um teste E2E de mensageria**.

## Testar
```bash
python -m unittest discover -s tests -v
```

Os testes unitários validam eventos e o contrato do publicador, **não** uma conexão real com Kafka. O serviço em produção exigiria autenticação, TLS, idempotência e controle de retenção.

## Documentação técnica

- [Especificação de projeto](docs/projeto/ESPECIFICACAO.md)
- [Diagramas UML específicos](docs/uml/README.md)
- [Plano de testes](docs/testes/PLANO_DE_TESTES.md)
- [Controle de versões](docs/controle/VERSIONAMENTO.md)

## Contrato e integridade dos eventos

A criação do evento valida a representação JSON antes de contatar o broker: recusa números não finitos, objetos não serializáveis e mensagens maiores que **256 KiB**. A codificação permanece UTF-8 e os tópicos ficam restritos a `route`, `freight` e `simulation`. O workflow `.github/workflows/testes.yml` testa esse contrato; **não executa integração real com Kafka**, tolerância a falhas nem TLS.

## Compatibilidade com o Go Simulator — eventos nativos

O comando `publicar` original envia um **envelope didático genérico** (`id,topico,tipo,dados,criado_em`). Esse envelope **não é aceito diretamente** pelo consumidor de rastreamento Go, que lê `event` e os demais campos no nível principal.

Para publicar mensagens compatíveis com o fluxo NestJS → Kafka → Go, use o novo comando separado:

```bash
python principal.py --servidor localhost:9094 publicar-rastreamento --evento RouteCreated --dados '{"id":"507f1f77bcf86cd799439011","distance":4000,"directions":[{"lat":-16.6869,"lng":-49.2648},{"lat":-16.7,"lng":-49.3}]}'
python principal.py --servidor localhost:9094 publicar-rastreamento --evento DeliveryStarted --dados '{"route_id":"507f1f77bcf86cd799439011"}'
```

O comando publica somente no tópico `route`, preservando os campos e a ordem esperados pelo Go. Valida IDs, distância, latitude/longitude, até **600 pontos** e orçamento de até **256 KiB**. Não conecta ao broker quando os dados são inválidos e só relata envio após receber confirmação do produtor Kafka.

A CLI antiga continua disponível para estudo **separado**. Misturar envelopes genéricos no tópico `route` quando o Go Simulator está consumindo pode interromper o consumidor por evento desconhecido. O ambiente é didático, sem TLS/SASL e sem garantia de E2E.
