# SafeAnalytics EC

**Sistema Inteligente de Analítica de Negocios para el Monitoreo y Análisis Estratégico de Homicidios Intencionales en Ecuador**

Proyecto integrador de Analítica de Negocios orientado a seguridad ciudadana. La solución usa el dataset real `mdi_homicidiosintencionalse_pm_2026_enero_mayo.xlsx`, consolida indicadores críticos sobre homicidios intencionales, identifica patrones geográficos y temporales, caracteriza el delito y entrega alertas estratégicas para apoyar decisiones ejecutivas sobre prevención, despliegue operativo y asignación de recursos.

## Arquitectura

```text
FUENTES                         ETL (Python)               MODELO ANALITICO             CONSUMO
----------------------------    ------------------------   -------------------------   --------------------------
Dataset homicidios Ecuador  ->  limpieza, tipado,       -> fact_homicidios          -> Dashboard Power BI
Power BI (.pbix.zip)            validacion, calidad        dim_tiempo                -> Dashboard Streamlit
Excel MDI enero-mayo 2026       enriquecimiento temporal   dim_geografia             -> Modelo predictivo
                                 KPIs ejecutivos            dim_delito                -> Informe y pitch ejecutivo
```

## Estructura del repositorio

| Ruta | Contenido |
|---|---|
| `src/etl/` | Transformación del Excel real a esquema estrella |
| `src/analytics/eda.py` | Estadística descriptiva, KPIs y resultados exploratorios |
| `src/models/` | Modelo predictivo de incidencia mensual y recomendaciones estratégicas |
| `dashboard/` | App Streamlit ejecutiva con Plotly |
| `powerbi/` | Guía de medidas DAX, tema visual y alineación con el PBIX entregado |
| `data/processed/` | Tablas listas para Power BI y Streamlit |
| `reports/` | KPIs, métricas del modelo y recomendaciones |
| `models/` | Modelo entrenado en formato `pkl` |
| `informe/` | Guion de pitch para exposición ejecutiva |

## Reproducir el pipeline

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

python src/etl/transform_load.py
python src/analytics/eda.py
python src/models/entrenar_modelo.py
python src/models/prescriptivo.py
```

## Dashboard

```bash
streamlit run dashboard/app.py
```

La app contiene ocho vistas:

- **Ejecutivo:** KPIs, evolución mensual, provincias críticas y resumen de decisión.
- **Riesgo territorial:** índice 0-100 por provincia o cantón con semáforo Alto/Medio/Bajo.
- **Simulador:** estimación de casos evitables bajo escenarios de reducción de incidencia.
- **Geográfico:** concentración por provincia, cantón y zona.
- **Temporal:** patrones por mes, día y hora crítica.
- **Caracterización:** tipo de arma, sexo, edad, lugar y presunta motivación.
- **Predictiva:** estimación mensual de incidencia por provincia y nivel de riesgo.
- **Datos:** esquema estrella, calidad y descarga de tablas.

## Relación con el PBIX

El archivo `Dashboards de criminalistica de homicidios.pbix.zip` ya contiene páginas alineadas al proyecto:

- Dashboard Ejecutivo
- Análisis Geográfico y Temporal
- Caracterización del Delito
- Predicción y Recomendaciones Estratégicas

Este repositorio complementa ese trabajo con una app reproducible, pipeline documentado y artefactos ejecutivos para entrega académica o presentación ante un responsable institucional.

## Resultados clave

- **Periodo analizado:** 2026-01-01 a 2026-05-31.
- **Total de registros:** 3.485 homicidios intencionales.
- **Cobertura territorial:** 23 provincias y 138 cantones afectados.
- **Provincia con mayor incidencia:** Guayas.
- **Canton con mayor incidencia:** Guayaquil.
- **Arma predominante:** arma de fuego.

## Componentes ejecutivos agregados

- **Alertas ejecutivas:** reglas automáticas que resaltan concentración territorial, predominio de arma de fuego, ocurrencia en espacios públicos y hora crítica.
- **Índice de riesgo territorial:** score compuesto por volumen histórico, incidencia reciente, variación mensual, porcentaje de arma de fuego y porcentaje de lugar público.
- **Simulador de escenarios:** permite estimar casos evitables ante reducciones hipotéticas de incidencia por provincia o cantón.

## Documento del informe

- `informe/INFORME_TECNICO_SAFEANALYTICS_EC.docx`

## Nota de datos

Los datos provienen del archivo Excel real entregado para el proyecto. El repositorio genera copias procesadas en CSV para facilitar auditoria, visualizacion y carga en Power BI. Si se publica en GitHub, revisar politicas institucionales sobre difusion de coordenadas y microdatos.
