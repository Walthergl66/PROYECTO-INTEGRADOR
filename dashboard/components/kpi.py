import streamlit as st


def tarjeta_kpi(col, etiqueta: str, valor: str, ayuda: str = "") -> None:
    with col:
        st.markdown(
            f"""
<div class="kpi">
  <div class="label">{etiqueta}</div>
  <div class="value">{valor}</div>
  <div class="hint">{ayuda}</div>
</div>
""",
            unsafe_allow_html=True,
        )
