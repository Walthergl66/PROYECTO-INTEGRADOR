# Justificación del Modelo Predictivo

## Decisión Metodológica

El proyecto SafeAnalytics EC utiliza un modelo predictivo baseline provincial ajustado por día de semana y tendencia reciente. Esta decisión se tomó porque el dataset disponible contiene registros reales de enero a mayo de 2026, es decir, un horizonte temporal corto para entrenar un modelo estadístico complejo sin riesgo de sobreajuste.

En lugar de aplicar un algoritmo más sofisticado únicamente para cumplir una expectativa técnica, se priorizó un enfoque explicable, auditable y coherente con los datos disponibles.

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

El modelo fue evaluado con una división temporal entre entrenamiento y prueba.

| Métrica | Valor |
|---|---:|
| Registros de entrenamiento | 813 |
| Registros de prueba | 199 |
| MAE | 1,539 |
| RMSE | 2,621 |

El MAE indica que el error promedio es de aproximadamente 1,54 homicidios diarios por provincia. El RMSE penaliza errores grandes y permite evaluar desviaciones más fuertes.

## Relación con Algoritmos Clásicos

Un modelo de regresión, árbol de decisión o random forest podría incorporarse en una versión futura del proyecto. Sin embargo, con el volumen temporal actual, un modelo más complejo podría aprender patrones demasiado específicos de enero a mayo de 2026 y perder capacidad de generalización.

Por esta razón, el baseline se presenta como una alternativa metodológicamente válida para:

- Establecer una primera línea de comparación.
- Mantener explicabilidad.
- Evitar conclusiones sobredimensionadas.
- Priorizar utilidad ejecutiva sobre complejidad técnica.

## Cómo Defenderlo en la Exposición

La explicación recomendada es:

> Se eligió un baseline predictivo porque el dataset real cubre cinco meses. En seguridad ciudadana, un modelo debe ser explicable y prudente. Por eso se estimó incidencia diaria por provincia con promedio histórico, día de semana y tendencia reciente. Esto permite obtener métricas, generar señales de priorización y evitar sobreajuste. En una etapa futura, con más meses de datos, este baseline serviría como punto de comparación para modelos más complejos como árboles de decisión o random forest.

## Limitación Declarada

El modelo no debe interpretarse como un pronóstico operativo definitivo ni como una explicación causal. Su función es apoyar la priorización territorial y complementar el criterio técnico de los responsables de seguridad.
