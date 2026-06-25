"""Carga 10 propiedades de ejemplo en Olavarria."""
from database import init_db, SessionLocal
from models import Propiedad

SEED_DATA = [
    dict(
        titulo="Casa familiar en el centro",
        descripcion="Amplia casa de tres dormitorios en pleno centro. Cochera, jardin y parrilla. A metros de la plaza principal.",
        operacion="venta", tipo="casa", estado="con_uso",
        precio=95000, moneda="USD",
        direccion="Rivadavia 1250, Olavarria", barrio="Centro",
        lat=-36.8927, lng=-60.3224, imagenes="[]",
    ),
    dict(
        titulo="Departamento a estrenar en San Martin",
        descripcion="Luminoso departamento de dos dormitorios a estrenar. Piso 3 con balcon y vista despejada. Edificio con amenities.",
        operacion="alquiler", tipo="departamento", estado="a_estrenar",
        precio=320000, moneda="ARS",
        direccion="San Martin 455, Olavarria", barrio="Centro",
        lat=-36.8952, lng=-60.3190, imagenes="[]",
    ),
    dict(
        titulo="Casa esquina en Barrio Union",
        descripcion="Propiedad en esquina ideal para reformar. Gran terreno de 360 m2, todos los servicios. Muy buena ubicacion.",
        operacion="venta", tipo="casa", estado="a_reciclar",
        precio=42000, moneda="USD",
        direccion="Av. del Trabajo 840, Olavarria", barrio="Barrio Union",
        lat=-36.9020, lng=-60.3310, imagenes="[]",
    ),
    dict(
        titulo="Terreno residencial zona norte",
        descripcion="Terreno plano de 600 m2 en zona residencial en crecimiento. Cuenta con agua, luz y cloacas. Apto banco hipotecario.",
        operacion="venta", tipo="terreno", estado=None,
        precio=18000, moneda="USD",
        direccion="Calle 12 y Av. Colon, Olavarria", barrio="Zona Norte",
        lat=-36.8780, lng=-60.3150, imagenes="[]",
    ),
    dict(
        titulo="Local comercial sobre Rivadavia",
        descripcion="Local en planta baja sobre peatonal de alta circulacion. 60 m2, bano independiente y deposito trasero. Llave en mano.",
        operacion="alquiler", tipo="local", estado="con_uso",
        precio=280000, moneda="ARS",
        direccion="Rivadavia 550, Olavarria", barrio="Centro",
        lat=-36.8940, lng=-60.3200, imagenes="[]",
    ),
    dict(
        titulo="Casa moderna a estrenar en Villa Fortabat",
        descripcion="Casa de diseno contemporaneo a estrenar. Tres dormitorios en suite, garaje doble, piscina y quincho cubierto.",
        operacion="venta", tipo="casa", estado="a_estrenar",
        precio=130000, moneda="USD",
        direccion="Los Aromos 320, Olavarria", barrio="Villa Fortabat",
        lat=-36.8850, lng=-60.3070, imagenes="[]",
    ),
    dict(
        titulo="Departamento equipado para estadias cortas",
        descripcion="Totalmente equipado: WiFi de alta velocidad, Smart TV 55\", ropa de cama, cocina completa y estacionamiento incluido. Por dia o semana.",
        operacion="alquiler_temp", tipo="departamento", estado="a_estrenar",
        precio=15000, moneda="ARS",
        direccion="Espana 320, Olavarria", barrio="Centro",
        lat=-36.8910, lng=-60.3240, imagenes="[]",
    ),
    dict(
        titulo="Lote en barrio privado Parque",
        descripcion="Lote de 400 m2 dentro de barrio cerrado con porteria 24 h, acceso a areas verdes, SUM y cancha de tenis.",
        operacion="venta", tipo="lote", estado=None,
        precio=22000, moneda="USD",
        direccion="Sarmiento 1800, Olavarria", barrio="Barrio Parque",
        lat=-36.8890, lng=-60.3340, imagenes="[]",
    ),
    dict(
        titulo="Local amplio sobre Av. Colon",
        descripcion="Espacioso local de 120 m2 con vidriera doble, deposito trasero y dos banos. Ideal supermercado, ferreteria o salon de ventas.",
        operacion="alquiler", tipo="local", estado="con_uso",
        precio=450000, moneda="ARS",
        direccion="Av. Colon 1340, Olavarria", barrio="Palermo Chico",
        lat=-36.8870, lng=-60.3180, imagenes="[]",
    ),
    dict(
        titulo="Casa con pileta en Palermo Chico",
        descripcion="Coqueta casa de 4 dormitorios, piscina climatizada, quincho con parrilla y amplio jardin. Excelente estado de conservacion.",
        operacion="venta", tipo="casa", estado="con_uso",
        precio=115000, moneda="USD",
        direccion="Los Jazmines 456, Olavarria", barrio="Palermo Chico",
        lat=-36.8862, lng=-60.3060, imagenes="[]",
    ),
]


def main():
    init_db()
    with SessionLocal() as db:
        count = db.query(Propiedad).count()
        if count > 0:
            print(f"Ya hay {count} propiedades. Borra inmobiliaria.db para re-sembrar.")
            return
        for data in SEED_DATA:
            db.add(Propiedad(**data))
        db.commit()
    print(f"OK: {len(SEED_DATA)} propiedades de Olavarria cargadas.")


if __name__ == "__main__":
    main()
