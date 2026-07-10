"""EDA y KPIs ejecutivos de SafeAnalytics EC."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
PROCESSED = RAIZ / "data" / "processed"
REPORTS = RAIZ / "reports"

# Permite importar el modulo de la API publica (Banco Mundial) al ejecutar
# este script de forma directa (python src/analytics/eda.py).
ETL = RAIZ / "src" / "etl"
if str(ETL) not in sys.path:
    sys.path.insert(0, str(ETL))
from poblacion_api import obtener_poblacion_ecuador  # noqa: E402


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


def _resumen_dispersion(serie: pd.Series) -> dict:
    """Medidas de tendencia central y dispersion de una variable numerica."""
    s = serie.dropna().astype(float)
    media = float(s.mean())
    return {
        "n": int(s.size),
        "media": round(media, 2),
        "mediana": round(float(s.median()), 2),
        "desviacion_estandar": round(float(s.std()), 2),
        "varianza": round(float(s.var()), 2),
        "minimo": round(float(s.min()), 2),
        "maximo": round(float(s.max()), 2),
        "rango": round(float(s.max() - s.min()), 2),
        "p25": round(float(s.quantile(0.25)), 2),
        "p75": round(float(s.quantile(0.75)), 2),
        "rango_intercuartil": round(float(s.quantile(0.75) - s.quantile(0.25)), 2),
        "coef_variacion_pct": round(float(s.std() / media * 100), 1) if media else None,
    }


def calcular_dispersion(df: pd.DataFrame) -> dict:
    """Dispersion de las variables clave: edad, incidencia diaria y territorial."""
    edad = df["edad_num"]
    diaria = df.groupby(df["fecha_infraccion"].dt.date)["total_homicidios"].sum()
    por_provincia = df.groupby("provincia")["total_homicidios"].sum()
    return {
        "edad_victimas": _resumen_dispersion(edad),
        "incidencia_diaria_nacional": _resumen_dispersion(diaria),
        "incidencia_por_provincia": _resumen_dispersion(por_provincia),
    }


def calcular_correlacion(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Construye indicadores numericos por provincia y su matriz de correlacion.

    Responde a la pregunta "que variables se mueven juntas": relaciona el volumen
    de homicidios por provincia con el porcentaje de arma de fuego, el perfil de
    la victima, la amplitud territorial y la incidencia reciente. La correlacion
    describe asociacion, no causalidad.
    """
    ultimo_mes = int(df["mes"].max())
    filas = []
    for provincia, g in df.groupby("provincia"):
        edad_media = g["edad_num"].dropna().mean()
        filas.append(
            {
                "provincia": provincia,
                "total_homicidios": int(g["total_homicidios"].sum()),
                "pct_arma_fuego": round((g["arma"] == "ARMA DE FUEGO").mean() * 100, 2),
                "pct_hombres": round((g["sexo"] == "HOMBRE").mean() * 100, 2),
                "edad_promedio": round(float(edad_media), 2) if pd.notna(edad_media) else None,
                "cantones_afectados": int(g["canton"].nunique()),
                "homicidios_ultimo_mes": int(g.loc[g["mes"] == ultimo_mes, "total_homicidios"].sum()),
            }
        )
    tabla = pd.DataFrame(filas).set_index("provincia")
    corr = tabla.corr(numeric_only=True).round(3)

    pares = {
        "total_vs_cantones": float(corr.loc["total_homicidios", "cantones_afectados"]),
        "total_vs_ultimo_mes": float(corr.loc["total_homicidios", "homicidios_ultimo_mes"]),
        "total_vs_pct_arma_fuego": float(corr.loc["total_homicidios", "pct_arma_fuego"]),
        "arma_fuego_vs_edad": float(corr.loc["pct_arma_fuego", "edad_promedio"]),
    }
    return tabla, corr, pares


def calcular_tasa_100k(df: pd.DataFrame, total: int) -> dict:
    """Calcula la tasa de homicidios por 100.000 habitantes.

    Usa la poblacion de Ecuador obtenida de la API publica del Banco Mundial.
    Como el dataset cubre solo enero-mayo 2026, se reporta la tasa del periodo
    y una estimacion anualizada proyectando la incidencia diaria a 365 dias.
    """
    poblacion = obtener_poblacion_ecuador()
    hab = poblacion["poblacion"]
    dias_periodo = (df["fecha_infraccion"].max() - df["fecha_infraccion"].min()).days + 1
    tasa_periodo = total / hab * 100_000
    tasa_anualizada = (total * 365 / dias_periodo) / hab * 100_000
    return {
        "poblacion_ecuador": hab,
        "años_poblacion": poblacion["años"],
        "fuente_poblacion": poblacion["fuente"],
        "origen_poblacion": poblacion["origen"],
        "dias_periodo": int(dias_periodo),
        "tasa_100k_periodo": round(tasa_periodo, 2),
        "tasa_100k_anualizada": round(tasa_anualizada, 2),
    }


if __name__ == "__main__":
    REPORTS.mkdir(parents=True, exist_ok=True)
    base = cargar_base()
    resultados = calcular_kpis(base)
    resultados.update(calcular_tasa_100k(base, resultados["total_homicidios"]))
    resultados["dispersion"] = calcular_dispersion(base)

    indicadores_prov, matriz_corr, pares_corr = calcular_correlacion(base)
    resultados["correlacion"] = {
        "matriz": {c: {i: (None if pd.isna(v) else float(v)) for i, v in col.items()}
                   for c, col in matriz_corr.items()},
        "pares_destacados": {k: round(v, 3) for k, v in pares_corr.items()},
    }

    indicadores_prov.to_csv(REPORTS / "indicadores_provincia.csv", encoding="utf-8-sig")
    matriz_corr.to_csv(REPORTS / "correlacion_provincias.csv", encoding="utf-8-sig")
    (REPORTS / "eda_resultados.json").write_text(
        json.dumps(resultados, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print("EDA completado: reports/eda_resultados.json")
    print(
        f"Tasa anualizada estimada: {resultados['tasa_100k_anualizada']} por 100.000 hab. "
        f"(poblacion {resultados['poblacion_ecuador']:,}, origen: {resultados['origen_poblacion']})"
    )
    disp = resultados["dispersion"]["incidencia_por_provincia"]
    print(
        f"Dispersion incidencia por provincia -> media {disp['media']}, "
        f"desv. est. {disp['desviacion_estandar']}, CV {disp['coef_variacion_pct']}%"
    )
    print(f"Correlaciones destacadas: {resultados['correlacion']['pares_destacados']}")
