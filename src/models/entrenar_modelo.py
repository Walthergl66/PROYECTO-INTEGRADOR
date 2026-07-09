"""Modelo predictivo auditable de incidencia diaria por provincia.

Con solo enero-mayo 2026, se usa un baseline explicable: promedio historico por
provincia ajustado por dia de semana y tendencia reciente. Evita dependencias
pesadas y deja claro el alcance exploratorio del pronostico.
"""

from __future__ import annotations

import json
import pickle
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
PROCESSED = RAIZ / "data" / "processed"
REPORTS = RAIZ / "reports"
MODELS = RAIZ / "models"


def preparar_dataset() -> pd.DataFrame:
    fact = pd.read_csv(PROCESSED / "fact_homicidios.csv", parse_dates=["fecha_infraccion"])
    geo = pd.read_csv(PROCESSED / "dim_geografia.csv")
    base = fact.merge(geo[["id_geografia", "provincia"]], on="id_geografia", how="left")
    diario = (
        base.groupby(["fecha_infraccion", "provincia"], as_index=False)["total_homicidios"]
        .sum()
        .rename(columns={"total_homicidios": "homicidios"})
    )
    diario["dia_semana"] = diario["fecha_infraccion"].dt.dayofweek
    diario["mes"] = diario["fecha_infraccion"].dt.month
    return diario.sort_values("fecha_infraccion")


def entrenar(df: pd.DataFrame) -> tuple[dict, pd.DataFrame, dict]:
    split_date = df["fecha_infraccion"].quantile(0.8)
    train = df[df["fecha_infraccion"] <= split_date].copy()
    test = df[df["fecha_infraccion"] > split_date].copy()

    media_global = float(train["homicidios"].mean())
    media_prov = train.groupby("provincia")["homicidios"].mean().to_dict()
    factor_dia = (train.groupby("dia_semana")["homicidios"].mean() / media_global).to_dict()

    recientes = train[train["fecha_infraccion"] >= train["fecha_infraccion"].max() - pd.Timedelta(days=30)]
    anteriores = train[train["fecha_infraccion"] < train["fecha_infraccion"].max() - pd.Timedelta(days=30)]
    tendencia = (
        recientes.groupby("provincia")["homicidios"].mean()
        / anteriores.groupby("provincia")["homicidios"].mean().replace(0, 1)
    ).fillna(1).clip(0.75, 1.5).to_dict()

    modelo = {
        "media_global": media_global,
        "media_provincia": media_prov,
        "factor_dia_semana": factor_dia,
        "factor_tendencia": tendencia,
    }

    def predecir(row: pd.Series) -> float:
        base = modelo["media_provincia"].get(row["provincia"], modelo["media_global"])
        dia = modelo["factor_dia_semana"].get(int(row["dia_semana"]), 1)
        trend = modelo["factor_tendencia"].get(row["provincia"], 1)
        return max(base * dia * trend, 0)

    test = test.copy()
    test["prediccion"] = test.apply(predecir, axis=1)
    if len(test):
        mae = float((test["homicidios"] - test["prediccion"]).abs().mean())
        rmse = float(((test["homicidios"] - test["prediccion"]) ** 2).mean() ** 0.5)
    else:
        mae = rmse = None

    metricas = {
        "modelo": "Baseline provincial ajustado por dia de semana y tendencia",
        "objetivo": "homicidios diarios por provincia",
        "registros_entrenamiento": int(len(train)),
        "registros_prueba": int(len(test)),
        "mae": round(mae, 3) if mae is not None else None,
        "rmse": round(rmse, 3) if rmse is not None else None,
        "nota": "Modelo exploratorio. Con cinco meses de datos reales debe usarse como senal de priorizacion, no como pronostico operativo definitivo.",
    }
    return modelo, test, metricas


if __name__ == "__main__":
    REPORTS.mkdir(parents=True, exist_ok=True)
    MODELS.mkdir(parents=True, exist_ok=True)
    data = preparar_dataset()
    modelo, prueba, metricas = entrenar(data)
    with (MODELS / "modelo_incidencia_diaria.pkl").open("wb") as fh:
        pickle.dump(modelo, fh)
    data.to_csv(PROCESSED / "dataset_modelo_diario.csv", index=False, encoding="utf-8-sig")
    prueba.to_csv(REPORTS / "predicciones_prueba.csv", index=False, encoding="utf-8-sig")
    (REPORTS / "modelo_resultados.json").write_text(
        json.dumps(metricas, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print("Modelo entrenado: models/modelo_incidencia_diaria.pkl")
