# Laboratório Kafka — estratégia de testes

> **Documento MSG-KAFKA-TST** | v1.0.0 | 2026-11-11 | Código `main` @ `754092c70eeb10efb241d1e072cc05ab94931392`
> Análise do código efetivo deste repositório; cenários “pendente” não representam testes executados.


## Suíte existente
`tests/test_eventos.py` implementa `ProdutorFalso` e evita dependência do cluster. Isso permite checar contrato e chamada do adaptador, não a semântica do broker.

| ID | Teste | Automatizado? | Resultado |
|---|---|---|---|
| KFK-01 | Serializar evento `route` com `dados.rota=8` | Sim: `test_serializacao` | JSON contém campos corretos |
| KFK-02 | Rejeitar tópico não autorizado | Sim: `test_topico_invalido` | `ValueError` |
| KFK-03 | Rejeitar payload do tipo lista | Sim: `test_corpo_invalido` | `ValueError` |
| KFK-04 | Publicar no tópico e chamar `flush` | Sim: `test_publicacao` | Produtor falso registra envio e `flushes==1` |
| KFK-05 | Falha de `.send()` no broker | Pendente | Retorno/erro previsível sem marcar como entregue |
| KFK-06 | Consumo seguido de commit de offset | Pendente | Commit apenas depois de processar |
| KFK-07 | Interrupção antes do commit | Pendente | Evento pode reaparecer; receptor idempotente |
| KFK-08 | Configuração OUTSIDE localhost:9094 e bind de loopback | Sim: `infra-tests/test_compose.py` | Configuração declarativa validada; conexão real ainda pendente |
| KFK-09 | Evento UTF-8 com acentos | Pendente | Bytes preservam acentos |
| KFK-10 | Dois eventos com mesma chave de negócio | Pendente | Decidir regra de duplicata |

## Testes do Compose adicionados (v1.1)

Comando: `python -m unittest discover -s infra-tests -p 'test_compose.py' -v` (requer Docker Compose CLI, mas não executa contêineres).

| ID | Cenário | Esperado |
| --- | --- | --- |
| KFK-C01 | Configuração contém os 4 serviços | Lista completa |
| KFK-C02 | Kafka publica apenas porta externa 9094 em loopback | `host_ip=127.0.0.1` |
| KFK-C03 | Control Center publica apenas 9021 em loopback | `host_ip=127.0.0.1` |
| KFK-C04 | Anúncios interno/externo são corretos | `kafka:9092` interno; `localhost:9094` externo |
| KFK-C05 | Gerador de tópicos | `route`, `freight` e `simulation` presentes |

Esses testes **não validam conexão real com Kafka**, TLS, SASL, autenticação nem controles de rede fora da máquina local.

## Ambientes
- **Unitário:** Python `unittest`, `ProdutorFalso`, sem Kafka ou rede.
- **Integração:** Kafka Docker local; verificar criação dos tópicos, anúncio de broker, send, receive e commit.
- **Não funcional:** produtor concorrente, falhas de broker, retenção e tamanho máximo de mensagens — ainda não executados.

## Comandos
```bash
python -m unittest discover -s tests -v
docker compose ps
docker compose logs kafka --tail=80
```

## Portão de qualidade
Registre commit, versão de `docker-compose.yaml`, event schema e evidências do consumo. Apenas os quatro testes da suíte existente não certificam entrega ao consumidor ou operação confiável em produção.
