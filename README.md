# SafeAnalytics EC

**Sistema Inteligente de Analítica de Negocios para el Monitoreo y Análisis Estratégico de Homicidios Intencionales en Ecuador**

Proyecto integrador de Analítica de Negocios orientado a seguridad ciudadana. La solución usa el dataset real `mdi_homicidiosintencionalse_pm_2026_enero_mayo.xlsx`, consolida indicadores críticos sobre homicidios intencionales, identifica patrones geográficos y temporales, caracteriza el delito y entrega alertas estratégicas para apoyar decisiones ejecutivas sobre prevención, despliegue operativo y asignación de recursos.

## Arquitectura

```text
FUENTES                          ETL (Python)               MODELO ANALITICO            CONSUMO
-----------------------------    ------------------------   ------------------------    --------------------------
Excel MDI enero-mayo 2026    ->  limpieza, tipado,       -> fact_homicidios         -> Dashboard Power BI
(fuente principal)               validacion, calidad        dim_tiempo               -> Dashboard Streamlit
API Banco Mundial (poblacion)    enriquecimiento temporal   dim_geografia            -> Modelo predictivo + regresion
(fuente complementaria)          KPIs y tasa por 100k       dim_delito               -> Informe, pitch y presentacion
                                                            dim_victima
```

### Fuentes de datos

- **Principal (archivo real):** `mdi_homicidiosintencionalse_pm_2026_enero_mayo.xlsx`, dataset oficial del Ministerio del Interior (MDI) con 3.485 homicidios intencionales de enero a mayo de 2026.
- **Complementaria (API publica):** [API del Banco Mundial](https://api.worldbank.org/v2/country/ECU/indicator/SP.POP.TOTL?format=json), indicador `SP.POP.TOTL` (poblacion total de Ecuador). Se consume desde `src/etl/poblacion_api.py` y se usa para calcular la **tasa de homicidios por 100.000 habitantes**. Cumple el requisito de utilizar al menos una API publica.

## Estructura del repositorio

| Ruta | Contenido |
|---|---|
| `src/etl/transform_load.py` | Transformación del Excel real a esquema estrella |
| `src/etl/poblacion_api.py` | Consumo de la API pública del Banco Mundial (población de Ecuador) |
| `src/analytics/eda.py` | Estadística descriptiva y de dispersión, correlación, KPIs y tasa por 100k |
| `src/models/entrenar_modelo.py` | Modelo baseline + Regresión Lineal (scikit-learn) con MAE, RMSE y R² |
| `src/models/prescriptivo.py` | Índice de riesgo territorial y recomendaciones estratégicas |
| `dashboard/` | App Streamlit ejecutiva con Plotly (9 vistas) |
| `powerbi/` | Guía de medidas DAX, tema visual y alineación con el PBIX entregado |
| `data/processed/` | Tablas del modelo estrella + caché de población de la API |
| `reports/` | KPIs, dispersión, matriz de correlación, métricas del modelo y recomendaciones |
| `models/` | Modelo entrenado en formato `pkl` |
| `informe/` | Informe técnico, guion y presentación de defensa |
| `docs/` | Explicación del proyecto y justificación del modelo predictivo |

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

La app contiene nueve vistas:

- **Ejecutivo:** KPIs, evolución mensual, provincias críticas y resumen de decisión.
- **Riesgo territorial:** índice 0-100 por provincia o cantón con semáforo Alto/Medio/Bajo.
- **Simulador:** estimación de casos evitables bajo escenarios de reducción de incidencia.
- **Geográfico:** concentración por provincia, cantón y zona.
- **Temporal:** patrones por mes, día y hora crítica.
- **Caracterización:** tipo de arma, sexo, edad, lugar y presunta motivación.
- **Predictiva:** incidencia estimada por provincia, comparación de modelos (baseline vs. Regresión Lineal con R²) y explicabilidad (XAI).
- **Datos:** esquema estrella, calidad y descarga de tablas.
- **Metodologia:** fuentes de datos (Excel + API), medidas de dispersión, matriz de correlación, modelo dimensional y control de calidad.

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
- **Arma predominante:** arma de fuego (87,8% de los casos).
- **Tasa por 100.000 habitantes:** 19,05 en el periodo; 46,06 anualizada (con población del Banco Mundial).

## Analítica avanzada (fases 3 y 4)

- **Medidas de dispersión (EDA):** desviación estándar, mediana y coeficiente de variación (CV) de edad, incidencia diaria e incidencia por provincia. El CV de 218% por provincia demuestra estadísticamente la concentración territorial.
- **Análisis de correlación:** matriz de Pearson entre indicadores provinciales (`reports/correlacion_provincias.csv`). El volumen se asocia fuertemente con los cantones afectados (r=0,91) y la incidencia reciente (r=0,99). La correlación no implica causalidad.
- **Modelado predictivo:** un baseline explicable (MAE 1,54 · RMSE 2,62 · **R² 0,53**) se compara contra una **Regresión Lineal** de scikit-learn (R² 0,53). Al obtener un desempeño equivalente, se mantiene el baseline por su transparencia. La pestaña Predictiva muestra la explicabilidad (peso de cada variable).

## Componentes ejecutivos agregados

- **Alertas ejecutivas:** reglas automáticas que resaltan concentración territorial, predominio de arma de fuego, ocurrencia en espacios públicos y hora crítica.
- **Índice de riesgo territorial:** score compuesto por volumen histórico, incidencia reciente, variación mensual, porcentaje de arma de fuego y porcentaje de lugar público.
- **Simulador de escenarios:** permite estimar casos evitables ante reducciones hipotéticas de incidencia por provincia o cantón.

## Documento del informe

- `informe/INFORME_TECNICO_SAFEANALYTICS_EC.docx`
- `informe/DEFENSA_SAFEANALYTICS_EC.pptx`
- `informe/GUION_PITCH.md`
- `docs/EXPLICACION_PROYECTO.md`
- `docs/JUSTIFICACION_MODELO_PREDICTIVO.md`

## Nota de datos

Los datos provienen del archivo Excel real entregado para el proyecto. El repositorio genera copias procesadas en CSV para facilitar auditoria, visualizacion y carga en Power BI. Si se publica en GitHub, revisar politicas institucionales sobre difusion de coordenadas y microdatos.
