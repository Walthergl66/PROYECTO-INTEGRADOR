import pandas as pd
import plotly.express as px
import streamlit as st

from dashboard.theme import AMBAR, ROJO, TEAL


def renderizar_caracterizacion(df: pd.DataFrame) -> None:
    col1, col2 = st.columns(2)
    arma = df["arma"].value_counts().reset_index()
    arma.columns = ["arma", "casos"]
    fig = px.pie(
        arma,
        names="arma",
        values="casos",
        title="Distribucion por tipo de arma",
        color_discrete_sequence=[TEAL, AMBAR, ROJO, "#64748B", "#94A3B8"],
        hole=0.48,
    )
    fig.update_layout(height=400)
    col1.plotly_chart(fig, width="stretch")

    motivacion = df["presunta_motivacion"].value_counts().head(10).sort_values()
    fig = px.bar(
        motivacion,
        orientation="h",
        title="Presunta motivacion",
        labels={"value": "Homicidios", "index": "Motivacion"},
        color_discrete_sequence=[TEAL],
    )
    fig.update_layout(height=400, showlegend=False)
    col2.plotly_chart(fig, width="stretch")

    col3, col4 = st.columns(2)
    sexo = df["sexo"].value_counts().reset_index()
    sexo.columns = ["sexo", "casos"]
    fig = px.pie(sexo, names="sexo", values="casos", title="Victimas por sexo")
    fig.update_layout(height=360)
    col3.plotly_chart(fig, width="stretch")

    edades = df.dropna(subset=["edad_num"])
    fig = px.histogram(
        edades,
        x="edad_num",
        nbins=28,
        title="Distribucion de edad de victimas",
        labels={"edad_num": "Edad"},
        color_discrete_sequence=[AMBAR],
    )
    fig.update_layout(height=360)
    col4.plotly_chart(fig, width="stretch")
