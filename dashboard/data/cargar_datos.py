"""Carga de datos procesados para el dashboard."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

RAIZ = Path(__file__).resolve().parents[2]
PROCESSED = RAIZ / "data" / "processed"
REPORTS = RAIZ / "reports"


@st.cache_data
def cargar_base() -> pd.DataFrame:
    fact = pd.read_csv(PROCESSED / "fact_homicidios.csv", parse_dates=["fecha_infraccion"])
    geo = pd.read_csv(PROCESSED / "dim_geografia.csv")
    delito = pd.read_csv(PROCESSED / "dim_delito.csv")
    victima = pd.read_csv(PROCESSED / "dim_victima.csv")
    df = fact.merge(geo, on="id_geografia", how="left")
    df = df.merge(delito, on="id_delito", how="left")
    df = df.merge(victima, on="id_victima", how="left")
    df["mes"] = df["fecha_infraccion"].dt.month
    meses = {
        1: "Enero",
        2: "Febrero",
        3: "Marzo",
        4: "Abril",
        5: "Mayo",
        6: "Junio",
        7: "Julio",
        8: "Agosto",
        9: "Septiembre",
        10: "Octubre",
        11: "Noviembre",
        12: "Diciembre",
    }
    dias = {
        "Monday": "Lunes",
        "Tuesday": "Martes",
        "Wednesday": "Miercoles",
        "Thursday": "Jueves",
        "Friday": "Viernes",
        "Saturday": "Sabado",
        "Sunday": "Domingo",
    }
    df["mes_nombre"] = df["mes"].map(meses)
    df["dia_semana"] = df["fecha_infraccion"].dt.day_name()
    df["dia_semana_nombre"] = df["dia_semana"].map(dias)
    return df


@st.cache_data
def cargar_kpis() -> dict:
    return json.loads((REPORTS / "eda_resultados.json").read_text(encoding="utf-8"))


@st.cache_data
def cargar_modelo() -> dict:
    return json.loads((REPORTS / "modelo_resultados.json").read_text(encoding="utf-8"))


@st.cache_data
def cargar_recomendaciones() -> pd.DataFrame:
    return pd.read_csv(REPORTS / "recomendaciones_estrategicas.csv")


@st.cache_data
def cargar_tablas() -> dict[str, pd.DataFrame]:
    tablas = {}
    for path in sorted(PROCESSED.glob("*.csv")):
        tablas[path.stem] = pd.read_csv(path)
    return tablas
