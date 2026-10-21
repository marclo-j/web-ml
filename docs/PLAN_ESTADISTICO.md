# 📈 PLAN ESTADÍSTICO Y CAPÍTULO DE RESULTADOS

La metodología declara tres niveles de análisis. Este archivo dice qué se calcula, con qué función y cómo se presenta.

## Diseño: preprueba, intervención y posprueba
Diseño cuasiexperimental con grupos intactos (no se sortean alumnos):

| Elemento | En este proyecto | Estado |
|---|---|---|
| Grupo experimental | 4.° B (34 alumnos incluidos). Sus tutores usan la web | Definido |
| Grupo control | 3.° A (35 alumnos). Seguimiento habitual, sin la web | Definido |
| Preprueba (PRE) | Indicadores del I bimestre 2026 de ambos grupos (`2026_pre_v5.csv`) | ✅ Recolectada |
| Intervención | Los tutores del grupo experimental consultan la web, identifican a los alumnos en riesgo medio o alto y actúan (entrevista, citación a los padres, derivación) | ⬜ Fecha de inicio y fin por definir con la IE y el asesor |
| Posprueba (POST) | Las mismas 3 fichas, a ambos grupos, con los datos acumulados durante el periodo de la intervención | ⬜ Fecha de corte por definir |
| Desenlace (D2) | Deserción efectiva al cierre del año, para validar el modelo | ⬜ Al cierre del año lectivo |

Reglas para que la comparación sea defendible:
- La POST cubre un periodo comparable a la PRE (idealmente un bimestre completo) y usa las mismas fórmulas y fichas.
- Solo los tutores del grupo experimental tienen cuenta en la web durante la intervención. El investigador sí registra y clasifica a ambos grupos: eso es medición, no intervención.
- Se registra en `LOG_AVANCES.md` la fecha de inicio y fin de la intervención y el corte de la POST.
- La lectura esperada: PRE sin diferencias (ya comprobado: p = 0.540, 0.449, 0.616 y 0.864 en el nivel ordinal) y POST con diferencia a favor del experimental.

## Script (`stats/analisis.py`)
Exporta las tablas a `stats/output/` (gitignored, CSV con `;` y coma decimal). Con `--pre` calcula descriptivos, niveles, normalidad y contraste PRE; con `--post` agrega la posprueba; `--intragrupo` agrega Wilcoxon PRE vs POST (pendiente del asesor). Incluye la tabla de métricas del modelo. Los p que redondean a 0.000 se reportan como p < 0.001.
```bash
ml/.venv/Scripts/python stats/analisis.py --pre data/processed/2026_pre_v5.csv [--post data/processed/2026_post.csv] [--intragrupo]
```

## Nivel 1 — Descriptivo
Por **grupo** (control / experimental) × **momento** (pre / post) × **indicador**:
media, desviación estándar, mínimo, máximo y conteo por nivel de riesgo (bajo / medio / alto, con %).

## Nivel 2 — Desempeño del modelo
Accuracy, precision, recall, F1 y matriz de confusión (detalle en `MODELO.md`). Importancia de variables por dimensión → OE1, OE2, OE3.

## Nivel 3 — Inferencial

### Paso 1: Prueba de normalidad
**Hipótesis:**
- H0: los datos tienen distribución normal
- H1: los datos no tienen distribución normal

**Qué prueba corresponde:** n = 35 por grupo (< 50) → **Shapiro-Wilk**. Kolmogorov-Smirnov se reporta también porque lo pide la plantilla del docente, pero la decisión se toma con Shapiro-Wilk.

**Se aplica por separado a cada combinación** (la plantilla del docente muestra un solo grupo con n = 45 como ejemplo; aquí hay dos grupos de 35):

| Indicador | Filas de la tabla |
|---|---|
| Promedio de calificaciones | Pre-control, Pre-experimental, Post-control, Post-experimental |
| % de asistencia | Ídem |
| % asistencia a reuniones | Ídem |

