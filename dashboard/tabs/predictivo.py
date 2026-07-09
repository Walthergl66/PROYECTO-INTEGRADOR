import pandas as pd
import plotly.express as px
import streamlit as st

from dashboard.theme import AMBAR, TEAL


def renderizar_predictivo(df: pd.DataFrame, metricas: dict, recomendaciones: pd.DataFrame) -> None:
    st.markdown(
        f"""
<div class="note">
  <b>Modelo:</b> {metricas.get('modelo')}<br>
  <b>MAE:</b> {metricas.get('mae')} | <b>RMSE:</b> {metricas.get('rmse')}<br>
  {metricas.get('nota')}
</div>
""",
        unsafe_allow_html=True,
    )

    fig = px.scatter(
        recomendaciones,
        x="homicidios_ultimo_mes",
        y="variacion_mensual_pct",
        size="total_homicidios",
        color="accion",
        hover_name="provincia",
        title="Matriz de priorizacion: volumen reciente vs variacion mensual",
        labels={
            "homicidios_ultimo_mes": "Homicidios ultimo mes",
            "variacion_mensual_pct": "Variacion mensual %",
        },
        color_discrete_sequence=[TEAL, AMBAR, "#64748B"],
    )
    fig.update_layout(height=430)
    st.plotly_chart(fig, width="stretch")

    st.subheader("Recomendaciones por provincia")
    st.dataframe(
        recomendaciones[
            [
                "provincia",
                "total_homicidios",
                "homicidios_ultimo_mes",
                "variacion_mensual_pct",
                "pct_arma_fuego",
                "accion",
                "recomendacion",
            ]
        ],
        width="stretch",
        hide_index=True,
    )
