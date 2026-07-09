import pandas as pd
import plotly.express as px
import streamlit as st

from dashboard.theme import AZUL, TEAL


def renderizar_temporal(df: pd.DataFrame) -> None:
    col1, col2 = st.columns(2)
    hora = df.groupby("hora", as_index=False)["total_homicidios"].sum()
    fig = px.bar(
        hora,
        x="hora",
        y="total_homicidios",
        title="Incidencia por hora del dia",
        labels={"hora": "Hora", "total_homicidios": "Homicidios"},
        color_discrete_sequence=[AZUL],
    )
    fig.update_layout(height=390)
    col1.plotly_chart(fig, width="stretch")

    orden = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", "Domingo"]
    dia = df.groupby("dia_semana_nombre", as_index=False)["total_homicidios"].sum()
    dia["dia_semana_nombre"] = pd.Categorical(dia["dia_semana_nombre"], categories=orden, ordered=True)
    dia = dia.sort_values("dia_semana_nombre")
    fig = px.line(
        dia,
        x="dia_semana_nombre",
        y="total_homicidios",
        markers=True,
        title="Patron por dia de semana",
        labels={"dia_semana_nombre": "", "total_homicidios": "Homicidios"},
        color_discrete_sequence=[TEAL],
    )
    fig.update_layout(height=390)
    col2.plotly_chart(fig, width="stretch")

    matriz = df.pivot_table(
        index="dia_semana_nombre",
        columns="hora",
        values="total_homicidios",
        aggfunc="sum",
        fill_value=0,
    ).reindex(orden)
    fig = px.imshow(
        matriz,
        title="Mapa de calor: dia vs hora",
        labels=dict(x="Hora", y="Dia", color="Casos"),
        color_continuous_scale=["#F1FAF9", "#0F766E", "#12355B"],
    )
    fig.update_layout(height=440)
    st.plotly_chart(fig, width="stretch")
