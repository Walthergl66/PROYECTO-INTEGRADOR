import pandas as pd
import plotly.express as px
import streamlit as st

from dashboard.theme import AMBAR, TEAL


def renderizar_simulador(df: pd.DataFrame) -> None:
    st.markdown(
        '<div class="note">Simulador simple para estimar casos evitables bajo escenarios de reduccion porcentual de incidencia. No reemplaza una evaluacion causal.</div>',
        unsafe_allow_html=True,
    )
    col_cfg, col_res = st.columns((8, 12))

    with col_cfg:
        nivel = st.radio("Unidad de simulacion", ["provincia", "canton"], horizontal=True)
        territorio = st.selectbox("Territorio", sorted(df[nivel].dropna().unique()))
        reduccion = st.slider("Reduccion esperada de incidencia", 1, 40, 10, step=1)
        horizonte = st.slider("Horizonte de evaluacion (meses)", 1, 12, 3, step=1)
        incluir_arma = st.checkbox("Enfocar solo casos con arma de fuego", value=False)

    base = df[df[nivel] == territorio].copy()
    if incluir_arma:
        base = base[base["arma"] == "ARMA DE FUEGO"]

    mensual = base.groupby(["mes", "mes_nombre"], as_index=False)["total_homicidios"].sum()
    promedio_mensual = float(mensual["total_homicidios"].mean()) if len(mensual) else 0
    casos_esperados = promedio_mensual * horizonte
    casos_evitar = casos_esperados * reduccion / 100
    casos_post = casos_esperados - casos_evitar

    with col_res:
        a, b, c = st.columns(3)
        a.metric("Casos esperados", f"{casos_esperados:.1f}", f"{horizonte} meses")
        b.metric("Casos evitables", f"{casos_evitar:.1f}", f"-{reduccion}%")
        c.metric("Escenario posterior", f"{casos_post:.1f}", "estimado")

        escenario = pd.DataFrame(
            {
                "Escenario": ["Base esperada", "Con intervencion"],
                "Casos": [casos_esperados, casos_post],
            }
        )
        fig = px.bar(
            escenario,
            x="Escenario",
            y="Casos",
            color="Escenario",
            color_discrete_sequence=[AMBAR, TEAL],
            title=f"Impacto estimado en {territorio}",
            text_auto=".1f",
        )
        fig.update_layout(height=330, showlegend=False)
        st.plotly_chart(fig, width="stretch")

    st.subheader("Serie historica usada como linea base")
    fig = px.bar(
        mensual,
        x="mes_nombre",
        y="total_homicidios",
        title=f"Incidencia mensual observada - {territorio}",
        labels={"mes_nombre": "", "total_homicidios": "Homicidios"},
        color_discrete_sequence=[TEAL],
    )
    fig.update_layout(height=330)
    st.plotly_chart(fig, width="stretch")
