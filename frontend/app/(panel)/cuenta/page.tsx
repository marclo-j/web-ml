import { FormPassword } from "@/components/FormPassword";
import { Tarjeta } from "@/components/ui";
import { usuarioActual } from "@/lib/api";

export default async function Cuenta() {
  const usuario = await usuarioActual();
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Mi cuenta</h1>
        <p className="text-sm text-slate-600">
          {usuario.email} · rol <span className="font-medium">{usuario.rol}</span>
        </p>
      </div>
      <Tarjeta titulo="Cambiar contraseña">
        <FormPassword />
      </Tarjeta>
    </div>
  );
}
