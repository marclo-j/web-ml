# Prompt para el chat-proyecto de la tesis — Avance 2026-10-03

> Copia todo lo que está debajo de la línea y pégalo en el chat del proyecto en claude.ai.
> Contiene solo cifras agregadas: ningún dato individual de alumnos (Ley N.° 29733).

---

Hola. Te pongo al día del estado de mi tesis porque hoy presento un avance a mi docente. Te pido dos cosas, en este orden:

1. Que entiendas bien en qué punto estoy, qué voy a presentar, cómo lo hice y por qué, y qué NO debo presentar y por qué. No soy bueno en estadística ni en machine learning, así que cuando me expliques algo hazlo con palabras simples, con ejemplos y sin dar nada por sabido.
2. Que con todo esto me generes un **prompt para Claude Design** que cree la presentación (diapositivas) de mi avance.

## 1. Contexto de la tesis

- **Título:** Web con Machine Learning para determinar el nivel de riesgo de deserción escolar en una institución educativa de Lima, 2026.
- **Autor:** Joaquin Marcelo Calderón Salazar. **Asesor:** Dr. Rodolfo Santiago Vergara Calderon. Ingeniería de Sistemas, UCV.
- **Problema:** una IE de secundaria de Comas detectaba el riesgo de deserción de forma reactiva, cuando ya era tarde. La deserción subió de 29 % (2024) a 35 % (2025).
- **Variable independiente:** web con Machine Learning. **Variable dependiente:** nivel de riesgo de deserción (bajo / medio / alto).
- **Tres dimensiones e indicadores** (uno por ficha de registro):
  - Rendimiento académico → promedio de calificaciones (escala vigesimal 0–20) → OE1 / H1
  - Asistencia escolar → % de asistencia = días asistidos / días programados × 100 → OE2 / H2
  - Apoyo familiar → % de asistencia de los padres a reuniones = reuniones asistidas / reuniones totales × 100 → OE3 / H3
- **Diseño:** cuasiexperimental con preprueba y posprueba. 70 alumnos: 35 de 4.° (grupo experimental, usará la web) y 35 de 3.° (grupo control).
- **Modelo:** Random Forest (scikit-learn). Aprende de alumnos de años anteriores cuyo desenlace ya se conoce (desertó sí/no), da una probabilidad de deserción y esa probabilidad se convierte en nivel bajo / medio / alto.
- **Estadística:** Shapiro-Wilk (normalidad, porque n < 50 por grupo), luego t de Student o U de Mann-Whitney, α = 0.05. El docente usa SPSS en clase.

## 2. En qué fase estoy

| Fase | Estado |
|---|---|
| 0. Setup y documentación | Completa |
| 1. Fichas y recolección de datos PRE 2026 | Completa |
| 2. Dataset de entrenamiento (histórico 2024–2025) | Completa (hoy) |
| 3. Entrenamiento y evaluación del modelo | Modelo `rf_v1` entrenado con datos reales; faltan detalles (umbrales finales) |
| 4. Backend (API) | Pendiente |
| 5. Frontend (web) | Pendiente |
| 6. Despliegue e intervención con el grupo experimental | Pendiente |
| 7. Recolección POST | Pendiente |
| 8. Análisis estadístico final | Pendiente |
| 9. Redacción de Resultados y Discusión | Pendiente |

## 3. Lo que SÍ voy a presentar, cómo lo hice y por qué

### 3.1 Instrumentos: las 3 fichas de registro
- **Qué:** tres plantillas de Excel, una por dimensión, que aplican exactamente las fórmulas de mi metodología. Los alumnos se identifican con códigos anónimos (EST-001…), nunca con nombres.
- **Por qué:** es la técnica de análisis documental que declaré en la metodología, y la anonimización cumple la Ley N.° 29733 (los datos son de menores de edad).

