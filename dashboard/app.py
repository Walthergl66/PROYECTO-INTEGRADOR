"""Dashboard ejecutivo SafeAnalytics EC.

Ejecutar:
    streamlit run dashboard/app.py
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

import streamlit as st

from dashboard.components import renderizar_hero, tarjeta_kpi
from dashboard.data import (
    cargar_base,
    cargar_kpis,
    cargar_modelo,
    cargar_poblacion,
    cargar_recomendaciones,
    cargar_tablas,
)
from dashboard.tabs import (
    renderizar_alertas,
    renderizar_caracterizacion,
    renderizar_datos,
    renderizar_ejecutivo,
    renderizar_geografico,
    renderizar_metodologia,
    renderizar_predictivo,
    renderizar_riesgo,
    renderizar_simulador,
    renderizar_temporal,
)
from dashboard.theme import inyectar_css, registrar_tema_plotly

st.set_page_config(
    page_title="SafeAnalytics EC",
    page_icon="SA",
    layout="wide",
)
registrar_tema_plotly()
inyectar_css()

df = cargar_base()
cargar_kpis()
metricas_modelo = cargar_modelo()
recomendaciones = cargar_recomendaciones()
poblacion = cargar_poblacion()

renderizar_hero()

with st.sidebar:
    st.markdown("### Filtros")
    provincias = st.multiselect(
        "Provincia",
        sorted(df["provincia"].dropna().unique()),
        default=sorted(df["provincia"].dropna().unique()),
    )
    meses = st.multiselect(
        "Mes",
        sorted(df["mes"].unique()),
        default=sorted(df["mes"].unique()),
        format_func=lambda x: {1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo"}.get(x, x),
    )
    armas = st.multiselect(
        "Arma",
        sorted(df["arma"].dropna().unique()),
        default=sorted(df["arma"].dropna().unique()),
    )
    st.divider()
    st.caption("Datos reales del Excel MDI enero-mayo 2026. El modelo predictivo es exploratorio.")

df_f = df[df["provincia"].isin(provincias) & df["mes"].isin(meses) & df["arma"].isin(armas)]
if df_f.empty:
    st.warning("No hay datos para los filtros seleccionados.")
    st.stop()

total = int(df_f["total_homicidios"].sum())
arma_fuego = (df_f["arma"] == "ARMA DE FUEGO").mean() * 100
hombres = (df_f["sexo"] == "HOMBRE").mean() * 100
edad = df_f["edad_num"].dropna().mean()
prov_top = df_f["provincia"].value_counts().idxmax()

c1, c2, c3, c4, c5 = st.columns(5)
tarjeta_kpi(c1, "Total homicidios", f"{total:,}".replace(",", "."), "Registros filtrados")
tarjeta_kpi(c2, "Arma de fuego", f"{arma_fuego:.1f}%", "Participacion")
tarjeta_kpi(c3, "Victimas hombres", f"{hombres:.1f}%", "Perfil predominante")
tarjeta_kpi(c4, "Edad promedio", f"{edad:.1f}", "Años")
tarjeta_kpi(c5, "Provincia critica", prov_top, "Mayor incidencia")

# Tasa por 100.000 habitantes usando poblacion de la API publica del Banco Mundial.
# Se calcula a nivel nacional (dataset completo) y se anualiza porque el periodo
# disponible es enero-mayo 2026.
total_nacional = int(df["total_homicidios"].sum())
dias_periodo = (df["fecha_infraccion"].max() - df["fecha_infraccion"].min()).days + 1
tasa_anualizada = (total_nacional * 365 / dias_periodo) / poblacion["poblacion"] * 100_000
hab_fmt = f"{poblacion['poblacion']:,}".replace(",", ".")
st.markdown(
    f"""
<div class="note">
  <b>Tasa nacional estimada:</b> {tasa_anualizada:.1f} homicidios por 100.000 habitantes/año
  &nbsp;|&nbsp; Poblacion Ecuador: {hab_fmt} ({poblacion['años']})
  &nbsp;|&nbsp; Fuente: {poblacion['fuente']}
</div>
""",
    unsafe_allow_html=True,
)

st.markdown("### Alertas ejecutivas")
renderizar_alertas(df_f)

tabs = st.tabs(
    [
        "Ejecutivo",
        "Riesgo territorial",
        "Simulador",
        "Geografico",
        "Temporal",
        "Caracterizacion",
        "Predictiva",
        "Datos",
        "Metodologia",
    ]
)
with tabs[0]:
    renderizar_ejecutivo(df_f, recomendaciones[recomendaciones["provincia"].isin(provincias)])
with tabs[1]:
    renderizar_riesgo(df_f)
with tabs[2]:
    renderizar_simulador(df_f)
with tabs[3]:
    renderizar_geografico(df_f)
with tabs[4]:
    renderizar_temporal(df_f)
with tabs[5]:
    renderizar_caracterizacion(df_f)
with tabs[6]:
    renderizar_predictivo(df_f, metricas_modelo, recomendaciones[recomendaciones["provincia"].isin(provincias)])
with tabs[7]:
    renderizar_datos(cargar_tablas())
with tabs[8]:
    renderizar_metodologia(metricas_modelo)
