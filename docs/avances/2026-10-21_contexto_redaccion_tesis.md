# Contexto completo para la redacción final de la tesis

> Documento de traspaso, al 21/10/2026. Resume todo lo ejecutado en el proyecto (datos, modelo, web y análisis estadístico), las decisiones tomadas, cómo explicarlas y lo que falta redactar. Entrega de la tesis completa: sábado 24/10/2026.
> Todos los datos de alumnos están anonimizados con códigos `EST-###`. Las cifras de este documento son reales salvo donde se indica lo contrario.

---

## 1. Datos generales

| Campo | Valor |
|---|---|
| Título | Web con Machine Learning para determinar el nivel de riesgo de deserción escolar en una institución educativa de Lima, 2026 |
| Autor | Calderón Salazar, Joaquin Marcelo |
| Asesor | Dr. Rodolfo Santiago Vergara Calderon (sin comunicación en la última semana) |
| Universidad | Universidad César Vallejo, Escuela de Ingeniería de Sistemas |
| Línea de investigación | Sistema de información de comunicaciones |
| Formato de citas | IEEE, numeradas `[n]` |
| Institución | IE secundaria del distrito de Comas, Lima |
| Guía de redacción | `guia_de_elaboracion_tesis.md` (UCV, PP-G-02.02, versión 07) |

## 2. Problema, variables, objetivos e hipótesis

**Problema.** La IE realizaba un seguimiento reactivo: detectaba el riesgo cuando ya era tarde. La deserción subió de 29 % (2024) a 35 % (2025). Las causas principales identificadas son problemas económicos, la necesidad de que el hijo aporte ingresos y el embarazo adolescente. No existía una herramienta predictiva.

**Variables.**
| Tipo | Variable |
|---|---|
| Independiente | Web con Machine Learning |
| Dependiente | Nivel de riesgo de deserción escolar (bajo, medio, alto) |

| Dimensión de la VD | Indicador | Fórmula | Sustento |
|---|---|---|---|
| Rendimiento académico | Promedio de calificaciones | Promedio = Σ notas / n | Albonny y Duru [1] |
| Asistencia escolar | Porcentaje de asistencia | (DA / DP) × 100 | Albonny y Duru [1] |
| Apoyo familiar | Asistencia a reuniones de padres | CA = (RA / RT) × 100 | Ttito y Choque [39] |

DA = días asistidos, DP = días programados, RA = reuniones asistidas, RT = reuniones programadas. Escala de notas: vigesimal 0 a 20.

**Objetivo general.** Determinar en qué medida la implementación de una web con Machine Learning permite establecer el nivel de riesgo de deserción escolar en una IE de Lima, 2026.

| Código | Objetivo específico | Indicador |
|---|---|---|
| OE1 | Analizar cómo la web, mediante el rendimiento académico, permite determinar el nivel de riesgo | Promedio |
| OE2 | Examinar en qué medida la web, mediante la asistencia escolar, contribuye a determinar el nivel de riesgo | % asistencia |
| OE3 | Evaluar cómo la web, mediante la asistencia a reuniones de padres, permite determinar el nivel de riesgo | % reuniones |

**Hipótesis.**
| Código | Enunciado resumido |
|---|---|
| HG | La web con ML permite determinar con alto grado de precisión el nivel de riesgo |
| H1 | A través del rendimiento académico, lo determina con eficacia |
| H2 | Mediante la asistencia escolar, contribuye significativamente |
| H3 | Mediante la asistencia a reuniones de padres, lo determina con precisión |

## 3. Metodología tal como se ejecutó

