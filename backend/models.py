from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text
from database import Base


class Propiedad(Base):
    __tablename__ = "propiedades"

    id             = Column(Integer, primary_key=True, index=True, autoincrement=True)
    titulo         = Column(String(200), nullable=False)
    descripcion    = Column(Text, nullable=True)
    operacion      = Column(String(20), nullable=False)   # venta | alquiler | alquiler_temp
    tipo           = Column(String(30), nullable=False)    # casa | departamento | terreno | comercial | chacra_campo | quinta
    antiguedad     = Column(String(20), nullable=True)     # a_estrenar | 1_10 | 10_20 | mas_20
    precio         = Column(Float, nullable=False)
    moneda         = Column(String(3), default="USD")
    direccion      = Column(String(300), nullable=False)
    barrio         = Column(String(100), nullable=True)
    lat            = Column(Float, nullable=True)
    lng            = Column(Float, nullable=True)
    imagenes       = Column(Text, default="[]")            # JSON string: list of image paths
    activa         = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    poligono_zona  = Column(Text, nullable=True)           # JSON string: [[lat, lng], ...] para chacra_campo / quinta
    dimension_m2   = Column(Float, nullable=True)          # superficie del terreno en m²


class Mensaje(Base):
    __tablename__ = "mensajes"

    id       = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre   = Column(String(200), nullable=False)
    email    = Column(String(200), nullable=False)
    telefono = Column(String(50), nullable=True)
    mensaje  = Column(Text, nullable=False)
    leido    = Column(Boolean, default=False)
    fecha    = Column(DateTime, default=datetime.utcnow)
