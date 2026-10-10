import { FormLogin } from "@/components/FormLogin";
import { Aviso } from "@/components/ui";

export default async function Login({ searchParams }: PageProps<"/login">) {
  const { expirada } = await searchParams;
  return (
    <main className="flex flex-1 items-center justify-center px-4 py-12">
      <div className="w-full max-w-sm">
        <div className="mb-8 text-center">
          <p className="text-sm font-semibold text-indigo-600">IE · Comas, Lima</p>
          <h1 className="mt-1 text-2xl font-bold tracking-tight text-slate-900">
            Riesgo de deserción escolar
          </h1>
          <p className="mt-2 text-sm text-slate-600">
            Ingresa con la cuenta que te asignó la dirección.
          </p>
        </div>
        {expirada && (
          <div className="mb-4">
            <Aviso tipo="info">Tu sesión venció. Vuelve a ingresar.</Aviso>
          </div>
        )}
        <FormLogin />
      </div>
    </main>
  );
}
