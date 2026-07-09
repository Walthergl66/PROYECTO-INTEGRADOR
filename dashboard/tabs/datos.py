import json
from pathlib import Path

import streamlit as st

RAIZ = Path(__file__).resolve().parents[2]


def renderizar_datos(tablas: dict) -> None:
    calidad_path = RAIZ / "data" / "processed" / "reporte_calidad.json"
    calidad = json.loads(calidad_path.read_text(encoding="utf-8"))
    st.markdown(
        f"""
<div class="note">
  <b>Fuente:</b> {calidad['fuente']}<br>
  <b>Periodo:</b> {calidad['periodo']['inicio']} a {calidad['periodo']['fin']}<br>
  <b>Registros:</b> {calidad['registros']} | <b>Coordenadas validas:</b> {calidad['coordenadas_validas_pct']}%
</div>
""",
        unsafe_allow_html=True,
    )
    nombres = list(tablas)
    seleccion = st.selectbox("Tabla procesada", nombres)
    st.dataframe(tablas[seleccion], width="stretch", hide_index=True)
    st.download_button(
        "Descargar CSV",
        tablas[seleccion].to_csv(index=False).encode("utf-8-sig"),
        file_name=f"{seleccion}.csv",
        mime="text/csv",
    )
