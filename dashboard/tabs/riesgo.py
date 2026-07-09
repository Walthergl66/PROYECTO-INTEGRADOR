import pandas as pd
import plotly.express as px
import streamlit as st

from dashboard.theme import AMBAR, ROJO, TEAL


def _es_lugar_publico(serie: pd.Series) -> pd.Series:
    normalizada = serie.astype(str).str.normalize("NFKD").str.encode("ascii", errors="ignore").str.decode("ascii")
    return normalizada.str.upper().eq("PUBLICO")


def _normalizar(serie: pd.Series) -> pd.Series:
    rango = serie.max() - serie.min()
    if rango == 0:
        return pd.Series(50, index=serie.index)
    return (serie - serie.min()) / rango * 100


def calcular_riesgo_territorial(df: pd.DataFrame, nivel: str = "provincia") -> pd.DataFrame:
    max_mes = int(df["mes"].max())
    grupo = df.groupby(nivel).agg(
        total_homicidios=("total_homicidios", "sum"),
        pct_arma_fuego=("arma", lambda s: (s == "ARMA DE FUEGO").mean() * 100),
        pct_lugar_publico=("tipo_lugar", lambda s: _es_lugar_publico(s).mean() * 100),
        hora_critica=("hora", lambda s: int(s.value_counts().idxmax())),
    )
    ultimo = df[df["mes"] == max_mes].groupby(nivel)["total_homicidios"].sum()
    previo = df[df["mes"] == max_mes - 1].groupby(nivel)["total_homicidios"].sum()
    riesgo = grupo.join(ultimo.rename("homicidios_ultimo_mes"), how="left").join(
        previo.rename("homicidios_mes_previo"), how="left"
    ).fillna(0)
    riesgo["variacion_mensual_pct"] = (
        (riesgo["homicidios_ultimo_mes"] - riesgo["homicidios_mes_previo"])
        / riesgo["homicidios_mes_previo"].replace(0, 1)
        * 100
    ).round(1)
    riesgo["indice_riesgo"] = (
        _normalizar(riesgo["total_homicidios"]) * 0.42
        + _normalizar(riesgo["homicidios_ultimo_mes"]) * 0.22
        + _normalizar(riesgo["variacion_mensual_pct"].clip(-50, 100)) * 0.18
        + riesgo["pct_arma_fuego"] * 0.10
        + riesgo["pct_lugar_publico"] * 0.08
    ).round(1)
    riesgo["nivel_riesgo"] = pd.cut(
        riesgo["indice_riesgo"],
        bins=[-1, 39.99, 69.99, 100],
        labels=["Bajo", "Medio", "Alto"],
    ).astype(str)
    return riesgo.reset_index().sort_values("indice_riesgo", ascending=False)


def renderizar_riesgo(df: pd.DataFrame) -> None:
    st.markdown(
        '<div class="note">Indice compuesto: volumen historico, incidencia reciente, variacion mensual, uso de arma de fuego y ocurrencia en espacios publicos.</div>',
        unsafe_allow_html=True,
    )
    nivel = st.radio("Nivel territorial", ["provincia", "canton"], horizontal=True)
    riesgo = calcular_riesgo_territorial(df, nivel)

    col1, col2 = st.columns((11, 9))
    top = riesgo.head(15).sort_values("indice_riesgo")
    color_map = {"Alto": ROJO, "Medio": AMBAR, "Bajo": TEAL}
    fig = px.bar(
        top,
        x="indice_riesgo",
        y=nivel,
        color="nivel_riesgo",
        orientation="h",
        color_discrete_map=color_map,
        title=f"Indice de riesgo territorial por {nivel}",
        labels={"indice_riesgo": "Indice 0-100", nivel: nivel.title(), "nivel_riesgo": "Nivel"},
    )
    fig.update_layout(height=450)
    col1.plotly_chart(fig, width="stretch")

    fig = px.scatter(
        riesgo,
        x="homicidios_ultimo_mes",
        y="variacion_mensual_pct",
        size="total_homicidios",
        color="nivel_riesgo",
        hover_name=nivel,
        color_discrete_map=color_map,
        title="Matriz ejecutiva: incidencia reciente vs crecimiento",
        labels={
            "homicidios_ultimo_mes": "Homicidios ultimo mes",
            "variacion_mensual_pct": "Variacion mensual %",
            "nivel_riesgo": "Nivel",
        },
    )
    fig.update_layout(height=450)
    col2.plotly_chart(fig, width="stretch")

    st.subheader("Tabla de priorizacion")
    st.dataframe(
        riesgo[
            [
                nivel,
                "nivel_riesgo",
                "indice_riesgo",
                "total_homicidios",
                "homicidios_ultimo_mes",
                "variacion_mensual_pct",
                "pct_arma_fuego",
                "pct_lugar_publico",
                "hora_critica",
            ]
        ],
        width="stretch",
        hide_index=True,
    )
