"""Consumo de una API publica (Banco Mundial) para la poblacion de Ecuador.

Esta fuente complementa al dataset principal del MDI (Excel oficial de
homicidios intencionales) y permite calcular la tasa de homicidios por
100.000 habitantes. Con ello el proyecto integra al menos una API publica
como fuente de datos, ademas del archivo oficial.

API utilizada:
    Banco Mundial - World Development Indicators
    Indicador SP.POP.TOTL (poblacion total), pais Ecuador (ECU).
    https://api.worldbank.org/v2/country/ECU/indicator/SP.POP.TOTL?format=json

Se eligio esta API porque es publica, no requiere clave de acceso, entrega
JSON directo y es de acceso global (a diferencia del portal Datos Abiertos
Ecuador, cuyo endpoint /api/ esta restringido por el servidor y responde 403).
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
PROCESSED = RAIZ / "data" / "processed"
CACHE = PROCESSED / "poblacion_ecuador.json"

WORLD_BANK_URL = (
    "https://api.worldbank.org/v2/country/ECU/indicator/SP.POP.TOTL"
    "?format=json&per_page=100"
)

# Valor de respaldo (Banco Mundial, poblacion total de Ecuador, 2024) por si no
# hay conexion durante la defensa. La API en vivo lo reemplaza automaticamente.
POBLACION_FALLBACK = 18_135_478
AÑOS_FALLBACK = 2024


def _guardar_cache(resultado: dict) -> None:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")


def obtener_poblacion_ecuador(timeout: int = 15) -> dict:
    """Devuelve la poblacion total de Ecuador con una estrategia resiliente.

    1. Consulta la API publica del Banco Mundial (SP.POP.TOTL).
    2. Si la API falla, usa la ultima respuesta cacheada en disco.
    3. Si no hay cache, usa un valor de respaldo documentado.

    Retorna un dict con: poblacion, años, fuente, origen y consultado.
    """
    # 1. API en vivo
    try:
        import requests

        resp = requests.get(WORLD_BANK_URL, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        registros = data[1] if isinstance(data, list) and len(data) > 1 and data[1] else []
        for row in registros:  # vienen ordenados del año mas reciente al mas antiguo
            if row.get("value") is not None:
                resultado = {
                    "poblacion": int(row["value"]),
                    "años": int(row["date"]),
                    "fuente": "Banco Mundial - World Development Indicators (SP.POP.TOTL)",
                    "origen": "api",
                    "consultado": datetime.now().strftime("%Y-%m-%d %H:%M"),
                }
                _guardar_cache(resultado)
                return resultado
    except Exception as exc:  # noqa: BLE001
        print(f"[poblacion_api] API no disponible ({exc}); se intenta cache o respaldo.")

    # 2. Cache previa (ultima consulta exitosa)
    if CACHE.exists():
        cache = json.loads(CACHE.read_text(encoding="utf-8"))
        cache["origen"] = "cache"
        return cache

    # 3. Respaldo documentado
    return {
        "poblacion": POBLACION_FALLBACK,
        "años": AÑOS_FALLBACK,
        "fuente": "Banco Mundial - valor de respaldo cacheado (SP.POP.TOTL)",
        "origen": "fallback",
        "consultado": None,
    }


if __name__ == "__main__":
    info = obtener_poblacion_ecuador()
    print(json.dumps(info, ensure_ascii=False, indent=2))
    print(f"\nPoblacion Ecuador ({info['años']}): {info['poblacion']:,} habitantes")
    print(f"Origen del dato: {info['origen']}")
