"""Contrato nativo do Go Simulator no tópico route (sem envelope didático).

RouteCreated: {event,id,distance,directions:[{lat,lng}, ...]}
DeliveryStarted: {event,route_id}
O produtor NestJS e o simulador Go utilizam este mesmo formato.
"""
import json
import math
import re

MAX_EVENTO_BYTES = 256 * 1024
MAX_PONTOS = 600
ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,127}$")


def _identificador(valor):
    return isinstance(valor, str) and bool(ID.fullmatch(valor))


def serializar_evento_rastreamento(evento: str, dados: dict) -> bytes:
    if not isinstance(dados, dict):
        raise ValueError("Dados do rastreamento devem ser um objeto JSON.")

    if evento == "RouteCreated":
        if set(dados) != {"id", "distance", "directions"}:
            raise ValueError("RouteCreated exige somente id, distance e directions.")
        if not _identificador(dados["id"]):
            raise ValueError("RouteCreated exige id válido.")
        distancia = dados["distance"]
        if type(distancia) is not int or distancia < 0:
            raise ValueError("distance deve ser inteiro não negativo.")
        pontos = dados["directions"]
        if not isinstance(pontos, list) or not 1 <= len(pontos) <= MAX_PONTOS:
            raise ValueError("directions deve ter entre 1 e 600 pontos.")
        for indice, ponto in enumerate(pontos):
            if not isinstance(ponto, dict) or set(ponto) != {"lat", "lng"}:
                raise ValueError(f"Ponto {indice}: exige lat e lng.")
            for chave, limite in (("lat", 90), ("lng", 180)):
                numero = ponto[chave]
                if type(numero) not in (int, float) or not math.isfinite(numero) or abs(numero) > limite:
                    raise ValueError(f"Ponto {indice}: {chave} inválido.")
    elif evento == "DeliveryStarted":
        if set(dados) != {"route_id"} or not _identificador(dados["route_id"]):
            raise ValueError("DeliveryStarted exige somente route_id válido.")
    else:
        raise ValueError("Evento de rastreamento desconhecido.")

    bruto = json.dumps(
        {"event": evento, **dados}, ensure_ascii=False,
        separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")
    if len(bruto) > MAX_EVENTO_BYTES:
        raise ValueError("Evento de rastreamento excede 256 KiB.")
    return bruto
