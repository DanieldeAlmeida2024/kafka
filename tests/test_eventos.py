import json
import unittest
from mensageria.eventos import criar_evento
from mensageria.servico import PublicadorEventos

class ProdutorFalso:
    def __init__(self):
        self.mensagens = []
        self.flushes = 0
    def send(self, topico, value):
        self.mensagens.append((topico, value))
        return 'resultado-simulado'
    def flush(self, timeout): self.flushes += 1

class TestesMensageria(unittest.TestCase):
    def test_serializacao(self):
        evento = criar_evento('route', 'ROTA_CRIADA', {'rota': 8})
        bruto = json.loads(evento.serializar())
        self.assertEqual('route', bruto['topico'])
        self.assertEqual(8, bruto['dados']['rota'])
    def test_topico_invalido(self):
        with self.assertRaises(ValueError): criar_evento('outro', 'X', {})
    def test_corpo_invalido(self):
        with self.assertRaises(ValueError): criar_evento('freight', 'X', ['lista'])
    def test_publicacao(self):
        simulado = ProdutorFalso()
        retorno = PublicadorEventos(simulado).publicar(criar_evento('simulation', 'INICIADA', {'id': 1}))
        self.assertEqual('resultado-simulado', retorno)
        self.assertEqual('simulation', simulado.mensagens[0][0])
        self.assertEqual(1, simulado.flushes)
