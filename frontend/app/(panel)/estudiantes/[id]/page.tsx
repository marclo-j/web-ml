import Link from "next/link";
import { notFound } from "next/navigation";

import {
  formatoPct,
  formatoProbabilidad,
  NivelBadge,
  Tarjeta,
} from "@/components/ui";
import { api, ErrorApi } from "@/lib/api";
import type { EstudianteDetalle, Registro } from "@/lib/tipos";

function Indicador({
  nombre,
  valor,
  formula,
  datos,
}: {
  nombre: string;
  valor: string;
  formula: string;
  datos: string;
}) {
  return (
    <div className="rounded-lg border border-slate-200 p-4">
      <p className="text-sm font-medium text-slate-600">{nombre}</p>
      <p className="mt-1 text-2xl font-bold tabular-nums">{valor}</p>
      <p className="mt-2 text-xs text-slate-500">
        {formula} · {datos}
      </p>
    </div>
  );
}

function BloqueRegistro({ r }: { r: Registro }) {
  return (
    <Tarjeta
      titulo={
        <span className="flex flex-wrap items-center gap-3">
          {r.momento === "pre" ? "Preprueba" : "Posprueba"}
          {r.prediccion && <NivelBadge nivel={r.prediccion.nivel_riesgo} />}
        </span>
      }
    >
      <div className="grid gap-3 sm:grid-cols-3">
        <Indicador
          nombre="Rendimiento académico"
          valor={r.promedio.toLocaleString("es-PE")}
          formula="Promedio = Σ notas / n"
          datos={`${r.suma_notas} / ${r.n_notas} notas`}
        />
        <Indicador
          nombre="Asistencia escolar"
          valor={formatoPct(r.pct_asistencia)}
          formula="(DA / DP) × 100"
          datos={`${r.dias_asistidos} de ${r.dias_programados} días`}
        />
        <Indicador
          nombre="Apoyo familiar"
          valor={formatoPct(r.pct_reuniones)}
          formula="(RA / RT) × 100"
          datos={`${r.reuniones_asistidas} de ${r.reuniones_programadas} reuniones`}
        />
      </div>
      {r.prediccion && (
        <p className="mt-4 text-sm text-slate-600">
          Probabilidad de deserción estimada:{" "}
          <strong className="tabular-nums text-slate-900">
            {formatoProbabilidad(r.prediccion.probabilidad)}
          </strong>{" "}
          · modelo {r.prediccion.version_modelo}
        </p>
      )}
    </Tarjeta>
  );
}

export default async function DetalleEstudiante({
  params,
}: PageProps<"/estudiantes/[id]">) {
  const { id } = await params;
  let estudiante: EstudianteDetalle;
  try {
    estudiante = await api<EstudianteDetalle>(`/estudiantes/${encodeURIComponent(id)}`);
  } catch (error) {
    if (error instanceof ErrorApi && (error.status === 404 || error.status === 422)) {
      notFound();
    }
    throw error;
  }

  return (
    <div className="flex flex-col gap-6">
      <div>
        <Link href="/" className="text-sm text-indigo-600 hover:underline">
          ← Estudiantes
        </Link>
        <h1 className="mt-2 font-mono text-2xl font-bold tracking-tight">
          {estudiante.codigo}
        </h1>
        <p className="text-sm text-slate-600">
          {estudiante.grado}.° {estudiante.seccion} · grupo{" "}
          <span className="capitalize">{estudiante.grupo}</span>
        </p>
      </div>
      {estudiante.registros.length === 0 ? (
        <p className="text-sm text-slate-600">
          Todavía no tiene datos.{" "}
          <Link href="/registrar" className="text-indigo-600 hover:underline">
            Registrar sus fichas
          </Link>
        </p>
      ) : (
        estudiante.registros.map((r) => <BloqueRegistro key={r.id} r={r} />)
      )}
    </div>
  );
}
