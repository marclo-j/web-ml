"""Base de datos (docs/ARQUITECTURA.md → Modelo de datos).

En producción es PostgreSQL en Neon (DATABASE_URL con el host -pooler); en
desarrollo y pruebas, SQLite. El esquema de producción se crea con
sql/001_esquema.sql; create_all solo se usa con SQLite.
"""

import uuid
from collections.abc import Iterator
from datetime import UTC, datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    Uuid,
    create_engine,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
    relationship,
    sessionmaker,
)


def _ahora() -> datetime:
    return datetime.now(UTC)


class Base(DeclarativeBase):
    pass


class Usuario(Base):
    """Personal de la IE que usa la web (tutor o directivo). Solo correo, rol y
    el hash de la contraseña (Argon2id); nunca la contraseña."""

    __tablename__ = "usuarios"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(254), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    rol: Mapped[str] = mapped_column(String(16))
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_ahora
    )

    __table_args__ = (
        CheckConstraint("rol IN ('tutor', 'directivo')", name="ck_usuarios_rol"),
    )


class Estudiante(Base):
    __tablename__ = "estudiantes"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    codigo: Mapped[str] = mapped_column(String(16), unique=True)
    grado: Mapped[int] = mapped_column(Integer)
    seccion: Mapped[str] = mapped_column(String(8))
    grupo: Mapped[str] = mapped_column(String(16))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_ahora
    )

    registros: Mapped[list["Registro"]] = relationship(
        back_populates="estudiante", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("grado IN (3, 4)", name="ck_estudiantes_grado"),
        CheckConstraint(
            "grupo IN ('control', 'experimental')", name="ck_estudiantes_grupo"
        ),
    )


class Registro(Base):
    """Datos crudos de un alumno en un momento (pre/post) + indicadores calculados."""

    __tablename__ = "registros"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    estudiante_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("estudiantes.id", ondelete="CASCADE")
    )
    momento: Mapped[str] = mapped_column(String(8))
    suma_notas: Mapped[float] = mapped_column(Float)
    n_notas: Mapped[int] = mapped_column(Integer)
    dias_asistidos: Mapped[int] = mapped_column(Integer)
    dias_programados: Mapped[int] = mapped_column(Integer)
    reuniones_asistidas: Mapped[int] = mapped_column(Integer)
    reuniones_programadas: Mapped[int] = mapped_column(Integer)
    promedio: Mapped[float] = mapped_column(Float)
    pct_asistencia: Mapped[float] = mapped_column(Float)
    pct_reuniones: Mapped[float] = mapped_column(Float)
    # Desenlace efectivo al cierre del periodo (D2); se llena en la Fase 7
    nivel_riesgo_real: Mapped[str | None] = mapped_column(String(16), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_ahora
    )

    estudiante: Mapped[Estudiante] = relationship(back_populates="registros")
    prediccion: Mapped["Prediccion | None"] = relationship(
        back_populates="registro", cascade="all, delete-orphan", uselist=False
    )

    __table_args__ = (
        UniqueConstraint(
            "estudiante_id", "momento", name="uq_registros_estudiante_momento"
        ),
        CheckConstraint("momento IN ('pre', 'post')", name="ck_registros_momento"),
    )


class Prediccion(Base):
    __tablename__ = "predicciones"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    registro_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("registros.id", ondelete="CASCADE"), unique=True
    )
    probabilidad: Mapped[float] = mapped_column(Float)
    nivel_riesgo: Mapped[str] = mapped_column(String(8))
    version_modelo: Mapped[str] = mapped_column(String(32))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_ahora
    )

    registro: Mapped[Registro] = relationship(back_populates="prediccion")

    __table_args__ = (
        CheckConstraint(
            "nivel_riesgo IN ('bajo', 'medio', 'alto')", name="ck_predicciones_nivel"
        ),
    )


def crear_sesiones(database_url: str) -> sessionmaker[Session]:
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+psycopg://", 1)
    elif database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    opciones = {}
    if database_url.startswith("sqlite"):
        opciones["connect_args"] = {"check_same_thread": False}
        if database_url in ("sqlite://", "sqlite:///:memory:"):
            from sqlalchemy.pool import StaticPool

            opciones["poolclass"] = StaticPool
    else:
        opciones["pool_pre_ping"] = True
    motor = create_engine(database_url, **opciones)
    if motor.dialect.name == "sqlite":
        Base.metadata.create_all(motor)
    return sessionmaker(motor, expire_on_commit=False)


def sesion_desde(fabrica: sessionmaker[Session]) -> Iterator[Session]:
    with fabrica() as sesion:
        yield sesion
