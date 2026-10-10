import { Aviso, Tarjeta } from "@/components/ui";
import { api } from "@/lib/api";
import type { InfoModelo } from "@/lib/tipos";

const NOMBRE_METRICA: Record<string, string> = {
  roc_auc: "AUC-ROC",
  f1: "F1",
  recall: "Recall (sensibilidad)",
  precision: "Precisión",
  accuracy: "Exactitud",
};

const NOMBRE_FEATURE: Record<string, string> = {
  promedio: "Promedio de notas",
  pct_asistencia: "% de asistencia",
  pct_reuniones: "% de reuniones asistidas",
};

const numero = (v: number, d = 3) =>
  v.toLocaleString("es-PE", { minimumFractionDigits: d, maximumFractionDigits: d });

export default async function Modelo() {
  const m = await api<InfoModelo>("/modelo");
  const cv = m.metricas.cv_5x5_sobre_reales;
  const matriz = m.metricas.holdout_20pct?.matriz_confusion?.valores;

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Modelo {m.version}</h1>
        <p className="text-sm text-slate-600">
          Random Forest · entrenado el {m.entrenado} con {m.n_entrenamiento} alumnos reales
          {m.aumento ? ` + aumento ${m.aumento.metodo.toUpperCase()} ×${m.aumento.factor} solo en entrenamiento` : ""}
        </p>
      </div>
      {m.aviso && <Aviso tipo="error">{m.aviso}</Aviso>}

      <div className="grid gap-6 lg:grid-cols-2">
        <Tarjeta titulo="Umbrales de nivel de riesgo">
          <ul className="space-y-2 text-sm">
            <li>
              <strong className="text-emerald-700">Bajo:</strong> probabilidad menor a{" "}
              {numero(m.umbrales.medio, 2)}
            </li>
            <li>
              <strong className="text-amber-700">Medio:</strong> de {numero(m.umbrales.medio, 2)}{" "}
              a menos de {numero(m.umbrales.alto, 2)}
            </li>
            <li>
              <strong className="text-red-700">Alto:</strong> {numero(m.umbrales.alto, 2)} o más
            </li>
          </ul>
          <p className="mt-4 text-xs text-slate-500">
            Variables: {m.features.map((f) => NOMBRE_FEATURE[f] ?? f).join(", ")}.
          </p>
        </Tarjeta>

        {cv && (
          <Tarjeta titulo="Desempeño (validación cruzada 5×5, solo alumnos reales)">
            <table className="w-full text-sm">
              <tbody className="divide-y divide-slate-100">
                {Object.entries(cv).map(([k, v]) => (
                  <tr key={k}>
                    <td className="py-1.5 text-slate-600">{NOMBRE_METRICA[k] ?? k}</td>
                    <td className="py-1.5 text-right font-semibold tabular-nums">
                      {numero(v.media)} ± {numero(v.desviacion, 2)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Tarjeta>
        )}

        {matriz && (
          <Tarjeta titulo="Matriz de confusión (holdout 20 %)">
            <table className="text-center text-sm">
              <thead>
                <tr>
                  <th />
                  <th className="px-3 pb-2 text-xs font-medium text-slate-500">Predijo: no deserta</th>
                  <th className="px-3 pb-2 text-xs font-medium text-slate-500">Predijo: deserta</th>
                </tr>
              </thead>
              <tbody>
                {["Real: no desertó", "Real: desertó"].map((etiqueta, i) => (
                  <tr key={etiqueta}>
                    <th className="pr-3 text-right text-xs font-medium text-slate-500">{etiqueta}</th>
                    {matriz[i].map((v, j) => (
                      <td
                        key={j}
                        className={`m-1 rounded-lg px-6 py-3 text-lg font-bold tabular-nums ${i === j ? "bg-emerald-50 text-emerald-800" : "bg-slate-50 text-slate-700"}`}
                      >
                        {v}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
            <p className="mt-3 text-xs text-slate-500">
              Holdout pequeño: la métrica principal es la validación cruzada.
            </p>
          </Tarjeta>
        )}
      </div>
    </div>
  );
}