| Aspecto | Definición |
|---|---|
| Enfoque | Cuantitativo |
| Tipo | Aplicada (en el documento figura el Manual de Frascati; la guía UCV 2026 pide el Manual de Oslo de la OCDE 2018; ver sección 10) |
| Nivel o alcance | Explicativo |
| Diseño | Cuasiexperimental con preprueba y posprueba, grupo control y grupo experimental (grupos intactos) |
| Método | Hipotético-deductivo |
| Población y muestra | 70 estudiantes: 35 de 4.° B (experimental) y 35 de 3.° A (control) |
| Muestreo | No probabilístico, intencional por conveniencia |
| Unidad de análisis | Cada estudiante de 3.° o 4.° de secundaria |
| Técnica | Análisis documental de registros institucionales |
| Instrumento | 3 fichas de registro de datos, una por dimensión |
| Métricas del modelo | Accuracy, precision, recall, F1 y matriz de confusión (AUC como complemento) |
| Estadística inferencial | Shapiro-Wilk, luego t de Student o U de Mann-Whitney, α = 0.05 |
| Herramientas | Python 3.11, pandas, scikit-learn, scipy, statsmodels; web en Next.js + FastAPI + PostgreSQL (Neon) |
| Ética | Anonimización por códigos, autorización de la IE, Ley N.° 29733 y D.S. N.° 003-2013-JUS |

**Criterios.** Inclusión: matriculado en 3.° o 4.°, asistencia registrada, historial de calificaciones. Exclusión: traslado definitivo antes del cierre, registros inconsistentes o vacíos en alguna de las 3 dimensiones.

**Las 3 fichas (instrumentos).** Ficha 1 de rendimiento: nota de las 10 áreas curriculares (matemática, comunicación, inglés, arte y cultura, ciencias sociales, DPCC, educación física, educación religiosa, ciencia y tecnología, EPT), de las que calcula número de notas, suma y promedio. Ficha 2 de asistencia: días programados y asistidos, y el porcentaje. Ficha 3 de apoyo familiar: reuniones programadas y asistidas, y el porcentaje. Las 3 comparten código, grado, sección, grupo, momento (pre o post), año, deserto (solo en el histórico), excluido, motivo y observaciones. El sistema recalcula los indicadores a partir de los datos crudos con las mismas fórmulas.

### Cronología de los datos
| Momento | Periodo | Uso |
|---|---|---|
| Histórico 2024 | I bimestre, con desenlace conocido | Entrenar y evaluar el modelo |
| Preprueba (PRE) 2026 | I bimestre 2026 | Medición inicial de ambos grupos |
| Intervención | Entre el PRE y el POST | Los tutores del experimental usan la web; el control sigue con el seguimiento habitual |
| Posprueba (POST) 2026 | III bimestre, del 10/08/2026 al 09/10/2026 (45 días programados, 2 reuniones) | Medición final de ambos grupos |
| Desenlace real 2026 | Deserción efectiva hasta el 09/10/2026 | Validación externa del modelo |

El IV bimestre termina en diciembre, por eso el POST es el III bimestre. Los indicadores del histórico y del PRE se calculan solo con datos hasta el cierre del I bimestre para evitar la fuga de información: si se usara el año completo, un alumno que desertó a mitad de año tendría menos asistencia porque ya se había ido, y el modelo aprendería la consecuencia de la deserción y no sus señales tempranas.

### Muestra final
| Momento | Incluidos | Control | Experimental | Excluidos |
|---|---|---|---|---|
| Histórico 2024 | 70 (13 desertores, 18.6 %) | 35 (6 desertores) | 35 (7 desertores) | 0 |
| PRE 2026 | 69 | 35 | 34 | 1 (EST-020, traslado definitivo) |
| POST 2026 | 69 | 35 | 34 | 1 (EST-020, traslado definitivo, sin notas) |
| Desenlace 2026 | 69 (11 desertores) | 9 desertores | 2 desertores | EST-020 sin dato |

## 4. El modelo de Machine Learning

**Planteamiento.** Aprendizaje supervisado con `RandomForestClassifier` de scikit-learn. La tarea es binaria: el modelo aprende si el alumno desertó (1) o no (0) a partir de los 3 indicadores, y devuelve una probabilidad que luego se convierte en nivel bajo, medio o alto. Se eligió así porque el hecho que la IE registra es "desertó o no"; entrenar sobre ese dato observable evita inventar etiquetas de "riesgo medio" que nadie registró.

**Configuración.** 200 árboles, profundidad sin límite, mínimo 2 muestras por hoja, `class_weight="balanced"`, semilla 42. Se probó una búsqueda de hiperparámetros con validación cruzada anidada (100, 200 y 400 árboles; profundidad sin límite, 3, 5 y 8; hojas de 1, 2 y 4) y no mejoró la configuración inicial (AUC 0.993 en ambas), por lo que se mantuvo la más simple.

