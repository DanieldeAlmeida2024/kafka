# KAFKA-DLQ-01 — Quarentena do tópico route

14/11/2026 · Infraestrutura local com Kafka/ZooKeeper.

## Motivação
Eventos incompatíveis ou JSON malformado podem provocar falha do consumidor Go e impedir a progressão de uma partição. A política segura exige armazenar a mensagem no tópico separado antes de reconhecer o offset original, em vez de descartá-la ou reiniciar indefinidamente.

## Infraestrutura
- Gerar topic `route-dlq` junto de route/freight/simulation/laboratorio.
- Tópico de quarentena é distinto do fluxo de simulação e não deve ser consumido automaticamente como evento operacional.
- CI confirma presença do tópico na configuração resolvida; casos de integração reais exigem broker e testes de falha de escrita.

## Observações operacionais
Mensagens podem conter dados de rotas; restringir acesso à DLQ, retenção, auditoria e transporte TLS antes de publicar. Quando a DLQ estiver indisponível, consumidor deve deixar o offset original sem commit.
