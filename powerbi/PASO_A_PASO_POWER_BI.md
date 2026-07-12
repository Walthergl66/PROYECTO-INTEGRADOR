# Guía paso a paso para construir el entregable en Power BI

**Proyecto:** SafeAnalytics EC — Analítica de Negocios 7A

Esta guía te lleva de la mano, punto por punto, desde abrir Power BI hasta tener el
dashboard terminado y listo para entregar. Está pensada para que la siga cualquier
persona, incluso sin experiencia previa en Power BI.

> **Si ya tienes el archivo `Dashboards de criminalistica de homicidios.pbix`**, puedes
> saltarte los PASOS 1–6 (importar y modelar) y usar esta guía para revisar el modelo,
> crear las medidas que falten (PASO 7) y completar las páginas (PASO 8).

---

## PASO 0. Antes de empezar (requisitos)

1. Tener instalado **Power BI Desktop** (gratis desde la Microsoft Store o powerbi.microsoft.com).
2. Todos los datos ya están reunidos en una sola carpeta: **`powerbi/data/`**. Contiene:
   - Las 5 tablas del modelo estrella: `fact_homicidios.csv`, `dim_tiempo.csv`,
     `dim_geografia.csv`, `dim_delito.csv`, `dim_victima.csv`.
   - Los 4 reportes extra (para páginas avanzadas): `riesgo_territorial.csv`,
     `recomendaciones_estrategicas.csv`, `correlacion_provincias.csv`,
     `indicadores_provincia.csv`.
   - **`SafeAnalytics_EC_datos.xlsx`**: las 9 tablas anteriores combinadas en un solo
     libro de Excel, una por hoja. Es el archivo recomendado para importar (ver PASO 3).
3. Tener el tema visual: `powerbi/tema_safeanalytics.json`.

> Si `powerbi/data/` no existiera o quedara desactualizada, regenera las tablas base con
> `python src/etl/transform_load.py` (quedan en `data/processed/` y `reports/`).

---

## PASO 1. Crear el archivo y desactivar una opción molesta

1. Abre **Power BI Desktop**.
2. Ve a **Archivo → Opciones y configuración → Opciones**.
3. En **Carga de datos**, **desmarca** la casilla *"Detección automática de fecha y hora"*
   (evita que Power BI cree jerarquías de fecha innecesarias).
4. Pulsa **Aceptar**.
5. Guarda el archivo desde ya: **Archivo → Guardar como** → `SafeAnalytics_EC.pbix`.

---

## PASO 2. Aplicar el tema visual (colores del proyecto)

1. En la cinta superior, ve a la pestaña **Vista**.
2. Haz clic en **Temas → Buscar temas**.
3. Selecciona el archivo `powerbi/tema_safeanalytics.json`.
4. Verás que la paleta cambia a los colores institucionales:
   - Teal `#0F766E` (color principal de análisis).
   - Azul `#12355B` (institucional).
   - Ámbar `#D99A21` (advertencia).
   - Rojo `#B42318` (riesgo alto/alerta).

---

## PASO 3. Importar las tablas (método recomendado: Excel combinado)

El conector de Texto/CSV de Power BI no siempre permite seleccionar varios archivos a la
vez. Para evitar ese problema, las 9 tablas ya están combinadas en un solo libro de Excel
(`powerbi/data/SafeAnalytics_EC_datos.xlsx`), una tabla por hoja. Esto permite cargarlas
**todas de una sola vez**:

1. En la pestaña **Inicio**, haz clic en **Obtener datos → Excel**.
2. Selecciona el archivo `powerbi/data/SafeAnalytics_EC_datos.xlsx` y ábrelo.
3. Se abre el **Navegador**, con las 9 hojas listadas y una casilla de verificación junto
   a cada una.
4. **Marca las 9 casillas** (o usa "Seleccionar varios elementos" si aparece esa opción).
5. Haz clic en **Transformar datos** (NO en "Cargar" todavía; primero ajustamos los tipos
   de datos en el PASO 4).
6. Se abre el **Editor de Power Query** con las 9 consultas en el panel izquierdo.