**Datos de entrenamiento.** 70 alumnos reales de la IE con desenlace conocido (13 desertores y 57 no desertores). Diferencias entre desertores y no desertores en el histórico (mediana y U de Mann-Whitney):

| Indicador | Desertó (n = 13) | No desertó (n = 57) | U | p | r |
|---|---|---|---|---|---|
| Promedio | 10.60 | 14.80 | 170.5 | 0.003 | 0.54 |
| % asistencia | 28.89 | 64.44 | 32.5 | < 0.001 | 0.91 |
| % reuniones | 0.00 | 50.00 | 110.5 | < 0.001 | 0.70 |

**Datos sintéticos y equilibrio de clases.** Como la muestra es pequeña y desbalanceada (57 frente a 13), el docente observó que entrenar con clases tan alejadas sesga al modelo hacia la clase mayoritaria y recomendó acercar las clases a 40 % y 60 %. Se generaron con SMOTE (interpolación entre alumnos reales de la misma clase, Chawla et al., 2002) 25 desertores sintéticos hasta que los desertores fueran el 40 % del entrenamiento: 13 reales + 25 sintéticos frente a 57 no desertores reales (95 filas). No se descartó ningún alumno real. Los sintéticos se usan solo en el entrenamiento; todas las métricas se calculan solo con alumnos reales. Antes se comparó SMOTE con CTGAN (red generativa adversarial tabular, Xu et al., 2019) y sin aumento: CTGAN no reprodujo bien a los desertores con solo 13 casos (prueba KS de 0.23 a 0.73 frente a ≤ 0.19 de SMOTE), por lo que se eligió SMOTE.

**Validación.** La métrica principal es la validación cruzada estratificada repetida 5 × 5 sobre los 70 alumnos reales. Un holdout de 14 alumnos (3 desertores) es muy inestable con tan pocos positivos, así que se reporta como complemento. El modelo final se reentrenó con todo el histórico; en Metodología se declara: "las métricas se obtuvieron por validación cruzada; el modelo final se reentrenó con la totalidad del histórico".

| Métrica (CV 5 × 5 sobre reales, modelo final `rf_v5`) | Media | DE |
|---|---|---|
| AUC | 0.994 | 0.014 |
| F1 | 0.928 | 0.112 |
| Recall | 1.000 | 0.000 |
| Precision | 0.884 | 0.177 |
| Accuracy | 0.969 | 0.050 |

Holdout 20 % (14 alumnos): accuracy 0.929, precision 0.75, recall 1.00, F1 0.857; matriz de confusión VN = 10, FP = 1, FN = 0, VP = 3.

Comparación de alternativas (CV 5 × 5, todas dentro del margen de error; se eligió el equilibrio al 40 % por seguir la recomendación del docente sin descartar datos reales):

| Configuración | AUC | F1 | Recall | Precision |
|---|---|---|---|---|
| Sin aumento | 0.994 | 0.927 | 1.000 | 0.883 |
| SMOTE ×2, proporción original 18.6 % | 0.993 | 0.911 | 0.967 | 0.893 |
| Equilibrado al 40 % (modelo final) | 0.994 | 0.928 | 1.000 | 0.884 |
| Equilibrado 40 % + refuerzo ×1 | 0.997 | 0.927 | 1.000 | 0.883 |
| Reducir la clase mayoritaria a 28 % y equilibrar | 0.989 | 0.888 | 0.980 | 0.831 |

**Importancia de las variables (sustento de OE1 a OE3).**
| Indicador | MDI (Gini) | Permutación (F1) |
|---|---|---|
| Promedio | 0.150 | 0.000 |
| % asistencia | 0.587 | 0.434 |
| % reuniones | 0.263 | 0.330 |

La asistencia es la dimensión que más pesa, seguida por las reuniones de padres. El promedio casi no aporta cuando ya se conocen las otras dos (por permutación su aporte es nulo), aunque por sí solo sí diferencia a desertores de no desertores (p = 0.003).

