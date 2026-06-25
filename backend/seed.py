"""Carga datos de ejemplo en la base de datos."""
import asyncio
from database import init_db, AsyncSessionLocal
from models import Propiedad

SEED_DATA = [
    dict(titulo="Casa moderna en Palermo",           tipo="casa",         operacion="venta",    precio=280000, moneda="USD", ubicacion="Palermo, CABA",    barrio="Palermo",    dormitorios=4, banos=3, m2=220, lat=-34.5882, lng=-58.4315),
    dict(titulo="Departamento luminoso en Recoleta", tipo="departamento", operacion="alquiler", precio=650000, moneda="ARS", ubicacion="Recoleta, CABA",   barrio="Recoleta",   dormitorios=2, banos=1, m2=75,  lat=-34.5888, lng=-58.3932),
    dict(titulo="PH amplio en Villa Crespo",         tipo="ph",           operacion="venta",    precio=145000, moneda="USD", ubicacion="Villa Crespo, CABA",barrio="Villa Crespo",dormitorios=3, banos=2, m2=130, lat=-34.6001, lng=-58.4388),
    dict(titulo="Loft con terraza en San Telmo",     tipo="departamento", operacion="alquiler", precio=480000, moneda="ARS", ubicacion="San Telmo, CABA",   barrio="San Telmo",  dormitorios=1, banos=1, m2=55,  lat=-34.6215, lng=-58.3726),
    dict(titulo="Casa con pileta en Belgrano",       tipo="casa",         operacion="venta",    precio=420000, moneda="USD", ubicacion="Belgrano, CABA",    barrio="Belgrano",   dormitorios=5, banos=4, m2=350, lat=-34.5608, lng=-58.4552),
    dict(titulo="Departamento en Caballito",         tipo="departamento", operacion="venta",    precio=98000,  moneda="USD", ubicacion="Caballito, CABA",   barrio="Caballito",  dormitorios=2, banos=1, m2=62,  lat=-34.6186, lng=-58.4404),
]


async def main():
    await init_db()
    async with AsyncSessionLocal() as session:
        for data in SEED_DATA:
            prop = Propiedad(**data)
            session.add(prop)
        await session.commit()
    print(f"✓ {len(SEED_DATA)} propiedades cargadas.")


if __name__ == "__main__":
    asyncio.run(main())
