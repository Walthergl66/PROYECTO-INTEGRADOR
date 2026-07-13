# Exposición de la aplicación — SafeAnalytics EC

**Guion hablado para la defensa (10–15 minutos). Escrito en primera persona, listo para
leer en voz alta o memorizar por bloques. Los tiempos son sugeridos.**

---

## 1. Apertura (1 minuto)

Buenos días. Nuestro proyecto se llama **SafeAnalytics EC**: un sistema de analítica de
negocios para el monitoreo estratégico de homicidios intencionales en Ecuador.

La idea central es simple de decir y difícil de lograr: **convertir un archivo de Excel
con 3.485 registros en decisiones**. No en gráficos bonitos — en decisiones: qué
provincia priorizar, en qué horario reforzar operativos, y qué impacto tendría una
intervención antes de ejecutarla.

## 2. El problema (1 minuto)

Las instituciones de seguridad no sufren por falta de datos; sufren por falta de
**lectura estratégica**. Los registros existen, pero viven en archivos tabulares donde
nadie puede responder rápido preguntas como: ¿dónde se concentra la incidencia?,
¿cuándo ocurre?, ¿qué territorios están empeorando?

Ese es el dolor del negocio que atacamos: el análisis manual retrasa la decisión, y en
seguridad ciudadana el retraso cuesta vidas.

## 3. Las fuentes de datos (1,5 minutos)

Trabajamos con **dos fuentes**:

- **La principal:** el dataset oficial del Ministerio del Interior — 3.485 homicidios
  intencionales de enero a mayo de 2026, con variables territoriales, temporales,
  del delito y de la víctima. Son datos reales, no simulados.
- **La complementaria, vía API pública:** el Banco Mundial, de donde obtenemos la
  población de Ecuador (18.289.896 habitantes, 2025) en JSON y sin clave de acceso.
  Con ella calculamos la **tasa de homicidios por 100.000 habitantes**, que permite
  comparar con estándares internacionales y no depender solo del conteo absoluto.

Todo pasa por un pipeline ETL en Python que limpia, tipifica y organiza los datos en un
**modelo estrella**: una tabla de hechos y cuatro dimensiones (tiempo, geografía,
delito y víctima). Cada transformación es reproducible y auditable.

## 4. Recorrido por la aplicación (7–8 minutos)

*(Aquí abro la app en vivo: `streamlit run dashboard/app.py`)*

### 4.1. Lo que siempre está visible

Antes de entrar a las pestañas, tres elementos acompañan toda la navegación:

- **La fila de KPIs:** total de homicidios (3.485), % de arma de fuego (87,8%),
  % de víctimas hombres (90,9%), edad promedio (31,6 años) y la provincia crítica.
  Debajo, la **tasa nacional estimada: 46 homicidios por 100.000 habitantes al año**,
  calculada con la población de la API del Banco Mundial.
- **Las alertas ejecutivas:** reglas automáticas que se encienden solas cuando detectan
  concentración territorial, predominio de arma de fuego, ocurrencia en espacios
  públicos o una hora crítica. El sistema avisa; no hay que ir a buscar el problema.
- **Los cinco filtros globales** (barra lateral): provincia, mes, arma, sexo de la
  víctima y franja horaria. Cualquier combinación filtra las seis pestañas a la vez, y
  un contador indica cuántos registros están en pantalla — por ejemplo, "Mostrando
  1.521 de 3.485 registros" si filtro solo Guayas. Eso garantiza transparencia: el
  usuario siempre sabe sobre qué subconjunto está mirando.

### 4.2. Las seis pestañas — y por qué van en ese orden

La app está organizada siguiendo la **progresión de madurez analítica**: primero
describir, luego diagnosticar, después predecir y finalmente prescribir. No es un orden
decorativo: cada nivel se construye sobre el anterior.

**Pestaña 1 — Ejecutivo** *(analítica descriptiva)*.
Responde "¿qué está pasando?". Evolución mensual (de 761 casos en enero baja a 667 en
marzo y repunta a 696 en mayo), ranking de provincias y las cinco prioridades
estratégicas. Es la vista para un director: la foto completa en diez segundos.

**Pestaña 2 — Caracterización** *(descriptiva/diagnóstica)*.
Responde "¿cómo es el delito y quiénes son las víctimas?". El arma de fuego domina con
87,8%. El 90,9% de víctimas son hombres, con edad concentrada entre los 20 y 40 años.
Ese perfil orienta políticas específicas: control de armas y prevención en población
joven masculina.

**Pestaña 3 — Geográfico y Temporal** *(diagnóstica, con dos sub-pestañas)*.
Responde "¿dónde y cuándo?". En lo geográfico: un mapa georreferenciado de los 3.485
eventos, donde Guayas concentra 1.521 casos y Guayaquil 944. En lo temporal: la
incidencia sube en la noche, la **hora crítica es las 20:00**, y el mapa de calor
día-por-hora muestra que **sábado y domingo en la noche** son la combinación más
peligrosa. Ese cruce es directamente accionable para planificar operativos.

Y aquí un punto de rigor estadístico: la concentración territorial no es una impresión
visual. El **coeficiente de variación de la incidencia por provincia es 218%** — la
media es 151 casos pero la mediana es 23, una distribución extremadamente asimétrica.
Y la correlación confirma el patrón: el volumen histórico se asocia con la incidencia
reciente (r = 0,99) y con la cantidad de cantones afectados (r = 0,91). Siempre
aclaramos: **correlación no es causalidad** — una provincia con más casos no "causa"
el delito; influyen población, densidad y dinámicas que el dataset no captura.

