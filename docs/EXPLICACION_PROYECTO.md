# Explicación del Proyecto SafeAnalytics EC

## 1. Descripción General

SafeAnalytics EC es un sistema inteligente de analítica de negocios para monitorear y analizar homicidios intencionales en Ecuador. El proyecto transforma un dataset real en un modelo analítico, reportes, recomendaciones y un dashboard ejecutivo para apoyar la toma de decisiones en seguridad ciudadana.

El sistema permite responder:

- Dónde se concentran los homicidios intencionales.
- Cuándo ocurren con mayor frecuencia.
- Qué tipos de armas predominan.
- Qué perfil general presentan las víctimas.
- Qué territorios requieren mayor priorización.
- Qué impacto podría tener una reducción hipotética de la incidencia.

## 2. Fuente de Datos

La fuente principal es el archivo:

`mdi_homicidiosintencionalse_pm_2026_enero_mayo.xlsx`

El dataset contiene registros reales de enero a mayo de 2026 e incluye variables territoriales, temporales, delictivas y sociodemográficas.

## 3. Estructura del Proyecto

| Carpeta | Función |
|---|---|
| `src/etl/` | Limpieza, transformación y generación del modelo estrella. |
| `src/analytics/` | Cálculo de KPIs y análisis exploratorio. |
| `src/models/` | Modelo predictivo exploratorio y recomendaciones prescriptivas. |
| `dashboard/` | Aplicación Streamlit para visualización ejecutiva. |
| `data/raw/` | Copia procesada de la fuente original en CSV. |
| `data/processed/` | Tablas del modelo estrella listas para análisis. |
| `reports/` | Resultados de EDA, métricas, predicciones y recomendaciones. |
| `models/` | Modelo predictivo guardado. |
| `powerbi/` | Guía DAX y tema para Power BI. |
| `informe/` | Informe técnico y guion de defensa. |

## 4. Pipeline ETL

El pipeline principal se encuentra en:

`src/etl/transform_load.py`

Este script:

- Lee el Excel original.
- Normaliza texto.
- Convierte fechas y horas.
- Extrae hora y franja horaria.
- Convierte edad a número.
- Normaliza coordenadas.
- Genera claves analíticas.
- Construye el modelo estrella.
- Exporta tablas CSV a `data/processed/`.
- Genera un reporte de calidad.

## 5. Modelo Estrella

El modelo analítico usado es de tipo estrella.

Tabla de hechos:

- `fact_homicidios`

Dimensiones:

- `dim_tiempo`
- `dim_geografia`
- `dim_delito`
- `dim_victima`

Este modelo permite analizar los homicidios por tiempo, territorio, características del delito y características generales de la víctima.

## 6. Análisis Exploratorio y KPIs

El script:

`src/analytics/eda.py`

calcula los indicadores principales:

- Total de homicidios.
- Provincias afectadas.
- Cantones afectados.
- Porcentaje de arma de fuego.
- Porcentaje de víctimas hombres.
- Edad promedio.
- Provincia y cantón con mayor incidencia.
- Hora crítica.
- Serie mensual.

Los resultados se guardan en:

`reports/eda_resultados.json`

## 7. Modelo Predictivo

El modelo se encuentra en:

`src/models/entrenar_modelo.py`

Se utiliza un baseline provincial ajustado por:

- Promedio histórico por provincia.
- Día de semana.
- Tendencia reciente.

El modelo se evalúa con MAE y RMSE, y se guarda en:

`models/modelo_incidencia_diaria.pkl`

Este modelo es exploratorio y se usa para apoyar la priorización, no para tomar decisiones automáticas.

## 8. Analítica Prescriptiva

El script:

`src/models/prescriptivo.py`

genera:

- Recomendaciones estratégicas por provincia.
- Índice de riesgo territorial.
- Clasificación en riesgo alto, medio o bajo.

Los resultados se guardan en:

- `reports/recomendaciones_estrategicas.csv`
- `reports/riesgo_territorial.csv`

## 9. Dashboard Ejecutivo

La app se ejecuta con:

```bash
streamlit run dashboard/app.py
```

La aplicación incluye:

- Vista ejecutiva.
- Riesgo territorial.
- Simulador de escenarios.
- Análisis geográfico.
- Análisis temporal.
- Caracterización del delito.
- Vista predictiva.
- Explorador de datos.

## 10. Funcionalidades Clave

- Filtros por provincia, mes y arma.
- KPIs ejecutivos.
- Alertas automáticas.
- Mapa geográfico.
- Ranking de provincias y cantones.
- Mapa de calor temporal.
- Índice de riesgo territorial.
- Simulador de reducción de incidencia.
- Tabla de recomendaciones.
- Descarga de tablas procesadas.

## 11. Cómo Reproducir el Proyecto

1. Crear entorno virtual.

```bash
python -m venv .venv
```

2. Activar entorno.

```bash
.venv\Scripts\activate
```

3. Instalar dependencias.

```bash
pip install -r requirements.txt
```

4. Ejecutar pipeline.

```bash
python src/etl/transform_load.py
python src/analytics/eda.py
python src/models/entrenar_modelo.py
python src/models/prescriptivo.py
```

5. Ejecutar dashboard.

```bash
streamlit run dashboard/app.py
```

## 12. Consideraciones Éticas

El proyecto analiza datos sensibles relacionados con seguridad ciudadana. Por ello:

- Se trabaja principalmente con agregaciones.
- No se busca identificar personas.
- Las variables demográficas se interpretan con cautela.
- El modelo no debe usarse para criminalizar territorios o grupos.
- Las recomendaciones deben complementar el criterio técnico institucional.

## 13. Conclusión

SafeAnalytics EC integra ingeniería de datos, analítica descriptiva, diagnóstica, predictiva y prescriptiva en una herramienta ejecutiva. El proyecto permite transformar registros de homicidios intencionales en información accionable para planificación, monitoreo y toma de decisiones estratégicas.