**Umbrales de nivel de riesgo.** Salen de las probabilidades fuera de muestra del propio histórico:
| Probabilidad | Nivel | Justificación |
|---|---|---|
| ≥ 0.50 | Alto | Es el corte con que el clasificador predice deserción; con él se identificaron los 13 desertores del histórico con 2 falsos positivos |
| 0.222 a < 0.50 | Medio | 0.222 es el percentil 90 de la probabilidad de los no desertores: solo 1 de cada 10 que no desertaron lo supera. Es una franja de seguimiento preventivo |
| < 0.222 | Bajo | El 90 % de los no desertores del histórico |

**Corridas de prueba que no son resultados.** Se usaron datos sintéticos y una etiqueta por reglas de umbral (opción B) solo para probar que el sistema funcionaba. Con la opción B el modelo dio accuracy 1.0 porque solo reprodujo la regla de etiquetado; eso confirmó que hacía falta el histórico real. Nada de esto se reporta como hallazgo.

## 5. La web (variable independiente)

Arquitectura de tres partes, como la define la tesis [26], más el modelo como componente del backend.
| Capa | Tecnología |
|---|---|
| Frontend | Next.js 16 con TypeScript y Tailwind: inicio de sesión, tabla de alumnos con nivel de riesgo y color, resumen por grupo, filtros, registro de un alumno, carga masiva por CSV con detalle de excluidos, vista de detalle con los 3 indicadores y sus fórmulas, página del modelo con umbrales, validación cruzada y matriz de confusión |
| Backend | FastAPI (Python): valida los datos crudos, calcula los 3 indicadores con las fórmulas de la tesis, pide la probabilidad al modelo y la convierte en nivel |
| Base de datos | PostgreSQL en Neon: tablas de usuarios, estudiantes, registros y predicciones; guarda los datos crudos para que cada valor sea trazable hasta su ficha |
| Modelo | Random Forest guardado en `.joblib`, versión `rf_v5` |

Flujo: el tutor registra o carga los datos crudos del alumno, el sistema calcula los indicadores, el modelo devuelve la probabilidad y la web muestra el nivel con su color. Seguridad: contraseñas con hash Argon2id, sesión con token JWT en cookie `httpOnly`, bloqueo tras 5 intentos fallidos, sin registro público y sin nombres ni DNI en la base (solo el código; la tabla código ↔ nombre queda en la IE). Con los 69 alumnos PRE cargados, la web muestra 55 en riesgo bajo, 11 en medio y 3 en alto.

## 6. Resultados obtenidos (para el Capítulo III)

Las tablas están en `stats/output/` como CSV con punto y coma y coma decimal, listas para pasar a Word.

### 6.1 Descriptivos por grupo y momento
| Indicador | Momento | Grupo | n | Media | DE | Mín | Máx | Mediana |
|---|---|---|---|---|---|---|---|---|
| Promedio | PRE | Control | 35 | 14.75 | 2.43 | 7.6 | 17.9 | 15.5 |
| Promedio | PRE | Experimental | 34 | 15.00 | 2.27 | 8.0 | 17.4 | 15.8 |
| Promedio | POST | Control | 35 | 12.03 | 1.37 | 8.7 | 14.6 | 12.0 |
| Promedio | POST | Experimental | 34 | 14.05 | 1.90 | 10.8 | 18.6 | 13.8 |
| % asistencia | PRE | Control | 35 | 63.30 | 28.09 | 6.67 | 100.0 | 71.11 |
| % asistencia | PRE | Experimental | 34 | 60.91 | 21.00 | 2.22 | 93.33 | 62.22 |
| % asistencia | POST | Control | 35 | 35.87 | 16.17 | 13.33 | 73.33 | 33.33 |
| % asistencia | POST | Experimental | 34 | 66.41 | 22.67 | 20.0 | 100.0 | 73.33 |
| % reuniones | PRE | Control | 35 | 57.14 | 34.60 | 0.0 | 100.0 | 50.0 |
| % reuniones | PRE | Experimental | 34 | 52.94 | 34.69 | 0.0 | 100.0 | 50.0 |
| % reuniones | POST | Control | 35 | 37.14 | 37.07 | 0.0 | 100.0 | 50.0 |
| % reuniones | POST | Experimental | 34 | 79.41 | 27.85 | 0.0 | 100.0 | 100.0 |

