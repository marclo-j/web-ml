import "server-only";

import { redirect } from "next/navigation";
import { cache } from "react";

import { leerToken } from "./sesion";
import type { Usuario } from "./tipos";

// URL del backend, solo del lado del servidor (no NEXT_PUBLIC_)
const API_URL = (process.env.API_URL ?? "http://localhost:8000").replace(/\/$/, "");

export class ErrorApi extends Error {
  constructor(
    public status: number,
    mensaje: string,
  ) {
    super(mensaje);
  }
}

type Opciones = {
  metodo?: "GET" | "POST";
  json?: unknown;
  formulario?: FormData | URLSearchParams;
  sinSesion?: boolean;
};

// FastAPI devuelve detail como texto o como lista de errores de validación
function mensajeDeError(cuerpo: unknown, status: number): string {
  const detalle = (cuerpo as { detail?: unknown } | null)?.detail;
  if (typeof detalle === "string") return detalle;
  if (Array.isArray(detalle)) {
    return detalle
      .map((e: { loc?: unknown[]; msg?: string }) => {
        const campo = e.loc?.filter((p) => p !== "body").join(".");
        return campo ? `${campo}: ${e.msg}` : e.msg;
      })
      .join("; ");
  }
  if (status === 503) return "El modelo no está cargado en el servidor";
  return `Error ${status} del servidor`;
}

export async function api<T>(ruta: string, opciones: Opciones = {}): Promise<T> {
  const encabezados: Record<string, string> = { Accept: "application/json" };
  if (!opciones.sinSesion) {
    const token = await leerToken();
    if (!token) redirect("/login");
    encabezados.Authorization = `Bearer ${token}`;
  }
  let cuerpo: BodyInit | undefined;
  if (opciones.json !== undefined) {
    encabezados["Content-Type"] = "application/json";
    cuerpo = JSON.stringify(opciones.json);
  } else if (opciones.formulario) {
    cuerpo = opciones.formulario;
  }

  let respuesta: Response;
  try {
    respuesta = await fetch(`${API_URL}${ruta}`, {
      method: opciones.metodo ?? (cuerpo ? "POST" : "GET"),
      headers: encabezados,
      body: cuerpo,
      cache: "no-store",
    });
  } catch {
    throw new ErrorApi(0, "No se pudo conectar con el servidor de la API");
  }

  // Token vencido o usuario desactivado: volver a iniciar sesión
  if (respuesta.status === 401 && !opciones.sinSesion) redirect("/login?expirada=1");
  if (respuesta.status === 204) return undefined as T;

  const datos = await respuesta.json().catch(() => null);
  if (!respuesta.ok) {
    throw new ErrorApi(respuesta.status, mensajeDeError(datos, respuesta.status));
  }
  return datos as T;
}

// Una sola consulta por petición aunque varios componentes lo pidan
export const usuarioActual = cache(() => api<Usuario>("/auth/yo"));
