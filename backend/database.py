import os
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./inmobiliaria.db")

# Render (y otros proveedores) entregan la URL con el esquema viejo "postgres://",
# que SQLAlchemy 1.4+ ya no acepta - hay que normalizarlo a "postgresql://".
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Sin "+driver", SQLAlchemy elige el driver por defecto según su versión (2.1 usa psycopg v3,
# que no instalamos). Forzamos psycopg2 (psycopg2-binary en requirements.txt).
# Si la URL ya trae un driver explícito (postgresql+algo://), se respeta.
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from models import Propiedad  # noqa: ensure table is registered with Base.metadata
    Base.metadata.create_all(bind=engine)
    _migrar_columnas_nuevas()
    migrar_v3_borradores()


# Columnas que eran NOT NULL y pasan a aceptar NULL para poder guardar borradores incompletos.
COLUMNAS_OPCIONALES_V3 = ("titulo", "operacion", "tipo", "precio", "direccion")


def migrar_v3_borradores(eng=None, log=print) -> list[str]:
    """Migración v3 (borradores): quita NOT NULL de COLUMNAS_OPCIONALES_V3.

    Idempotente: solo toca las columnas que todavía son NOT NULL. No borra ni modifica datos.
    El valor "borrador" de estado_operacion no requiere cambios de esquema (es un VARCHAR libre).
    - PostgreSQL: ALTER TABLE ... ALTER COLUMN ... DROP NOT NULL (una sentencia por columna).
    - SQLite: no soporta ALTER COLUMN, así que reconstruye la tabla (crear nueva con el esquema
      del modelo, copiar filas, borrar la vieja, renombrar) dentro de una transacción.
    Devuelve la lista de columnas modificadas (vacía si no había nada que hacer).
    """
    eng = eng or engine
    inspector = inspect(eng)
    if "propiedades" not in inspector.get_table_names():
        return []
    cols = {c["name"]: c for c in inspector.get_columns("propiedades")}
    pendientes = [n for n in COLUMNAS_OPCIONALES_V3 if n in cols and not cols[n]["nullable"]]
    if not pendientes:
        return []

    dialecto = eng.dialect.name
    if dialecto == "postgresql":
        with eng.begin() as conn:
            for nombre in pendientes:
                conn.execute(text(f'ALTER TABLE propiedades ALTER COLUMN "{nombre}" DROP NOT NULL'))
    elif dialecto == "sqlite":
        _reconstruir_tabla_sqlite(eng, list(cols))
    else:
        raise RuntimeError(f"migrar_v3_borradores: dialecto no soportado ({dialecto})")
    log(f"[migración v3] columnas ahora opcionales ({dialecto}): {', '.join(pendientes)}")
    return pendientes


def _reconstruir_tabla_sqlite(eng, columnas_existentes: list[str]) -> None:
    from sqlalchemy.schema import CreateTable
    from models import Propiedad

    tabla = Propiedad.__table__
    temporal = tabla.to_metadata(Base.metadata.__class__(), name="propiedades__v3")
    comunes = [c.name for c in tabla.columns if c.name in columnas_existentes]
    lista = ", ".join(f'"{c}"' for c in comunes)
    with eng.begin() as conn:
        conn.exec_driver_sql("PRAGMA foreign_keys=OFF")
        conn.exec_driver_sql("DROP TABLE IF EXISTS propiedades__v3")
        conn.execute(CreateTable(temporal))
        conn.exec_driver_sql(f"INSERT INTO propiedades__v3 ({lista}) SELECT {lista} FROM propiedades")
        n_old = conn.exec_driver_sql("SELECT COUNT(*) FROM propiedades").scalar()
        n_new = conn.exec_driver_sql("SELECT COUNT(*) FROM propiedades__v3").scalar()
        if n_old != n_new:
            raise RuntimeError(f"migración v3: se copiaron {n_new} de {n_old} filas, se cancela")
        conn.exec_driver_sql("DROP TABLE propiedades")  # also drops its indexes
        conn.exec_driver_sql("ALTER TABLE propiedades__v3 RENAME TO propiedades")
        for idx in tabla.indexes:
            idx.create(conn, checkfirst=True)


def _migrar_columnas_nuevas():
    """Agrega columnas nuevas a tablas ya existentes (create_all no las modifica)."""
    columnas_nuevas = {
        "cantidad_pisos": "INTEGER",
    }
    inspector = inspect(engine)
    existentes = {col["name"] for col in inspector.get_columns("propiedades")}
    faltantes = {nombre: tipo for nombre, tipo in columnas_nuevas.items() if nombre not in existentes}
    if not faltantes:
        return
    with engine.begin() as conn:
        for nombre, tipo in faltantes.items():
            conn.execute(text(f"ALTER TABLE propiedades ADD COLUMN {nombre} {tipo}"))