### 6.2 Nivel de riesgo por grupo y momento
| Momento | Grupo | n | Bajo | Medio | Alto |
|---|---|---|---|---|---|
| PRE | Control | 35 | 28 (80.0 %) | 7 (20.0 %) | 0 (0.0 %) |
| PRE | Experimental | 34 | 27 (79.4 %) | 4 (11.8 %) | 3 (8.8 %) |
| POST | Control | 35 | 8 (22.9 %) | 18 (51.4 %) | 9 (25.7 %) |
| POST | Experimental | 34 | 28 (82.4 %) | 5 (14.7 %) | 1 (2.9 %) |

### 6.3 Normalidad (decide Shapiro-Wilk porque n < 50; K-S con corrección de Lilliefors se reporta porque lo pide la plantilla del docente)
| Indicador | Grupo y momento | K-S | gl | Sig. | S-W | gl | Sig. | Normal |
|---|---|---|---|---|---|---|---|---|
| Promedio | PRE control | 0.264 | 35 | 0.001 | 0.799 | 35 | < 0.001 | No |
| Promedio | PRE experimental | 0.283 | 34 | 0.001 | 0.753 | 34 | < 0.001 | No |
| Promedio | POST control | 0.080 | 35 | 0.821 | 0.969 | 35 | 0.429 | Sí |
| Promedio | POST experimental | 0.137 | 34 | 0.114 | 0.973 | 34 | 0.548 | Sí |
| % asistencia | PRE control | 0.152 | 35 | 0.042 | 0.926 | 35 | 0.021 | No |
| % asistencia | PRE experimental | 0.114 | 34 | 0.322 | 0.960 | 34 | 0.236 | Sí |
| % asistencia | POST control | 0.124 | 35 | 0.200 | 0.944 | 35 | 0.075 | Sí |
| % asistencia | POST experimental | 0.149 | 34 | 0.055 | 0.945 | 34 | 0.086 | Sí |
| % reuniones | PRE control | 0.267 | 35 | 0.001 | 0.800 | 35 | < 0.001 | No |
| % reuniones | PRE experimental | 0.269 | 34 | 0.001 | 0.805 | 34 | < 0.001 | No |
| % reuniones | POST control | 0.270 | 35 | 0.001 | 0.786 | 35 | < 0.001 | No |
| % reuniones | POST experimental | 0.388 | 34 | 0.001 | 0.674 | 34 | < 0.001 | No |

Regla: si cualquiera de los dos grupos no es normal, se usa U de Mann-Whitney; si ambos lo son, t de Student (con Levene). El nivel de riesgo es ordinal, así que va directo a Mann-Whitney.

### 6.4 Contraste control frente a experimental (prueba principal declarada en la metodología)
| Momento | Variable | Prueba | Estadístico | p | Tamaño del efecto | Decisión |
|---|---|---|---|---|---|---|
| PRE | Promedio | U de Mann-Whitney | 543.5 | 0.540 | r = 0.07 | No se rechaza H0 |
| PRE | % asistencia | U de Mann-Whitney | 658.5 | 0.449 | r = 0.09 | No se rechaza H0 |
| PRE | % reuniones | U de Mann-Whitney | 633.5 | 0.616 | r = 0.06 | No se rechaza H0 |
| PRE | Nivel de riesgo | U de Mann-Whitney | 581.0 | 0.817 | r = 0.02 | No se rechaza H0 |
| POST | Promedio | t de Student | −5.077 | < 0.001 | d = 1.22 | Se rechaza H0 |
| POST | % asistencia | t de Student | −6.454 | < 0.001 | d = 1.55 | Se rechaza H0 |
| POST | % reuniones | U de Mann-Whitney | 246.5 | < 0.001 | r = 0.50 | Se rechaza H0 |
| POST | Nivel de riesgo | U de Mann-Whitney | 962.5 | < 0.001 | r = 0.53 | Se rechaza H0 |

Lectura: en el PRE los grupos eran comparables (ninguna diferencia significativa). En el POST el grupo experimental presentó mejor promedio, más asistencia, más asistencia a reuniones y menor nivel de riesgo que el control, con tamaños de efecto grandes. Con la corrección de Bonferroni para cuatro contrastes (p < 0.0125) todas las diferencias del POST siguen siendo significativas.

