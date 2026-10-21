# Prompt de corrección para Claude Design — Avance 2026-10-03

> Pégalo en Claude Design, en el mismo proyecto de la presentación "Avance de Tesis".
> Antes de pegarlo, completa los dos campos marcados con [CONFIRMAR].

---

Necesito corregir la presentación "Avance de tesis" que hiciste. Mantén el mismo estilo visual, la misma tipografía y los mismos colores. Aplica exactamente estos cambios y no agregues afirmaciones ni datos que no estén en este mensaje.

## A. Errores que debes corregir

1. **Diapositiva 1 (portada):** reemplaza "Universidad César Vallejo — Los Olivos, 2026" por "Universidad César Vallejo — [CONFIRMAR: sede], 2026". No supongas la sede.
2. **Diapositiva 5 (instrumentos):** elimina la frase "(aprobadas por la dirección de la IE)". Yo no te di ese dato. El instrumento queda como "Ficha de registro de datos".
3. **Diapositiva 5:** la cita de la escala vigesimal está mal. "Escala vigesimal 0–20" no se sustenta con [1], sino con la norma del MINEDU (RVM N.° 094-2020-MINEDU). Escribe "Escala vigesimal 0–20 (RVM N.° 094-2020-MINEDU)" sin número de cita. Las fórmulas sí mantienen sus citas: [1] para promedio y asistencia, y [39] para reuniones.
4. **Regla general:** no inventes datos, aprobaciones, lugares ni citas. Si te falta un dato, deja un marcador [CONFIRMAR] visible.

## B. Contenido que debes quitar

El histórico 2024–2025 está en revisión: sus registros fuente aún no se han validado. Por eso todo lo que depende de él sale de esta presentación:

- **Diapositiva 6:** quita el bloque "Histórico de entrenamiento 2024–2025", con los 140 alumnos, los 37 desertores y la tabla de desertaron frente a no desertaron. Deja solo la parte de la preprueba 2026.
- **Diapositiva 7 (Modelo y métricas):** elimínala completa: AUC, accuracy, recall, precision, F1, matriz de confusión y ajuste de hiperparámetros.
- **Diapositiva 8 (Importancia de variables):** elimínala completa.
- **Diapositiva 11 (Vista previa del resultado de la web):** elimínala completa. Usaba un modelo entrenado con el histórico.
- **Diapositiva 12:** quita la limitación "El dato 'desertó' tenía discrepancias entre fichas; se corrigió con confirmación de la IE".

No menciones en ninguna diapositiva cifras de métricas del modelo ni porcentajes de desertores de 2024 o 2025. Solo se mantienen el 29 % y el 35 % de la diapositiva 2, porque son el problema de investigación tal como está en la tesis.

## C. Contenido nuevo

### Nueva diapositiva "Fase 3 · Pipeline del modelo (listo, en espera del histórico validado)"
Va después de la diapositiva 6. Diagrama de flujo horizontal con 5 pasos:

1. **Fichas Excel**: las 3 fichas por alumno.
2. **Consolidación y validación**: une las 3 fichas por código, aplica criterios de inclusión y exclusión, y detecta registros inconsistentes.
3. **Cálculo de indicadores**: promedio, % asistencia y % reuniones, con las fórmulas de la tesis.
4. **Entrenamiento**: Random Forest con validación cruzada estratificada repetida (5 partes × 5 repeticiones) y búsqueda de hiperparámetros.
5. **Salida**: probabilidad de deserción → nivel bajo / medio / alto.

Debajo, un recuadro con este texto: "El pipeline está implementado y probado (34 pruebas automáticas). El entrenamiento definitivo se hará con el histórico 2024–2025 una vez validado contra los registros fuente de la IE."

Notas del orador: "Aquí muestro que el sistema que entrena el modelo ya funciona de principio a fin. No muestro métricas porque los datos de entrenamiento todavía se están validando con los documentos originales de la IE. Prefiero presentar métricas cuando estén sobre datos verificados."

### Diapositiva 12 (Limitaciones y próximos pasos), versión corregida
- Limitaciones:
  - "Solo 3 variables: las causas principales de deserción en la IE (económicas, trabajo, embarazo adolescente) no están en las fichas."
  - "El histórico de entrenamiento 2024–2025 está en validación contra los registros fuente de la IE."
- Por validar con el asesor: las mismas 2 preguntas que ya tenía.
- Próximos pasos (en este orden):
  1. Validar el histórico 2024–2025 con los registros fuente de la IE.
  2. Entrenar y evaluar el modelo definitivo.
  3. Fijar los umbrales bajo / medio / alto.
  4. Backend (FastAPI).
  5. Frontend web para tutores.
  6. Despliegue e intervención con el grupo experimental.
  7. Recolección posprueba y análisis estadístico final.
  8. Redacción de Resultados y Discusión.

## D. Lo que se mantiene sin cambios
Diapositivas 2, 3, 4, 9 y 10, y la parte de preprueba 2026 de la diapositiva 6: 69 incluidos de 70, 1 excluido por traslado definitivo, control 35 y experimental 34, datos al cierre del I bimestre. Las tablas de SPSS (normalidad y equivalencia de grupos) quedan igual, con sus espacios para la captura de SPSS.

## E. Orden final (10 diapositivas)
1. Portada
2. Realidad problemática
3. Objetivo e hipótesis
4. Arquitectura de la web
5. Instrumentos: 3 fichas
6. Datos recolectados: preprueba 2026
7. Pipeline del modelo (nueva)
8. SPSS (A): prueba de normalidad
9. SPSS (B): equivalencia de grupos
10. Limitaciones y próximos pasos

Actualiza la numeración "NN / 10" del pie de página y los rótulos de sección (por ejemplo, "07 · Fase 3").
