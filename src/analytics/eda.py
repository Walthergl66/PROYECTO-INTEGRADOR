"""EDA y KPIs ejecutivos de SafeAnalytics EC."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
PROCESSED = RAIZ / "data" / "processed"
REPORTS = RAIZ / "reports"


def cargar_base() -> pd.DataFrame:
    fact = pd.read_csv(PROCESSED / "fact_homicidios.csv", parse_dates=["fecha_infraccion"])
    geo = pd.read_csv(PROCESSED / "dim_geografia.csv")
    delito = pd.read_csv(PROCESSED / "dim_delito.csv")
    victima = pd.read_csv(PROCESSED / "dim_victima.csv")
    df = fact.merge(geo, on="id_geografia", how="left")
    df = df.merge(delito, on="id_delito", how="left")
    df = df.merge(victima, on="id_victima", how="left")
    df["mes"] = df["fecha_infraccion"].dt.month
    df["dia_semana"] = df["fecha_infraccion"].dt.day_name()
    return df


def calcular_kpis(df: pd.DataFrame) -> dict:
    total = int(df["total_homicidios"].sum())
    arma_fuego = int((df["arma"] == "ARMA DE FUEGO").sum())
    hombres = int((df["sexo"] == "HOMBRE").sum())
    edad_prom = float(df["edad_num"].dropna().mean())
    provincia_top = df["provincia"].value_counts().idxmax()
    canton_top = df["canton"].value_counts().idxmax()
    hora_top = int(df["hora"].value_counts().idxmax())
    dia_top = df["dia_semana"].value_counts().idxmax()

    mensual = df.groupby("mes")["total_homicidios"].sum().to_dict()
    provincias = df["provincia"].value_counts().head(10).to_dict()
    cantones = df["canton"].value_counts().head(10).to_dict()
    armas = df["arma"].value_counts().to_dict()
    motivaciones = df["presunta_motivacion"].value_counts().head(8).to_dict()

    return {
        "total_homicidios": total,
        "provincias_afectadas": int(df["provincia"].nunique()),
        "cantones_afectados": int(df["canton"].nunique()),
        "porcentaje_arma_fuego": round(arma_fuego / total * 100, 2),
        "porcentaje_victimas_hombres": round(hombres / total * 100, 2),
        "edad_promedio": round(edad_prom, 1),
        "provincia_mayor_incidencia": provincia_top,
        "canton_mayor_incidencia": canton_top,
        "hora_critica": hora_top,
        "dia_mas_critico": dia_top,
        "serie_mensual": {str(k): int(v) for k, v in mensual.items()},
        "top_provincias": {k: int(v) for k, v in provincias.items()},
        "top_cantones": {k: int(v) for k, v in cantones.items()},
        "distribucion_armas": {k: int(v) for k, v in armas.items()},
        "motivaciones": {k: int(v) for k, v in motivaciones.items()},
    }


if __name__ == "__main__":
    REPORTS.mkdir(parents=True, exist_ok=True)
    base = cargar_base()
    resultados = calcular_kpis(base)
    (REPORTS / "eda_resultados.json").write_text(
        json.dumps(resultados, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print("EDA completado: reports/eda_resultados.json")
