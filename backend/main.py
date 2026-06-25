from contextlib import asynccontextmanager
from typing import Optional
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from database import get_db, init_db
from models import Propiedad, Contacto


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="Leonardograf Propiedades API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:5500", "*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Schemas ──────────────────────────────────────

class PropiedadOut(BaseModel):
    id:          int
    titulo:      str
    tipo:        str
    operacion:   str
    precio:      float
    moneda:      str
    ubicacion:   Optional[str]
    barrio:      Optional[str]
    descripcion: Optional[str]
    dormitorios: Optional[int]
    banos:       Optional[int]
    m2:          Optional[float]
    estado:      Optional[str]
    lat:         Optional[float]
    lng:         Optional[float]
    imagen:      Optional[str]

    class Config:
        from_attributes = True


class PropiedadesResponse(BaseModel):
    items: list[PropiedadOut]
    total: int
    page:  int
    limit: int


class ContactoIn(BaseModel):
    nombre:   str
    apellido: str
    email:    str
    telefono: Optional[str] = None
    interes:  Optional[str] = None
    mensaje:  str


# ── Endpoints ────────────────────────────────────

@app.get("/api/propiedades", response_model=PropiedadesResponse)
async def listar_propiedades(
    tipo:      Optional[str] = Query(None),
    operacion: Optional[str] = Query(None),
    barrio:    Optional[str] = Query(None),
    page:      int = Query(1, ge=1),
    limit:     int = Query(12, ge=1, le=50),
    db:        AsyncSession = Depends(get_db),
):
    stmt = select(Propiedad).where(Propiedad.activa == True)
    if tipo:
        stmt = stmt.where(Propiedad.tipo == tipo)
    if operacion:
        stmt = stmt.where(Propiedad.operacion == operacion)
    if barrio:
        stmt = stmt.where(Propiedad.barrio.ilike(f"%{barrio}%"))

    total_stmt = select(func.count()).select_from(stmt.subquery())
    total      = (await db.execute(total_stmt)).scalar_one()

    stmt   = stmt.offset((page - 1) * limit).limit(limit)
    result = await db.execute(stmt)
    items  = result.scalars().all()

    return PropiedadesResponse(items=items, total=total, page=page, limit=limit)


@app.get("/api/propiedades/{propiedad_id}", response_model=PropiedadOut)
async def obtener_propiedad(propiedad_id: int, db: AsyncSession = Depends(get_db)):
    prop = await db.get(Propiedad, propiedad_id)
    if not prop or not prop.activa:
        raise HTTPException(status_code=404, detail="Propiedad no encontrada")
    return prop


@app.post("/api/contacto", status_code=201)
async def crear_contacto(datos: ContactoIn, db: AsyncSession = Depends(get_db)):
    contacto = Contacto(**datos.model_dump())
    db.add(contacto)
    await db.commit()
    return {"ok": True, "mensaje": "Consulta recibida"}


@app.get("/api/health")
async def health():
    return {"status": "ok"}
