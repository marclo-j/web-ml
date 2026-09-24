# 📈 PLAN ESTADÍSTICO Y CAPÍTULO DE RESULTADOS

La metodología declara tres niveles de análisis. Este archivo dice qué se calcula, con qué función y cómo se presenta.

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

❓ **Validar con el asesor:** (a) si la variable contrastada es la correcta; (b) si se añade comparación pre vs post **dentro** de cada grupo (Wilcoxon o t pareada: `scipy.stats.wilcoxon`, `scipy.stats.ttest_rel`), que la metodología actual no menciona.

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
