import json
import os
import secrets
import shutil
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, File, HTTPException, Query, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, field_validator
from sqlalchemy.orm import Session

from database import get_db, init_db
from models import Propiedad

load_dotenv()

ADMIN_USER     = os.getenv("ADMIN_USER", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "cambiarme123")
IMAGES_DIR     = Path(__file__).parent.parent / "assets" / "images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Leonardograf Propiedades API", version="2.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBasic()

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


# ── Schemas ──────────────────────────────────────────────────────────────────

class PropiedadIn(BaseModel):
    titulo:      str
    descripcion: Optional[str] = None
    operacion:   str
    tipo:        str
    estado:      Optional[str] = None
    precio:      float
    moneda:      str = "USD"
    direccion:   str
    barrio:      Optional[str] = None
    lat:         Optional[float] = None
    lng:         Optional[float] = None


class PropiedadOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:             int
    titulo:         str
    descripcion:    Optional[str]
    operacion:      str
    tipo:           str
    estado:         Optional[str]
    precio:         float
    moneda:         str
    direccion:      str
    barrio:         Optional[str]
    lat:            float
    lng:            float
    imagenes:       list[str]
    activa:         bool
    fecha_creacion: str

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


# ── Helpers ──────────────────────────────────────────────────────────────────

def get_prop_or_404(prop_id: int, db: Session) -> Propiedad:
    prop = db.query(Propiedad).filter(Propiedad.id == prop_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Propiedad no encontrada")
    return prop


# ── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/propiedades", response_model=list[PropiedadOut])
def listar_propiedades(
    operacion:  Optional[str]   = Query(None),
    tipo:       Optional[str]   = Query(None),
    estado:     Optional[str]   = Query(None),
    precio_min: Optional[float] = Query(None),
    precio_max: Optional[float] = Query(None),
    moneda:     Optional[str]   = Query(None),
    todas:      bool            = Query(False, description="Si True incluye propiedades inactivas"),
    db: Session = Depends(get_db),
):
    q = db.query(Propiedad)
    if not todas:
        q = q.filter(Propiedad.activa == True)  # noqa: E712
    if operacion:              q = q.filter(Propiedad.operacion == operacion)
    if tipo:                   q = q.filter(Propiedad.tipo == tipo)
    if estado:                 q = q.filter(Propiedad.estado == estado)
    if moneda:                 q = q.filter(Propiedad.moneda == moneda)
    if precio_min is not None: q = q.filter(Propiedad.precio >= precio_min)
    if precio_max is not None: q = q.filter(Propiedad.precio <= precio_max)
    return q.all()


@app.get("/propiedades/{prop_id}", response_model=PropiedadOut)
def obtener_propiedad(prop_id: int, db: Session = Depends(get_db)):
    return get_prop_or_404(prop_id, db)


@app.post("/propiedades", response_model=PropiedadOut, status_code=201)
def crear_propiedad(
    datos: PropiedadIn,
    db: Session = Depends(get_db),
    _: str = Depends(require_auth),
):
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
        ext    = Path(archivo.filename).suffix.lower() if archivo.filename else ".jpg"
        nombre = f"prop_{prop_id}_{uuid.uuid4().hex[:8]}{ext}"
        dest   = IMAGES_DIR / nombre
        with dest.open("wb") as f:
            shutil.copyfileobj(archivo.file, f)
        imagenes.append(f"assets/images/{nombre}")

    prop.imagenes = json.dumps(imagenes)
    db.commit()
    db.refresh(prop)
    return prop
