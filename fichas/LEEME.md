# Fichas de registro de datos (instrumento)

Plantillas **vacías** de las 3 fichas de la metodología, una por dimensión de la variable dependiente.

| Archivo | Dimensión | Fórmula (tesis) | Columna calculada |
|---|---|---|---|
| `ficha_1_rendimiento.xlsx` | Rendimiento académico | Promedio = Σ Notas / n [1] | `n_notas`, `suma_notas`, `promedio` |
| `ficha_2_asistencia.xlsx` | Asistencia escolar | Asistencia = (DA / DP) × 100 [1] | `pct_asistencia` |
| `ficha_3_reuniones.xlsx` | Apoyo familiar | CA = (RA / RT) × 100 [39] | `pct_reuniones` |

Cada libro tiene la hoja **Instrucciones** (fórmula, periodo de corte, privacidad y diccionario de columnas) y la hoja **Datos**. La ficha 1 incluye además la hoja **Conversión** para la escala literal (provisional, decisión D1).

## ⚠️ Una ficha llena es un dato real
No se llena en esta carpeta. Se copia la plantilla, se llena y se guarda en `data/raw/` (gitignored). Aquí solo se versionan plantillas vacías.

## Cómo se usan
- **Periodo de corte:** I bimestre (la IE trabaja por bimestres), igual para el PRE 2026 y para el histórico 2024–2025 (decisión D3 en `docs/VARIABLES.md`).
- **Una fila por estudiante y momento.** El `codigo` (`EST-###`) une las 3 fichas; `grupo` se calcula a partir del grado (3.° = control, 4.° = experimental).
- **Histórico 2024–2025:** mismas fichas, con `anio` y `deserto` (0/1) llenos.
- **Colores:** gris = calculada (bloqueada) · ámbar = falta un dato obligatorio · rojo = valor inconsistente.
- Las hojas están protegidas **sin contraseña** (Revisar → Desproteger hoja) solo para evitar borrar fórmulas por accidente.

## Regenerar
```bash
ml/.venv/Scripts/python fichas/generar_fichas.py            # Windows
python fichas/generar_fichas.py --filas 200                 # más filas
```
Si cambia una fórmula o una regla de `docs/VARIABLES.md`, se edita `generar_fichas.py` y se regeneran las plantillas; no se editan los `.xlsx` a mano.
