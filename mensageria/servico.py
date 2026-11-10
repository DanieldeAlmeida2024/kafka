"""Publicação desacoplada do SDK Kafka para testes isolados."""
from mensageria.eventos import Evento

class PublicadorEventos:
    def __init__(self, produtor):
        self.produtor = produtor

    def publicar(self, evento: Evento):
        resultado = self.produtor.send(evento.topico, value=evento.serializar())
        self.produtor.flush(timeout=10)
        return resultado

def criar_produtor(servidor: str):
    try:
        from kafka import KafkaProducer
    except ImportError as erro:
        raise RuntimeError('Instale dependências com pip install -r requirements.txt') from erro
    return KafkaProducer(bootstrap_servers=[servidor], acks='all', retries=3)

def criar_consumidor(servidor: str, topico: str, grupo: str):
    try:
        from kafka import KafkaConsumer
    except ImportError as erro:
        raise RuntimeError('Instale dependências com pip install -r requirements.txt') from erro
    return KafkaConsumer(topico, bootstrap_servers=[servidor], group_id=grupo,
                         auto_offset_reset='earliest', enable_auto_commit=False)
