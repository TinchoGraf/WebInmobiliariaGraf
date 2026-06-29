/* api.js — comunicación con el backend FastAPI */

const API_BASE = 'http://localhost:8000'; // cambiar al dominio real en producción

async function apiFetch(endpoint, opts = {}) {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    headers: { 'Content-Type': 'application/json', ...opts.headers },
    ...opts,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

/* ── Propiedades ─────────────────────────────── */

/**
 * Devuelve el array de propiedades activas con filtros opcionales.
 * Retorna null si hay error de red (para distinguir de [] sin resultados).
 */
async function fetchPropiedades(filtros = {}) {
  const params = {};

  if (filtros.operacion && filtros.operacion !== 'todos') params.operacion = filtros.operacion;
  if (filtros.tipo)       params.tipo       = filtros.tipo;
  if (filtros.antiguedad) params.antiguedad = filtros.antiguedad;

  // Moneda y precio: solo cuando se filtra por rango de precio
  const hasPrecio = filtros.precioMin || filtros.precioMax;
  if (hasPrecio) {
    if (filtros.moneda)    params.moneda    = filtros.moneda;
    if (filtros.precioMin) params.precio_min = filtros.precioMin;
    if (filtros.precioMax) params.precio_max = filtros.precioMax;
  }

  const qs = new URLSearchParams(params).toString();
  try {
    return await apiFetch(`/propiedades${qs ? '?' + qs : ''}`);
  } catch {
    return null; // null = error de red; [] = respuesta vacía del servidor
  }
}

/**
 * Devuelve una propiedad por ID, o null si no existe o hay error.
 */
async function fetchPropiedad(id) {
  try {
    return await apiFetch(`/propiedades/${id}`);
  } catch {
    return null;
  }
}

/* ── Mensajes / Contacto ─────────────────────── */

async function enviarMensaje(datos) {
  return apiFetch('/mensajes', {
    method: 'POST',
    body: JSON.stringify(datos),
  });
}