### 6.5 Análisis complementario: PRE frente a POST dentro de cada grupo (Wilcoxon)
| Grupo | Variable | Mediana PRE | Mediana POST | W | p | Decisión |
|---|---|---|---|---|---|---|
| Control | Promedio | 15.5 | 12.0 | 54.5 | < 0.001 | Se rechaza H0 |
| Control | % asistencia | 71.11 | 33.33 | 60.0 | < 0.001 | Se rechaza H0 |
| Control | % reuniones | 50.0 | 50.0 | 150.5 | 0.039 | Se rechaza H0 |
| Experimental | Promedio | 15.8 | 13.8 | 188.0 | 0.061 | No se rechaza H0 |
| Experimental | % asistencia | 62.22 | 73.33 | 240.0 | 0.325 | No se rechaza H0 |
| Experimental | % reuniones | 50.0 | 100.0 | 100.0 | 0.006 | Se rechaza H0 |

Lectura: el control empeoró en los tres indicadores entre el I y el III bimestre. El experimental se mantuvo en promedio y asistencia, y mejoró en asistencia a reuniones de padres.

### 6.6 Validación del modelo con la deserción real 2026 (validación externa)
El directivo de la IE entregó la deserción efectiva de los 69 alumnos hasta el 09/10/2026 (11 desertores). Se comparó con la predicción que hizo el modelo usando los indicadores del PRE (I bimestre).

| Criterio | VP | FN | FP | VN | Recall | Precision | F1 | Accuracy |
|---|---|---|---|---|---|---|---|---|
| Corte del nivel alto (0.50) | 1 | 10 | 2 | 56 | 0.09 | 0.33 | 0.14 | 0.83 |
| Corte del nivel medio (0.222) | 5 | 6 | 9 | 49 | 0.45 | 0.36 | 0.40 | 0.78 |

AUC 0.687 (control 0.583 con 9 desertores; experimental 0.922 con 2). Desertores por nivel PRE: bajo 6 de 55, medio 4 de 11, alto 1 de 3. Es una validación descriptiva: con 11 desertores no hay potencia para una prueba de hipótesis.

Hallazgo exploratorio (no es una hipótesis de la tesis): desertaron 9 de 35 alumnos del control (25.7 %) y 2 de 34 del experimental (5.9 %); prueba exacta de Fisher p = 0.045.

## 7. Decisiones metodológicas tomadas (y cómo explicarlas)

| Código | Decisión | Cómo explicarla en la tesis |
|---|---|---|
| D1 | Escala de calificación vigesimal 0 a 20, confirmada por la IE el 25/09/2026 | La ficha de rendimiento registra las notas en la escala oficial de la IE |
| D2 | El valor real contra el que se evalúa el modelo en 2026 es la deserción efectiva al cierre del periodo | Coherente con un modelo binario entrenado con "desertó o no" |
| D3 | Indicadores calculados con datos hasta el cierre del I bimestre, igual en histórico y PRE | Evita la fuga de información y permite detectar señales tempranas |
| D7 | Un alumno del histórico es desertor si está marcado así en las 3 fichas | Un único valor por alumno, igual en todas las fichas |
| D8 | Aumento de datos con SMOTE solo en el entrenamiento; CTGAN descartado | Muestra pequeña; las métricas se calculan solo con alumnos reales |
| D9 | Umbrales de nivel a partir de las probabilidades fuera de muestra del histórico | Ver tabla de umbrales; no son arbitrarios |
| D10 | Base de datos Neon (PostgreSQL) y autenticación propia (Argon2id + JWT) | Seguridad y privacidad de datos de menores |
| D11 | El modelo final se reentrena con todo el histórico; las métricas son las de la validación cruzada | Práctica habitual: la evaluación estima el rendimiento del procedimiento |
| D12 | Entrenamiento equilibrado a 40 % de desertores con SMOTE (recomendación del docente) | Corrige el sesgo hacia la clase mayoritaria sin descartar alumnos reales |
| D13 | POST = III bimestre (10/08 al 09/10/2026) | El IV bimestre termina en diciembre; un bimestre completo es comparable al PRE |
| D14 | Validación externa con la deserción real hasta el 09/10/2026 | Responde a qué son los "valores reales registrados en la institución" |
| D15 | Variable contrastada: nivel de riesgo para HG y cada indicador para H1 a H3; Wilcoxon solo como análisis complementario | Sigue la metodología declarada (comparación entre grupos) y suma la evolución de cada grupo sin reemplazarla |

