from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text
from database import Base


class Propiedad(Base):
    __tablename__ = "propiedades"

    id             = Column(Integer, primary_key=True, index=True, autoincrement=True)
    titulo         = Column(String(200), nullable=False)
    descripcion    = Column(Text, nullable=True)
    operacion      = Column(String(20), nullable=False)   # venta | alquiler | alquiler_temp
    tipo           = Column(String(30), nullable=False)    # casa | departamento | terreno | lote | local
    estado         = Column(String(20), nullable=True)     # a_estrenar | con_uso | a_reciclar
    precio         = Column(Float, nullable=False)
    moneda         = Column(String(3), default="USD")
    direccion      = Column(String(300), nullable=False)
    barrio         = Column(String(100), nullable=True)
    lat            = Column(Float, nullable=True)
    lng            = Column(Float, nullable=True)
    imagenes       = Column(Text, default="[]")            # JSON string: list of image paths
    activa         = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
