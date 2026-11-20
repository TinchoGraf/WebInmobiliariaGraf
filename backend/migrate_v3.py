"""Migración v3: borradores ("pendiente de finalizar").

Quita NOT NULL de titulo, operacion, tipo, precio y direccion para poder guardar propiedades
incompletas con estado_operacion = "borrador". Es la misma migración que corre sola al arrancar
el backend (init_db), así que normalmente NO hace falta ejecutarla a mano.

Uso manual (usa DATABASE_URL del entorno / .env, igual que el backend):
    python migrate_v3.py

Idempotente: si ya se aplicó, no hace nada. No borra ni modifica datos.
"""
from dotenv import load_dotenv

load_dotenv()

from database import engine, migrar_v3_borradores  # noqa: E402  (después de cargar .env)


def main():
    print(f"=== Migración v3 ({engine.dialect.name}) ===")
    cambiadas = migrar_v3_borradores(engine)
    if cambiadas:
        print(f"  OK: columnas ahora opcionales: {', '.join(cambiadas)}")
    else:
        print("  ~ nada que hacer (ya estaba aplicada o la tabla no existe)")
    print("=== Migración v3 completada ===")


if __name__ == "__main__":
    main()