**Formato de tabla (replica la plantilla del docente):**
| Grupo / Momento | K-S Estadístico | gl | Sig. | S-W Estadístico | gl | Sig. |
|---|---|---|---|---|---|---|
| Pre – Control | | 35 | | | 35 | |
| Pre – Experimental | | 35 | | | 35 | |
| Post – Control | | 35 | | | 35 | |
| Post – Experimental | | 35 | | | 35 | |

**Regla de decisión (α = 0.05):**
- Sig. ≥ 0.05 → no se rechaza H0 → distribución normal → **t de Student**
- Sig. < 0.05 → se rechaza H0, se acepta H1 → distribución no normal → **U de Mann-Whitney**

> Si en una comparación **cualquiera de los dos grupos** no es normal, se usa Mann-Whitney para esa comparación.

**Funciones:**
| Prueba | Python |
|---|---|
| Shapiro-Wilk | `scipy.stats.shapiro(x)` |
| K-S con corrección de Lilliefors (equivalente al de SPSS) | `statsmodels.stats.diagnostic.lilliefors(x, dist="norm")` |

### Paso 2: Contraste de hipótesis
Comparación **control vs experimental** (grupos independientes), en pre y en post:
| Caso | Prueba | Python |
|---|---|---|
| Ambos normales | t de Student (verificar varianzas con Levene) | `scipy.stats.levene`, `scipy.stats.ttest_ind(equal_var=...)` |
| Alguno no normal | U de Mann-Whitney | `scipy.stats.mannwhitneyu(a, b, alternative="two-sided")` |
| Nivel de riesgo (ordinal bajo/medio/alto) | U de Mann-Whitney directo (no aplica normalidad a una variable ordinal) | Ídem |

**Lectura esperada:** en la **preprueba** no debería haber diferencia significativa (grupos comparables); en la **posprueba** sí, a favor del grupo experimental.

### Mapa hipótesis → prueba
| Hipótesis | Variable contrastada | Evidencia adicional |
|---|---|---|
| HG | Nivel de riesgo (control vs experimental, post) | Métricas del modelo |
| H1 | Promedio de calificaciones | Importancia de `promedio` |
| H2 | % de asistencia | Importancia de `pct_asistencia` |
| H3 | % asistencia a reuniones | Importancia de `pct_reuniones` |

✅ **Decisión D15 (2026-10-21, sin asesor disponible):** (a) variable contrastada = la VD de la tesis, el nivel de riesgo (HG), y cada indicador de sus dimensiones (H1-H3), tal como están en la tabla; no se agrega la probabilidad continua. (b) Wilcoxon PRE vs POST dentro de cada grupo se reporta como análisis **complementario** (no sustituye el contraste declarado en la metodología) para describir el cambio de cada grupo; se redacta como tal.

**Tamaño del efecto (opcional, recomendable):** r = Z / √N para Mann-Whitney; d de Cohen para t de Student.

---

## Estructura del capítulo III. Resultados
Reglas de la guía UCV: orden **objetivo general → específicos**, cada resultado en tabla o figura + descripción narrativa breve **en tiempo pasado**, sin subtítulos, viñetas ni negritas, sin repetir los datos de la tabla. Notas (abreviaturas) debajo de la tabla. Mínimo 4 páginas.

| Orden | Objetivo | Tablas / figuras |
|---|---|---|
| 1 | General | Niveles de riesgo por grupo y momento · métricas del modelo · matriz de confusión · normalidad · contraste HG |
| 2 | OE1 | Descriptivos del promedio · normalidad · contraste H1 · importancia de la variable |
| 3 | OE2 | Ídem con % de asistencia |
| 4 | OE3 | Ídem con % de reuniones |

**Plantilla de redacción tras una tabla de contraste:**
> En la Tabla N se observó que, en la posprueba, el grupo experimental obtuvo [dato clave] frente a [dato] del grupo control. La prueba U de Mann-Whitney arrojó un valor p de [valor], inferior a 0.05, por lo que se rechazó la hipótesis nula y se aceptó que [enunciado de la hipótesis].

## Salida del script
`stats/analisis.py` debe exportar cada tabla a `stats/output/*.csv` (y opcionalmente `.xlsx`) con el orden de filas de este documento, para pasarlas directo a Word.
