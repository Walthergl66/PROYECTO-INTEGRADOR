# Fase 1: Definición del Negocio y Entendimiento del Problema

## 1.1. Contexto del Negocio

**SafeAnalytics EC** es una solución analítica orientada al monitoreo estratégico de homicidios intencionales en Ecuador. El proyecto se enfoca en el ámbito de la seguridad ciudadana y está dirigido a instituciones, autoridades, unidades de análisis criminal, responsables de planificación operativa y tomadores de decisiones que necesitan interpretar grandes volúmenes de información delictiva de forma rápida, clara y confiable.

Las instituciones encargadas de la seguridad generan y administran registros relacionados con muertes violentas, ubicación geográfica, fechas, horarios, tipo de arma, presunta motivación y características de las víctimas. Sin embargo, cuando esta información se mantiene únicamente en archivos tabulares o reportes aislados, su valor estratégico disminuye, ya que se dificulta detectar patrones, comparar territorios, priorizar zonas críticas y tomar decisiones basadas en evidencia.

En este contexto, SafeAnalytics EC busca transformar datos operativos sobre homicidios intencionales en inteligencia ejecutiva para apoyar la prevención del delito, la asignación de recursos y el seguimiento de indicadores de seguridad.

## 1.2. Planteamiento del Problema

Las instituciones de seguridad ciudadana generan diariamente grandes volúmenes de información sobre homicidios intencionales. No obstante, estos datos suelen encontrarse dispersos en bases de datos, archivos Excel o reportes tabulares, lo que dificulta su análisis oportuno y limita la capacidad de identificar patrones delictivos de manera eficiente.

El problema principal es que el análisis manual de esta información retrasa la toma de decisiones estratégicas. Esto afecta la planificación de operativos, la distribución de recursos policiales, la identificación de zonas de mayor incidencia y la implementación de políticas públicas orientadas a la prevención del delito.

Además, sin una plataforma visual e interactiva resulta complejo responder preguntas clave como:

- ¿Qué provincias y cantones concentran la mayor cantidad de homicidios intencionales?
- ¿Cuáles son los horarios, días o meses con mayor incidencia?
- ¿Qué tipos de armas son más utilizados?
- ¿Qué características predominan en las víctimas?
- ¿Qué territorios requieren intervención prioritaria?
- ¿Cómo evoluciona la incidencia delictiva durante el periodo analizado?

Ante esta problemática, surge la necesidad de desarrollar un dashboard ejecutivo que consolide la información en una única plataforma analítica, permitiendo visualizar indicadores, detectar patrones geográficos y temporales, y generar recomendaciones para apoyar la toma de decisiones basada en datos.

## 1.3. Objetivos de Analítica

### Objetivo General

Diseñar e implementar un dashboard ejecutivo interactivo que permita visualizar y analizar los principales indicadores relacionados con homicidios intencionales registrados en Ecuador, facilitando el monitoreo de la incidencia delictiva, la identificación de patrones geográficos y temporales, y el apoyo a la toma de decisiones estratégicas en materia de seguridad ciudadana.

### Analítica Descriptiva

Responder qué está ocurriendo en el periodo analizado mediante indicadores generales y visualizaciones de resumen.

Preguntas principales:

- ¿Cuántos homicidios intencionales se registraron?
- ¿Cuántas provincias y cantones fueron afectados?
- ¿Cuál es la distribución por tipo de arma?
- ¿Cuál es el perfil predominante de las víctimas?
- ¿Qué lugares y zonas presentan mayor frecuencia de eventos?

Indicadores asociados:

- Total de homicidios intencionales.
- Provincias afectadas.
- Cantones afectados.
- Porcentaje de casos con arma de fuego.
- Porcentaje de víctimas hombres.
- Edad promedio de víctimas.

### Analítica Diagnóstica

Explicar dónde, cuándo y bajo qué características se concentra la incidencia delictiva.

Preguntas principales:

- ¿Qué provincias y cantones concentran la mayor incidencia?
- ¿En qué horarios se presentan más casos?
- ¿Qué patrones existen por mes, día de semana y franja horaria?
- ¿Qué relación existe entre tipo de lugar, tipo de arma y concentración territorial?

Resultados esperados:

- Rankings territoriales por provincia y cantón.
- Identificación de hora crítica.
- Comparación mensual de incidencia.
- Caracterización del delito por arma, lugar y motivación.

### Analítica Predictiva

Estimar señales de incidencia futura o esperada a partir del comportamiento histórico disponible.

Preguntas principales:

- ¿Qué territorios presentan mayor probabilidad de mantener niveles altos de incidencia?
- ¿Qué provincias requieren monitoreo reforzado por tendencia reciente?
- ¿Cómo puede proyectarse la incidencia diaria o mensual con los datos disponibles?

Resultado esperado:

- Modelo predictivo exploratorio de incidencia diaria por provincia.
- Métricas de evaluación como MAE y RMSE.
- Identificación de territorios con mayor prioridad de seguimiento.

### Analítica Prescriptiva

Proponer acciones estratégicas a partir de los hallazgos descriptivos, diagnósticos y predictivos.

Preguntas principales:

- ¿Qué provincias o cantones deben priorizarse?
- ¿Qué territorios requieren monitoreo preventivo, reforzado o intervención prioritaria?
- ¿Qué impacto podría tener una reducción porcentual de la incidencia?

Resultados esperados:

- Índice de riesgo territorial.
- Alertas ejecutivas.
- Recomendaciones estratégicas por provincia.
- Simulador de escenarios para estimar casos evitables ante reducciones hipotéticas de incidencia.

## 1.4. Identificación de Fuentes de Datos y Ética Inicial

### Fuente de Datos Principal

La fuente de datos utilizada en el proyecto es el archivo:

`mdi_homicidiosintencionalse_pm_2026_enero_mayo.xlsx`

Este archivo contiene registros de homicidios intencionales correspondientes al periodo de enero a mayo de 2026. La información incluye variables relacionadas con:

- Tipo de muerte.
- Zona, subzona, distrito, circuito y subcircuito.
- Provincia y cantón.
- Coordenadas geográficas.
- Área y lugar del hecho.
- Fecha y hora de la infracción.
- Arma y tipo de arma.
- Presunta motivación.
- Edad, sexo, género, etnia, nacionalidad e instrucción de la víctima.

El dataset permite construir un modelo analítico multidimensional para estudiar los homicidios intencionales desde perspectivas territoriales, temporales, delictivas y sociodemográficas.

### Estrategia Inicial de Gobernanza y Ética

Debido a que el proyecto trabaja con datos relacionados con seguridad ciudadana y características de víctimas, se consideran principios básicos de gobernanza y ética de datos:

- **Privacidad desde el diseño:** el análisis se enfoca en patrones agregados y no en la identificación individual de personas.
- **Minimización de datos sensibles:** las variables personales se utilizan únicamente con fines estadísticos y de caracterización general.
- **Uso responsable de coordenadas:** la información geográfica debe emplearse para análisis territorial y planificación, evitando exponer ubicaciones sensibles de forma innecesaria.
- **No discriminación:** variables como sexo, género, etnia o nacionalidad no deben utilizarse para estigmatizar grupos poblacionales.
- **Transparencia:** los indicadores, reglas de riesgo y recomendaciones deben ser explicables para los usuarios ejecutivos.
- **Limitación del modelo predictivo:** las predicciones se interpretan como señales de apoyo a la decisión, no como conclusiones absolutas ni determinaciones causales.

### Consideraciones Éticas Iniciales

El dashboard debe evitar interpretaciones que criminalicen territorios o grupos humanos. Su propósito es apoyar la planificación institucional, la prevención del delito y la asignación eficiente de recursos, no generar perfiles discriminatorios.

Por ello, los resultados se presentan principalmente a nivel agregado por provincia, cantón, zona, tiempo y características generales del evento. Las recomendaciones deben entenderse como insumos para análisis estratégico y no como sustituto del criterio técnico de las autoridades competentes.