**Cómo responder cada hipótesis.**
| Hipótesis | Evidencia principal | Evidencia complementaria |
|---|---|---|
| HG | Métricas del modelo (CV: AUC 0.994, F1 0.928, recall 1.000) y contraste del nivel de riesgo en el POST (p < 0.001, r = 0.53) | Validación externa con la deserción real (AUC 0.687), reportada con transparencia como limitación |
| H1 | Contraste del promedio en el POST (t, p < 0.001, d = 1.22) | Importancia del promedio (MDI 0.150; por permutación 0) y diferencia en el histórico (p = 0.003) |
| H2 | Contraste de la asistencia en el POST (t, p < 0.001, d = 1.55) | Es la variable de mayor peso en el modelo (MDI 0.587, permutación 0.434) |
| H3 | Contraste de reuniones en el POST (U, p < 0.001, r = 0.50) | Segunda variable en peso (MDI 0.263, permutación 0.330) y mejora intragrupo del experimental (p = 0.006) |

## 8. Limitaciones que deben declararse

1. Diseño cuasiexperimental con grupos intactos de distinto grado (3.° control y 4.° experimental); el efecto se redacta como asociado al uso de la web, no como causal.
2. Un solo bimestre de intervención y de posprueba (III bimestre).
3. No se midió cuántas veces ni cómo usaron la web los tutores del experimental, ni qué acciones tomaron.
4. El modelo se entrenó con un solo año lectivo, 70 alumnos y 13 desertores, completado con 25 desertores sintéticos (SMOTE); la tasa del histórico (18.6 %) es menor que la institucional (29 % y 35 %).
5. Las clases del histórico estaban casi separadas por asistencia y reuniones, por eso las métricas de validación cruzada están cerca del máximo.
6. En la validación externa el modelo detectó pocos desertores reales (AUC 0.687). Explicaciones posibles: el PRE usa solo el I bimestre y la deserción real hasta el 09/10 incluye abandonos del II y III bimestre; la intervención en el experimental pudo cambiar el desenlace que el modelo predecía; hay causas de deserción (económicas, embarazo adolescente) que los 3 indicadores no capturan.
7. El umbral de 50 % en reuniones de la regla de etiquetado de prueba es un supuesto del autor (solo afecta a las corridas de prueba, no a los resultados).
8. La mejora del equilibrio al 40 % frente a otras configuraciones no es estadísticamente demostrable con 13 desertores.

## 9. Referencias pendientes de agregar

- [42] R. Balfanz y J. Byrnes, "Chronic Absenteeism: A Significant, Overlooked Challenge to Student Success", Everyone Graduates Center / Attendance Works (sustento del umbral de asistencia de 85 % de la regla de prueba).
- N. V. Chawla, K. W. Bowyer, L. O. Hall y W. P. Kegelmeyer, "SMOTE: Synthetic Minority Over-sampling Technique", Journal of Artificial Intelligence Research, vol. 16, pp. 321-357, 2002.
- L. Xu, M. Skoularidou, A. Cuesta-Infante y K. Veeramachaneni, "Modeling Tabular Data using Conditional GAN", NeurIPS, 2019 (CTGAN, alternativa descartada).
- Referencias de las pruebas estadísticas si se citan (Shapiro-Wilk, Mann-Whitney, Wilcoxon, Lilliefors) y de scikit-learn [28].
- Verificar que el número [9] esté libre antes de usarlo y que la lista de Referencias no esté vacía.

## 10. Observaciones pendientes en el documento