Al terminar el PASO 4, harás clic en **Cerrar y aplicar** y tendrás las 9 tablas en el
panel **Datos** (a la derecha).

> **Alternativa (si prefieres importar CSV por separado):** repite **Obtener datos →
> Texto/CSV** una vez por cada archivo en `powerbi/data/*.csv`, confirmando en cada uno
> que el **Origen de archivo** sea *65001: Unicode (UTF-8)* (así se ven bien los acentos
> y la ñ). El resultado final es el mismo; el método del Excel combinado solo ahorra
> pasos.

---

## PASO 4. Revisar y ajustar los tipos de datos

Entra al **Editor de Power Query** (pestaña **Inicio → Transformar datos**) y, para cada
tabla, haz clic en el ícono a la izquierda del nombre de cada columna para fijar su tipo.
Usa esta referencia:

**fact_homicidios**

| Columna | Tipo de dato |
|---|---|
| id_homicidio, id_fecha, id_delito, id_victima | Número entero |
| id_geografia | **Texto** (importante: es un código, ver nota abajo) |
| fecha_infraccion | **Fecha** (NO "Fecha/hora", ver nota abajo) |
| hora, total_homicidios | Número entero |
| edad_num | Número decimal |
| latitud, longitud | Número decimal |
| franja_horaria | Texto |

> ⚠️ **Sobre `fecha_infraccion`:** esta columna solo contiene la fecha (ej. `2026-05-31`);
> nunca tuvo información de hora. Si la marcas como "Fecha/hora", Power BI mostrará
> `12:00 AM` en todos los registros — no es un error, es que no hay otra hora que
> mostrar. Márcala como **Fecha** a secas para evitar esa confusión. **La hora real del
> suceso está en la columna separada `hora`** (número de 0 a 23), que es la que se usa
> para los análisis por hora del día (PASO 8, Página 2).

**dim_tiempo**

| Columna | Tipo de dato |
|---|---|
| fecha | Fecha |
| id_fecha, anio, mes, dia, semana | Número entero |
| mes_nombre, nombre_dia | Texto |
| dia_semana | Número entero |

**dim_geografia**: `id_geografia` y `codigo_canton` como **Texto**; el resto (provincia,
canton, zona, etc.) como **Texto**.

**dim_delito**: `id_delito` como **Número entero**; el resto como **Texto**.

**dim_victima**: `id_victima` como **Número entero**; el resto como **Texto**.

> **Regla de oro:** la columna que une dos tablas debe tener el **mismo tipo** en ambas.
> Por ejemplo, `id_geografia` debe ser Texto tanto en `fact_homicidios` como en
> `dim_geografia`. Si no coinciden, la relación fallará.

> **¿Por qué `id_geografia` va como Texto y no como Número?** Porque así se diseñó desde
> el propio código del ETL (`src/etl/transform_load.py`, línea
> `df["id_geografia"] = df["codigo_canton"].astype(str)`): es un código geográfico
> (como un código postal), no una cantidad que tenga sentido sumar o promediar. Además,
> como Número, Power BI le pondría separador de miles (se vería "1,705" en vez de
> "1705"), lo cual es incorrecto para un código. Lo importante en la práctica es que
> quede **igual en ambas tablas relacionadas**.

Cuando termines, **Cerrar y aplicar**.

---

## PASO 5. Construir el modelo estrella (relaciones)

1. En la barra izquierda, entra a la **Vista de modelo** (ícono de tablas conectadas).
2. Verás las 5 tablas. Vas a crear 4 relaciones **arrastrando** una clave sobre la otra:

   | Desde (tabla de hechos) | Hacia (dimensión) |
   |---|---|
   | `fact_homicidios[id_fecha]` | `dim_tiempo[id_fecha]` |
   | `fact_homicidios[id_geografia]` | `dim_geografia[id_geografia]` |
   | `fact_homicidios[id_delito]` | `dim_delito[id_delito]` |
   | `fact_homicidios[id_victima]` | `dim_victima[id_victima]` |

3. Para cada una: arrastra la columna de `fact_homicidios` y suéltala sobre la columna
   correspondiente de la dimensión.
