# 📌 CONTEXTO DEL PROYECTO

> Fuente de verdad resumida de la tesis. Si algo aquí contradice `introduccion.md` o `metodologia.md`, manda la tesis y se corrige este archivo.

## Datos generales
| Campo | Valor |
|---|---|
| Título | Web con Machine Learning para determinar el nivel de riesgo de deserción escolar en una institución educativa de Lima, 2026 |
| Autor | Calderón Salazar, Joaquin Marcelo |
| Asesor | Dr. Rodolfo Santiago Vergara Calderon |
| Universidad | Universidad César Vallejo — Escuela de Ingeniería de Sistemas |
| Línea de investigación | Sistema de información de comunicaciones |
| Formato de citas | IEEE |
| Institución de estudio | IE secundaria, distrito de Comas, Lima |

## Problema
La IE tenía un seguimiento **reactivo**: detectaba el riesgo cuando ya era tarde. La deserción subió de **29 % (2024)** a **35 % (2025)**. Causas principales identificadas: problemas económicos, necesidad de que el hijo aporte ingresos y embarazo adolescente. No existía herramienta predictiva.

## Variables
| Tipo | Variable |
|---|---|
| Independiente (VI) | Web con Machine Learning |
| Dependiente (VD) | Nivel de riesgo de deserción escolar |

| Dimensión de la VD | Indicador | Fórmula (tesis) | Sustento |
|---|---|---|---|
| Rendimiento académico | Promedio de calificaciones | Promedio = Σ Notas / n | Albonny y Duru [1] |
| Asistencia escolar | Porcentaje de asistencia | Asistencia = (DA / DP) × 100 | Albonny y Duru [1] |
| Apoyo familiar | Asistencia a reuniones de padres | CA = (RA / RT) × 100 | Ttito y Choque [39] |

Detalle técnico de cada campo → `VARIABLES.md`.

## Objetivos
**General:** Determinar en qué medida la implementación de una web con Machine Learning permite establecer el nivel de riesgo de deserción escolar en una IE de Lima, 2026.

| Código | Objetivo específico | Indicador |
|---|---|---|
| OE1 | Analizar cómo la web, mediante el rendimiento académico, permite determinar el nivel de riesgo | Promedio de calificaciones |
| OE2 | Examinar en qué medida la web, mediante la asistencia escolar, contribuye a determinar el nivel de riesgo | % de asistencia |
| OE3 | Evaluar cómo la web, mediante la asistencia a reuniones de padres, permite determinar el nivel de riesgo | % asistencia a reuniones |

## Hipótesis
| Código | Enunciado resumido |
|---|---|
| HG | La web con ML permite determinar con alto grado de precisión el nivel de riesgo |
| H1 | …a través del rendimiento académico, lo determina con eficacia |
| H2 | …mediante la asistencia escolar, contribuye significativamente |
| H3 | …mediante la asistencia a reuniones de padres, lo determina con precisión |

## Metodología (resumen)
| Aspecto | Definición |
|---|---|
| Enfoque | Cuantitativo |
| Tipo | Aplicada (Manual de Frascati, OCDE) |
| Nivel | Explicativo |
| Diseño | Cuasiexperimental con preprueba y posprueba, grupo control y experimental |
| Método | Hipotético-deductivo |
| Población / muestra | 70 estudiantes: 35 de 4.° (experimental) y 35 de 3.° (control) |
| Muestreo | No probabilístico, intencional por conveniencia (grupos intactos) |
| Unidad de análisis | Cada estudiante de 3.° o 4.° de secundaria |
| Técnica | Análisis documental de registros institucionales |
| Instrumento | 3 fichas de registro de datos (una por dimensión) |
| Métricas del modelo | Accuracy, precision, recall, F1 |
| Estadística inferencial | Shapiro-Wilk → t de Student o U de Mann-Whitney, α = 0.05 |
| Herramientas | Python + scikit-learn |
| Ética | Anonimización por códigos, autorización de la IE, Ley N.° 29733 y D.S. N.° 003-2013-JUS |

## Criterios de la muestra
- **Inclusión:** matriculado en 3.° o 4.°, asistencia completa en el sistema, historial de calificaciones.
- **Exclusión:** traslado definitivo antes del cierre, registros inconsistentes o vacíos en alguna de las 3 dimensiones.

## Estructura del documento de tesis
Proyecto: Introducción → Metodología → Aspectos administrativos (recursos, financiamiento, cronograma).
Informe final: + Resultados → Discusión → Conclusiones → Recomendaciones (reglas en `PLAN_ESTADISTICO.md`).