**Pestaña 4 — Predictiva** *(analítica predictiva)*.
Responde "¿qué puede esperarse?". Aquí está la decisión metodológica más importante del
proyecto. Entrenamos **dos modelos** sobre la misma partición temporal (813 registros de
entrenamiento, 199 de prueba):

| Modelo | MAE | RMSE | R² |
|---|---|---|---|
| Baseline provincial explicable | 1,539 | 2,621 | 0,533 |
| Regresión Lineal (scikit-learn) | 1,547 | 2,623 | 0,532 |

El resultado es idéntico. Eso demuestra **con datos** que un algoritmo más complejo no
mejora la predicción con solo cinco meses de historia. Por eso desplegamos el baseline:
igual de preciso, pero transparente y auditable — en seguridad ciudadana, la
explicabilidad no es un lujo, es un requisito ético. La pestaña además muestra el
componente XAI: qué variable pesa cuánto (pertenecer a Guayas suma ~8,3 homicidios
diarios a la estimación).

**Pestaña 5 — Riesgo y Simulador** *(analítica prescriptiva, dos sub-pestañas)*.
Responde "¿qué hacemos?". El **índice de riesgo territorial** combina cinco factores
(volumen histórico, casos recientes, variación mensual, % arma de fuego, % lugar
público) en un score de 0 a 100 con semáforo: Guayas marca **84,2 — riesgo alto**. El
sistema clasifica las 23 provincias en tres acciones: priorizar intervención (13),
monitoreo reforzado (4) y monitoreo preventivo (6).

El **simulador** completa el ciclo: elijo un territorio, propongo una reducción — por
ejemplo 10% en Guayas — y estima cuántos casos se evitarían en los próximos meses.
Permite discutir el impacto de una decisión **antes** de gastarse el presupuesto.

**Pestaña 6 — Datos y Metodología** *(soporte y transparencia)*.
Responde "¿puedo confiar en esto?". Cualquier persona puede ver las tablas del modelo
estrella, el reporte de calidad (100% de coordenadas válidas, 0% de nulos en claves),
descargar los CSV, y revisar las medidas de dispersión y la matriz de correlación. Nada
está escondido: del Excel original al gráfico final, todo es trazable.

## 5. Ética y gobernanza (1 minuto)

Trabajamos con datos sensibles, y eso impone límites que respetamos por diseño:

- Los resultados se presentan **agregados**; nunca identifican personas.
- Las variables demográficas (sexo, etnia, nacionalidad) se usan solo para
  caracterización estadística, jamás para perfilar o criminalizar.
- El modelo predictivo es una **señal de apoyo**, no un pronóstico operativo: puede
  arrastrar sesgos históricos (subregistro, diferencias de capacidad de denuncia entre
  territorios), y por eso sus resultados deben complementar el criterio institucional,
  no reemplazarlo.

## 6. Cierre (30 segundos)

SafeAnalytics EC recorre el ciclo completo de la analítica de negocios: datos reales,
ingeniería de datos con modelo estrella, una API pública integrada, estadística
descriptiva y de dispersión, correlación, un modelo predictivo validado contra un
algoritmo clásico, y recomendaciones prescriptivas con simulación de escenarios.

Los datos dejaron de ser un archivo de Excel. Ahora son inteligencia accionable.
Gracias — quedamos atentos a sus preguntas.

---

## Anexo: preguntas probables del docente y cómo responderlas

**«¿Por qué no usaron un modelo más sofisticado (random forest, redes)?»**
Porque lo comprobamos empíricamente: la Regresión Lineal rinde igual que nuestro
baseline (R² 0,532 vs 0,533). Con cinco meses de datos, más complejidad solo agrega
riesgo de sobreajuste y pérdida de explicabilidad. Con más meses de historia, esos
modelos serían el siguiente paso natural, y nuestro baseline queda como punto de
comparación.

**«¿Qué significa el R² de 0,53?»**
Que el modelo explica alrededor del 53% de la variabilidad de la incidencia diaria por
provincia. Es razonable para un horizonte corto y sin variables externas (población
local, operativos, contexto socioeconómico). Lo importante: es suficiente para
*priorizar territorios*, que es su función, no para pronóstico operativo exacto.

**«¿Dónde está la API pública que pide la rúbrica?»**
Banco Mundial, indicador SP.POP.TOTL, consumida en vivo desde `src/etl/poblacion_api.py`
con una estrategia de tres niveles: API en vivo → caché en disco → valor de respaldo.
Su producto visible es la tasa por 100.000 habitantes del encabezado. Además
investigamos la API CKAN de Datos Abiertos Ecuador para el dataset del MDI, pero el
portal bloquea el acceso programático (error 403), decisión que documentamos en el
informe.

**«¿Los cuatro tipos de analítica dónde están?»**
En el propio orden de las pestañas: Ejecutivo y Caracterización (descriptiva),
Geográfico y Temporal (diagnóstica), Predictiva (predictiva), Riesgo y Simulador
(prescriptiva). La navegación de la app *es* la progresión de madurez analítica.

**«¿Cómo garantizan que los datos no fueron alterados?»**
Trazabilidad completa: el Excel original se conserva, el ETL es un script reproducible,
cada tabla generada tiene reporte de calidad, y la pestaña Datos permite descargar y
auditar todo. Cualquiera puede regenerar el proyecto con cuatro comandos.

**«¿Una provincia con más homicidios es más peligrosa?»**
No necesariamente, y la app lo advierte: correlación no es causalidad. Guayas concentra
más casos en parte por tamaño poblacional y densidad urbana. Por eso integramos la tasa
por 100.000 habitantes y por eso las recomendaciones son insumos para el criterio
técnico, no sentencias automáticas.
