"""Migración v2: superficies, estado de la propiedad, destacadas y estado de operación."""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "inmobiliaria.db"

NUEVAS_COLUMNAS = [
    ("superficie_cubierta",    "REAL"),
    ("superficie_descubierta", "REAL"),
    ("superficie_total",       "REAL"),
    ("estado_propiedad",       "TEXT"),
    ("destacada",              "INTEGER NOT NULL DEFAULT 0"),
    ("estado_operacion",       "TEXT NOT NULL DEFAULT 'activa'"),
    ("precio_venta_final",     "REAL"),
    ("moneda_venta_final",     "TEXT"),
]


def column_exists(conn, table, column):
    cursor = conn.execute(f"PRAGMA table_info({table})")
    return any(row[1] == column for row in cursor.fetchall())


def main():
    conn = sqlite3.connect(DB_PATH)

    print("=== Migración v2 ===")

    for nombre, tipo in NUEVAS_COLUMNAS:
        if not column_exists(conn, "propiedades", nombre):
            conn.execute(f"ALTER TABLE propiedades ADD COLUMN {nombre} {tipo}")
            print(f"  + columna '{nombre}' agregada")
        else:
            print(f"  ~ columna '{nombre}' ya existe")

    # Propiedades existentes: activa=True -> estado_operacion='activa'; activa=False -> 'pausada'
    conn.execute("""
        UPDATE propiedades
        SET estado_operacion = CASE WHEN activa = 1 THEN 'activa' ELSE 'pausada' END
        WHERE estado_operacion IS NULL OR estado_operacion = ''
    """)
    print("  OK: 'estado_operacion' inicializado a partir de 'activa' para filas existentes")

    conn.commit()
    conn.close()
    print("=== Migración v2 completada ===")


if __name__ == "__main__":
    main()
