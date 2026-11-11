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
| KFK-08 | `host.docker.internal:9094` inacessível | Pendente | Diagnóstico de listener/DNS |
| KFK-09 | Evento UTF-8 com acentos | Pendente | Bytes preservam acentos |
| KFK-10 | Dois eventos com mesma chave de negócio | Pendente | Decidir regra de duplicata |

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
