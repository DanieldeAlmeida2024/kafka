"""Contrato de evento independente do transporte."""
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from uuid import uuid4
import json

TOPICOS_PERMITIDOS = frozenset({'route', 'freight', 'simulation'})

@dataclass(frozen=True)
class Evento:
    id: str
    topico: str
    tipo: str
    dados: dict
    criado_em: str

    def serializar(self) -> bytes:
        return json.dumps(asdict(self), ensure_ascii=False, separators=(',', ':')).encode('utf-8')

def criar_evento(topico: str, tipo: str, dados: dict) -> Evento:
    if topico not in TOPICOS_PERMITIDOS:
        raise ValueError(f'Tópico inválido: {topico}')
    if not isinstance(tipo, str) or not tipo.strip():
        raise ValueError('Informe o tipo do evento.')
    if not isinstance(dados, dict):
        raise ValueError('Os dados precisam ser um objeto JSON.')
    return Evento(str(uuid4()), topico, tipo.strip(), dados,
                  datetime.now(timezone.utc).isoformat())