### 3.2 Datos PRE 2026 (preprueba)
- **Qué:** recolecté las 3 fichas de los 70 alumnos con datos hasta el cierre del I bimestre. Se aplicaron los criterios de inclusión y exclusión: **69 incluidos, 1 excluido** (traslado definitivo). Quedaron 35 en control y 34 en experimental.
- **Por qué hasta el I bimestre:** para que el modelo use señales tempranas. Si usara el año completo, un alumno que ya se fue tendría menos asistencia porque ya no estaba, y el modelo aprendería la consecuencia de la deserción, no la alerta temprana (a esto se le llama "fuga de información").

### 3.3 Histórico de entrenamiento 2024–2025 (datos reales de la IE)
- **Qué:** la IE entregó las fichas de 2024 y 2025 con el desenlace real de cada alumno (desertó o no). En total: **140 alumnos, 37 desertores (26,4 %)**: 2024 con 19 de 70 (27 %) y 2025 con 18 de 70 (26 %).
- **Cómo lo resolví:** al procesarlas encontré que el dato "desertó" no coincidía entre las tres fichas en 37 alumnos (una ficha decía que sí, otra que no). Confirmé el criterio con la IE (un alumno desertó si está marcado como tal) y corregí las fichas para que las tres coincidan. Antes de la corrección, la regla estricta excluía a todos los desertores y el modelo no se podía entrenar.
- **Qué muestran los datos:** los alumnos que desertaron tenían peores indicadores al cierre del I bimestre:

| Indicador | Desertaron (n=37) | No desertaron (n=103) | U de Mann-Whitney, p |
|---|---|---|---|
| Promedio | 12,4 (DE 2,1) | 14,1 (DE 1,1) | p < 0,001 → diferencia significativa |
| % asistencia | 73,2 % (DE 13,2) | 77,5 % (DE 13,1) | p = 0,069 → no significativa |
| % reuniones de padres | 36,5 % (DE 38,5) | 54,9 % (DE 42,9) | p = 0,024 → diferencia significativa |

  Se usó Mann-Whitney porque Shapiro-Wilk indicó que los datos no son normales (p < 0,05 en al menos un grupo de cada indicador).

### 3.4 El modelo `rf_v1` y sus métricas
- **Cómo lo entrené:** Random Forest con 200 árboles, `min_samples_leaf=2` y `class_weight="balanced"` (para compensar que hay menos desertores que no desertores). Lo evalué con **validación cruzada estratificada 5×5**: los 140 alumnos se dividen en 5 partes, se entrena con 4 y se prueba con la quinta, rotando, y todo se repite 5 veces con mezclas distintas (25 pruebas). Se reporta la media ± desviación estándar.
- **Por qué validación cruzada y no una sola división 80/20:** con 140 alumnos, una sola división deja solo 7 desertores para probar y el resultado cambia muchísimo según qué alumnos caigan ahí. La validación cruzada repetida usa a todos los alumnos para probar y da una cifra estable.
- **Resultados:**

| Métrica | Valor | Qué significa en simple |
|---|---|---|
| AUC | 0,79 ± 0,08 | Si tomo un desertor y un no desertor al azar, el modelo le da más riesgo al desertor el 79 % de las veces (50 % sería adivinar) |
| Accuracy | 0,73 ± 0,05 | Acierta 73 de cada 100 alumnos |
| Recall | 0,60 ± 0,20 | De cada 10 desertores reales, detecta unos 6 |
| Precision | 0,49 ± 0,09 | De cada 10 alumnos que marca en riesgo, unos 5 desertaron de verdad |
| F1 | 0,53 ± 0,11 | Equilibrio entre recall y precision |

- **Matriz de confusión** (validación cruzada de 5 partes, los 140 alumnos): de 103 no desertores, 79 bien clasificados y 24 marcados en riesgo sin desertar; de 37 desertores, 21 detectados y 16 no detectados.
- **Ajuste de hiperparámetros:** probé una grilla de 36 combinaciones (número de árboles, profundidad, tamaño de hoja) con validación cruzada anidada. No mejoró: F1 0,52 frente a 0,51, dentro del margen de error, y cada partición elegía una combinación distinta. Por eso mantuve la configuración inicial. Esto es un hallazgo, no un fallo: con 140 alumnos y 3 variables, el límite lo pone la cantidad de datos, no la configuración.

