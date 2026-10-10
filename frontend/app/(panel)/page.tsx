import Link from "next/link";

import {
  Aviso,
  claseBoton,
  claseBotonSecundario,
  claseInput,
  formatoProbabilidad,
  NivelBadge,
  Tarjeta,
} from "@/components/ui";
import { api } from "@/lib/api";
import {
  type EstudianteConPrediccion,
  type Grupo,
  type Momento,
  type Nivel,
  NIVELES,
  type Resumen,
} from "@/lib/tipos";

const GRUPOS: Grupo[] = ["control", "experimental"];
const ETIQUETA_GRUPO: Record<Grupo, string> = {
  control: "Control (3.°)",
  experimental: "Experimental (4.°)",
};

function valor<T extends string>(v: string | string[] | undefined, permitidos: readonly T[]) {
  return typeof v === "string" && (permitidos as readonly string[]).includes(v)
    ? (v as T)
    : undefined;
}

export default async function Estudiantes({ searchParams }: PageProps<"/">) {
  const params = await searchParams;
  const grupo = valor<Grupo>(params.grupo, GRUPOS);
  const momento = valor<Momento>(params.momento, ["pre", "post"]);
  const nivel = valor<Nivel>(params.nivel, NIVELES);

  const filtros = new URLSearchParams();
  if (grupo) filtros.set("grupo", grupo);
  if (momento) filtros.set("momento", momento);
  if (nivel) filtros.set("nivel", nivel);

  const [resumen, estudiantes] = await Promise.all([
    api<Resumen>(`/resumen?momento=${momento ?? "pre"}`),
    api<EstudianteConPrediccion[]>(`/estudiantes?${filtros}`),
  ]);

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Estudiantes</h1>
          <p className="text-sm text-slate-600">
            Nivel de riesgo de deserción según el modelo, por alumno.
          </p>
        </div>
        <Link href="/registrar" className={claseBoton}>
          Registrar alumno
        </Link>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        {GRUPOS.map((g) => {
          const conteo = resumen[g];
          const total = NIVELES.reduce((s, n) => s + conteo[n], 0);
          return (
            <Tarjeta
              key={g}
              titulo={
                <span className="flex items-baseline justify-between">
                  <span>{ETIQUETA_GRUPO[g]}</span>
                  <span className="text-xs font-normal text-slate-500">
                    {momento === "post" ? "Posprueba" : "Preprueba"} · {total} alumnos
                  </span>
                </span>
              }
            >
              <dl className="grid grid-cols-3 gap-3">
                {NIVELES.map((n) => (
                  <Link
                    key={n}
                    href={`/?grupo=${g}&momento=${momento ?? "pre"}&nivel=${n}`}
                    className="rounded-lg border border-slate-200 p-3 hover:border-slate-300 hover:bg-slate-50"
                  >
                    <dt>
                      <NivelBadge nivel={n} />
                    </dt>
                    <dd className="mt-2 text-2xl font-bold tabular-nums">{conteo[n]}</dd>
                  </Link>
                ))}
              </dl>
            </Tarjeta>
          );
        })}
      </div>

      <Tarjeta>
        <form className="mb-4 flex flex-wrap items-end gap-3" method="get">
          <label className="flex flex-col gap-1 text-sm">
            <span className="font-medium text-slate-700">Grupo</span>
            <select name="grupo" defaultValue={grupo ?? ""} className={claseInput}>
              <option value="">Todos</option>
              {GRUPOS.map((g) => (
                <option key={g} value={g}>
                  {ETIQUETA_GRUPO[g]}
                </option>
              ))}
            </select>
          </label>
          <label className="flex flex-col gap-1 text-sm">
            <span className="font-medium text-slate-700">Momento</span>
            <select name="momento" defaultValue={momento ?? ""} className={claseInput}>
              <option value="">Último disponible</option>
              <option value="pre">Preprueba</option>
              <option value="post">Posprueba</option>
            </select>
          </label>
          <label className="flex flex-col gap-1 text-sm">
            <span className="font-medium text-slate-700">Nivel</span>
            <select name="nivel" defaultValue={nivel ?? ""} className={claseInput}>
              <option value="">Todos</option>
              {NIVELES.map((n) => (
                <option key={n} value={n} className="capitalize">
                  {n}
                </option>
              ))}
            </select>
          </label>
          <button type="submit" className={claseBotonSecundario}>
            Filtrar
          </button>
          {filtros.size > 0 && (
            <Link href="/" className="py-2 text-sm text-indigo-600 hover:underline">
              Quitar filtros
            </Link>
          )}
        </form>

        {estudiantes.length === 0 ? (
          <Aviso tipo="info">
            No hay alumnos con estos filtros. Registra uno o importa un CSV.
          </Aviso>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-slate-200 text-xs uppercase text-slate-500">
                <tr>
                  <th className="py-2 pr-4 font-semibold">Código</th>
                  <th className="py-2 pr-4 font-semibold">Grado y sección</th>
                  <th className="py-2 pr-4 font-semibold">Grupo</th>
                  <th className="py-2 pr-4 font-semibold">Momento</th>
                  <th className="py-2 pr-4 font-semibold">Nivel de riesgo</th>
                  <th className="py-2 pr-4 text-right font-semibold">Probabilidad</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {estudiantes.map((e) => (
                  <tr key={e.id} className="hover:bg-slate-50">
                    <td className="py-2 pr-4">
                      <Link
                        href={`/estudiantes/${e.id}`}
                        className="font-mono font-medium text-indigo-700 hover:underline"
                      >
                        {e.codigo}
                      </Link>
                    </td>
                    <td className="py-2 pr-4">
                      {e.grado}.° {e.seccion}
                    </td>
                    <td className="py-2 pr-4 capitalize">{e.grupo}</td>
                    <td className="py-2 pr-4">
                      {e.ultima_prediccion?.momento === "post" ? "Posprueba" : e.ultima_prediccion ? "Preprueba" : "—"}
                    </td>
                    <td className="py-2 pr-4">
                      {e.ultima_prediccion ? (
                        <NivelBadge nivel={e.ultima_prediccion.nivel_riesgo} />
                      ) : (
                        <span className="text-slate-400">Sin registro</span>
                      )}
                    </td>
                    <td className="py-2 pr-4 text-right tabular-nums">
                      {e.ultima_prediccion
                        ? formatoProbabilidad(e.ultima_prediccion.probabilidad)
                        : "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            <p className="mt-3 text-xs text-slate-500">
              {estudiantes.length} {estudiantes.length === 1 ? "alumno" : "alumnos"}
            </p>
          </div>
        )}
      </Tarjeta>
    </div>
  );
}
