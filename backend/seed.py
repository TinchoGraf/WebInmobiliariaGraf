"""Carga propiedades de ejemplo en Olavarria."""
import json
from database import init_db, SessionLocal
from models import Propiedad

SEED_DATA = [
    dict(
        titulo="Casa familiar en el centro",
        descripcion="Amplia casa de tres dormitorios en pleno centro. Cochera, jardin y parrilla. A metros de la plaza principal.",
        operacion="venta", tipo="casa", antiguedad="1_10",
        precio=95000, moneda="USD",
        direccion="Rivadavia 1250, Olavarria", barrio="Centro",
        lat=-36.8927, lng=-60.3224, imagenes="[]",
    ),
    dict(
        titulo="Departamento a estrenar en San Martin",
        descripcion="Luminoso departamento de dos dormitorios a estrenar. Piso 3 con balcon y vista despejada. Edificio con amenities.",
        operacion="alquiler", tipo="departamento", antiguedad="a_estrenar",
        precio=320000, moneda="ARS",
        direccion="San Martin 455, Olavarria", barrio="Centro",
        lat=-36.8952, lng=-60.3190, imagenes="[]",
    ),
    dict(
        titulo="Casa esquina en Barrio Union",
        descripcion="Propiedad en esquina ideal para reformar. Gran terreno de 360 m2, todos los servicios. Muy buena ubicacion.",
        operacion="venta", tipo="casa", antiguedad="mas_20",
        precio=42000, moneda="USD",
        direccion="Av. del Trabajo 840, Olavarria", barrio="Barrio Union",
        lat=-36.9020, lng=-60.3310, imagenes="[]",
    ),
    dict(
        titulo="Terreno residencial zona norte",
        descripcion="Terreno plano de 600 m2 en zona residencial en crecimiento. Cuenta con agua, luz y cloacas. Apto banco hipotecario.",
        operacion="venta", tipo="terreno", antiguedad=None,
        precio=18000, moneda="USD",
        direccion="Calle 12 y Av. Colon, Olavarria", barrio="Zona Norte",
        lat=-36.8780, lng=-60.3150, imagenes="[]",
        dimension_m2=600.0,
    ),
    dict(
        titulo="Local comercial sobre Rivadavia",
        descripcion="Local en planta baja sobre peatonal de alta circulacion. 60 m2, bano independiente y deposito trasero. Llave en mano.",
        operacion="alquiler", tipo="comercial", antiguedad="1_10",
        precio=280000, moneda="ARS",
        direccion="Rivadavia 550, Olavarria", barrio="Centro",
        lat=-36.8940, lng=-60.3200, imagenes="[]",
    ),
    dict(
        titulo="Casa moderna a estrenar en Villa Fortabat",
        descripcion="Casa de diseno contemporaneo a estrenar. Tres dormitorios en suite, garaje doble, piscina y quincho cubierto.",
        operacion="venta", tipo="casa", antiguedad="a_estrenar",
        precio=130000, moneda="USD",
        direccion="Los Aromos 320, Olavarria", barrio="Villa Fortabat",
        lat=-36.8850, lng=-60.3070, imagenes="[]",
    ),
    dict(
        titulo="Departamento equipado para estadias cortas",
        descripcion="Totalmente equipado: WiFi de alta velocidad, Smart TV 55\", ropa de cama, cocina completa y estacionamiento incluido. Por dia o semana.",
        operacion="alquiler_temp", tipo="departamento", antiguedad="a_estrenar",
        precio=15000, moneda="ARS",
        direccion="Espana 320, Olavarria", barrio="Centro",
        lat=-36.8910, lng=-60.3240, imagenes="[]",
    ),
    dict(
        titulo="Terreno en barrio privado Parque",
        descripcion="Terreno de 400 m2 dentro de barrio cerrado con porteria 24 h, acceso a areas verdes, SUM y cancha de tenis.",
        operacion="venta", tipo="terreno", antiguedad=None,
        precio=22000, moneda="USD",
        direccion="Sarmiento 1800, Olavarria", barrio="Barrio Parque",
        lat=-36.8890, lng=-60.3340, imagenes="[]",
        dimension_m2=400.0,
    ),
    dict(
        titulo="Local amplio sobre Av. Colon",
        descripcion="Espacioso local de 120 m2 con vidriera doble, deposito trasero y dos banos. Ideal supermercado, ferreteria o salon de ventas.",
        operacion="alquiler", tipo="comercial", antiguedad="1_10",
        precio=450000, moneda="ARS",
        direccion="Av. Colon 1340, Olavarria", barrio="Palermo Chico",
        lat=-36.8870, lng=-60.3180, imagenes="[]",
    ),
    dict(
        titulo="Casa con pileta en Palermo Chico",
        descripcion="Coqueta casa de 4 dormitorios, piscina climatizada, quincho con parrilla y amplio jardin. Excelente estado de conservacion.",
        operacion="venta", tipo="casa", antiguedad="1_10",
        precio=115000, moneda="USD",
        direccion="Los Jazmines 456, Olavarria", barrio="Palermo Chico",
        lat=-36.8862, lng=-60.3060, imagenes="[]",
    ),
    dict(
        titulo="Chacra productiva en las afueras de Olavarria",
        descripcion="50 hectareas con casa principal de 4 ambientes, galpones, aguada natural y molino en funcionamiento. Acceso por camino consolidado. Ideal tambo o agricultura.",
        operacion="venta", tipo="chacra_campo", antiguedad="mas_20",
        precio=280000, moneda="USD",
        direccion="Ruta 51 km 12, Olavarria", barrio=None,
        lat=-36.9500, lng=-60.4200, imagenes="[]",
        dimension_m2=500000.0,
        poligono_zona=json.dumps([
            [-36.9400, -60.4300],
            [-36.9400, -60.4100],
            [-36.9600, -60.4100],
            [-36.9600, -60.4300],
            [-36.9400, -60.4300],
        ]),
    ),
    dict(
        titulo="Campo mixto con laguna — ideal ganaderia",
        descripcion="80 hectareas con laguna interior, alambrados en buen estado y dos casas de personal. Pasturas naturales y artificiales. Gran potencial ganadero.",
        operacion="venta", tipo="chacra_campo", antiguedad=None,
        precio=420000, moneda="USD",
        direccion="Camino vecinal s/n, partido de Olavarria", barrio=None,
        lat=-37.0100, lng=-60.3800, imagenes="[]",
        dimension_m2=800000.0,
        poligono_zona=json.dumps([
            [-37.0000, -60.3900],
            [-37.0000, -60.3700],
            [-37.0200, -60.3700],
            [-37.0200, -60.3900],
            [-37.0000, -60.3900],
        ]),
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
