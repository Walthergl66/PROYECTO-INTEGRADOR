import json
from pathlib import Path

import streamlit as st

RAIZ = Path(__file__).resolve().parents[2]


def renderizar_metodologia(metricas: dict) -> None:
    calidad = json.loads((RAIZ / "data" / "processed" / "reporte_calidad.json").read_text(encoding="utf-8"))

    st.markdown(
        f"""
<div class="note">
  <b>Fuente:</b> {calidad['fuente']}<br>
  <b>Periodo analizado:</b> {calidad['periodo']['inicio']} a {calidad['periodo']['fin']}<br>
  <b>Registros procesados:</b> {calidad['registros']} | <b>Coordenadas validas:</b> {calidad['coordenadas_validas_pct']}%
</div>
""",
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Modelo dimensional")
        st.markdown(
            """
- **Tabla de hechos:** homicidios intencionales.
- **Dimensiones:** tiempo, geografia, delito y victima.
- **Granularidad:** un registro por evento procesado desde el Excel original.
- **Uso:** filtrar, agregar y comparar incidencia por territorio, fecha, arma, lugar y perfil de victima.
"""
        )
    with col2:
        st.subheader("Modelo predictivo")
        st.markdown(
            f"""
- **Tipo:** {metricas.get('modelo')}.
- **Objetivo:** {metricas.get('objetivo')}.
- **MAE:** {metricas.get('mae')} | **RMSE:** {metricas.get('rmse')}.
- **Alcance:** baseline exploratorio para priorizacion, no pronostico operativo definitivo.
"""
        )

    st.subheader("Criterios de interpretacion")
    st.markdown(
        """
- Los indicadores muestran concentracion territorial, patrones horarios y factores predominantes.
- Las recomendaciones priorizan provincias con mayor volumen, crecimiento reciente y riesgo compuesto.
- Los resultados deben revisarse con criterio institucional, contexto territorial y validacion de campo.
"""
    )

    with st.expander("Control de calidad de datos"):
        st.json(calidad)
