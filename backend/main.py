import json
import logging
import os
import re
import secrets
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated, Optional
from urllib.parse import urlparse

import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, File, HTTPException, Query, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, computed_field, field_validator
from sqlalchemy import or_
from sqlalchemy.orm import Session

from database import get_db, init_db
from models import Mensaje, Propiedad

load_dotenv()

logger = logging.getLogger("leonardograf")

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)

ADMIN_USER = os.getenv("ADMIN_USER")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

if not ADMIN_USER or not ADMIN_PASSWORD:
    raise RuntimeError(
        "❌ ADMIN_USER y ADMIN_PASSWORD deben estar definidos en el archivo .env. "
        "Copiar .env.example como .env y completar los valores."
    )
IMAGES_DIR      = Path(__file__).parent.parent / "assets" / "images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
BACKUP_DIR      = Path(__file__).parent / "backup"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)
MENSAJES_BACKUP = BACKUP_DIR / "mensajes_backup.jsonl"


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Leonardo Graf Propiedades API", version="2.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBasic()
security_opcional = HTTPBasic(auto_error=False)

app.mount("/assets", StaticFiles(directory=str(IMAGES_DIR.parent)), name="assets")


# ── Auth ─────────────────────────────────────────────────────────────────────

def require_auth(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    ok_user = secrets.compare_digest(credentials.username.encode(), ADMIN_USER.encode())
    ok_pass = secrets.compare_digest(credentials.password.encode(), ADMIN_PASSWORD.encode())
    if not (ok_user and ok_pass):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


def credenciales_validas(credentials: Optional[HTTPBasicCredentials]) -> bool:
    if credentials is None:
        return False
    ok_user = secrets.compare_digest(credentials.username.encode(), ADMIN_USER.encode())
    ok_pass = secrets.compare_digest(credentials.password.encode(), ADMIN_PASSWORD.encode())
    return ok_user and ok_pass


def auth_opcional(credentials: Optional[HTTPBasicCredentials] = Depends(security_opcional)) -> bool:
    """True if valid admin credentials were sent. Public endpoints use it to show drafts only to the admin."""
    return credenciales_validas(credentials)


# ── Borradores ───────────────────────────────────────────────────────────────

ESTADO_BORRADOR = "borrador"

# Same required fields the admin form asks for when publishing (label shown to the user)
CAMPOS_OBLIGATORIOS = {
    "titulo":    "título",
    "operacion": "operación",
    "tipo":      "tipo",
    "precio":    "precio",
    "direccion": "dirección",
}


def _getter(obj):
    return obj.get if isinstance(obj, dict) else (lambda k: getattr(obj, k, None))


def calcular_campos_faltantes(obj) -> list[str]:
    """Required fields still empty, as user-facing labels. Works with ORM objects, schemas or dicts."""
    get = _getter(obj)
    faltan = []
    for campo, etiqueta in CAMPOS_OBLIGATORIOS.items():
        v = get(campo)
        if v is None or (isinstance(v, str) and not v.strip()) or (campo == "precio" and v <= 0):
            faltan.append(etiqueta)
    if get("estado_operacion") in ("vendida", "alquilada") and get("precio_venta_final") is None:
        faltan.append("precio final")
    return faltan


def validar_publicable(obj) -> None:
    """Drafts may be incomplete; any other state must have every required field (422 otherwise)."""
    if (_getter(obj)("estado_operacion") or "activa") == ESTADO_BORRADOR:
        return
    faltan = calcular_campos_faltantes(obj)
    if faltan:
        raise HTTPException(
            status_code=422,
            detail={"mensaje": f"Faltan campos obligatorios: {', '.join(faltan)}", "campos_faltantes": faltan},
        )


def filtrar_borradores(q, incluir: bool):
    if incluir:
        return q
    # NULL-safe: rows without estado_operacion are not drafts
    return q.filter(or_(Propiedad.estado_operacion.is_(None), Propiedad.estado_operacion != ESTADO_BORRADOR))


# ── Schemas ──────────────────────────────────────────────────────────────────

class PropiedadIn(BaseModel):
    # Optional so drafts can be saved incomplete; validar_publicable() enforces them otherwise
    titulo:        Optional[str]   = None
    descripcion:   Optional[str]   = None
    operacion:     Optional[str]   = None
    tipo:          Optional[str]   = None
    antiguedad:    Optional[str]   = None
    precio:        Optional[float] = None
    moneda:        str             = "USD"
    direccion:     Optional[str]   = None
    barrio:        Optional[str]   = None
    lat:           Optional[float] = None
    lng:           Optional[float] = None
    poligono_zona: Optional[str]   = None
    dimension_m2:  Optional[float] = None

    superficie_cubierta:    Optional[float] = None
    superficie_descubierta: Optional[float] = None
    superficie_total:       Optional[float] = None
    estado_propiedad:       Optional[str]   = None
    cantidad_pisos:         Optional[int]   = None
    estado_operacion:       str             = "activa"
    precio_venta_final:     Optional[float] = None
    moneda_venta_final:     Optional[str]   = None


class PropiedadOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:             int
    titulo:         Optional[str]
    descripcion:    Optional[str]
    operacion:      Optional[str]
    tipo:           Optional[str]
    antiguedad:     Optional[str]
    precio:         Optional[float]
    moneda:         Optional[str]
    direccion:      Optional[str]
    barrio:         Optional[str]
    lat:            Optional[float]
    lng:            Optional[float]
    imagenes:       list[str]
    activa:         bool
    fecha_creacion: str
    poligono_zona:  Optional[str]
    dimension_m2:   Optional[float]

    superficie_cubierta:    Optional[float]
    superficie_descubierta: Optional[float]
    superficie_total:       Optional[float]
    estado_propiedad:       Optional[str]
    cantidad_pisos:         Optional[int]
    destacada:               bool
    estado_operacion:        Optional[str]
    precio_venta_final:      Optional[float]
    moneda_venta_final:      Optional[str]

    @computed_field
    @property
    def campos_faltantes(self) -> list[str]:
        """Required fields still incomplete (for drafts: what's missing before publishing)."""
        return calcular_campos_faltantes(self)

    @field_validator("imagenes", mode="before")
    @classmethod
    def parse_imagenes(cls, v):
        if isinstance(v, str):
            return json.loads(v) if v else []
        return v or []

    @field_validator("fecha_creacion", mode="before")
    @classmethod
    def serialize_fecha(cls, v):
        if hasattr(v, "isoformat"):
            return v.isoformat()
        return str(v) if v else ""


class EstadoOperacionIn(BaseModel):
    estado_operacion:   str
    precio_venta_final: Optional[float] = None
    moneda_venta_final: Optional[str]   = None


class ImagenesOrdenIn(BaseModel):
    imagenes: list[Annotated[str, StringConstraints(min_length=1, max_length=1000)]] = Field(max_length=100)


class MensajeIn(BaseModel):
    nombre:   str
    email:    str
    telefono: Optional[str] = None
    mensaje:  str


class MensajeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:       int
    nombre:   str
    email:    str
    telefono: Optional[str]
    mensaje:  str
    leido:    bool
    fecha:    str

    @field_validator("fecha", mode="before")
    @classmethod
    def serialize_fecha(cls, v):
        if hasattr(v, "isoformat"):
            return v.isoformat()
        return str(v) if v else ""


# ── Helpers ──────────────────────────────────────────────────────────────────

def get_prop_or_404(prop_id: int, db: Session, incluir_borrador: bool = True) -> Propiedad:
    prop = db.query(Propiedad).filter(Propiedad.id == prop_id).first()
    if not prop or (not incluir_borrador and prop.estado_operacion == ESTADO_BORRADOR):
        raise HTTPException(status_code=404, detail="Propiedad no encontrada")
    return prop


def get_mensaje_or_404(mensaje_id: int, db: Session) -> Mensaje:
    msg = db.query(Mensaje).filter(Mensaje.id == mensaje_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Mensaje no encontrado")
    return msg


# ── Endpoints: Propiedades ────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/propiedades", response_model=list[PropiedadOut])
def listar_propiedades(
    operacion:        Optional[str]   = Query(None),
    tipo:             Optional[str]   = Query(None),
    antiguedad:       Optional[str]   = Query(None),
    precio_min:       Optional[float] = Query(None),
    precio_max:       Optional[float] = Query(None),
    moneda:           Optional[str]   = Query(None),
    todas:            bool            = Query(False, description="Si True incluye propiedades en cualquier estado de operación (salvo borradores)"),
    estado_operacion: Optional[str]   = Query(None, description="Filtra por estado de operación (activa | pausada | alquilada | vendida | borrador*)"),
    seccion:          Optional[str]   = Query(None, description="'suenos_cumplidos' devuelve solo vendidas/alquiladas con precio_venta_final cargado"),
    incluir_borradores: bool          = Query(False, description="*Incluye borradores. Solo con autenticación (admin)"),
    db: Session = Depends(get_db),
    es_admin: bool = Depends(auth_opcional),
):
    if incluir_borradores and not es_admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="incluir_borradores requiere autenticación",
            headers={"WWW-Authenticate": "Basic"},
        )
    # Drafts never reach the public site, whatever the other filters say
    q = filtrar_borradores(db.query(Propiedad), incluir_borradores)

    if seccion == "suenos_cumplidos":
        q = q.filter(Propiedad.estado_operacion.in_(["vendida", "alquilada"]))
        q = q.filter(Propiedad.precio_venta_final.isnot(None))
    elif todas:
        if estado_operacion:
            q = q.filter(Propiedad.estado_operacion == estado_operacion)
    else:
        q = q.filter(Propiedad.estado_operacion == (estado_operacion or "activa"))

    if operacion:  q = q.filter(Propiedad.operacion == operacion)
    if tipo:       q = q.filter(Propiedad.tipo == tipo)
    if antiguedad:
        vals = [v.strip() for v in antiguedad.split(',') if v.strip()]
        q = q.filter(Propiedad.antiguedad.in_(vals))
    if moneda:                 q = q.filter(Propiedad.moneda == moneda)
    if precio_min is not None: q = q.filter(Propiedad.precio >= precio_min)
    if precio_max is not None: q = q.filter(Propiedad.precio <= precio_max)
    return q.order_by(Propiedad.destacada.desc(), Propiedad.fecha_creacion.desc()).all()


@app.get("/propiedades/{prop_id}", response_model=PropiedadOut)
def obtener_propiedad(prop_id: int, db: Session = Depends(get_db), es_admin: bool = Depends(auth_opcional)):
    # Drafts are never public: 404 unless the request carries valid admin credentials
    return get_prop_or_404(prop_id, db, incluir_borrador=es_admin)


@app.post("/propiedades", response_model=PropiedadOut, status_code=201)
def crear_propiedad(
    datos: PropiedadIn,
    db: Session = Depends(get_db),
    _: str = Depends(require_auth),
):
    validar_publicable(datos.model_dump())
    prop = Propiedad(**datos.model_dump(), imagenes="[]")
    db.add(prop)
    db.commit()
    db.refresh(prop)
    return prop


@app.put("/propiedades/{prop_id}", response_model=PropiedadOut)
def editar_propiedad(
    prop_id: int,
    datos: PropiedadIn,
    db: Session = Depends(get_db),
    _: str = Depends(require_auth),
):
    prop = get_prop_or_404(prop_id, db)
    validar_publicable(datos.model_dump())  # e.g. borrador -> activa needs every required field
    for field, value in datos.model_dump().items():
        setattr(prop, field, value)
    db.commit()
    db.refresh(prop)
    return prop


@app.patch("/propiedades/{prop_id}/toggle", response_model=PropiedadOut)
def toggle_propiedad(
    prop_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(require_auth),
):
    prop = get_prop_or_404(prop_id, db)
    prop.activa = not prop.activa
    db.commit()
    db.refresh(prop)
    return prop


@app.patch("/propiedades/{prop_id}/destacada", response_model=PropiedadOut)
def toggle_destacada(
    prop_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(require_auth),
):
    prop = get_prop_or_404(prop_id, db)
    prop.destacada = not prop.destacada
    db.commit()
    db.refresh(prop)
    return prop


@app.patch("/propiedades/{prop_id}/estado_operacion", response_model=PropiedadOut)
def actualizar_estado_operacion(
    prop_id: int,
    datos: EstadoOperacionIn,
    db: Session = Depends(get_db),
    _: str = Depends(require_auth),
):
    prop = get_prop_or_404(prop_id, db)
    prop.estado_operacion = datos.estado_operacion
    if datos.precio_venta_final is not None:
        prop.precio_venta_final = datos.precio_venta_final
    if datos.moneda_venta_final is not None:
        prop.moneda_venta_final = datos.moneda_venta_final
    try:
        validar_publicable(prop)  # leaving "borrador" requires a complete property
    except HTTPException:
        db.rollback()
        raise
    db.commit()
    db.refresh(prop)
    return prop


@app.delete("/propiedades/{prop_id}", status_code=204)
def eliminar_propiedad(
    prop_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(require_auth),
):
    prop = get_prop_or_404(prop_id, db)
    db.delete(prop)
    db.commit()


@app.post("/propiedades/{prop_id}/imagenes", response_model=PropiedadOut)
def subir_imagenes(
    prop_id: int,
    archivos: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
    _: str = Depends(require_auth),
):
    prop = get_prop_or_404(prop_id, db)
    imagenes: list[str] = json.loads(prop.imagenes or "[]")

    for archivo in archivos:
        resultado = cloudinary.uploader.upload(archivo.file, folder="leonardograf")
        imagenes.append(resultado["secure_url"])

    prop.imagenes = json.dumps(imagenes)
    db.commit()
    db.refresh(prop)
    return prop


def cloudinary_public_id(url: str) -> Optional[str]:
    """Derive the Cloudinary public_id from a delivery URL, or None if it isn't one.

    https://res.cloudinary.com/<cloud>/image/upload/[...transforms/]v123/folder/name.jpg
      -> "folder/name"
    Upload secure_urls always carry the version segment; everything after it is the public_id.
    """
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or parsed.hostname != "res.cloudinary.com":
        return None
    parts = parsed.path.split("/upload/", 1)
    if len(parts) != 2:
        return None
    segments = [s for s in parts[1].split("/") if s]
    version_idx = next((i for i, s in enumerate(segments) if re.fullmatch(r"v\d+", s)), None)
    if version_idx is not None:
        segments = segments[version_idx + 1:]
    if not segments:
        return None
    path = "/".join(segments)
    return path.rsplit(".", 1)[0] if "." in segments[-1] else path


@app.put("/propiedades/{prop_id}/imagenes/orden", response_model=PropiedadOut)
def ordenar_imagenes(
    prop_id: int,
    datos: ImagenesOrdenIn,
    db: Session = Depends(get_db),
    _: str = Depends(require_auth),
):
    """Replace the property's image list with the given ordered list.

    The list may only reorder/remove images the property already has (no foreign URLs).
    imagenes[0] is the cover photo. Removed Cloudinary images are destroyed (best effort).
    """
    prop = get_prop_or_404(prop_id, db)
    actuales: list[str] = json.loads(prop.imagenes or "[]")
    nuevas = datos.imagenes

    if len(set(nuevas)) != len(nuevas):
        raise HTTPException(status_code=422, detail="La lista de imágenes tiene duplicados")
    desconocidas = [u for u in nuevas if u not in actuales]
    if desconocidas:
        raise HTTPException(status_code=422, detail="La lista incluye imágenes que no pertenecen a la propiedad")

    eliminadas = [u for u in actuales if u not in nuevas]
    prop.imagenes = json.dumps(nuevas)
    db.commit()
    db.refresh(prop)

    # Best effort: never fail the request because Cloudinary cleanup failed
    for url in eliminadas:
        public_id = cloudinary_public_id(url)
        if not public_id:
            continue
        try:
            cloudinary.uploader.destroy(public_id, invalidate=True)
        except Exception as exc:  # noqa: BLE001
            logger.warning("No se pudo borrar %s de Cloudinary: %s", public_id, exc)

    return prop


# ── Endpoints: Mensajes ───────────────────────────────────────────────────────

@app.post("/mensajes", response_model=MensajeOut, status_code=201)
def crear_mensaje(datos: MensajeIn, db: Session = Depends(get_db)):
    msg = Mensaje(**datos.model_dump())
    db.add(msg)
    db.commit()
    db.refresh(msg)

    record = {
        "id":       msg.id,
        "nombre":   msg.nombre,
        "email":    msg.email,
        "telefono": msg.telefono,
        "mensaje":  msg.mensaje,
        "fecha":    msg.fecha.isoformat() if hasattr(msg.fecha, "isoformat") else str(msg.fecha),
    }
    with MENSAJES_BACKUP.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    return msg


@app.get("/mensajes", response_model=list[MensajeOut])
def listar_mensajes(
    no_leidos: bool = Query(False),
    db: Session = Depends(get_db),
    _: str = Depends(require_auth),
):
    q = db.query(Mensaje)
    if no_leidos:
        q = q.filter(Mensaje.leido == False)  # noqa: E712
    return q.order_by(Mensaje.fecha.desc()).all()


@app.patch("/mensajes/{mensaje_id}/leido", response_model=MensajeOut)
def marcar_leido(
    mensaje_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(require_auth),
):
    msg = get_mensaje_or_404(mensaje_id, db)
    msg.leido = True
    db.commit()
    db.refresh(msg)
    return msg
