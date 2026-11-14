# Laboratório Kafka — especificação técnica

> **Documento MSG-KAFKA-PROJ** | v1.0.0 | 2026-11-11 | Código `main` @ `754092c70eeb10efb241d1e072cc05ab94931392`
> Análise do código efetivo deste repositório; cenários “pendente” não representam testes executados.


## Propósito
Experimento Python de publicação e consumo de eventos para os tópicos `route`, `freight` e `simulation`. O contrato de mensagem é independente do cliente Kafka e o produtor é injetado no serviço para permitir testes sem broker.

## Eventos e contrato
`mensageria/eventos.py` define `Evento` como `@dataclass(frozen=True)` com os campos:
- `id`: UUID v4.
- `topico`: um dos três tópicos de `TOPICOS_PERMITIDOS`.
- `tipo`: string não vazia após `strip`.
- `dados`: objeto `dict`, serializável em JSON.
- `criado_em`: timestamp ISO-8601 UTC.

`Evento.serializar()` retorna bytes UTF-8 JSON com `ensure_ascii=False` e separadores compactos. `criar_evento()` rejeita tópico, tipo e corpo inválidos, mas **não define schema versionado de payload**, idempotência ou validação semântica por tipo.

## Produção
`PublicadorEventos.publicar(evento)` chama `produtor.send(topico, value=evento.serializar())` e `flush(timeout=10)`. `criar_produtor()` configura `acks='all'` e `retries=3`. A CLI ainda chama `.get(timeout=10)`, aguardando a confirmação do broker. Isso não equivale a garantia de processamento pelo consumidor.

## Consumo
`criar_consumidor()` usa `group_id`, `auto_offset_reset='earliest'` e `enable_auto_commit=False`. Após imprimir cada mensagem, `principal.py` executa `commit()`. O cenário comporta reentrega após interrupção, portanto o consumidor real deve tratar duplicatas antes de produzir efeitos de negócio. Nenhum banco de deduplicação está implementado.

## Ambiente Docker
`docker-compose.yaml` define Zookeeper, Confluent Kafka 7.3.0, criador de tópicos e Control Center na porta 9021. `INTERNAL://kafka:9092` serve somente contêineres; `OUTSIDE://localhost:9094` atende o host via porta 127.0.0.1:9094. A porta interna 9092 não é publicada no host e o Control Center (9021) só escuta em 127.0.0.1. Isso remove a dependência de `host.docker.internal:172.17.0.1` e reduz a exposição acidental. Nenhum desses controles substitui TLS/SASL. Esta configuração é **laboratório sem TLS/SASL e com fator de replicação 1**: não usar como baseline de produção.

## Validação específica da rede local (v1.1)

`infra-tests/test_compose.py` executa `docker compose config --format json` e verifica listener interno/externo, host_ip das portas, console local e presença dos três tópicos. O CI também executa essa suíte sem iniciar broker; teste real de conexão continua pendente.

## Exemplos de CLI
```bash
docker compose up -d
python -m pip install -r requirements.txt
python principal.py --servidor localhost:9094 publicar --topico route --tipo ROTA_CRIADA --dados '{"rota":8}'
python principal.py --servidor localhost:9094 consumir --topico route --grupo laboratorio-python
```

## Evolução recomendada
Documentar esquema de versão do evento, serialização de erro/DLQ, chave de partição para preservar ordenação quando necessária e idempotência do lado do consumidor; testar `advertised.listeners` do host antes de diagnosticar falha de publicação.
