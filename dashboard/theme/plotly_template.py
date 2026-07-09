"""Tema Plotly para SafeAnalytics EC."""

import plotly.io as pio

from dashboard.theme.colores import AMBAR, AZUL, FONDO, ROJO, TEAL, TEAL_CLARO, TINTA


def registrar_tema_plotly() -> None:
    pio.templates["safeanalytics"] = {
        "layout": {
            "font": {"family": "Inter, Segoe UI, sans-serif", "color": TINTA},
            "paper_bgcolor": "white",
            "plot_bgcolor": "white",
            "colorway": [TEAL, AZUL, AMBAR, ROJO, TEAL_CLARO],
            "margin": {"l": 30, "r": 20, "t": 60, "b": 35},
            "xaxis": {"gridcolor": "#E8EEF2", "zerolinecolor": "#D9E2E8"},
            "yaxis": {"gridcolor": "#E8EEF2", "zerolinecolor": "#D9E2E8"},
        }
    }
    pio.templates.default = "safeanalytics"
