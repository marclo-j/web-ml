// Tipos de las respuestas del backend (docs/API.md)

export type Nivel = "bajo" | "medio" | "alto";
export type Grupo = "control" | "experimental";
export type Momento = "pre" | "post";
export type Rol = "tutor" | "directivo";

export const NIVELES: Nivel[] = ["bajo", "medio", "alto"];

export type Usuario = { email: string; rol: Rol };

export type DatosCrudos = {
  suma_notas: number;
  n_notas: number;
  dias_asistidos: number;
  dias_programados: number;
  reuniones_asistidas: number;
  reuniones_programadas: number;
};

export type Indicadores = {
  promedio: number;
  pct_asistencia: number;
  pct_reuniones: number;
};

export type Prediccion = {
  probabilidad: number;
  nivel_riesgo: Nivel;
  version_modelo: string;
};

export type Estudiante = {
  id: string;
  codigo: string;
  grado: number;
  seccion: string;
  grupo: Grupo;
};

export type EstudianteConPrediccion = Estudiante & {
  ultima_prediccion: {
    momento: Momento;
    nivel_riesgo: Nivel;
    probabilidad: number;
  } | null;
};

export type Registro = DatosCrudos &
  Indicadores & {
    id: string;
    estudiante_id: string;
    momento: Momento;
    nivel_riesgo_real: string | null;
    prediccion: Prediccion | null;
  };

export type EstudianteDetalle = Estudiante & { registros: Registro[] };

export type Resumen = Record<Grupo, Record<Nivel, number>>;

export type Excluido = { fila: number; codigo: string | null; motivo: string };

export type ResultadoImportacion = {
  procesados: number;
  excluidos: number;
  detalle_excluidos: Excluido[];
};

type Metrica = { media: number; desviacion: number };

export type InfoModelo = {
  version: string;
  entrenado: string;
  fuente_datos: string;
  features: string[];
  n_entrenamiento: number;
  metricas: {
    cv_5x5_sobre_reales?: Record<string, Metrica>;
    holdout_20pct?: Record<string, unknown> & {
      matriz_confusion?: { valores: number[][] };
    };
  };
  umbrales: { medio: number; alto: number };
  aumento: { metodo: string; factor: number } | null;
  aviso: string | null;
};