### 3.5 Importancia de variables (sustenta OE1, OE2, OE3)
Calculada por permutación dentro de la validación cruzada: cuánto empeora el AUC si se "desordena" una variable. Cuanto más empeora, más importa.

| Variable | Caída del AUC | Peso relativo (MDI) |
|---|---|---|
| Promedio (OE1) | 0,19 ± 0,08 | 0,55 |
| % asistencia (OE2) | 0,08 ± 0,06 | 0,33 |
| % reuniones de padres (OE3) | 0,05 ± 0,05 | 0,12 |

Lectura: el rendimiento académico es la dimensión que más aporta a la predicción; asistencia y apoyo familiar aportan menos y con más variabilidad.

### 3.6 Prueba de equivalencia de grupos en la preprueba (lo que se puede mostrar en SPSS)
En un diseño cuasiexperimental, antes de aplicar la web hay que demostrar que los dos grupos empiezan en condiciones parecidas. Si no, al final no se sabría si la diferencia la causó la web o ya existía.

| Indicador | Control (n=35) | Experimental (n=34) | Shapiro-Wilk (p) | Prueba | p | Conclusión |
|---|---|---|---|---|---|---|
| Promedio | 13,35 (DE 1,71) | 13,30 (DE 1,52) | 0,509 / 0,166 → normal | t de Student (Levene p = 0,523) | 0,901 | Sin diferencia |
| % asistencia | 88,25 (DE 9,87) | 89,09 (DE 12,93) | 0,004 / <0,001 → no normal | U de Mann-Whitney | 0,355 | Sin diferencia |
| % reuniones | 64,29 (DE 33,37) | 67,65 (DE 29,85) | <0,001 / <0,001 → no normal | U de Mann-Whitney | 0,733 | Sin diferencia |

Kolmogorov-Smirnov (Lilliefors) también se calculó porque lo pide la plantilla del docente, pero la decisión se toma con Shapiro-Wilk porque n < 50. Tabla de normalidad completa, en el formato de salida de SPSS:

| Indicador | Grupo (preprueba) | K-S Estadístico | gl | Sig. | S-W Estadístico | gl | Sig. |
|---|---|---|---|---|---|---|---|
| Promedio | Control | 0,103 | 35 | 0,455 | 0,972 | 35 | 0,509 |
| Promedio | Experimental | 0,108 | 34 | 0,407 | 0,954 | 34 | 0,166 |
| % asistencia | Control | 0,128 | 35 | 0,168 | 0,899 | 35 | 0,004 |
| % asistencia | Experimental | 0,221 | 34 | 0,001 | 0,773 | 34 | <0,001 |
| % reuniones | Control | 0,266 | 35 | 0,001 | 0,779 | 35 | <0,001 |
| % reuniones | Experimental | 0,311 | 34 | 0,001 | 0,746 | 34 | <0,001 |

(SPSS limita la Sig. de K-S a 0,200 cuando es mayor; si en SPSS aparece "0,200*" en lugar de 0,455 o 0,407, es lo mismo: normal.)

**Conclusión:** en la preprueba no hay diferencias significativas entre los grupos (todas las p > 0,05). Los grupos son comparables, que es justo lo que se espera antes de la intervención.

**Para SPSS:** tengo dos archivos locales (no se suben a internet porque son datos de menores): `spss_pre2026.csv` y `spss_historico.csv`, separados por punto y coma y con coma decimal. Pasos en SPSS:
1. Archivo → Importar datos → CSV.
2. Normalidad: Analizar → Estadísticos descriptivos → Explorar → variables dependientes `promedio`, `pct_asistencia`, `pct_reuniones`; lista de factores `grupo` → Gráficos → marcar "Gráficos de normalidad con pruebas". Sale la tabla de Kolmogorov-Smirnov y Shapiro-Wilk.
3. Si es normal: Analizar → Comparar medias → Prueba T para muestras independientes (variable de agrupación `grupo`). SPSS muestra también la prueba de Levene.
4. Si no es normal: Analizar → Pruebas no paramétricas → Cuadros de diálogo antiguos → 2 muestras independientes → U de Mann-Whitney.
Las cifras de SPSS deben coincidir con las de la tabla de arriba (se calcularon en Python con las mismas pruebas).

