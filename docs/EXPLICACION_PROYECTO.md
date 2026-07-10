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

## 2. Fuentes de Datos

El proyecto combina dos fuentes:

**Fuente principal (archivo real).** El archivo `mdi_homicidiosintencionalse_pm_2026_enero_mayo.xlsx`, publicado por el Ministerio del Interior (MDI). Contiene registros reales de enero a mayo de 2026 con variables territoriales, temporales, delictivas y sociodemográficas.

**Fuente complementaria (API pública).** La API del Banco Mundial (indicador `SP.POP.TOTL`), que entrega la población total de Ecuador en formato JSON, sin necesidad de clave de acceso. Se consume desde el módulo `src/etl/poblacion_api.py` y sirve para calcular la **tasa de homicidios por cada 100.000 habitantes**, una medida más justa que el conteo absoluto porque tiene en cuenta el tamaño de la población.

> En palabras simples: el Excel nos dice *cuántos* homicidios hubo y *dónde*; la API nos dice *cuántas personas viven en el país*, y al combinarlos obtenemos una tasa comparable con estándares internacionales.

Nota: el dataset del MDI también existe en el portal Datos Abiertos Ecuador (CKAN), que tiene una API, pero el portal bloquea el acceso a esa API (error 403). Por eso se usa el archivo oficial descargado y se complementa con la API del Banco Mundial, que sí funciona de forma abierta.

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
- Tasa por 100.000 habitantes (19,05 en el periodo; 46,06 anualizada).

Además del "promedio" (tendencia central), el análisis calcula **medidas de dispersión** y **correlación**:

**Medidas de dispersión.** Indican qué tan dispersos o parecidos son los datos. Se usa el coeficiente de variación (CV): cuanto más alto, más desigual es el dato.

- Edad de las víctimas: CV 38,7% (dispersión moderada; la mayoría entre 23 y 39 años).
- Incidencia diaria nacional: CV 32,5% (ocurren en promedio 23 homicidios por día, bastante estable).
- Incidencia por provincia: CV 218,4% (dispersión extrema: la media es 151 casos pero la mediana solo 23, porque Guayas concentra 1.521 y otras apenas 4). Esto demuestra, con números, la fuerte concentración territorial.

**Análisis de correlación.** Mide qué variables "se mueven juntas" usando el coeficiente de Pearson (de -1 a 1). Las relaciones más fuertes fueron:

- Volumen total vs. incidencia del último mes: r = 0,99 (las provincias con más casos siguen altas).
- Volumen total vs. cantones afectados: r = 0,91 (el problema se extiende a más cantones).
- % de arma de fuego vs. edad promedio: r = -0,49 (donde predomina el arma de fuego, las víctimas son más jóvenes).

Importante: **correlación no es causalidad**. Que dos cosas ocurran juntas no significa que una cause la otra.

Los resultados se guardan en:

- `reports/eda_resultados.json` (KPIs, dispersión y correlación).
- `reports/correlacion_provincias.csv` (matriz de correlación completa).
- `reports/indicadores_provincia.csv` (indicadores numéricos por provincia).

## 7. Modelo Predictivo

El modelo se encuentra en:

`src/models/entrenar_modelo.py`

Se entrenan y comparan **dos modelos** sobre la misma partición de datos (80% entrenamiento, 20% prueba):

1. **Baseline provincial** (modelo desplegado): ajustado por promedio histórico por provincia, día de semana y tendencia reciente. Es simple y fácil de explicar.
2. **Regresión Lineal** (scikit-learn): un algoritmo clásico de aprendizaje automático, usado como comparación.

Ambos se evalúan con tres métricas: MAE y RMSE (miden el error) y R² (mide qué porcentaje del comportamiento explica el modelo):

| Modelo | MAE | RMSE | R² |
|---|---|---|---|
| Baseline provincial | 1,539 | 2,621 | 0,533 |
| Regresión Lineal | 1,547 | 2,623 | 0,532 |

**Conclusión clave:** los dos modelos rinden casi igual (R² 0,53 en ambos). Esto demuestra que usar un algoritmo más complejo no mejora el resultado con solo cinco meses de datos. Por eso se mantiene el baseline: da el mismo poder predictivo pero es más transparente, algo esencial en seguridad ciudadana.

**Explicabilidad (XAI).** La Regresión Lineal permite ver cuánto pesa cada variable en la predicción. Por ejemplo, pertenecer a Guayas suma unos 8,3 homicidios diarios a la estimación. Estos pesos se visualizan en la pestaña Predictiva del dashboard.

El modelo desplegado se guarda en `models/modelo_incidencia_diaria.pkl` y las métricas en `reports/modelo_resultados.json`. Es exploratorio: apoya la priorización, no toma decisiones automáticas.

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

La aplicación incluye nueve vistas:

- **Ejecutiva:** KPIs, tendencia mensual y prioridades. Incluye la tasa por 100.000 habitantes (calculada con la API del Banco Mundial).
- **Riesgo territorial:** índice 0-100 por provincia/cantón con semáforo.
- **Simulador de escenarios:** casos evitables ante una reducción hipotética.
- **Análisis geográfico:** mapa, ranking de cantones y concentración por zona.
- **Análisis temporal:** patrones por hora, día y mapa de calor.
- **Caracterización del delito:** arma, motivación, sexo y edad.
- **Predictiva:** comparación de modelos (baseline vs. Regresión Lineal con R²) y explicabilidad (peso de cada variable).
- **Datos:** exploración y descarga de las tablas del modelo estrella.
- **Metodología:** fuentes de datos (Excel + API), medidas de dispersión, mapa de calor de correlación y control de calidad.

## 10. Funcionalidades Clave

- Filtros por provincia, mes y arma.
- KPIs ejecutivos y tasa por 100.000 habitantes (API del Banco Mundial).
- Alertas automáticas.
- Mapa geográfico.
- Ranking de provincias y cantones.
- Mapa de calor temporal.
- Medidas de dispersión y mapa de calor de correlación (pestaña Metodología).
- Comparación de modelos (baseline vs. Regresión Lineal con R²) y explicabilidad XAI.
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
