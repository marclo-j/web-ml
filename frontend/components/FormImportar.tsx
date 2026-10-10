"use client";

import Link from "next/link";
import { useActionState } from "react";

import { importarCsv } from "@/app/acciones";
import { Aviso, claseBoton, claseInput, Tarjeta } from "./ui";

export function FormImportar() {
  const [estado, accion, pendiente] = useActionState(importarCsv, {});
  const r = estado.resultado;
  return (
    <div className="flex flex-col gap-6">
      <Tarjeta>
        <form action={accion} className="flex flex-wrap items-end gap-3">
          <label className="flex flex-col gap-1 text-sm">
            <span className="font-medium text-slate-700">Archivo CSV (máx. 1 MB)</span>
            <input
              name="archivo"
              type="file"
              accept=".csv,text/csv"
              required
              className={`${claseInput} file:mr-3 file:rounded file:border-0 file:bg-slate-100 file:px-2 file:py-1 file:text-sm`}
            />
          </label>
          <button type="submit" disabled={pendiente} className={claseBoton}>
            {pendiente ? "Procesando…" : "Importar"}
          </button>
        </form>
      </Tarjeta>

      {estado.error && <Aviso tipo="error">{estado.error}</Aviso>}

      {r && (
        <Tarjeta titulo="Resultado de la importación">
          <div className="mb-4 flex flex-wrap gap-4 text-sm">
            <span className="rounded-lg bg-emerald-50 px-3 py-2 text-emerald-800">
              <strong className="tabular-nums">{r.procesados}</strong> procesados
            </span>
            <span
              className={`rounded-lg px-3 py-2 ${r.excluidos ? "bg-amber-50 text-amber-800" : "bg-slate-50 text-slate-600"}`}
            >
              <strong className="tabular-nums">{r.excluidos}</strong> excluidos
            </span>
            {r.procesados > 0 && (
              <Link href="/" className="py-2 text-indigo-600 hover:underline">
                Ver estudiantes →
              </Link>
            )}
          </div>
          {r.detalle_excluidos.length > 0 && (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="border-b border-slate-200 text-xs uppercase text-slate-500">
                  <tr>
                    <th className="py-2 pr-4 font-semibold">Fila</th>
                    <th className="py-2 pr-4 font-semibold">Código</th>
                    <th className="py-2 pr-4 font-semibold">Motivo</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {r.detalle_excluidos.map((e) => (
                    <tr key={`${e.fila}-${e.codigo}`}>
                      <td className="py-2 pr-4 tabular-nums">{e.fila}</td>
                      <td className="py-2 pr-4 font-mono">{e.codigo ?? "—"}</td>
                      <td className="py-2 pr-4">{e.motivo}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Tarjeta>
      )}
    </div>
  );
}