### 3.7 Vista previa del resultado que dará la web (sin web todavía)
Apliqué `rf_v1` a los 69 alumnos de 2026 con los umbrales provisionales (probabilidad < 0,33 = bajo; 0,33–0,66 = medio; ≥ 0,66 = alto):

| Grupo | Bajo | Medio | Alto |
|---|---|---|---|
| Control (35) | 21 (60,0 %) | 11 (31,4 %) | 3 (8,6 %) |
| Experimental (34) | 21 (61,8 %) | 8 (23,5 %) | 5 (14,7 %) |
| Total (69) | 42 | 19 | 8 |

Es lo que verá el tutor en la web: una lista de alumnos con su nivel de riesgo. Se presenta como **demostración del funcionamiento**, no como resultado final, porque los umbrales aún son provisionales.

## 4. Lo que NO debo presentar y por qué

| No presentar | Por qué |
|---|---|
| El F1 = 0,38 y la accuracy = 0,54 de la primera prueba (holdout 80/20) | Salió de solo 28 alumnos de prueba con 7 desertores. Es una cifra inestable que cambia mucho según qué alumnos caen en la prueba. La cifra correcta es la de validación cruzada (F1 0,53, AUC 0,79) |
| La importancia de variables de la primera prueba (valores negativos) | Se calculó con esos mismos 28 alumnos y por eso salió ruido. La correcta es la de la sección 3.5 |
| Los modelos `rf_v0` (datos sintéticos) y `rf_v0b` (accuracy = 1,00) | `rf_v0` usa datos inventados para probar el programa; nunca puede citarse como hallazgo. `rf_v0b` se entrenó con etiquetas puestas por reglas de umbral y solo aprendió a repetir esas reglas; su 100 % es engañoso |
| Que el modelo "predice con alto grado de precisión" (como dice la HG) | Todavía no: el F1 es moderado (0,53). Se puede decir que distingue el riesgo mejor que el azar (AUC 0,79) y que la hipótesis se contrastará con la posprueba |
| El nivel de riesgo de 2026 como resultado final | Los umbrales bajo/medio/alto son provisionales y aún no hay posprueba |
| Cualquier conclusión sobre si la web reduce el riesgo | La web aún no existe ni se ha usado con el grupo experimental. Eso se mide en la posprueba (fases 6–8) |
| Datos individuales de alumnos (aunque sea con código) | Son datos de menores; en la presentación solo van cifras agregadas |

## 5. Lo que me falta hacer y por qué

1. **Fijar los umbrales finales bajo / medio / alto** viendo la distribución real de probabilidades, y justificarlos en la tesis.
2. **Backend (FastAPI):** recibe los datos del alumno, calcula los 3 indicadores con las fórmulas de la tesis y llama al modelo.
3. **Frontend (web):** login de tutor, tabla de alumnos con color por nivel de riesgo, registro y carga masiva por CSV, detalle por alumno.
4. **Despliegue e intervención:** publicar la web y que los tutores del grupo experimental la usen durante un periodo.
5. **Recolección POST:** las mismas 3 fichas, para ambos grupos.
6. **Análisis estadístico final:** normalidad y contraste control vs experimental en la posprueba (si sale significativo a favor del experimental, se aceptan las hipótesis).
7. **Pendiente con el asesor:** confirmar qué variable se contrasta en la posprueba (nivel de riesgo, cada indicador o ambos) y si se añade la comparación pre vs post dentro de cada grupo (Wilcoxon o t pareada).
8. **Redacción** de Resultados y Discusión.