| # | Observación | Dónde | Qué corregir |
|---|---|---|---|
| 1 | La cita [39] se usa para dos fuentes distintas: la definición de "web con ML" y Ttito y Choque | Metodología | Asignar un número distinto a cada fuente y renumerar |
| 2 | No se define qué son los "valores reales registrados en la institución" contra los que se calculan las métricas | Metodología, análisis de datos | Son la deserción efectiva del histórico 2024 (validación cruzada) y la deserción efectiva 2026 hasta el 09/10, entregada por la IE (validación externa) |
| 3 | Falta precisar que la escala de la IE es vigesimal (0 a 20) | Metodología, ficha de rendimiento | Indicar la escala vigesimal confirmada por la IE |
| 4 | Falta indicar el origen de los datos etiquetados para entrenar el modelo | Metodología | Registros de 70 alumnos de la IE con desenlace conocido (13 desertores), completados con 25 desertores sintéticos SMOTE solo en el entrenamiento |
| 5 | Falta definir el periodo del PRE y del POST | Metodología, instrumentos | PRE: I bimestre 2026; POST: III bimestre, del 10/08 al 09/10/2026 |

Observaciones adicionales detectadas al cruzar con la guía UCV 2026:
| # | Observación | Qué hacer |
|---|---|---|
| 6 | La guía pide el tipo de investigación según el Manual de Oslo de la OCDE (2018); el documento cita el Manual de Frascati | Cambiar o justificar la fuente |
| 7 | Los instrumentos diseñados para el estudio deben validarse con mínimo 3 jueces expertos, con fichas firmadas en anexos | Confirmar si las 3 fichas tienen validación de expertos; si no, declararlo |
| 8 | Mínimo 30 referencias, 70 % artículos indexados en Scopus, WoS o SciELO (SJR) y 30 % en idioma extranjero | Revisar la lista final |
| 9 | Se debe declarar el uso de herramientas de inteligencia artificial y su versión | Declararlo en Metodología o Aspectos éticos |
| 10 | Anexos en el orden del numeral 4.5.6: operacionalización, instrumentos, validación, consentimientos, autorización de la IE, análisis complementario, evidencias, matriz de consistencia, Turnitin | Armar los anexos en ese orden |
| 11 | Se registró en el desarrollo que el histórico se tomó de otros años lectivos según lo pactado con el directivo (rotulado como 2024) | El autor decide cómo describir el origen exacto en Metodología |

## 11. Qué falta redactar o completar

1. Actualizar la Metodología con lo ejecutado: periodos, tamaños finales, exclusión de EST-020, origen de los datos de entrenamiento, SMOTE y equilibrio al 40 %, validación cruzada 5 × 5, umbrales, análisis estadístico con el complementario de Wilcoxon y validación externa; corregir las observaciones 1 a 6 y 9.
2. Capítulo III, Resultados: orden general, OE1, OE2, OE3. Para el general: niveles de riesgo por grupo y momento, métricas del modelo, matriz de confusión, normalidad y contraste del nivel de riesgo; para cada específico: descriptivos del indicador, normalidad, contraste e importancia de la variable. Agregar el análisis complementario y la validación externa. Mínimo 4 páginas.
3. Capítulo IV, Discusión: contrastar con los antecedentes de la Introducción, explicar convergencias y divergencias, incluir las limitaciones. Mínimo 4 páginas.
4. Capítulo V, Conclusiones: una por objetivo, general primero. Mínimo 1 página.
5. Capítulo VI, Recomendaciones: con destinatario, acción, finalidad, sustento en los resultados y mecanismo. Mínimo 1 página.
6. Resumen y Abstract.
7. Referencias completas en IEEE y anexos.
8. Índices de contenidos, tablas y figuras.

Punto para confirmar con el autor antes de redactar: las fechas exactas de inicio y fin de la intervención y cómo usaron la web los tutores del grupo experimental (la web aún no está desplegada en un servidor público).

## 12. Reglas que no se deben romper al redactar

- Los datos sintéticos y las corridas de prueba (opción B, `rf_v0`) nunca se reportan como resultados.
- No se publican nombres ni DNI; solo códigos `EST-###`.
- Las fórmulas de los indicadores son las de la tesis; no se inventan indicadores nuevos.
- No se presentan los resultados como causales ni se ocultan la validación externa y las limitaciones.
- Capítulos en prosa, sin subtítulos, viñetas, guiones ni negrita (ver la guía), citas IEEE.
