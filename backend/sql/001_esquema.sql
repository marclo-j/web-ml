-- Esquema de producción en Neon (PostgreSQL 16+). Ejecutar una vez en el
-- SQL Editor del proyecto. Debe coincidir con backend/app/db.py.
-- Ningún nombre ni DNI de estudiantes: solo el código anonimizado (Ley N.° 29733).

-- Personal de la IE que usa la web. Solo el hash Argon2id de la contraseña.
-- Se crean con: python -m app.crear_usuario (no hay registro público).
create table if not exists usuarios (
  id uuid primary key default gen_random_uuid(),
  email varchar(254) not null unique,
  password_hash varchar(255) not null,
  rol varchar(16) not null check (rol in ('tutor', 'directivo')),
  activo boolean not null default true,
  created_at timestamptz not null default now()
);

create table if not exists estudiantes (
  id uuid primary key default gen_random_uuid(),
  codigo varchar(16) not null unique,
  grado integer not null check (grado in (3, 4)),
  seccion varchar(8) not null,
  grupo varchar(16) not null check (grupo in ('control', 'experimental')),
  created_at timestamptz not null default now()
);

create table if not exists registros (
  id uuid primary key default gen_random_uuid(),
  estudiante_id uuid not null references estudiantes(id) on delete cascade,
  momento varchar(8) not null check (momento in ('pre', 'post')),
  suma_notas double precision not null,
  n_notas integer not null,
  dias_asistidos integer not null,
  dias_programados integer not null,
  reuniones_asistidas integer not null,
  reuniones_programadas integer not null,
  promedio double precision not null,
  pct_asistencia double precision not null,
  pct_reuniones double precision not null,
  nivel_riesgo_real varchar(16),
  created_at timestamptz not null default now(),
  constraint uq_registros_estudiante_momento unique (estudiante_id, momento)
);

create table if not exists predicciones (
  id uuid primary key default gen_random_uuid(),
  registro_id uuid not null unique references registros(id) on delete cascade,
  probabilidad double precision not null,
  nivel_riesgo varchar(8) not null check (nivel_riesgo in ('bajo', 'medio', 'alto')),
  version_modelo varchar(32) not null,
  created_at timestamptz not null default now()
);
