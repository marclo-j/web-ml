import type { ReactNode } from "react";

import type { Nivel } from "@/lib/tipos";

// Colores de docs/MODELO.md: bajo verde, medio amarillo, alto rojo. Siempre
// con el texto del nivel, para no depender solo del color.
const ESTILO_NIVEL: Record<Nivel, string> = {
  bajo: "bg-emerald-50 text-emerald-800 ring-emerald-600/20",
  medio: "bg-amber-50 text-amber-800 ring-amber-600/30",
  alto: "bg-red-50 text-red-800 ring-red-600/20",
};
const PUNTO_NIVEL: Record<Nivel, string> = {
  bajo: "bg-emerald-500",
  medio: "bg-amber-500",
  alto: "bg-red-500",
};

export function NivelBadge({ nivel }: { nivel: Nivel }) {
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-semibold capitalize ring-1 ring-inset ${ESTILO_NIVEL[nivel]}`}
    >
      <span className={`size-1.5 rounded-full ${PUNTO_NIVEL[nivel]}`} aria-hidden />
      {nivel}
    </span>
  );
}

export function Tarjeta({
  titulo,
  children,
  className = "",
}: {
  titulo?: ReactNode;
  children: ReactNode;
  className?: string;
}) {
  return (
    <section
      className={`rounded-xl border border-slate-200 bg-white p-5 shadow-sm ${className}`}
    >
      {titulo && <h2 className="mb-4 text-base font-semibold text-slate-900">{titulo}</h2>}
      {children}
    </section>
  );
}

export function Campo({
  etiqueta,
  ayuda,
  children,
}: {
  etiqueta: string;
  ayuda?: string;
  children: ReactNode;
}) {
  return (
    <label className="flex flex-col gap-1 text-sm">
      <span className="font-medium text-slate-700">{etiqueta}</span>
      {children}
      {ayuda && <span className="text-xs text-slate-500">{ayuda}</span>}
    </label>
  );
}

export const claseInput =
  "rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 shadow-xs outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 disabled:bg-slate-100";

export const claseBoton =
  "inline-flex items-center justify-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 disabled:cursor-not-allowed disabled:opacity-60";

export const claseBotonSecundario =
  "inline-flex items-center justify-center gap-2 rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700 shadow-xs hover:bg-slate-50";

export function Aviso({
  tipo,
  children,
}: {
  tipo: "error" | "exito" | "info";
  children: ReactNode;
}) {
  const estilos = {
    error: "border-red-200 bg-red-50 text-red-800",
    exito: "border-emerald-200 bg-emerald-50 text-emerald-800",
    info: "border-slate-200 bg-slate-50 text-slate-700",
  };
  return (
    <div
      role={tipo === "error" ? "alert" : "status"}
      className={`rounded-lg border px-4 py-3 text-sm ${estilos[tipo]}`}
    >
      {children}
    </div>
  );
}

export function formatoPct(valor: number) {
  return `${valor.toLocaleString("es-PE", { maximumFractionDigits: 2 })} %`;
}

export function formatoProbabilidad(valor: number) {
  return `${(valor * 100).toLocaleString("es-PE", { maximumFractionDigits: 1 })} %`;
}
