import pandas as pd
import plotly.express as px
import streamlit as st

from dashboard.theme import AMBAR, TEAL


def renderizar_ejecutivo(df: pd.DataFrame, recomendaciones: pd.DataFrame) -> None:
    st.markdown(
        '<div class="note">Vista para direccion: incidencia acumulada, tendencia mensual y territorios que requieren priorizacion.</div>',
        unsafe_allow_html=True,
    )
    mensual = df.groupby(["mes", "mes_nombre"], as_index=False)["total_homicidios"].sum()
    col1, col2 = st.columns((11, 9))
    fig = px.line(
        mensual,
        x="mes_nombre",
        y="total_homicidios",
        markers=True,
        title="Evolucion mensual de homicidios intencionales",
        labels={"mes_nombre": "", "total_homicidios": "Homicidios"},
    )
    fig.update_traces(line_width=3, marker_size=9)
    fig.update_layout(height=390)
    col1.plotly_chart(fig, width="stretch")

    ranking = df["provincia"].value_counts().head(10).sort_values()
    fig = px.bar(
        ranking,
        orientation="h",
        title="Top 10 provincias por incidencia",
        labels={"value": "Homicidios", "index": "Provincia"},
        color_discrete_sequence=[TEAL],
    )
    fig.update_layout(height=390, showlegend=False)
    col2.plotly_chart(fig, width="stretch")

    st.subheader("Prioridades estrategicas")
    top = recomendaciones.sort_values("total_homicidios", ascending=False).head(5)
    cols = st.columns(5)
    for col, (_, row) in zip(cols, top.iterrows()):
        col.markdown(
            f"""
<div class="risk-card">
  <strong>{row['provincia']}</strong><br>
  {int(row['total_homicidios'])} casos<br>
  <span style="color:{AMBAR};font-weight:700">{row['accion']}</span>
</div>
""",
            unsafe_allow_html=True,
        )
