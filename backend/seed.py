"""Carga las 8 propiedades de ejemplo de Olavarria en la base de datos."""
import asyncio
from database import init_db, AsyncSessionLocal
from models import Propiedad

SEED_DATA = [
    dict(
        titulo="Casa familiar en el centro",
        tipo="casa", operacion="venta", estado="con_uso",
        precio=95000, moneda="USD",
        ubicacion="Rivadavia 1250, Olavarria", barrio="Centro",
        descripcion="Amplia casa de tres dormitorios en pleno centro. Cochera, jardin y parrilla.",
        dormitorios=3, banos=2, m2=180,
        lat=-36.8927, lng=-60.3224,
    ),
    dict(
        titulo="Departamento a estrenar en San Martin",
        tipo="departamento", operacion="alquiler", estado="a_estrenar",
        precio=320000, moneda="ARS",
        ubicacion="San Martin 455, Olavarria", barrio="Centro",
        descripcion="Luminoso departamento de dos dormitorios a estrenar. Piso 3, balcon con vista.",
        dormitorios=2, banos=1, m2=68,
        lat=-36.8952, lng=-60.3190,
    ),
    dict(
        titulo="Casa esquina en Barrio Union",
        tipo="casa", operacion="venta", estado="a_reciclar",
        precio=42000, moneda="USD",
        ubicacion="Av. del Trabajo 840, Olavarria", barrio="Barrio Union",
        descripcion="Propiedad en esquina ideal para reformar. Gran terreno de 360 m2, todos los servicios.",
        dormitorios=3, banos=1, m2=120,
        lat=-36.9020, lng=-60.3310,
    ),
    dict(
        titulo="Terreno residencial zona norte",
        tipo="terreno", operacion="venta", estado=None,
        precio=18000, moneda="USD",
        ubicacion="Calle 12 y Av. Colon, Olavarria", barrio="Zona Norte",
        descripcion="Terreno plano de 600 m2 en zona residencial en crecimiento. Agua, luz y cloacas.",
        dormitorios=None, banos=None, m2=600,
        lat=-36.8780, lng=-60.3150,
    ),
    dict(
        titulo="Local comercial sobre Rivadavia",
        tipo="local", operacion="alquiler", estado="con_uso",
        precio=280000, moneda="ARS",
        ubicacion="Rivadavia 550, Olavarria", barrio="Centro",
        descripcion="Local en planta baja sobre peatonal de alta circulacion. 60 m2, bano y deposito.",
        dormitorios=None, banos=1, m2=60,
        lat=-36.8940, lng=-60.3200,
    ),
    dict(
        titulo="Casa moderna a estrenar en Villa Fortabat",
        tipo="casa", operacion="venta", estado="a_estrenar",
        precio=130000, moneda="USD",
        ubicacion="Los Aromos 320, Olavarria", barrio="Villa Fortabat",
        descripcion="Casa de diseno contemporaneo a estrenar. 3 dormitorios en suite, garaje doble y piscina.",
        dormitorios=3, banos=3, m2=210,
        lat=-36.8850, lng=-60.3070,
    ),
    dict(
        titulo="Departamento equipado para estadias cortas",
        tipo="departamento", operacion="alquiler_temporario", estado="a_estrenar",
        precio=15000, moneda="ARS",
        ubicacion="Espana 320, Olavarria", barrio="Centro",
        descripcion="Departamento totalmente equipado: WiFi, Smart TV, ropa de cama y cocina completa. Por dia.",
        dormitorios=1, banos=1, m2=48,
        lat=-36.8910, lng=-60.3240,
    ),
    dict(
        titulo="Lote en barrio privado Parque",
        tipo="lote", operacion="venta", estado=None,
        precio=22000, moneda="USD",
        ubicacion="Sarmiento 1800, Olavarria", barrio="Barrio Parque",
        descripcion="Lote de 400 m2 dentro de barrio con porteria 24 h. Acceso a areas verdes y SUM.",
        dormitorios=None, banos=None, m2=400,
        lat=-36.8890, lng=-60.3340,
    ),
]


async def main():
    await init_db()
    async with AsyncSessionLocal() as session:
        for data in SEED_DATA:
            prop = Propiedad(**data)
            session.add(prop)
        await session.commit()
    print(f"OK: {len(SEED_DATA)} propiedades de Olavarria cargadas.")


if __name__ == "__main__":
    asyncio.run(main())
