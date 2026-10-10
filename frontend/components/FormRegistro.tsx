"use client";

import Link from "next/link";
import { useActionState } from "react";

import { registrarAlumno } from "@/app/acciones";
import {
  Aviso,
  Campo,
  claseBoton,
  claseInput,
  formatoPct,
  formatoProbabilidad,
  NivelBadge,
  Tarjeta,
} from "./ui";

function Numero({ nombre, etiqueta, ayuda, min = 0, max, paso = 1 }: {
  nombre: string;
  etiqueta: string;
  ayuda?: string;
  min?: number;
  max?: number;
  paso?: number | "any";
}) {
  return (
    <Campo etiqueta={etiqueta} ayuda={ayuda}>
      <input
        name={nombre}
        type="number"
        inputMode="decimal"
        min={min}
        max={max}
        step={paso}
        required
        className={claseInput}
      />
    </Campo>
  );
}

export function FormRegistro() {
  const [estado, accion, pendiente] = useActionState(registrarAlumno, {});
  const r = estado.resultado;
  return (
    <div className="grid gap-6 lg:grid-cols-[1fr_20rem]">
      <form action={accion} className="flex flex-col gap-6">
        <Tarjeta titulo="Alumno">
          <div className="grid gap-4 sm:grid-cols-4">
            <Campo etiqueta="Código" ayuda="EST-001; nunca nombres">
              <input
                name="codigo"
                required
                pattern="[Ee][Ss][Tt]-\d{3}"
                placeholder="EST-001"
                className={`${claseInput} font-mono uppercase`}
              />
            </Campo>
            <Campo etiqueta="Grado" ayuda="3.° control · 4.° experimental">
              <select name="grado" required className={claseInput} defaultValue="">
                <option value="" disabled>
                  Elegir
                </option>
                <option value="3">3.°</option>
                <option value="4">4.°</option>
              </select>
            </Campo>
            <Campo etiqueta="Sección">
              <input
                name="seccion"
                required
                maxLength={8}
                placeholder="A"
                className={`${claseInput} uppercase`}
              />
            </Campo>
            <Campo etiqueta="Momento">
              <select name="momento" required className={claseInput} defaultValue="pre">
                <option value="pre">Preprueba</option>
                <option value="post">Posprueba</option>
              </select>
            </Campo>
          </div>
        </Tarjeta>

        <Tarjeta titulo="Ficha 1 · Rendimiento académico">
          <div className="grid gap-4 sm:grid-cols-2">
            <Numero nombre="suma_notas" etiqueta="Suma de notas" ayuda="Escala vigesimal (0–20)" paso="any" />
            <Numero nombre="n_notas" etiqueta="Número de notas" ayuda="Áreas con nota" min={1} />
          </div>
        </Tarjeta>
        <Tarjeta titulo="Ficha 2 · Asistencia escolar">
          <div className="grid gap-4 sm:grid-cols-2">
            <Numero nombre="dias_asistidos" etiqueta="Días asistidos (DA)" />
            <Numero nombre="dias_programados" etiqueta="Días programados (DP)" min={1} />
          </div>
        </Tarjeta>
        <Tarjeta titulo="Ficha 3 · Apoyo familiar">
          <div className="grid gap-4 sm:grid-cols-2">
            <Numero nombre="reuniones_asistidas" etiqueta="Reuniones asistidas (RA)" />
            <Numero nombre="reuniones_programadas" etiqueta="Reuniones programadas (RT)" min={1} />
          </div>
        </Tarjeta>

        {estado.error && <Aviso tipo="error">{estado.error}</Aviso>}
        <div>
          <button type="submit" disabled={pendiente} className={claseBoton}>
            {pendiente ? "Calculando…" : "Guardar y calcular riesgo"}
          </button>
        </div>
      </form>

      <aside aria-live="polite">
        {r ? (
          <Tarjeta titulo="Resultado">
            <p className="font-mono text-lg font-semibold">{r.codigo}</p>
            <p className="text-xs text-slate-500">
              {r.creado ? "Alumno nuevo" : "Alumno existente"} ·{" "}
              {r.momento === "pre" ? "preprueba" : "posprueba"}
            </p>
            <dl className="mt-4 space-y-2 text-sm">
              <div className="flex justify-between">
                <dt className="text-slate-600">Promedio</dt>
                <dd className="font-semibold tabular-nums">{r.indicadores.promedio}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-slate-600">Asistencia</dt>
                <dd className="font-semibold tabular-nums">
                  {formatoPct(r.indicadores.pct_asistencia)}
                </dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-slate-600">Reuniones</dt>
                <dd className="font-semibold tabular-nums">
                  {formatoPct(r.indicadores.pct_reuniones)}
                </dd>
              </div>
            </dl>
            <div className="mt-4 flex items-center justify-between border-t border-slate-100 pt-4">
              <NivelBadge nivel={r.prediccion.nivel_riesgo} />
              <span className="text-sm tabular-nums text-slate-600">
                {formatoProbabilidad(r.prediccion.probabilidad)}
              </span>
            </div>
            <Link
              href={`/estudiantes/${r.estudianteId}`}
              className="mt-4 inline-block text-sm text-indigo-600 hover:underline"
            >
              Ver detalle del alumno →
            </Link>
          </Tarjeta>
        ) : (
          <Aviso tipo="info">
            Copia los datos de las 3 fichas. El sistema calcula los indicadores con las
            fórmulas de la tesis y el modelo estima el nivel de riesgo. Si el alumno ya
            tiene datos en ese momento, se reemplazan.
          </Aviso>
        )}
      </aside>
    </div>
  );
}
