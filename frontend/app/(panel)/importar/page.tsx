import { FormImportar } from "@/components/FormImportar";
import { Tarjeta } from "@/components/ui";

const EJEMPLO = `codigo,grado,seccion,grupo,momento,suma_notas,n_notas,dias_asistidos,dias_programados,reuniones_asistidas,reuniones_programadas
EST-001,4,B,experimental,pre,142,10,40,45,1,2`;

export default function Importar() {
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Importar CSV</h1>
        <p className="text-sm text-slate-600">
          Carga masiva de las fichas de una sección. Los alumnos que no existan se crean;
          las filas que no cumplen una regla se excluyen y se informan.
        </p>
      </div>
      <FormImportar />
      <Tarjeta titulo="Formato">
        <p className="mb-3 text-sm text-slate-600">
          Separado por comas o por punto y coma (como lo guarda Excel en español); se
          admite coma decimal. <code>grupo</code> puede ir vacío: se deduce del grado.
        </p>
        <pre className="overflow-x-auto rounded-lg bg-slate-900 p-4 text-xs text-slate-100">
          {EJEMPLO}
        </pre>
      </Tarjeta>
    </div>
  );
}
