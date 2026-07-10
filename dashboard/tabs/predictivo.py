import pandas as pd
import plotly.express as px
import streamlit as st

from dashboard.theme import AMBAR, TEAL


def renderizar_predictivo(df: pd.DataFrame, metricas: dict, recomendaciones: pd.DataFrame) -> None:
    st.markdown(
        f"""
<div class="note">
  <b>Modelo desplegado:</b> {metricas.get('modelo')}<br>
  <b>MAE:</b> {metricas.get('mae')} | <b>RMSE:</b> {metricas.get('rmse')} | <b>R2:</b> {metricas.get('r2')}<br>
  {metricas.get('nota')}
</div>
""",
        unsafe_allow_html=True,
    )

    comparacion = metricas.get("comparacion_modelos")
    if comparacion:
        st.subheader("Comparacion de modelos (misma particion temporal)")
        tabla = pd.DataFrame(comparacion)[["modelo", "mae", "rmse", "r2"]]
        tabla.columns = ["Modelo", "MAE", "RMSE", "R2"]
        st.dataframe(tabla, hide_index=True, width="stretch")
        st.caption(
            "La Regresion Lineal (algoritmo clasico) obtiene un desempeno equivalente al baseline. "
            "Por ello se mantiene el baseline explicable como modelo desplegado."
        )

    coefs = metricas.get("regresion_lineal", {}).get("coeficientes_top")
    if coefs:
        with st.expander("Explicabilidad (XAI): variables con mayor peso en la Regresion Lineal"):
            imp = pd.DataFrame({"variable": list(coefs.keys()), "coeficiente": list(coefs.values())})
            fig_imp = px.bar(
                imp.sort_values("coeficiente"),
                x="coeficiente",
                y="variable",
                orientation="h",
                color="coeficiente",
                color_continuous_scale="RdBu_r",
                title="Peso de cada variable en la prediccion (coeficientes)",
            )
            fig_imp.update_layout(height=380, showlegend=False, coloraxis_showscale=False)
            st.plotly_chart(fig_imp, width="stretch")

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