## 6. Limitaciones que conviene decir antes de que me las pregunten

- La muestra de entrenamiento es pequeña (140 alumnos) y solo hay 3 variables. Las causas principales de deserción en la IE (problemas económicos, trabajo, embarazo adolescente) no están en las fichas. Eso limita lo que el modelo puede aprender.
- El dato "desertó" venía con discrepancias entre fichas. Se corrigieron con confirmación de la IE.
- El umbral de 50 % en reuniones de padres usado en una etapa previa es un criterio mío, no de la literatura.

## 7. Preguntas probables del docente y cómo responderlas

- **¿Por qué el F1 es bajo?** → Con 140 alumnos y 3 variables es lo esperable; el AUC de 0,79 muestra que el modelo ordena bien el riesgo, y el ajuste de hiperparámetros confirmó que el límite es la cantidad de datos.
- **¿Por qué validación cruzada y no 80/20?** → Con pocos desertores, una sola partición es inestable; la validación cruzada repetida usa a todos los alumnos para evaluar.
- **¿Los grupos son comparables?** → Sí, en la preprueba no hay diferencias significativas en ningún indicador (p > 0,05).
- **¿Qué variable pesa más?** → El promedio de calificaciones (OE1).
- **¿Por qué Shapiro-Wilk?** → Porque cada grupo tiene menos de 50 alumnos.

## 8. Lo que te pido ahora

1. Revisa que entiendas todo y explícame con palabras simples cualquier punto que creas que no domino (sobre todo AUC, validación cruzada, Shapiro-Wilk vs Kolmogorov-Smirnov, t de Student vs Mann-Whitney, y matriz de confusión).
2. Genérame un **prompt para Claude Design** que cree mi presentación de avance con estas condiciones:
   - Entre 10 y 12 diapositivas, en español, para unos 10 minutos.
   - Orden sugerido: portada → problema → objetivo e hipótesis → arquitectura de la web (frontend, backend, base de datos, modelo) → instrumentos (3 fichas y fórmulas) → datos recolectados (PRE 2026 e histórico 2024–2025) → modelo y métricas → importancia de variables → **análisis estadístico en SPSS (2 diapositivas)** → vista previa de niveles de riesgo → limitaciones → próximos pasos.
   - **Las 2 diapositivas de SPSS** (es la herramienta que usa el docente, así que es lo que más reconocerá):
     - Diapositiva A, "Prueba de normalidad": tabla con el formato de salida de SPSS (Kolmogorov-Smirnov y Shapiro-Wilk, con estadístico, gl y Sig., por grupo e indicador) y la regla de decisión: Sig. ≥ 0,05 → normal → t de Student; Sig. < 0,05 → no normal → U de Mann-Whitney. Remarcar que se decide con Shapiro-Wilk porque n < 50.
     - Diapositiva B, "Equivalencia de grupos en la preprueba": tabla con la prueba aplicada a cada indicador y su p, y la conclusión de que los grupos son comparables (todas las p > 0,05).
     - Dejar un espacio marcado como "captura de SPSS" en cada una, para que yo pegue la tabla real que me dé SPSS al replicar el análisis.
     - En las notas del orador, explicar en simple por qué esta prueba importa en un diseño cuasiexperimental: si los grupos empiezan iguales, una diferencia al final se puede atribuir a la web.
   - Usar solo las cifras de las secciones 3 y 6; no incluir nada de la sección 4.
   - Estilo académico y sobrio (Ingeniería de Sistemas, UCV), con tablas limpias y algún gráfico simple: barras de importancia de variables, matriz de confusión 2×2, barras apiladas de niveles de riesgo por grupo.
   - Colores de riesgo: verde = bajo, amarillo = medio, rojo = alto.
   - Notas del orador en cada diapositiva, en lenguaje sencillo, para que yo sepa qué decir.
   - Citas en formato IEEE si aparece alguna referencia.
