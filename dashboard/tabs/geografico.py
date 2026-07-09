import pandas as pd
import plotly.express as px
import streamlit as st

from dashboard.theme import AMBAR, TEAL


def renderizar_geografico(df: pd.DataFrame) -> None:
    col1, col2 = st.columns((10, 10))
    puntos = df.dropna(subset=["latitud", "longitud"]).copy()
    muestra = puntos.sample(min(len(puntos), 1200), random_state=42) if len(puntos) else puntos
    fig = px.scatter_mapbox(
        muestra,
        lat="latitud",
        lon="longitud",
        color="provincia",
        hover_name="canton",
        hover_data=["zona", "arma", "fecha_infraccion"],
        zoom=5,
        height=430,
        title="Distribucion georreferenciada de eventos",
    )
    fig.update_layout(mapbox_style="open-street-map", margin=dict(l=0, r=0, t=50, b=0))
    col1.plotly_chart(fig, width="stretch")

    cantones = df["canton"].value_counts().head(15).sort_values()
    fig = px.bar(
        cantones,
        orientation="h",
        title="Cantones con mayor incidencia",
        labels={"value": "Homicidios", "index": "Canton"},
        color_discrete_sequence=[AMBAR],
    )
    fig.update_layout(height=430, showlegend=False)
    col2.plotly_chart(fig, width="stretch")

    zona = df.groupby(["zona", "provincia"], as_index=False)["total_homicidios"].sum()
    fig = px.treemap(
        zona,
        path=["zona", "provincia"],
        values="total_homicidios",
        title="Concentracion por zona y provincia",
        color="total_homicidios",
        color_continuous_scale=["#DFF7F4", TEAL],
    )
    fig.update_layout(height=420)
    st.plotly_chart(fig, width="stretch")