4. Haz doble clic en cada línea de relación y confirma que sea:
   - **Cardinalidad:** *Varios a uno (\*:1)* — muchos hechos, una dimensión.
   - **Dirección del filtro cruzado:** *Única*.
5. El resultado debe verse como una estrella: `fact_homicidios` en el centro y las 4
   dimensiones alrededor.

---

## PASO 6. Marcar la tabla de calendario (recomendado)

1. Selecciona la tabla **dim_tiempo** en el panel de datos.
2. En la cinta, **Herramientas de tabla → Marcar como tabla de fechas**.
3. Elige la columna **fecha**. Acepta.

Esto permite que los análisis temporales (por mes, semana, etc.) funcionen correctamente.

---

## PASO 7. Crear las medidas (DAX)

Las medidas son cálculos reutilizables. Para mantener orden, crea una tabla vacía solo
para medidas:

1. Pestaña **Inicio → Escribir una consulta DAX** no; mejor: **Inicio → Nueva tabla**
   (o simplemente crea las medidas dentro de `fact_homicidios`).
2. Para crear cada medida: clic derecho sobre la tabla → **Nueva medida**, y pega el
   código. Repite para cada una.

> **Convención de nombres:** las medidas usan espacio (`Total Homicidios`) en vez de
> guion bajo, para diferenciarlas de un vistazo de las columnas de las tablas (que sí
> usan guion bajo, ej. `total_homicidios`). Si una medida referencia a otra dentro de su
> fórmula (ej. `[Total Homicidios]` dentro de `Casos Arma de Fuego`), el nombre debe
> coincidir exactamente, espacio incluido. **Créalas en el orden de abajo**, porque
> varias dependen de las anteriores.

```DAX
Total Homicidios = SUM(fact_homicidios[total_homicidios])

Provincias Afectadas = DISTINCTCOUNT(dim_geografia[provincia])

Cantones Afectados = DISTINCTCOUNT(dim_geografia[canton])

Casos Arma de Fuego =
CALCULATE([Total Homicidios], dim_delito[arma] = "ARMA DE FUEGO")

% Arma de Fuego = DIVIDE([Casos Arma de Fuego], [Total Homicidios])

Victimas Hombres =
CALCULATE([Total Homicidios], dim_victima[sexo] = "HOMBRE")

% Victimas Hombres = DIVIDE([Victimas Hombres], [Total Homicidios])

Edad Promedio = AVERAGE(fact_homicidios[edad_num])

-- Poblacion de Ecuador (API del Banco Mundial, SP.POP.TOTL).
-- Ajusta el valor con data/processed/poblacion_ecuador.json.
Poblacion Ecuador = 18289896

-- Tasa acumulada del periodo (enero-mayo 2026) por 100.000 habitantes.
Tasa x100k Periodo =
DIVIDE([Total Homicidios], [Poblacion Ecuador]) * 100000

-- Tasa anualizada estimada (proyecta la incidencia diaria a 365 dias).
Tasa x100k Anualizada =
VAR Dias = DISTINCTCOUNT(dim_tiempo[fecha])
RETURN DIVIDE([Total Homicidios] * 365 / Dias, [Poblacion Ecuador]) * 100000
```

> Formato: para `% Arma de Fuego` y `% Victimas Hombres`, con la medida seleccionada ve a
> **Herramientas de medida → Formato → Porcentaje**. Para `Edad Promedio` y las tasas,
> usa 1 o 2 decimales.

---

## PASO 8. Construir las páginas del dashboard

Cada página se crea con el botón **+** abajo (pestañas de página). Renómbralas con doble
clic. Para poner un título, usa **Insertar → Cuadro de texto**.

### Página 1 — Dashboard Ejecutivo

1. **Título** (cuadro de texto): "Dashboard Ejecutivo — Homicidios Intencionales 2026".
2. **Cinco tarjetas (Card)** en fila. Inserta un visual **Tarjeta** por cada una y arrastra:
   - `Total Homicidios`
   - `Provincias Afectadas`
   - `Cantones Afectados`
   - `% Arma de Fuego`
   - `Tasa x100k Anualizada`
