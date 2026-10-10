"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";

import { api, ErrorApi } from "@/lib/api";
import { borrarSesion, guardarSesion } from "@/lib/sesion";
import type {
  Estudiante,
  EstudianteConPrediccion,
  Indicadores,
  Prediccion,
  Registro,
  ResultadoImportacion,
  Usuario,
} from "@/lib/tipos";

// Solo se capturan errores de la API: redirect() también lanza y debe seguir
function mensaje(error: unknown): string {
  if (error instanceof ErrorApi) return error.message;
  throw error;
}

function texto(formData: FormData, campo: string): string {
  return String(formData.get(campo) ?? "").trim();
}

// --- Sesión -------------------------------------------------------------------

export type EstadoLogin = { error?: string; email?: string };

export async function iniciarSesion(
  _previo: EstadoLogin,
  formData: FormData,
): Promise<EstadoLogin> {
  const email = texto(formData, "email");
  const password = String(formData.get("password") ?? "");
  if (!email || !password) return { error: "Ingresa tu correo y contraseña", email };

  let respuesta: { access_token: string; expira_en: number; usuario: Usuario };
  try {
    respuesta = await api("/auth/login", {
      formulario: new URLSearchParams({ username: email, password }),
      sinSesion: true,
    });
  } catch (error) {
    return { error: mensaje(error), email };
  }
  await guardarSesion(respuesta.access_token, respuesta.expira_en);
  redirect("/");
}

export async function cerrarSesion() {
  await borrarSesion();
  redirect("/login");
}

export type EstadoPassword = { error?: string; ok?: boolean };

export async function cambiarPassword(
  _previo: EstadoPassword,
  formData: FormData,
): Promise<EstadoPassword> {
  const actual = String(formData.get("actual") ?? "");
  const nueva = String(formData.get("nueva") ?? "");
  if (nueva !== String(formData.get("repetir") ?? "")) {
    return { error: "Las contraseñas nuevas no coinciden" };
  }
  try {
    await api("/auth/cambiar-password", {
      json: { password_actual: actual, password_nueva: nueva },
    });
  } catch (error) {
    return { error: mensaje(error) };
  }
  return { ok: true };
}

// --- Registro de un alumno -----------------------------------------------------

const CRUDOS = [
  "suma_notas",
  "n_notas",
  "dias_asistidos",
  "dias_programados",
  "reuniones_asistidas",
  "reuniones_programadas",
] as const;

export type EstadoRegistro = {
  error?: string;
  resultado?: {
    estudianteId: string;
    codigo: string;
    momento: string;
    indicadores: Indicadores;
    prediccion: Prediccion;
    creado: boolean;
  };
};

export async function registrarAlumno(
  _previo: EstadoRegistro,
  formData: FormData,
): Promise<EstadoRegistro> {
  const codigo = texto(formData, "codigo").toUpperCase();
  const grado = Number(texto(formData, "grado"));
  const seccion = texto(formData, "seccion").toUpperCase();
  const momento = texto(formData, "momento");
  const crudos = Object.fromEntries(
    CRUDOS.map((c) => [c, Number(texto(formData, c).replace(",", "."))]),
  );
  if (CRUDOS.some((c) => texto(formData, c) === "" || Number.isNaN(crudos[c]))) {
    return { error: "Completa todos los datos de las fichas con números" };
  }

  try {
    // Alumno existente (por código) o nuevo
    const lista = await api<EstudianteConPrediccion[]>("/estudiantes");
    let estudiante: Estudiante | undefined = lista.find((e) => e.codigo === codigo);
    const creado = !estudiante;
    if (!estudiante) {
      estudiante = await api<Estudiante>("/estudiantes", {
        json: { codigo, grado, seccion },
      });
    } else if (estudiante.grado !== grado || estudiante.seccion !== seccion) {
      return {
        error: `${codigo} ya está registrado en ${estudiante.grado}.° ${estudiante.seccion}`,
      };
    }
    const registro = await api<Registro>("/registros", {
      json: { estudiante_id: estudiante.id, momento, ...crudos },
    });
    revalidatePath("/");
    return {
      resultado: {
        estudianteId: estudiante.id,
        codigo,
        momento,
        indicadores: {
          promedio: registro.promedio,
          pct_asistencia: registro.pct_asistencia,
          pct_reuniones: registro.pct_reuniones,
        },
        prediccion: registro.prediccion!,
        creado,
      },
    };
  } catch (error) {
    return { error: mensaje(error) };
  }
}

// --- Carga masiva --------------------------------------------------------------

export type EstadoImportacion = { error?: string; resultado?: ResultadoImportacion };

export async function importarCsv(
  _previo: EstadoImportacion,
  formData: FormData,
): Promise<EstadoImportacion> {
  const archivo = formData.get("archivo");
  if (!(archivo instanceof File) || archivo.size === 0) {
    return { error: "Elige un archivo CSV" };
  }
  if (archivo.size > 1_000_000) return { error: "El CSV supera 1 MB" };
  const envio = new FormData();
  envio.append("archivo", archivo, archivo.name);
  try {
    const resultado = await api<ResultadoImportacion>("/registros/importar", {
      formulario: envio,
    });
    revalidatePath("/");
    return { resultado };
  } catch (error) {
    return { error: mensaje(error) };
  }
}
