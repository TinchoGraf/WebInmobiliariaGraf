from datetime import datetime
from sqlalchemy import String, Integer, Float, Text, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column
from database import Base
import enum


class OperacionEnum(str, enum.Enum):
    venta   = "venta"
    alquiler = "alquiler"


class TipoEnum(str, enum.Enum):
    casa         = "casa"
    departamento = "departamento"
    ph           = "ph"
    local        = "local"
    terreno      = "terreno"
    oficina      = "oficina"


class Propiedad(Base):
    __tablename__ = "propiedades"

    id:          Mapped[int]   = mapped_column(Integer, primary_key=True, index=True)
    titulo:      Mapped[str]   = mapped_column(String(200), nullable=False)
    tipo:        Mapped[str]   = mapped_column(String(50), nullable=False)
    operacion:   Mapped[str]   = mapped_column(String(20), nullable=False)
    precio:      Mapped[float] = mapped_column(Float, nullable=False)
    moneda:      Mapped[str]   = mapped_column(String(3), default="USD")
    ubicacion:   Mapped[str]   = mapped_column(String(300), nullable=True)
    barrio:      Mapped[str]   = mapped_column(String(100), nullable=True)
    descripcion: Mapped[str]   = mapped_column(Text, nullable=True)
    dormitorios: Mapped[int]   = mapped_column(Integer, nullable=True)
    banos:       Mapped[int]   = mapped_column(Integer, nullable=True)
    m2:          Mapped[float] = mapped_column(Float, nullable=True)
    lat:         Mapped[float] = mapped_column(Float, nullable=True)
    lng:         Mapped[float] = mapped_column(Float, nullable=True)
    imagen:      Mapped[str]   = mapped_column(String(500), nullable=True)
    activa:      Mapped[bool]  = mapped_column(default=True)
    creada_en:   Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Contacto(Base):
    __tablename__ = "contactos"

    id:        Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre:    Mapped[str] = mapped_column(String(100))
    apellido:  Mapped[str] = mapped_column(String(100))
    email:     Mapped[str] = mapped_column(String(200))
    telefono:  Mapped[str] = mapped_column(String(30), nullable=True)
    interes:   Mapped[str] = mapped_column(String(50), nullable=True)
    mensaje:   Mapped[str] = mapped_column(Text)
    leido:     Mapped[bool] = mapped_column(default=False)
    creado_en: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
