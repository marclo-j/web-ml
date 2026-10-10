"use client";

import { useActionState } from "react";

import { cambiarPassword } from "@/app/acciones";
import { Aviso, Campo, claseBoton, claseInput } from "./ui";

export function FormPassword() {
  const [estado, accion, pendiente] = useActionState(cambiarPassword, {});
  return (
    <form action={accion} className="flex max-w-sm flex-col gap-4">
      <Campo etiqueta="Contraseña actual">
        <input name="actual" type="password" autoComplete="current-password" required className={claseInput} />
      </Campo>
      <Campo etiqueta="Nueva contraseña" ayuda="Mínimo 10 caracteres">
        <input name="nueva" type="password" autoComplete="new-password" minLength={10} required className={claseInput} />
      </Campo>
      <Campo etiqueta="Repite la nueva contraseña">
        <input name="repetir" type="password" autoComplete="new-password" minLength={10} required className={claseInput} />
      </Campo>
      {estado.error && <Aviso tipo="error">{estado.error}</Aviso>}
      {estado.ok && <Aviso tipo="exito">Contraseña actualizada.</Aviso>}
      <div>
        <button type="submit" disabled={pendiente} className={claseBoton}>
          {pendiente ? "Guardando…" : "Cambiar contraseña"}
        </button>
      </div>
    </form>
  );
}