3. **Gráfico de líneas** (evolución mensual):
   - Visual: **Gráfico de líneas**.
   - Eje X: `dim_tiempo[mes_nombre]` (ordénalo por `mes`: selecciona la columna
     `mes_nombre` → **Ordenar por columna → mes**).
   - Eje Y: `Total Homicidios`.
4. **Gráfico de barras horizontales** (top provincias):
   - Visual: **Gráfico de barras agrupadas**.
   - Eje Y: `dim_geografia[provincia]`; Eje X: `Total Homicidios`.
   - Filtro del visual: *Top 10* por `Total Homicidios` (en el panel Filtros).
5. **Gráfico de barras** (top cantones): igual que el anterior pero con
   `dim_geografia[canton]`, Top 10.

### Página 2 — Análisis Geográfico y Temporal

1. **Mapa** de puntos:
   - Visual: **Mapa** (o "Mapa de Azure").
   - Latitud: `fact_homicidios[latitud]`; Longitud: `fact_homicidios[longitud]`.
   - Tamaño: `Total Homicidios`; Leyenda: `dim_geografia[provincia]`.
   - Importante: en cada campo de lat/long, cámbialo a **No resumir** (clic en la flechita
     del campo → *No resumir*).
2. **Gráfico de columnas** por hora:
   - Eje X: `fact_homicidios[hora]`; Eje Y: `Total Homicidios`.
3. **Gráfico de líneas** por día de semana:
   - Eje X: `dim_tiempo[nombre_dia]` (ordénalo por `dia_semana`); Eje Y: `Total Homicidios`.
4. **Matriz / mapa de calor día × hora**:
   - Visual: **Matriz**.
   - Filas: `dim_tiempo[nombre_dia]`; Columnas: `fact_homicidios[hora]`;
     Valores: `Total Homicidios`.
   - En **Formato → Formato condicional → Color de fondo**, actívalo para pintar los
     valores altos (escala de color).

### Página 3 — Caracterización del Delito

1. **Anillo (Donut)** por tipo de arma:
   - Leyenda: `dim_delito[arma]`; Valores: `Total Homicidios`.
2. **Barras horizontales** por motivación:
   - Eje Y: `dim_delito[presunta_motivacion]`; Eje X: `Total Homicidios`; Top 10.
3. **Circular (Pie)** por sexo:
   - Leyenda: `dim_victima[sexo]`; Valores: `Total Homicidios`.
4. **Histograma de edad**:
   - Visual: **Gráfico de columnas agrupadas**.
   - Eje X: `fact_homicidios[edad_num]`; Eje Y: `Total Homicidios` (o Recuento).

### Página 4 — Predicción y Recomendaciones

Esta página usa la tabla `riesgo_territorial`, que ya trae el índice y las acciones
calculadas. Si seguiste el PASO 3 con el Excel combinado, esta hoja **ya está cargada**;
si importaste solo las 5 tablas base, agrégala ahora con **Obtener datos → Texto/CSV**
apuntando a `powerbi/data/riesgo_territorial.csv`.

1. **Dispersión (Scatter)** — matriz de priorización:
   - Eje X: `homicidios_ultimo_mes`; Eje Y: `variacion_mensual_pct`;
     Tamaño: `total_homicidios`; Leyenda: `accion`; Detalles: `provincia`.
2. **Tabla** de recomendaciones:
   - Columnas: `provincia`, `nivel_riesgo`, `indice_riesgo`, `total_homicidios`,
     `accion`, `recomendacion`.

### Página 5 — Riesgo Territorial

1. **Barras horizontales** del índice:
   - Eje Y: `provincia`; Eje X: `indice_riesgo`; Leyenda: `nivel_riesgo`.
2. **Tabla semaforizada**:
   - Columnas: `provincia`, `nivel_riesgo`, `indice_riesgo`, `total_homicidios`,
     `pct_arma_fuego`, `pct_lugar_publico`.
   - **Formato condicional** en `nivel_riesgo` o `indice_riesgo`
     (**Formato → Formato condicional → Color de fondo → Reglas**):
     - Alto → rojo `#B42318`
     - Medio → ámbar `#D99A21`
     - Bajo → teal `#0F766E`

