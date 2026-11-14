"""Regressão de contrato compartilhado com o Go Simulator, sem broker real."""
import json
import math
import unittest
from io import StringIO
from contextlib import redirect_stdout
from unittest.mock import MagicMock, patch

from mensageria.rastreamento import (
    MAX_EVENTO_BYTES, MAX_PONTOS, serializar_evento_rastreamento,
)


class TestesRastreamentoNativo(unittest.TestCase):
    def setUp(self):
        self.rota = {
            "id": "507f1f77bcf86cd799439011",
            "distance": 4000,
            "directions": [{"lat": -16.6869, "lng": -49.2648},
                           {"lat": -16.7000, "lng": -49.3000}],
        }

    def test_route_created_corresponde_ao_consumidor_go(self):
        evento = json.loads(serializar_evento_rastreamento("RouteCreated", self.rota))
        self.assertEqual(set(evento), {"event", "id", "distance", "directions"})
        self.assertEqual(evento["event"], "RouteCreated")
        self.assertEqual(evento["directions"], self.rota["directions"])

    def test_delivery_started_requer_route_id(self):
        raw = serializar_evento_rastreamento("DeliveryStarted", {"route_id": "r-1"})
        self.assertEqual(json.loads(raw), {"event": "DeliveryStarted", "route_id": "r-1"})

    def test_route_created_valida_distancia_e_id(self):
        for valor in (-1, True, False, 1.5, "4000", None):
            with self.subTest(valor=valor), self.assertRaises(ValueError):
                serializar_evento_rastreamento("RouteCreated", {**self.rota, "distance": valor})
        for valor in ("", "../../other", "x" * 129, 42, None):
            with self.subTest(id=valor), self.assertRaises(ValueError):
                serializar_evento_rastreamento("RouteCreated", {**self.rota, "id": valor})

    def test_limite_de_600_pontos_inclusive(self):
        pontos = [{"lat": 0, "lng": 0}] * MAX_PONTOS
        raw = serializar_evento_rastreamento("RouteCreated",
                                           {**self.rota, "directions": pontos})
        self.assertLessEqual(len(raw), MAX_EVENTO_BYTES)
        for invalid in ([], pontos + [{"lat": 0, "lng": 0}], "invalido"):
            with self.subTest(len=str(len(invalid))), self.assertRaises(ValueError):
                serializar_evento_rastreamento("RouteCreated",
                                               {**self.rota, "directions": invalid})

    def test_rejeita_coordenadas_invalidas_e_booleanos(self):
        for point in (
            {"lat": True, "lng": 0}, {"lat": math.nan, "lng": 0},
            {"lat": 90.1, "lng": 0}, {"lat": 0, "lng": -180.1},
            {"lat": 0, "lng": math.inf}, {"lat": "10", "lng": 0},
            {"lat": 0}, [0, 0],
        ):
            with self.subTest(point=str(point)), self.assertRaises(ValueError):
                serializar_evento_rastreamento("RouteCreated",
                                               {**self.rota, "directions": [point]})

    def test_limites_geograficos_sao_aceitos(self):
        raw = serializar_evento_rastreamento("RouteCreated", {
            **self.rota, "directions": [{"lat": 90, "lng": -180},
                                         {"lat": -90, "lng": 180}],
        })
        self.assertEqual(len(json.loads(raw)["directions"]), 2)

    def test_rejeita_eventos_e_campos_nao_contratados(self):
        for evento, dados in (
            ("Unknown", self.rota), ("DeliveryStarted", {"id": "x"}),
            ("DeliveryStarted", {"route_id": "", "event": "RouteCreated"}),
            ("RouteCreated", {**self.rota, "event": "DeliveryStarted"}),
            ("RouteCreated", []),
        ):
            with self.subTest(evento=evento, dados=str(dados)), self.assertRaises(ValueError):
                serializar_evento_rastreamento(evento, dados)

    def test_cli_envia_evento_nativo_no_topico_route_e_aguarda_ack(self):
        from principal import main
        producer = MagicMock()
        with patch("principal.criar_produtor", return_value=producer), patch(
            "sys.argv", ["principal.py", "publicar-rastreamento", "--evento",
                          "DeliveryStarted", "--dados", '{"route_id":"r-1"}']
        ), redirect_stdout(StringIO()) as stream:
            main()
        args, kwargs = producer.send.call_args
        self.assertEqual(args, ("route",))
        self.assertEqual(json.loads(kwargs["value"]),
                         {"event": "DeliveryStarted", "route_id": "r-1"})
        producer.send.return_value.get.assert_called_once_with(timeout=10)
        producer.close.assert_called_once()
        self.assertIn("publicado", stream.getvalue())

    def test_cli_nao_conecta_ao_broker_para_evento_invalido(self):
        from principal import main
        with patch("principal.criar_produtor") as create, patch(
            "sys.argv", ["principal.py", "publicar-rastreamento", "--evento",
                          "DeliveryStarted", "--dados", '{"route_id":""}']
        ):
            with self.assertRaises(SystemExit):
                main()
            create.assert_not_called()

    def test_cli_nao_declara_sucesso_quando_ack_falha(self):
        from principal import main
        producer = MagicMock()
        producer.send.return_value.get.side_effect = TimeoutError("Kafka ack timeout")
        with patch("principal.criar_produtor", return_value=producer), patch(
            "sys.argv", ["principal.py", "publicar-rastreamento", "--evento",
                          "DeliveryStarted", "--dados", '{"route_id":"r-1"}']
        ), redirect_stdout(StringIO()) as stream:
            with self.assertRaises(TimeoutError):
                main()
        producer.close.assert_called_once()
        self.assertNotIn("publicado", stream.getvalue())


if __name__ == "__main__":
    unittest.main()
