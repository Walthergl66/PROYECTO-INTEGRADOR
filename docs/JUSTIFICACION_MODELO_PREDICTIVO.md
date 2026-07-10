# Justificación del Modelo Predictivo

## Decisión Metodológica

El proyecto SafeAnalytics EC utiliza un modelo predictivo baseline provincial ajustado por día de semana y tendencia reciente. Esta decisión se tomó porque el dataset disponible contiene registros reales de enero a mayo de 2026, es decir, un horizonte temporal corto para entrenar un modelo estadístico complejo sin riesgo de sobreajuste.

Para respaldar esta decisión de forma objetiva, no se descartó el algoritmo clásico: se implementó una Regresión Lineal y se comparó contra el baseline (ver la sección de comparación). El baseline se mantuvo porque, con el mismo poder predictivo, ofrece mayor explicabilidad, auditabilidad y coherencia con los datos disponibles.

## Por Qué Se Eligió un Baseline

El baseline predictivo permite estimar la incidencia diaria esperada por provincia usando tres componentes:

- Promedio histórico provincial.
- Patrón por día de semana.
- Tendencia reciente.

La fórmula conceptual es:

```text
Predicción = promedio provincial x factor día de semana x factor de tendencia reciente
```

Este enfoque es adecuado para una primera versión porque:

- Evita sobreajuste con pocos meses de datos.
- Es fácil de explicar ante un comité ejecutivo.
- Permite auditar cómo se calcula cada predicción.
- Produce métricas cuantitativas de evaluación.
- Sirve como línea base para comparar modelos futuros.

## Métricas Obtenidas

El modelo fue evaluado con una división temporal entre entrenamiento (813 registros) y prueba (199 registros). Se añadieron tres métricas: MAE, RMSE y R² (coeficiente de determinación, que indica qué porcentaje de la variabilidad explica el modelo).

| Métrica | Valor |
|---|---:|
| Registros de entrenamiento | 813 |
| Registros de prueba | 199 |
| MAE | 1,539 |
| RMSE | 2,621 |
| R² | 0,533 |

El MAE indica que el error promedio es de aproximadamente 1,54 homicidios diarios por provincia. El RMSE penaliza errores grandes. El R² de 0,53 significa que el modelo explica cerca del 53% de la variabilidad de la incidencia diaria por provincia, un valor razonable para un horizonte temporal corto y sin variables externas.

## Comparación con un Algoritmo Clásico (Regresión Lineal)

Para justificar la elección de forma objetiva —y no solo por preferencia— se entrenó también una **Regresión Lineal** con scikit-learn sobre la misma partición de datos, codificando provincia y día de semana (One-Hot Encoding) e incorporando el mes y una tendencia temporal.

| Modelo | MAE | RMSE | R² |
|---|---:|---:|---:|
| Baseline provincial | 1,539 | 2,621 | 0,533 |
| Regresión Lineal (scikit-learn) | 1,547 | 2,623 | 0,532 |

**El resultado es contundente:** la Regresión Lineal obtiene un desempeño prácticamente idéntico al baseline (R² 0,532 frente a 0,533). Esto demuestra empíricamente que incorporar un algoritmo más estándar **no mejora** la predicción con los datos disponibles.

Por lo tanto, se mantiene el baseline como modelo desplegado porque, a igual poder predictivo, aporta:

- Mayor explicabilidad y transparencia.
- Auditabilidad de cada predicción.
- Prudencia adecuada al horizonte de cinco meses.
- Utilidad ejecutiva sobre complejidad técnica innecesaria.

La Regresión Lineal, además, aporta explicabilidad (XAI): sus coeficientes muestran cuánto pesa cada variable (por ejemplo, pertenecer a Guayas suma ~8,3 homicidios diarios a la estimación).

## Cómo Defenderlo en la Exposición

La explicación recomendada es:

> Se eligió un baseline predictivo porque el dataset real cubre solo cinco meses. En seguridad ciudadana, un modelo debe ser explicable y prudente. Por eso se estimó la incidencia diaria por provincia con promedio histórico, día de semana y tendencia reciente. Para validar la decisión, comparamos este baseline contra una Regresión Lineal de scikit-learn: ambos obtuvieron el mismo desempeño (R² de 0,53). Es decir, un algoritmo clásico no mejora el resultado, así que mantenemos el baseline porque es igual de preciso pero más transparente y auditable. En una etapa futura, con más meses de datos, se podría explorar árboles de decisión o random forest.

## Limitación Declarada

El modelo no debe interpretarse como un pronóstico operativo definitivo ni como una explicación causal. Su función es apoyar la priorización territorial y complementar el criterio técnico de los responsables de seguridad.
