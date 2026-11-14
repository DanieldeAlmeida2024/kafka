"""Contrato estático do Compose renderizado, sem iniciar contêineres."""
import json
import subprocess
import unittest


class KafkaComposeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        saida = subprocess.run(
            ["docker", "compose", "-f", "docker-compose.yaml", "config", "--format", "json"],
            check=True, capture_output=True, text=True, timeout=20,
        )
        cls.services = json.loads(saida.stdout)["services"]

    def test_lista_de_servicos(self):
        for name in ("zookeeper", "kafka", "kafka-topic-generator", "control-center"):
            self.assertIn(name, self.services)

    def test_broker_so_expõe_listener_externo_em_loopback(self):
        ports = self.services["kafka"].get("ports", [])
        self.assertEqual(1, len(ports))
        self.assertEqual("127.0.0.1", ports[0]["host_ip"])
        self.assertEqual(9094, ports[0]["published"])
        self.assertEqual(9094, ports[0]["target"])

    def test_console_sem_porta_publica(self):
        ports = self.services["control-center"].get("ports", [])
        self.assertEqual(1, len(ports))
        self.assertEqual("127.0.0.1", ports[0]["host_ip"])
        self.assertEqual(9021, ports[0]["published"])

    def test_listeners_interno_e_externo(self):
        env = self.services["kafka"]["environment"]
        self.assertIn("INTERNAL://kafka:9092", env["KAFKA_ADVERTISED_LISTENERS"])
        self.assertIn("OUTSIDE://localhost:9094", env["KAFKA_ADVERTISED_LISTENERS"])
        self.assertNotIn("host.docker.internal", env["KAFKA_ADVERTISED_LISTENERS"])
        self.assertEqual("INTERNAL:PLAINTEXT,OUTSIDE:PLAINTEXT",
                         env["KAFKA_LISTENER_SECURITY_PROTOCOL_MAP"])

    def test_gerador_tem_topicos_necessarios(self):
        cmd = self.services["kafka-topic-generator"]["command"]
        text = " ".join(cmd) if isinstance(cmd, list) else cmd
        for topico in ("route", "freight", "simulation"):
            self.assertIn("--topic " + topico, text)


if __name__ == "__main__":
    unittest.main()
