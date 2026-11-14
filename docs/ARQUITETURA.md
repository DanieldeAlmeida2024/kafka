# Arquitetura de kafka

Consulte a [especificação específica](projeto/ESPECIFICACAO.md) e os [diagramas de componentes, classes e sequência](uml/README.md) (v1.0.0).

## Eventos nativos de rastreamento e envelope didático

`mensageria/eventos.py` mantém o evento genérico para estudo isolado. `mensageria/rastreamento.py` valida o contrato nativo de `RouteCreated` e `DeliveryStarted` usado pelo Go Simulator e pelo NestJS.

`principal.py publicar-rastreamento` envia bytes JSON **sem envelope adicional**, sempre para `route`, e espera o ACK do produtor. Isso evita que o consumidor Go interprete `tipo` como campo `event` e encerre por tipo desconhecido. Não há tradução automática dos eventos genéricos: o operador escolhe explicitamente o modo.
