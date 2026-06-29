"""Migración: estado→antiguedad, nuevas columnas, tabla mensajes."""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "inmobiliaria.db"

ESTADO_MAP = {
    "a_estrenar": "a_estrenar",
    "con_uso":    "1_10",
    "a_reciclar": "mas_20",
}


def column_exists(conn, table, column):
    cursor = conn.execute(f"PRAGMA table_info({table})")
    return any(row[1] == column for row in cursor.fetchall())


def main():
    conn = sqlite3.connect(DB_PATH)

    print("=== Migración ===")

    # --- columnas nuevas en propiedades ---
    if not column_exists(conn, "propiedades", "antiguedad"):
        conn.execute("ALTER TABLE propiedades ADD COLUMN antiguedad TEXT")
        print("  + columna 'antiguedad' agregada")
    else:
        print("  ~ columna 'antiguedad' ya existe")

    if not column_exists(conn, "propiedades", "poligono_zona"):
        conn.execute("ALTER TABLE propiedades ADD COLUMN poligono_zona TEXT")
        print("  + columna 'poligono_zona' agregada")
    else:
        print("  ~ columna 'poligono_zona' ya existe")

    if not column_exists(conn, "propiedades", "dimension_m2"):
        conn.execute("ALTER TABLE propiedades ADD COLUMN dimension_m2 REAL")
        print("  + columna 'dimension_m2' agregada")
    else:
        print("  ~ columna 'dimension_m2' ya existe")

    # --- mapear estado → antiguedad ---
    if column_exists(conn, "propiedades", "estado"):
        for old, new in ESTADO_MAP.items():
            conn.execute(
                "UPDATE propiedades SET antiguedad = ? WHERE estado = ? AND (antiguedad IS NULL OR antiguedad = '')",
                (new, old),
            )
        print("  OK: valores de 'estado' mapeados a 'antiguedad'")

        try:
            conn.execute("ALTER TABLE propiedades DROP COLUMN estado")
            print("  - columna 'estado' eliminada")
        except sqlite3.OperationalError:
            print("  ! columna 'estado' no eliminable en esta version de SQLite (se mantiene)")
    else:
        print("  ~ columna 'estado' no existe (ya migrada)")

    # --- tabla mensajes ---
    conn.execute("""
        CREATE TABLE IF NOT EXISTS mensajes (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre   TEXT    NOT NULL,
            email    TEXT    NOT NULL,
            telefono TEXT,
            mensaje  TEXT    NOT NULL,
            leido    INTEGER NOT NULL DEFAULT 0,
            fecha    TEXT    NOT NULL DEFAULT (datetime('now'))
        )
    """)
    print("  OK: tabla 'mensajes' creada/verificada")

    conn.commit()
    conn.close()
    print("=== Migración completada ===")


if __name__ == "__main__":
    main()
