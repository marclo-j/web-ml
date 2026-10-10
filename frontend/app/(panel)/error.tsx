"use client";

import { Aviso, claseBotonSecundario } from "@/components/ui";

export default function ErrorPanel({
  error,
  retry,
}: {
  error: Error & { digest?: string };
  retry: () => void;
}) {
  return (
    <div className="flex flex-col items-start gap-4">
      <Aviso tipo="error">
        No se pudo cargar esta página. {error.digest ? "" : error.message}
        <br />
        Revisa que el backend esté en marcha y vuelve a intentar.
      </Aviso>
      <button type="button" onClick={() => retry()} className={claseBotonSecundario}>
        Reintentar
      </button>
    </div>
  );
}
