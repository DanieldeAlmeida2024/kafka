# Plano de testes

- CT-01: Serializar eventos e preservar os dados.
- CT-02: Rejeitar tópico inválido e payload não-objeto.
- CT-03: Verificar chamada ao adaptador de publicação simulado.
- CT-04 (pendente): Subir `docker compose up -d`, publicar evento e recebê-lo via consumidor.

Testes locais: `python -m unittest discover -s tests -v`. Os três primeiros casos **não** comprovam funcionamento do broker.
