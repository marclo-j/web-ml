import "server-only";

import { cookies } from "next/headers";

// El token del backend vive en una cookie httpOnly: el JavaScript del
// navegador no puede leerla, así que un script inyectado no puede robarla.
// Todas las llamadas a la API se hacen desde el servidor de Next.js.
export const COOKIE_SESION = "sesion";

export async function guardarSesion(token: string, segundos: number) {
  (await cookies()).set(COOKIE_SESION, token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    path: "/",
    maxAge: segundos,
  });
}

export async function leerToken(): Promise<string | undefined> {
  return (await cookies()).get(COOKIE_SESION)?.value;
}

export async function borrarSesion() {
  (await cookies()).delete(COOKIE_SESION);
}
