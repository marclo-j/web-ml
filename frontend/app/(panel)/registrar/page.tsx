import { FormRegistro } from "@/components/FormRegistro";

export default function Registrar() {
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Registrar alumno</h1>
        <p className="text-sm text-slate-600">
          Datos de las fichas de un alumno, al cierre del bimestre.
        </p>
      </div>
      <FormRegistro />
    </div>
  );
}
