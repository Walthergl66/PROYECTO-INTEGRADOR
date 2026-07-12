# Guia Power BI - SafeAnalytics EC

Esta guia complementa el archivo `powerbi/SafeAnalytics_EC.pbix` y las tablas reunidas en
`powerbi/data/` (las 5 tablas del modelo estrella mas 4 reportes, y el libro combinado
`SafeAnalytics_EC_datos.xlsx` con las 9 en hojas separadas, listo para importar de una
sola vez). Para el paso a paso detallado de clics, ver `powerbi/PASO_A_PASO_POWER_BI.md`.

## Tablas recomendadas

- `fact_homicidios.csv`: tabla de hechos con un registro por victima/evento.
- `dim_tiempo.csv`: calendario diario enero-mayo 2026.
- `dim_geografia.csv`: provincia, canton, zona, distrito, circuito y subcircuito.
- `dim_delito.csv`: tipo de muerte, arma, tipo de arma, lugar y motivacion.
- `dim_victima.csv`: sexo, genero, etnia, nacionalidad e instruccion.
- `indicadores_provincia.csv` (opcional): indicadores numericos por provincia para analisis de correlacion.
- `correlacion_provincias.csv` (opcional): matriz de correlacion lista para visualizar como matriz/heatmap.

### Tipos de dato que requieren atencion especial

- **`id_geografia`** (en `fact_homicidios` y `dim_geografia`): debe quedar como **Texto**
  en ambas tablas. Es un codigo geografico (definido asi desde el ETL,
  `df["id_geografia"] = df["codigo_canton"].astype(str)`), no una cantidad; si queda como
  Numero, Power BI le agrega separador de miles y se ve mal.
- **`fecha_infraccion`** (en `fact_homicidios`): debe quedar como **Fecha**, no
  "Fecha/hora". Esta columna nunca tuvo hora; si se marca como Fecha/hora, Power BI
  muestra `12:00 AM` en todos los registros (no es un error, es que no hay otra hora
  que mostrar). La hora real del suceso vive en la columna separada `hora` (0-23).

### Poblacion para la tasa por 100.000 habitantes

La poblacion de Ecuador proviene de la API publica del Banco Mundial (`SP.POP.TOTL`) y queda cacheada en `data/processed/poblacion_ecuador.json` (por ejemplo, 18.289.896 habitantes en 2025). Para Power BI puede cargarse ese valor como un parametro/tabla de una fila o escribirse directamente en la medida.

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

-- Poblacion de Ecuador obtenida de la API del Banco Mundial (SP.POP.TOTL).
-- Ajustar el valor segun data/processed/poblacion_ecuador.json.
Poblacion Ecuador = 18289896

-- Tasa acumulada del periodo (enero-mayo 2026) por cada 100.000 habitantes.
Tasa x100k Periodo =
DIVIDE([Total Homicidios], [Poblacion Ecuador]) * 100000

-- Tasa anualizada estimada (proyecta la incidencia diaria a 365 dias).
Tasa x100k Anualizada =
VAR Dias = DISTINCTCOUNT(dim_tiempo[fecha])
RETURN
DIVIDE([Total Homicidios] * 365 / Dias, [Poblacion Ecuador]) * 100000

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

1. **Dashboard Ejecutivo:** KPIs principales (incluida la tasa por 100.000 hab.), tendencia mensual, top provincias y top cantones.
2. **Analisis Geografico y Temporal:** mapa, zona/subzona, hora critica, dia de semana.
3. **Caracterizacion del Delito:** arma, tipo de arma, lugar, motivacion y perfil de victima.
4. **Prediccion y Recomendaciones:** matriz de priorizacion, acciones por provincia y observaciones.
5. **Riesgo Territorial:** tabla semaforizada por provincia/canton usando `indice_riesgo` y `nivel_riesgo`.
6. **Simulador Ejecutivo:** escenario de reduccion porcentual y casos evitables estimados.
7. **Metodologia y Estadistica (opcional):** medidas de dispersion (desviacion estandar, CV) y matriz de correlacion entre indicadores provinciales, cargando `reports/correlacion_provincias.csv` como matriz.

## Paleta sugerida

- Azul institucional: `#12355B`
- Teal analitico: `#0F766E`
- Ambar alerta: `#D99A21`
- Rojo critico: `#B42318`
- Fondo claro: `#F6F8FA`