### Página 6 (opcional) — Metodología y Estadística

Usa las hojas `correlacion_provincias` e `indicadores_provincia` (ya incluidas si
cargaste el Excel combinado del PASO 3; si no, impórtalas desde
`powerbi/data/correlacion_provincias.csv` e `powerbi/data/indicadores_provincia.csv`).

1. **Matriz de correlación**:
   - Visual: **Matriz**. La primera columna (sin nombre) son las variables; ponla en Filas
     y las demás columnas numéricas en Valores. Aplica formato condicional de color para
     que se vea como un mapa de calor.
2. **Tarjetas** con medidas de dispersión (opcional): puedes crear medidas como
   `Desv Est Edad = STDEV.P(fact_homicidios[edad_num])` y mostrarlas en tarjetas.

---

## PASO 9. Añadir filtros (segmentaciones)

En las páginas principales, agrega **Segmentaciones de datos** (visual *Slicer*) para que
el usuario filtre:

1. Inserta un visual **Segmentación**.
2. Campo: `dim_geografia[provincia]`.
3. Repite con `dim_tiempo[mes_nombre]` y `dim_delito[arma]`.
4. Colócalos arriba o en una franja lateral, iguales en todas las páginas.

---

## PASO 10. Storytelling y formato (para la nota del dashboard)

Aplica estos principios (la rúbrica evalúa percepción visual y psicología del color):

1. **Jerarquía:** las tarjetas de KPIs van arriba; los gráficos de apoyo, debajo.
2. **Color con significado:** reserva el **rojo** solo para riesgo alto/alertas; usa teal
   y azul para el análisis general. No abuses de colores.
3. **Títulos claros:** cada visual con un título que diga qué muestra (ej. "Incidencia por
   hora del día").
4. **Consistencia:** misma tipografía y misma posición de filtros en todas las páginas.
5. **Orden narrativo de las páginas:** Ejecutivo → Geográfico/Temporal → Caracterización →
   Predicción/Riesgo. Cuenta la historia del *dato* a la *decisión*.

---

## PASO 11. Revisión final, guardar y exportar

1. Revisa que **no haya errores** en los visuales (ninguno debe decir "no se puede mostrar").
2. Comprueba que los filtros afectan a todos los gráficos de la página.
3. **Guarda** el archivo: `SafeAnalytics_EC.pbix`.
4. (Opcional) Exporta a PDF para adjuntar como evidencia:
   **Archivo → Exportar → PDF**.
5. Entregable final: el archivo **`.pbix`** (y opcionalmente el PDF).

---

## Resumen rápido (checklist)

- [ ] Tema aplicado (`tema_safeanalytics.json`).
- [ ] 9 tablas importadas (vía `SafeAnalytics_EC_datos.xlsx` o CSV por separado).
- [ ] `id_geografia` como **Texto** en `fact_homicidios` y en `dim_geografia`.
- [ ] `fecha_infraccion` como **Fecha** (no "Fecha/hora"); la hora real está en `hora`.
- [ ] 4 relaciones (\*:1) formando la estrella.
- [ ] dim_tiempo marcada como tabla de fechas.
- [ ] Medidas DAX creadas (incluida la tasa por 100k).
- [ ] Página Ejecutiva con KPIs, tendencia y rankings.
- [ ] Página Geográfica y Temporal (mapa + calor día/hora).
- [ ] Página de Caracterización (arma, motivación, sexo, edad).
- [ ] Página de Predicción/Recomendaciones.
- [ ] Página de Riesgo con tabla semaforizada.
- [ ] (Opcional) Página de Metodología con correlación.
- [ ] Filtros por provincia, mes y arma.
- [ ] Archivo `.pbix` guardado y revisado.

> **Nota:** esta guía complementa a `powerbi/GUIA_POWER_BI.md` (referencia de medidas DAX
> y relaciones). Aquí tienes el "cómo hacerlo" clic por clic; allí, el "qué medidas usar".
