# Guion de Defensa - SafeAnalytics EC

## Apertura

Buenos dias. El proyecto que presentamos se llama **SafeAnalytics EC**, un sistema inteligente de analitica de negocios orientado al monitoreo estrategico de homicidios intencionales en Ecuador.

El objetivo central es convertir registros operativos en informacion ejecutiva para apoyar decisiones sobre prevencion, priorizacion territorial y asignacion de recursos.

## Problematica

Las instituciones de seguridad generan grandes volumenes de datos, pero muchas veces estos datos se mantienen en archivos Excel, bases tabulares o reportes aislados. Esto dificulta detectar rapidamente patrones por provincia, canton, hora, tipo de arma o caracteristicas de las victimas.

El problema no es solo tener datos, sino poder leerlos de manera estrategica y convertirlos en decisiones oportunas.

## Fuente y Alcance

Trabajamos con dos fuentes de datos:

- **Principal:** el archivo real `mdi_homicidiosintencionalse_pm_2026_enero_mayo.xlsx` del Ministerio del Interior, con 3.485 homicidios intencionales de enero a mayo de 2026, 23 provincias y 138 cantones afectados.
- **Complementaria (API pública):** la API del Banco Mundial, de la que obtenemos la población de Ecuador para calcular la tasa de homicidios por cada 100.000 habitantes. Así la lectura no depende solo del número absoluto de casos.

## Ingenieria de Datos

El proyecto utiliza un pipeline ETL en Python. Este proceso lee el Excel, limpia textos, convierte fechas y horas, normaliza coordenadas, genera claves analiticas y construye un modelo estrella.

La tabla de hechos es `fact_homicidios` y las dimensiones son:

- `dim_tiempo`
- `dim_geografia`
- `dim_delito`
- `dim_victima`

Este modelo permite analizar el fenomeno desde cuatro perspectivas: tiempo, territorio, delito y victima.

## Hallazgos Principales

Los principales hallazgos son:

- Guayas concentra la mayor incidencia provincial.
- Guayaquil lidera el ranking cantonal.
- El arma de fuego representa el 87,8% de los casos.
- La hora critica identificada es 20:00.
- La edad promedio de las victimas es 31,6 anos.
- El 90,9% de las victimas registradas corresponde a hombres.
- La tasa anualizada estimada es de 46 homicidios por cada 100.000 habitantes.

Ademas, el analisis estadistico confirma con numeros la concentracion territorial: el coeficiente de variacion de la incidencia por provincia es del 218%, y la correlacion muestra que las provincias con mas casos son las mismas que mantienen alta incidencia reciente (r = 0,99) y afectan a mas cantones (r = 0,91). Aclaramos siempre que correlacion no es causalidad.

Estos resultados permiten entender donde se concentra el problema y que variables requieren monitoreo prioritario.

## Dashboard Ejecutivo

La app desarrollada en Streamlit permite explorar la informacion mediante filtros por provincia, mes y arma.

Las vistas principales son:

- Ejecutivo.
- Riesgo territorial.
- Simulador.
- Geografico.
- Temporal.
- Caracterizacion.
- Predictiva.
- Datos.
- Metodologia (fuentes, dispersion y mapa de calor de correlacion).

Durante la demo se recomienda mostrar:

1. KPIs principales.
2. Alertas ejecutivas.
3. Riesgo territorial por provincia.
4. Mapa geografico.
5. Simulador de escenarios.
6. Tabla de recomendaciones.

## Modelo Predictivo

El componente predictivo utiliza un baseline provincial ajustado por dia de semana y tendencia reciente. Para justificar la eleccion de forma objetiva, lo comparamos contra una Regresion Lineal de scikit-learn sobre la misma particion de datos.

Las metricas fueron:

| Modelo | MAE | RMSE | R2 |
|---|---|---|---|
| Baseline provincial | 1,539 | 2,621 | 0,533 |
| Regresion Lineal | 1,547 | 2,623 | 0,532 |

El punto clave para la defensa: ambos modelos rinden practicamente igual (R2 de 0,53). Esto demuestra con datos que un algoritmo mas complejo no mejora la prediccion con solo cinco meses de informacion. Por eso mantenemos el baseline: igual de preciso, pero mas explicable y auditable, algo esencial en seguridad ciudadana.

Ademas, la Regresion Lineal aporta explicabilidad (XAI): sus coeficientes muestran cuanto pesa cada variable, por ejemplo, pertenecer a Guayas suma unos 8,3 homicidios diarios a la estimacion.

El modelo no se presenta como un pronostico definitivo, sino como una senal de apoyo para priorizacion territorial.

## Analitica Prescriptiva

El sistema genera un indice de riesgo territorial de 0 a 100. Este indice considera:

- Volumen historico.
- Incidencia reciente.
- Variacion mensual.
- Porcentaje de arma de fuego.
- Porcentaje de ocurrencia en lugares publicos.

Tambien genera recomendaciones como:

- Priorizar intervencion.
- Mantener monitoreo reforzado.
- Monitoreo preventivo.

## Etica y Gobernanza

El proyecto trabaja con datos sensibles, por lo que se aplican principios de privacidad y gobernanza.

Los resultados se presentan de forma agregada. Las variables sensibles como sexo, genero, etnia o nacionalidad no se usan para criminalizar personas ni territorios. El modelo complementa el criterio tecnico, pero no reemplaza la decision humana.

## Cierre

SafeAnalytics EC demuestra como un dataset real puede transformarse en una solucion completa de analitica de negocios: ETL, modelo estrella, integracion de una API publica, EDA con medidas de dispersion y correlacion, tasa por 100.000 habitantes, dashboard ejecutivo, modelo predictivo comparado con regresion lineal, recomendaciones y simulador.

La principal contribucion del proyecto es que los datos dejan de ser reportes aislados y se convierten en inteligencia accionable para apoyar decisiones estrategicas en seguridad ciudadana.
