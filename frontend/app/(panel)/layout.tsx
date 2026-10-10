import Link from "next/link";

import { cerrarSesion } from "@/app/acciones";
import { usuarioActual } from "@/lib/api";

const ENLACES = [
  { href: "/", texto: "Estudiantes" },
  { href: "/registrar", texto: "Registrar" },
  { href: "/importar", texto: "Importar CSV" },
  { href: "/modelo", texto: "Modelo" },
] as const;

export default async function PanelLayout({ children }: LayoutProps<"/">) {
  const usuario = await usuarioActual();
  return (
    <>
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center gap-x-6 gap-y-2 px-4 py-3">
          <Link href="/" className="font-semibold tracking-tight text-slate-900">
            Riesgo de deserción
          </Link>
          <nav className="order-last -mx-3 flex w-full gap-1 overflow-x-auto text-sm sm:order-none sm:mx-0 sm:w-auto sm:flex-1">
            {ENLACES.map((e) => (
              <Link
                key={e.href}
                href={e.href}
                className="shrink-0 rounded-md px-3 py-1.5 font-medium text-slate-600 hover:bg-slate-100 hover:text-slate-900"
              >
                {e.texto}
              </Link>
            ))}
          </nav>
          <div className="ml-auto flex items-center gap-3 text-sm">
            <Link href="/cuenta" className="text-slate-600 hover:text-slate-900">
              <span className="hidden sm:inline">{usuario.email} </span>
              <span className="rounded bg-slate-100 px-1.5 py-0.5 text-xs text-slate-600">
                {usuario.rol}
              </span>
            </Link>
            <form action={cerrarSesion}>
              <button
                type="submit"
                className="rounded-md px-2 py-1 font-medium text-slate-600 hover:bg-slate-100 hover:text-slate-900"
              >
                Salir
              </button>
            </form>
          </div>
        </div>
      </header>
      <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-8">{children}</main>
      <footer className="border-t border-slate-200 py-4 text-center text-xs text-slate-500">
        Tesis — Ingeniería de Sistemas, UCV 2026 · Solo códigos anonimizados (Ley N.° 29733)
      </footer>
    </>
  );
}
