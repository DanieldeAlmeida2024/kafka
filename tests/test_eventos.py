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
        evento = criar_evento('laboratorio', 'ROTA_CRIADA', {'rota': 8})
        bruto = json.loads(evento.serializar())
        self.assertEqual('laboratorio', bruto['topico'])
        self.assertEqual(8, bruto['dados']['rota'])
    def test_topico_invalido(self):
        with self.assertRaises(ValueError): criar_evento('outro', 'X', {})
    def test_corpo_invalido(self):
        with self.assertRaises(ValueError): criar_evento('laboratorio', 'X', ['lista'])
    def test_publicacao(self):
        simulado = ProdutorFalso()
        retorno = PublicadorEventos(simulado).publicar(criar_evento('laboratorio', 'INICIADA', {'id': 1}))
        self.assertEqual('resultado-simulado', retorno)
        self.assertEqual('laboratorio', simulado.mensagens[0][0])
        self.assertEqual(1, simulado.flushes)

    def test_nao_permite_dados_que_nao_sao_json(self):
        from datetime import datetime
        with self.assertRaises(ValueError):
            criar_evento('laboratorio', 'ROTA_CRIADA', {'data': datetime.now()})

    def test_rejeita_valores_nan_e_infinito(self):
        for numero in [float('nan'), float('inf'), -float('inf')]:
            with self.subTest(numero=str(numero)):
                with self.assertRaises(ValueError):
                    criar_evento('laboratorio', 'MOVIMENTO', {'lat': numero})

    def test_limite_bytes_em_evento(self):
        with self.assertRaises(ValueError):
            criar_evento('laboratorio', 'CRIADA', {'conteudo': 'x' * (257 * 1024)})

    def test_unicode_e_serializacao_utf8(self):
        evento = criar_evento('laboratorio', 'ENTREGA', {'cidade': 'Goiânia'})
        self.assertEqual('Goiânia', json.loads(evento.serializar())['dados']['cidade'])

class IsolamentoTopicosTest(unittest.TestCase):
    def test_envelope_genérico_nao_aceita_topicos_consumidos_pelo_go(self):
        from mensageria.eventos import TOPICOS_NATIVOS, TOPICOS_PERMITIDOS
        self.assertEqual(TOPICOS_PERMITIDOS, frozenset({'laboratorio'}))
        for topico in TOPICOS_NATIVOS:
            with self.subTest(topico=topico), self.assertRaises(ValueError):
                criar_evento(topico, 'TIPO_GENERICO', {'teste': True})

    def test_cli_generico_rejeita_topic_route_antes_de_conectar(self):
        from unittest.mock import patch
        from principal import main
        with patch('principal.criar_produtor') as produtor, patch('sys.argv', [
            'principal.py', 'publicar', '--topico', 'route',
            '--tipo', 'ROTA_CRIADA', '--dados', '{"codigo":"R001"}'
        ]):
            with self.assertRaises(SystemExit):
                main()
            produtor.assert_not_called()
