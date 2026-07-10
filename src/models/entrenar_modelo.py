"""Modelos predictivos de incidencia diaria por provincia.

Se entrenan y comparan dos enfoques sobre la misma particion temporal:

1. Baseline provincial explicable: promedio historico por provincia ajustado por
   dia de semana y tendencia reciente. Es el modelo desplegado por su claridad y
   robustez con un horizonte temporal corto (enero-mayo 2026).
2. Regresion Lineal (scikit-learn): algoritmo clasico de aprendizaje supervisado
   que sirve como linea de comparacion y aporta la metrica R2.

Ambos se evaluan con MAE, RMSE y R2 para justificar la eleccion metodologica.
"""

from __future__ import annotations

import json
import pickle
from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

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


def dividir_temporal(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Particion temporal 80/20 respetando el orden de las fechas."""
    split_date = df["fecha_infraccion"].quantile(0.8)
    train = df[df["fecha_infraccion"] <= split_date].copy()
    test = df[df["fecha_infraccion"] > split_date].copy()
    return train, test


def _metricas(y_true, y_pred) -> dict:
    return {
        "mae": round(float(mean_absolute_error(y_true, y_pred)), 3),
        "rmse": round(float(mean_squared_error(y_true, y_pred) ** 0.5), 3),
        "r2": round(float(r2_score(y_true, y_pred)), 3),
    }


def entrenar_baseline(train: pd.DataFrame, test: pd.DataFrame) -> tuple[dict, pd.DataFrame, dict]:
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
    test["prediccion_baseline"] = test.apply(predecir, axis=1)
    metricas = _metricas(test["homicidios"], test["prediccion_baseline"]) if len(test) else {}
    return modelo, test, metricas


def entrenar_regresion_lineal(
    train: pd.DataFrame, test: pd.DataFrame
) -> tuple[Pipeline, pd.Series, dict]:
    """Regresion Lineal sobre provincia, dia de semana, mes y tendencia temporal."""
    train, test = train.copy(), test.copy()
    fecha_min = train["fecha_infraccion"].min()
    for d in (train, test):
        d["dia_indice"] = (d["fecha_infraccion"] - fecha_min).dt.days

    categoricas = ["provincia", "dia_semana"]
    numericas = ["mes", "dia_indice"]
    preproceso = ColumnTransformer(
        [
            ("cat", OneHotEncoder(handle_unknown="ignore"), categoricas),
            ("num", "passthrough", numericas),
        ]
    )
    modelo = Pipeline([("prep", preproceso), ("reg", LinearRegression())])

    X_cols = categoricas + numericas
    modelo.fit(train[X_cols], train["homicidios"])
    pred = pd.Series(modelo.predict(test[X_cols]), index=test.index).clip(lower=0)

    metricas = _metricas(test["homicidios"], pred) if len(test) else {}

    nombres = modelo.named_steps["prep"].get_feature_names_out()
    coefs = modelo.named_steps["reg"].coef_
    top = sorted(zip(nombres, coefs), key=lambda t: abs(t[1]), reverse=True)[:8]
    metricas["n_features"] = int(len(nombres))
    metricas["coeficientes_top"] = {str(n): round(float(c), 3) for n, c in top}
    return modelo, pred, metricas


if __name__ == "__main__":
    REPORTS.mkdir(parents=True, exist_ok=True)
    MODELS.mkdir(parents=True, exist_ok=True)

    data = preparar_dataset()
    train, test = dividir_temporal(data)

    modelo_base, test_base, met_base = entrenar_baseline(train, test)
    _, pred_reg, met_reg = entrenar_regresion_lineal(train, test)
    test_base["prediccion_regresion"] = pred_reg

    resultados = {
        "modelo": "Baseline provincial ajustado por dia de semana y tendencia",
        "objetivo": "homicidios diarios por provincia",
        "registros_entrenamiento": int(len(train)),
        "registros_prueba": int(len(test)),
        # Metricas del modelo desplegado (baseline)
        "mae": met_base.get("mae"),
        "rmse": met_base.get("rmse"),
        "r2": met_base.get("r2"),
        "comparacion_modelos": [
            {"modelo": "Baseline provincial", **met_base},
            {
                "modelo": "Regresion Lineal (scikit-learn)",
                "mae": met_reg.get("mae"),
                "rmse": met_reg.get("rmse"),
                "r2": met_reg.get("r2"),
            },
        ],
        "regresion_lineal": met_reg,
        "nota": (
            "Se compara el baseline explicable contra una Regresion Lineal. El baseline se "
            "mantiene como modelo desplegado por su claridad; ambos son exploratorios y deben "
            "usarse como senal de priorizacion, no como pronostico operativo definitivo."
        ),
    }

    with (MODELS / "modelo_incidencia_diaria.pkl").open("wb") as fh:
        pickle.dump(modelo_base, fh)
    data.to_csv(PROCESSED / "dataset_modelo_diario.csv", index=False, encoding="utf-8-sig")
    test_base.to_csv(REPORTS / "predicciones_prueba.csv", index=False, encoding="utf-8-sig")
    (REPORTS / "modelo_resultados.json").write_text(
        json.dumps(resultados, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print("Modelo entrenado: models/modelo_incidencia_diaria.pkl")
    print(f"Baseline        -> MAE {met_base['mae']} | RMSE {met_base['rmse']} | R2 {met_base['r2']}")
    print(f"Regresion Lineal-> MAE {met_reg['mae']} | RMSE {met_reg['rmse']} | R2 {met_reg['r2']}")
