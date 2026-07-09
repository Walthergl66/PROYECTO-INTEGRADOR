"""Reglas prescriptivas para priorizacion ejecutiva."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
PROCESSED = RAIZ / "data" / "processed"
REPORTS = RAIZ / "reports"


def generar_recomendaciones() -> pd.DataFrame:
    fact = pd.read_csv(PROCESSED / "fact_homicidios.csv", parse_dates=["fecha_infraccion"])
    geo = pd.read_csv(PROCESSED / "dim_geografia.csv")
    delito = pd.read_csv(PROCESSED / "dim_delito.csv")
    base = fact.merge(geo[["id_geografia", "provincia", "canton", "zona"]], on="id_geografia")
    base = base.merge(delito[["id_delito", "arma", "tipo_lugar"]], on="id_delito")
    base["mes"] = base["fecha_infraccion"].dt.month

    max_mes = int(base["mes"].max())
    total_prov = base.groupby("provincia").agg(
        total_homicidios=("total_homicidios", "sum"),
        cantones_afectados=("canton", "nunique"),
        pct_arma_fuego=("arma", lambda s: round((s == "ARMA DE FUEGO").mean() * 100, 1)),
        pct_lugar_publico=("tipo_lugar", lambda s: round((s == "PÚBLICO").mean() * 100, 1)),
    )
    ultimo_mes = base[base["mes"] == max_mes].groupby("provincia")["total_homicidios"].sum()
    mes_previo = base[base["mes"] == max_mes - 1].groupby("provincia")["total_homicidios"].sum()

    rec = total_prov.join(ultimo_mes.rename("homicidios_ultimo_mes"), how="left").join(
        mes_previo.rename("homicidios_mes_previo"), how="left"
    ).fillna(0)
    rec["variacion_mensual_pct"] = (
        (rec["homicidios_ultimo_mes"] - rec["homicidios_mes_previo"])
        / rec["homicidios_mes_previo"].replace(0, 1)
        * 100
    ).round(1)

    def norm(serie: pd.Series) -> pd.Series:
        rango = serie.max() - serie.min()
        if rango == 0:
            return pd.Series(50, index=serie.index)
        return (serie - serie.min()) / rango * 100

    rec["score_volumen"] = norm(rec["total_homicidios"])
    rec["score_reciente"] = norm(rec["homicidios_ultimo_mes"])
    rec["score_tendencia"] = norm(rec["variacion_mensual_pct"].clip(lower=-50, upper=100))
    rec["indice_riesgo"] = (
        rec["score_volumen"] * 0.40
        + rec["score_reciente"] * 0.20
        + rec["score_tendencia"] * 0.20
        + rec["pct_arma_fuego"] * 0.10
        + rec["pct_lugar_publico"] * 0.10
    ).round(1)

    def nivel(score: float) -> str:
        if score >= 70:
            return "Alto"
        if score >= 40:
            return "Medio"
        return "Bajo"

    rec["nivel_riesgo"] = rec["indice_riesgo"].apply(nivel)

    q_alto = rec["total_homicidios"].quantile(0.75)
    q_medio = rec["total_homicidios"].quantile(0.5)

    def accion(row: pd.Series) -> str:
        if row["total_homicidios"] >= q_alto or row["variacion_mensual_pct"] >= 25:
            return "Priorizar intervencion"
        if row["total_homicidios"] >= q_medio:
            return "Mantener monitoreo reforzado"
        return "Monitoreo preventivo"

    def recomendacion(row: pd.Series) -> str:
        if row["accion"] == "Priorizar intervencion":
            return "Concentrar inteligencia territorial, patrullaje focalizado y control de armas."
        if row["accion"] == "Mantener monitoreo reforzado":
            return "Revisar horarios criticos y sostener seguimiento semanal de cantones afectados."
        return "Mantener vigilancia situacional y activar alertas ante crecimiento mensual."

    rec["accion"] = rec.apply(accion, axis=1)
    rec["recomendacion"] = rec.apply(recomendacion, axis=1)
    rec = rec.reset_index().sort_values("indice_riesgo", ascending=False)
    return rec


if __name__ == "__main__":
    REPORTS.mkdir(parents=True, exist_ok=True)
    recomendaciones = generar_recomendaciones()
    recomendaciones.to_csv(REPORTS / "recomendaciones_estrategicas.csv", index=False, encoding="utf-8-sig")
    recomendaciones[
        [
            "provincia",
            "indice_riesgo",
            "nivel_riesgo",
            "total_homicidios",
            "homicidios_ultimo_mes",
            "variacion_mensual_pct",
            "pct_arma_fuego",
            "pct_lugar_publico",
            "accion",
            "recomendacion",
        ]
    ].to_csv(REPORTS / "riesgo_territorial.csv", index=False, encoding="utf-8-sig")
    resumen = {
        "priorizadas": int((recomendaciones["accion"] == "Priorizar intervencion").sum()),
        "monitoreo_reforzado": int((recomendaciones["accion"] == "Mantener monitoreo reforzado").sum()),
        "monitoreo_preventivo": int((recomendaciones["accion"] == "Monitoreo preventivo").sum()),
    }
    (REPORTS / "recomendaciones_resumen.json").write_text(
        json.dumps(resumen, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print("Recomendaciones generadas: reports/recomendaciones_estrategicas.csv")
