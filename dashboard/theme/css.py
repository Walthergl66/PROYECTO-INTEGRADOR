"""CSS global del dashboard."""

import streamlit as st

from dashboard.theme.colores import AZUL, FONDO, TEAL, TINTA, TINTA_SUAVE


def inyectar_css() -> None:
    st.markdown(
        f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"], [data-testid="stAppViewContainer"] * {{
  font-family: 'Inter', 'Segoe UI', sans-serif;
}}
[data-testid="stAppViewContainer"] {{ background: {FONDO}; }}
[data-testid="stHeader"] {{ background: transparent; }}
[data-testid="stSidebar"] {{ background: linear-gradient(180deg, {AZUL}, #0B1F33); }}
[data-testid="stSidebar"] * {{ color: #EEF6F8 !important; }}
.hero {{
  background: linear-gradient(120deg, {AZUL} 0%, #0F3D4C 58%, {TEAL} 100%);
  color: white;
  border-radius: 8px;
  padding: 26px 30px;
  margin-bottom: 12px;
  box-shadow: 0 10px 26px rgba(18,53,91,.18);
}}
.hero h1 {{ margin: 0; font-size: 1.8rem; font-weight: 800; letter-spacing: 0; }}
.hero p {{ margin: 6px 0 0 0; color: rgba(255,255,255,.84); max-width: 980px; }}
.badge {{
  display: inline-block;
  margin-top: 14px;
  margin-right: 8px;
  border: 1px solid rgba(255,255,255,.26);
  background: rgba(255,255,255,.12);
  padding: 5px 10px;
  border-radius: 6px;
  font-size: .74rem;
  font-weight: 700;
}}
.kpi {{
  background: white;
  border: 1px solid #E1E8ED;
  border-top: 4px solid {TEAL};
  border-radius: 8px;
  padding: 16px 18px;
  min-height: 126px;
  box-shadow: 0 2px 10px rgba(23,32,42,.05);
}}
.kpi .label {{
  color: {TINTA_SUAVE};
  font-size: .72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .04em;
}}
.kpi .value {{
  color: {TINTA};
  font-size: 1.72rem;
  line-height: 1.15;
  font-weight: 800;
  margin-top: 8px;
}}
.kpi .hint {{ color: {TINTA_SUAVE}; font-size: .78rem; margin-top: 6px; }}
.note {{
  background: white;
  border: 1px solid #E1E8ED;
  border-left: 5px solid {TEAL};
  border-radius: 8px;
  padding: 14px 16px;
  color: {TINTA};
  margin: 4px 0 14px 0;
}}
.risk-card {{
  background: white;
  border: 1px solid #E1E8ED;
  border-radius: 8px;
  padding: 14px 16px;
  margin-bottom: 10px;
}}
.risk-card strong {{ color: {AZUL}; }}
.alert-card {{
  background: white;
  border: 1px solid #E1E8ED;
  border-left: 5px solid {TEAL};
  border-radius: 8px;
  padding: 14px 16px;
  min-height: 128px;
  box-shadow: 0 2px 10px rgba(23,32,42,.05);
}}
.alert-card.critico, .alert-card.alto {{ border-left-color: #B42318; }}
.alert-card.medio {{ border-left-color: #D99A21; }}
.alert-card.operativo {{ border-left-color: {AZUL}; }}
.alert-level {{
  color: {TINTA_SUAVE};
  font-size: .68rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: .06em;
  margin-bottom: 6px;
}}
.alert-card strong {{ color: {TINTA}; display: block; line-height: 1.25; }}
.alert-card p {{ color: {TINTA_SUAVE}; font-size: .82rem; margin: 8px 0 0 0; }}
footer, [data-testid="stToolbar"] {{ visibility: hidden; }}
[data-testid="stExpandSidebarButton"] {{ visibility: visible; }}
</style>
""",
        unsafe_allow_html=True,
    )
