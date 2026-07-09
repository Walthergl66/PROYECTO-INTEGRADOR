"""ETL principal de SafeAnalytics EC.

Lee el Excel oficial de homicidios intencionales, normaliza tipos y genera un
modelo estrella consumible por Streamlit y Power BI.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
FUENTE = RAIZ / "mdi_homicidiosintencionalse_pm_2026_enero_mayo.xlsx"
RAW = RAIZ / "data" / "raw"
PROCESSED = RAIZ / "data" / "processed"


def _limpiar_texto(serie: pd.Series) -> pd.Series:
    return (
        serie.astype("string")
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
        .fillna("SIN_DATO")
    )


def _coord(serie: pd.Series) -> pd.Series:
    return pd.to_numeric(
        serie.astype("string").str.replace(",", ".", regex=False),
        errors="coerce",
    )


def _edad(serie: pd.Series) -> pd.Series:
    return pd.to_numeric(serie.replace({"SIN_DATO": np.nan, "NO DETERMINADO": np.nan}), errors="coerce")


def cargar_fuente() -> pd.DataFrame:
    if not FUENTE.exists():
        raise FileNotFoundError(f"No se encontro el archivo fuente: {FUENTE}")
    df = pd.read_excel(FUENTE, sheet_name="1. Homicidios Intencionales")
    df.columns = [c.strip() for c in df.columns]
    return df


def transformar() -> dict[str, pd.DataFrame]:
    df = cargar_fuente()

    texto_cols = df.select_dtypes(include=["object", "string"]).columns
    for col in texto_cols:
        df[col] = _limpiar_texto(df[col])

    df["fecha_infraccion"] = pd.to_datetime(df["fecha_infraccion"], errors="coerce")
    hora = pd.to_datetime(df["hora_infraccion"].astype("string"), format="%H:%M:%S", errors="coerce")
    df["hora"] = hora.dt.hour.fillna(0).astype(int)
    df["franja_horaria"] = pd.cut(
        df["hora"],
        bins=[-1, 5, 11, 17, 23],
        labels=["Madrugada", "Manana", "Tarde", "Noche"],
    ).astype("string")
    df["edad_num"] = _edad(df["edad"])
    df["latitud"] = _coord(df["coordenada_y"])
    df["longitud"] = _coord(df["coordenada_x"])
    df["id_homicidio"] = np.arange(1, len(df) + 1)
    df["id_fecha"] = df["fecha_infraccion"].dt.strftime("%Y%m%d").astype(int)
    df["id_geografia"] = df["codigo_canton"].astype(str)
    df["id_delito"] = (
        df["arma"] + "|" + df["tipo_arma"] + "|" + df["presunta_motivacion"] + "|" + df["lugar"]
    ).astype("category").cat.codes + 1
    df["id_victima"] = (
        df["sexo"] + "|" + df["genero"] + "|" + df["etnia"] + "|" + df["nacionalidad"]
    ).astype("category").cat.codes + 1

    fechas = pd.date_range(df["fecha_infraccion"].min(), df["fecha_infraccion"].max(), freq="D")
    dim_tiempo = pd.DataFrame({"fecha": fechas})
    dim_tiempo["id_fecha"] = dim_tiempo["fecha"].dt.strftime("%Y%m%d").astype(int)
    dim_tiempo["anio"] = dim_tiempo["fecha"].dt.year
    dim_tiempo["mes"] = dim_tiempo["fecha"].dt.month
    dim_tiempo["mes_nombre"] = dim_tiempo["fecha"].dt.month_name(locale="C")
    dim_tiempo["dia"] = dim_tiempo["fecha"].dt.day
    dim_tiempo["dia_semana"] = dim_tiempo["fecha"].dt.dayofweek + 1
    dim_tiempo["nombre_dia"] = dim_tiempo["fecha"].dt.day_name(locale="C")
    dim_tiempo["semana"] = dim_tiempo["fecha"].dt.isocalendar().week.astype(int)

    dim_geografia = (
        df[
            [
                "id_geografia",
                "codigo_provincia",
                "provincia",
                "codigo_canton",
                "canton",
                "zona",
                "subzona",
                "distrito",
                "circuito",
                "subcircuito",
            ]
        ]
        .drop_duplicates("id_geografia")
        .sort_values(["provincia", "canton"])
    )

    dim_delito = (
        df[
            [
                "id_delito",
                "tipo_muerte",
                "arma",
                "tipo_arma",
                "presunta_motivacion",
                "presun_motiva_observada",
                "probable_causa_motivada",
                "area_hecho",
                "lugar",
                "tipo_lugar",
            ]
        ]
        .drop_duplicates("id_delito")
        .sort_values("id_delito")
    )

    dim_victima = (
        df[
            [
                "id_victima",
                "sexo",
                "genero",
                "etnia",
                "estado_civil",
                "nacionalidad",
                "discapacidad",
                "profesion_registro_civil",
                "instruccion",
            ]
        ]
        .drop_duplicates("id_victima")
        .sort_values("id_victima")
    )

    fact = df[
        [
            "id_homicidio",
            "id_fecha",
            "id_geografia",
            "id_delito",
            "id_victima",
            "fecha_infraccion",
            "hora",
            "franja_horaria",
            "edad_num",
            "latitud",
            "longitud",
        ]
    ].copy()
    fact["total_homicidios"] = 1

    return {
        "fact_homicidios": fact,
        "dim_tiempo": dim_tiempo,
        "dim_geografia": dim_geografia,
        "dim_delito": dim_delito,
        "dim_victima": dim_victima,
    }


def guardar(tablas: dict[str, pd.DataFrame]) -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    PROCESSED.mkdir(parents=True, exist_ok=True)
    fuente_csv = RAW / "homicidios_intencionales_2026_enero_mayo.csv"
    cargar_fuente().to_csv(fuente_csv, index=False, encoding="utf-8-sig")

    for nombre, tabla in tablas.items():
        tabla.to_csv(PROCESSED / f"{nombre}.csv", index=False, encoding="utf-8-sig")

    fact = tablas["fact_homicidios"]
    calidad = {
        "fuente": FUENTE.name,
        "registros": int(len(fact)),
        "periodo": {
            "inicio": str(pd.to_datetime(fact["fecha_infraccion"]).min().date()),
            "fin": str(pd.to_datetime(fact["fecha_infraccion"]).max().date()),
        },
        "tablas_generadas": {k: {"filas": int(len(v)), "columnas": int(v.shape[1])} for k, v in tablas.items()},
        "nulos_fact_pct": (fact.isna().mean() * 100).round(2).to_dict(),
        "coordenadas_validas_pct": round(float(fact[["latitud", "longitud"]].notna().all(axis=1).mean() * 100), 2),
    }
    (PROCESSED / "reporte_calidad.json").write_text(
        json.dumps(calidad, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


if __name__ == "__main__":
    guardar(transformar())
    print("ETL completado: data/processed actualizado.")
