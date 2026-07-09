# Guia Power BI - SafeAnalytics EC

Esta guia complementa el archivo `Dashboards de criminalistica de homicidios.pbix.zip` y las tablas generadas en `data/processed/`.

## Tablas recomendadas

- `fact_homicidios.csv`: tabla de hechos con un registro por victima/evento.
- `dim_tiempo.csv`: calendario diario enero-mayo 2026.
- `dim_geografia.csv`: provincia, canton, zona, distrito, circuito y subcircuito.
- `dim_delito.csv`: tipo de muerte, arma, tipo de arma, lugar y motivacion.
- `dim_victima.csv`: sexo, genero, etnia, nacionalidad e instruccion.

## Relaciones

- `fact_homicidios[id_fecha]` -> `dim_tiempo[id_fecha]`
- `fact_homicidios[id_geografia]` -> `dim_geografia[id_geografia]`
- `fact_homicidios[id_delito]` -> `dim_delito[id_delito]`
- `fact_homicidios[id_victima]` -> `dim_victima[id_victima]`

Todas las relaciones deben ser muchos a uno, con filtrado desde dimensiones hacia la tabla de hechos.

## Medidas DAX

```DAX
Total Homicidios = SUM(fact_homicidios[total_homicidios])

Provincias Afectadas = DISTINCTCOUNT(dim_geografia[provincia])

Cantones Afectados = DISTINCTCOUNT(dim_geografia[canton])

Casos Arma de Fuego =
CALCULATE([Total Homicidios], dim_delito[arma] = "ARMA DE FUEGO")

% Arma de Fuego =
DIVIDE([Casos Arma de Fuego], [Total Homicidios])

Victimas Hombres =
CALCULATE([Total Homicidios], dim_victima[sexo] = "HOMBRE")

% Victimas Hombres =
DIVIDE([Victimas Hombres], [Total Homicidios])

Edad Promedio =
AVERAGE(fact_homicidios[edad_num])

Provincia Mayor Incidencia =
VAR Ranking =
    TOPN(1, VALUES(dim_geografia[provincia]), [Total Homicidios], DESC)
RETURN
    CONCATENATEX(Ranking, dim_geografia[provincia], ", ")

Hora Critica =
VAR Ranking =
    TOPN(1, VALUES(fact_homicidios[hora]), [Total Homicidios], DESC)
RETURN
    CONCATENATEX(Ranking, fact_homicidios[hora], ", ")
```

## Paginas sugeridas

1. **Dashboard Ejecutivo:** KPIs principales, tendencia mensual, top provincias y top cantones.
2. **Analisis Geografico y Temporal:** mapa, zona/subzona, hora critica, dia de semana.
3. **Caracterizacion del Delito:** arma, tipo de arma, lugar, motivacion y perfil de victima.
4. **Prediccion y Recomendaciones:** matriz de priorizacion, acciones por provincia y observaciones.
5. **Riesgo Territorial:** tabla semaforizada por provincia/canton usando `indice_riesgo` y `nivel_riesgo`.
6. **Simulador Ejecutivo:** escenario de reduccion porcentual y casos evitables estimados.

## Paleta sugerida

- Azul institucional: `#12355B`
- Teal analitico: `#0F766E`
- Ambar alerta: `#D99A21`
- Rojo critico: `#B42318`
- Fondo claro: `#F6F8FA`
