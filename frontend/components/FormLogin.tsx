"use client";

import { useActionState } from "react";

import { iniciarSesion } from "@/app/acciones";
import { Aviso, Campo, claseBoton, claseInput } from "./ui";

export function FormLogin() {
  const [estado, accion, pendiente] = useActionState(iniciarSesion, {});
  return (
    <form
      action={accion}
      className="flex flex-col gap-4 rounded-xl border border-slate-200 bg-white p-6 shadow-sm"
    >
      <Campo etiqueta="Correo">
        <input
          name="email"
          type="email"
          autoComplete="username"
          required
          defaultValue={estado.email}
          className={claseInput}
        />
      </Campo>
      <Campo etiqueta="Contraseña">
        <input
          name="password"
          type="password"
          autoComplete="current-password"
          required
          className={claseInput}
        />
      </Campo>
      {estado.error && <Aviso tipo="error">{estado.error}</Aviso>}
      <button type="submit" disabled={pendiente} className={claseBoton}>
        {pendiente ? "Ingresando…" : "Ingresar"}
      </button>
    </form>
  );
}
