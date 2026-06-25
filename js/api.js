/* api.js — comunicación con el backend FastAPI */

const API_BASE = 'http://localhost:8000/api';

async function apiFetch(endpoint, opts = {}) {
  const url = `${API_BASE}${endpoint}`;
  const res  = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...opts.headers },
    ...opts,
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

/* ── Propiedades ─────────────────────────────── */

async function getPropiedades(params = {}) {
  const qs = new URLSearchParams(
    Object.fromEntries(Object.entries(params).filter(([, v]) => v != null && v !== ''))
  ).toString();
  return apiFetch(`/propiedades${qs ? '?' + qs : ''}`);
}

async function getPropiedad(id) {
  return apiFetch(`/propiedades/${id}`);
}

/* ── Contacto ────────────────────────────────── */

async function enviarContacto(datos) {
  return apiFetch('/contacto', {
    method: 'POST',
    body: JSON.stringify(datos),
  });
}

/* ── Datos de ejemplo — Olavarría, Buenos Aires ── */
const PROPIEDADES_DEMO = [
  {
    id: 1,
    titulo: 'Casa familiar en el centro',
    tipo: 'casa',
    operacion: 'venta',
    estado: 'con_uso',
    precio: 95000,
    moneda: 'USD',
    ubicacion: 'Rivadavia 1250, Olavarría',
    barrio: 'Centro',
    descripcion: 'Amplia casa de tres dormitorios en pleno centro. Cochera, jardín y parrilla. Excelentes terminaciones.',
    dormitorios: 3,
    banos: 2,
    m2: 180,
    lat: -36.8927,
    lng: -60.3224,
    imagen: '',
  },
  {
    id: 2,
    titulo: 'Departamento a estrenar en San Martín',
    tipo: 'departamento',
    operacion: 'alquiler',
    estado: 'a_estrenar',
    precio: 320000,
    moneda: 'ARS',
    ubicacion: 'San Martín 455, Olavarría',
    barrio: 'Centro',
    descripcion: 'Luminoso departamento de dos dormitorios a estrenar. Piso 3°, balcón con vista al boulevard.',
    dormitorios: 2,
    banos: 1,
    m2: 68,
    lat: -36.8952,
    lng: -60.3190,
    imagen: '',
  },
  {
    id: 3,
    titulo: 'Casa esquina en Barrio Unión',
    tipo: 'casa',
    operacion: 'venta',
    estado: 'a_reciclar',
    precio: 42000,
    moneda: 'USD',
    ubicacion: 'Av. del Trabajo 840, Olavarría',
    barrio: 'Barrio Unión',
    descripcion: 'Propiedad en esquina ideal para reformar o invertir. Gran terreno de 360 m², todos los servicios.',
    dormitorios: 3,
    banos: 1,
    m2: 120,
    lat: -36.9020,
    lng: -60.3310,
    imagen: '',
  },
  {
    id: 4,
    titulo: 'Terreno residencial zona norte',
    tipo: 'terreno',
    operacion: 'venta',
    estado: null,
    precio: 18000,
    moneda: 'USD',
    ubicacion: 'Calle 12 y Av. Colón, Olavarría',
    barrio: 'Zona Norte',
    descripcion: 'Terreno plano de 600 m² en zona residencial en crecimiento. Agua, luz y cloacas.',
    dormitorios: null,
    banos: null,
    m2: 600,
    lat: -36.8780,
    lng: -60.3150,
    imagen: '',
  },
  {
    id: 5,
    titulo: 'Local comercial sobre Rivadavia',
    tipo: 'local',
    operacion: 'alquiler',
    estado: 'con_uso',
    precio: 280000,
    moneda: 'ARS',
    ubicacion: 'Rivadavia 550, Olavarría',
    barrio: 'Centro',
    descripcion: 'Local en planta baja sobre peatonal de alta circulación. 60 m², baño y depósito independiente.',
    dormitorios: null,
    banos: 1,
    m2: 60,
    lat: -36.8940,
    lng: -60.3200,
    imagen: '',
  },
  {
    id: 6,
    titulo: 'Casa moderna a estrenar en Villa Fortabat',
    tipo: 'casa',
    operacion: 'venta',
    estado: 'a_estrenar',
    precio: 130000,
    moneda: 'USD',
    ubicacion: 'Los Aromos 320, Olavarría',
    barrio: 'Villa Fortabat',
    descripcion: 'Casa de diseño contemporáneo a estrenar. 3 dormitorios en suite, garaje doble y piscina.',
    dormitorios: 3,
    banos: 3,
    m2: 210,
    lat: -36.8850,
    lng: -60.3070,
    imagen: '',
  },
  {
    id: 7,
    titulo: 'Departamento equipado para estadías cortas',
    tipo: 'departamento',
    operacion: 'alquiler_temporario',
    estado: 'a_estrenar',
    precio: 15000,
    moneda: 'ARS',
    ubicacion: 'España 320, Olavarría',
    barrio: 'Centro',
    descripcion: 'Departamento totalmente equipado: WiFi, Smart TV, ropa de cama y cocina completa. Precio por día.',
    dormitorios: 1,
    banos: 1,
    m2: 48,
    lat: -36.8910,
    lng: -60.3240,
    imagen: '',
  },
  {
    id: 8,
    titulo: 'Lote en barrio privado Parque',
    tipo: 'lote',
    operacion: 'venta',
    estado: null,
    precio: 22000,
    moneda: 'USD',
    ubicacion: 'Sarmiento 1800, Olavarría',
    barrio: 'Barrio Parque',
    descripcion: 'Lote de 400 m² dentro de barrio con portería 24 h. Acceso a áreas verdes y SUM.',
    dormitorios: null,
    banos: null,
    m2: 400,
    lat: -36.8890,
    lng: -60.3340,
    imagen: '',
  },
];

/* Filtrado local (sin backend) */
function filtrarLocal(datos, filtros = {}) {
  const { operacion, tipo, estado, moneda, precioMin, precioMax } = filtros;
  let res = [...datos];

  if (operacion && operacion !== 'todos') {
    res = res.filter(p => p.operacion === operacion);
  }
  if (tipo)   res = res.filter(p => p.tipo === tipo);
  if (estado) res = res.filter(p => p.estado === estado);

  if ((precioMin || precioMax)) {
    const m = moneda || 'USD';
    res = res.filter(p => p.moneda === m);
    if (precioMin) res = res.filter(p => p.precio >= Number(precioMin));
    if (precioMax) res = res.filter(p => p.precio <= Number(precioMax));
  }

  return { items: res, total: res.length };
}

async function getPropiedadesConFallback(filtros = {}) {
  try {
    return await getPropiedades(filtros);
  } catch {
    return filtrarLocal(PROPIEDADES_DEMO, filtros);
  }
}
