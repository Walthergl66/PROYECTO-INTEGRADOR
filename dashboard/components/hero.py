import streamlit as st


def renderizar_hero() -> None:
    st.markdown(
        """
<section class="hero">
  <h1>SafeAnalytics EC</h1>
  <p>Sistema inteligente de analítica de negocios para el monitoreo y análisis estratégico de homicidios intencionales en Ecuador.</p>
  <span class="badge">Enero-mayo 2026</span>
  <span class="badge">Dashboard ejecutivo</span>
  <span class="badge">Seguridad ciudadana</span>
</section>
""",
        unsafe_allow_html=True,
    )
