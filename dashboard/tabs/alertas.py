import pandas as pd
import streamlit as st


def _es_lugar_publico(serie: pd.Series) -> pd.Series:
    normalizada = serie.astype(str).str.normalize("NFKD").str.encode("ascii", errors="ignore").str.decode("ascii")
    return normalizada.str.upper().eq("PUBLICO")


def construir_alertas(df: pd.DataFrame) -> list[dict[str, str]]:
    total = max(int(df["total_homicidios"].sum()), 1)
    provincia_top = df["provincia"].value_counts().idxmax()
    provincia_pct = df["provincia"].value_counts().iloc[0] / total * 100
    canton_top = df["canton"].value_counts().idxmax()
    canton_pct = df["canton"].value_counts().iloc[0] / total * 100
    arma_fuego = (df["arma"] == "ARMA DE FUEGO").mean() * 100
    hora_top = int(df["hora"].value_counts().idxmax())
    lugar_publico = _es_lugar_publico(df["tipo_lugar"]).mean() * 100

    alertas = []
    if provincia_pct >= 35:
        alertas.append(
            {
                "nivel": "Critico",
                "titulo": "Concentracion provincial alta",
                "detalle": f"{provincia_top} concentra {provincia_pct:.1f}% de los casos filtrados.",
            }
        )
    if canton_pct >= 20:
        alertas.append(
            {
                "nivel": "Alto",
                "titulo": "Canton dominante",
                "detalle": f"{canton_top} concentra {canton_pct:.1f}% de los casos filtrados.",
            }
        )
    if arma_fuego >= 85:
        alertas.append(
            {
                "nivel": "Alto",
                "titulo": "Predominio de arma de fuego",
                "detalle": f"El {arma_fuego:.1f}% de los casos registra arma de fuego.",
            }
        )
    if lugar_publico >= 65:
        alertas.append(
            {
                "nivel": "Medio",
                "titulo": "Alta ocurrencia en espacios publicos",
                "detalle": f"El {lugar_publico:.1f}% ocurre en lugares publicos.",
            }
        )
    alertas.append(
        {
            "nivel": "Operativo",
            "titulo": "Hora critica",
            "detalle": f"La hora con mayor recurrencia es {hora_top:02d}:00.",
        }
    )
    return alertas


def renderizar_alertas(df: pd.DataFrame) -> None:
    alertas = construir_alertas(df)
    cols = st.columns(min(len(alertas), 5))
    for col, alerta in zip(cols, alertas[:5]):
        clase = alerta["nivel"].lower()
        col.markdown(
            f"""
<div class="alert-card {clase}">
  <div class="alert-level">{alerta['nivel']}</div>
  <strong>{alerta['titulo']}</strong>
  <p>{alerta['detalle']}</p>
</div>
""",
            unsafe_allow_html=True,
        )
