import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from dashboard.data import cargar_poblacion

RAIZ = Path(__file__).resolve().parents[2]
REPORTS = RAIZ / "reports"


def renderizar_metodologia(metricas: dict) -> None:
    calidad = json.loads((RAIZ / "data" / "processed" / "reporte_calidad.json").read_text(encoding="utf-8"))
    poblacion = cargar_poblacion()

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

    st.subheader("Fuentes de datos")
    st.markdown(
        f"""
- **Fuente principal (Excel MDI):** `{calidad['fuente']}` — dataset oficial de homicidios
  intencionales del Ministerio del Interior, enero-mayo 2026.
- **Fuente secundaria (API publica):** Banco Mundial, indicador `SP.POP.TOTL` (poblacion
  de Ecuador). Se usa para calcular la tasa por 100.000 habitantes.
  - Poblacion utilizada: **{poblacion['poblacion']:,}** habitantes ({poblacion['años']}).
  - Origen del dato en esta sesion: `{poblacion.get('origen', 'n/d')}` (api / cache / respaldo).
- **Nota:** el dataset del MDI tambien se publica en Datos Abiertos Ecuador (CKAN), pero su
  endpoint `/api/` esta restringido por el portal (responde 403), por lo que se emplea el
  archivo oficial descargado y se complementa con la API del Banco Mundial.
"""
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
- **MAE:** {metricas.get('mae')} | **RMSE:** {metricas.get('rmse')} | **R2:** {metricas.get('r2')}.
- **Comparacion:** validado contra una Regresion Lineal (scikit-learn) con desempeno equivalente.
- **Alcance:** baseline exploratorio para priorizacion, no pronostico operativo definitivo.
"""
        )

    _render_eda_estadistico()

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


def _render_eda_estadistico() -> None:
    """Medidas de dispersion y matriz de correlacion del EDA."""
    eda_path = REPORTS / "eda_resultados.json"
    corr_path = REPORTS / "correlacion_provincias.csv"
    if not eda_path.exists():
        return
    eda = json.loads(eda_path.read_text(encoding="utf-8"))

    dispersion = eda.get("dispersion")
    if dispersion:
        st.subheader("Medidas de dispersion")
        etiquetas = {
            "edad_victimas": "Edad de victimas (años)",
            "incidencia_diaria_nacional": "Incidencia diaria nacional",
            "incidencia_por_provincia": "Incidencia por provincia",
        }
        filas = []
        for clave, nombre in etiquetas.items():
            d = dispersion.get(clave, {})
            filas.append(
                {
                    "Variable": nombre,
                    "Media": d.get("media"),
                    "Mediana": d.get("mediana"),
                    "Desv. est.": d.get("desviacion_estandar"),
                    "Minimo": d.get("minimo"),
                    "Maximo": d.get("maximo"),
                    "CV (%)": d.get("coef_variacion_pct"),
                }
            )
        st.dataframe(pd.DataFrame(filas), hide_index=True, width="stretch")
        st.caption(
            "El coeficiente de variacion (CV) alto en la incidencia por provincia refleja una "
            "distribucion muy asimetrica: pocos territorios concentran la mayor parte de los casos."
        )

    if corr_path.exists():
        st.subheader("Matriz de correlacion (indicadores por provincia)")
        corr = pd.read_csv(corr_path, index_col=0)
        fig = px.imshow(
            corr,
            text_auto=".2f",
            color_continuous_scale="RdBu_r",
            zmin=-1,
            zmax=1,
            aspect="auto",
            title="Correlacion de Pearson entre indicadores provinciales",
        )
        fig.update_layout(height=460)
        st.plotly_chart(fig, width="stretch")
        st.caption(
            "La correlacion indica asociacion, no causalidad. Ej.: mayor volumen se asocia con mas "
            "cantones afectados (r=0,91) e incidencia reciente (r=0,99)."
        )
