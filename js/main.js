/* main.js — punto de entrada principal */

document.addEventListener('DOMContentLoaded', () => {
  initNavbarScroll();
  initHamburguesa();
  initActiveSections();
  initScrollReveal();
  initCounters();
  initFiltros();
  initContactForm();
  aplicarFiltros();
});

/* ── Estado de filtros ────────────────────────── */

const filtrosActivos = {
  operacion: 'todos',
  tipo:      '',
  estado:    '',
  moneda:    'USD',
  precioMin: '',
  precioMax: '',
};

/* ── Carga / filtrado ─────────────────────────── */

async function aplicarFiltros() {
  const grid = document.getElementById('propiedadesGrid');
  if (!grid) return;

  grid.innerHTML = skeletonCards(6);

  const { items, total } = await getPropiedadesConFallback({ ...filtrosActivos });

  grid.innerHTML = '';
  _actualizarContador(total);

  if (!items.length) {
    grid.innerHTML = `
      <div style="grid-column:1/-1;text-align:center;padding:3rem 1rem;color:var(--color-text-muted)">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="margin-bottom:1rem;opacity:.4"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
        <p style="font-size:1.125rem;font-weight:600;margin-bottom:.5rem">Sin resultados</p>
        <p>Probá con otros filtros.</p>
      </div>`;
    actualizarMapa([]);
    return;
  }

  items.forEach(prop => grid.appendChild(crearCard(prop)));
  actualizarMapa(items);
}

function _actualizarContador(total) {
  const el = document.getElementById('resultadosCount');
  if (!el) return;
  el.textContent = total === 0
    ? 'Sin propiedades para esta búsqueda'
    : total === 1
      ? '1 propiedad encontrada'
      : `${total} propiedades encontradas`;
}

/* ── Cards ───────────────────────────────────── */

const TIPO_LABELS = {
  casa: 'Casa', departamento: 'Departamento', terreno: 'Terreno',
  lote: 'Lote', local: 'Local comercial', ph: 'PH',
};
const ESTADO_LABELS = {
  a_estrenar: 'A estrenar', con_uso: 'Con uso', a_reciclar: 'A reciclar',
};
const OP_LABELS = {
  venta: 'VENTA', alquiler: 'ALQUILER', alquiler_temporario: 'ALQUILER TEMP.',
};
const OP_CLASSES = {
  venta: '', alquiler: 'badge--alquiler', alquiler_temporario: 'badge--temp',
};

function crearCard(prop) {
  const precio    = formatearPrecio(prop.precio, prop.moneda || 'USD');
  const img       = prop.imagen || imagenPlaceholder(400, 260);
  const wppLink   = generarLinkWhatsApp(prop);
  const opLabel   = OP_LABELS[prop.operacion]  || prop.operacion.toUpperCase();
  const opClass   = OP_CLASSES[prop.operacion] || '';
  const tipoLabel = TIPO_LABELS[prop.tipo]     || prop.tipo;
  const estadoLabel = prop.estado ? (ESTADO_LABELS[prop.estado] || prop.estado) : null;

  // Features: solo las que tienen valor
  const featureItems = [
    prop.dormitorios != null
      ? `<li class="propiedad-card__feature">
           <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M2 22V12a2 2 0 012-2h16a2 2 0 012 2v10M2 17h20M6 12V8a2 2 0 014 0v4M14 12V8a2 2 0 014 0v4"/></svg>
           ${prop.dormitorios} dorm.
         </li>`
      : '',
    prop.banos != null
      ? `<li class="propiedad-card__feature">
           <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M4 12h16M4 12a2 2 0 01-2-2V6a2 2 0 012-2h2M20 12a2 2 0 002-2V6a2 2 0 00-2-2h-2M6 4v8M18 4v8M2 22h20M4 18h16"/></svg>
           ${prop.banos} ${prop.banos === 1 ? 'baño' : 'baños'}
         </li>`
      : '',
    prop.m2 != null
      ? `<li class="propiedad-card__feature">
           <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18M9 21V9"/></svg>
           ${prop.m2} m²
         </li>`
      : '',
  ].filter(Boolean);

  const article = document.createElement('article');
  article.className = 'propiedad-card';
  article.setAttribute('role', 'listitem');
  article.dataset.propId = prop.id;

  article.innerHTML = `
    <a href="propiedad.html?id=${prop.id}" class="propiedad-card__image" aria-label="Ver ${truncar(prop.titulo, 50)}">
      <img src="${img}" alt="${prop.titulo}" width="400" height="260" loading="lazy" />
      <span class="propiedad-card__badge ${opClass}">${opLabel}</span>
      <button class="propiedad-card__fav" aria-label="Guardar en favoritos" aria-pressed="false" data-id="${prop.id}">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#1B4332" stroke-width="2"><path d="M20.84 4.61a5.5 5.5 0 00-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 00-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 000-7.78z"/></svg>
      </button>
    </a>
    <div class="propiedad-card__body">
      <div class="propiedad-card__precio">${precio}</div>
      <h3 class="propiedad-card__titulo">${prop.titulo}</h3>
      <div class="propiedad-card__meta">
        <span class="card-tipo">${tipoLabel}</span>
        ${estadoLabel ? `<span class="card-estado card-estado--${prop.estado}">${estadoLabel}</span>` : ''}
      </div>
      <div class="propiedad-card__ubicacion">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg>
        ${prop.ubicacion || '—'}
      </div>
      ${featureItems.length ? `<ul class="propiedad-card__features">${featureItems.join('')}</ul>` : ''}
    </div>
    <div class="propiedad-card__footer">
      <a href="propiedad.html?id=${prop.id}" class="btn-card-detail">Ver detalle</a>
      <a href="${wppLink}"
         class="btn-card-wpp"
         target="_blank" rel="noopener noreferrer"
         aria-label="Consultar por WhatsApp">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>
        WhatsApp
      </a>
    </div>`;

  // Hover → resaltar marcador en el mapa
  article.addEventListener('mouseenter', () => resaltarMarcador(prop.id));
  article.addEventListener('mouseleave', () => limpiarResaltado());

  // Favoritos (toggle fill del corazón)
  article.querySelector('.propiedad-card__fav').addEventListener('click', (e) => {
    e.preventDefault();
    e.stopPropagation();
    const btn    = e.currentTarget;
    const saved  = btn.getAttribute('aria-pressed') === 'true';
    btn.setAttribute('aria-pressed', String(!saved));
    btn.querySelector('svg').setAttribute('fill', saved ? 'none' : '#1B4332');
  });

  return article;
}

function skeletonCards(n) {
  return Array.from({ length: n }, () => `
    <div class="propiedad-card" aria-hidden="true" style="animation:pulse 1.5s ease infinite">
      <div style="aspect-ratio:16/10;background:var(--color-border)"></div>
      <div style="padding:1.25rem;display:flex;flex-direction:column;gap:.75rem">
        <div style="height:22px;background:var(--color-border);border-radius:4px;width:45%"></div>
        <div style="height:16px;background:var(--color-border);border-radius:4px;width:80%"></div>
        <div style="height:13px;background:var(--color-border);border-radius:4px;width:55%"></div>
      </div>
    </div>`).join('');
}

/* ── Panel de filtros ─────────────────────────── */

function initFiltros() {
  // Tabs operación
  document.querySelectorAll('.filtro-tab').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.filtro-tab').forEach(b => {
        b.classList.remove('active');
        b.setAttribute('aria-selected', 'false');
      });
      btn.classList.add('active');
      btn.setAttribute('aria-selected', 'true');
      filtrosActivos.operacion = btn.dataset.op;
      aplicarFiltros();
    });
  });

  // Dropdowns y precio → sólo se aplican con "Buscar"
  document.getElementById('filtroTipo')?.addEventListener('change', e  => { filtrosActivos.tipo  = e.target.value; });
  document.getElementById('filtroEstado')?.addEventListener('change', e => { filtrosActivos.estado = e.target.value; });
  document.getElementById('filtroMoneda')?.addEventListener('change', e => { filtrosActivos.moneda = e.target.value; });

  const debouncedBuscar = debounce(aplicarFiltros, 500);
  document.getElementById('filtroMin')?.addEventListener('input', e => {
    filtrosActivos.precioMin = e.target.value;
    debouncedBuscar();
  });
  document.getElementById('filtroMax')?.addEventListener('input', e => {
    filtrosActivos.precioMax = e.target.value;
    debouncedBuscar();
  });

  // Botón Buscar
  document.getElementById('btnBuscar')?.addEventListener('click', aplicarFiltros);

  // Limpiar filtros
  document.getElementById('btnLimpiar')?.addEventListener('click', () => {
    filtrosActivos.operacion = 'todos';
    filtrosActivos.tipo      = '';
    filtrosActivos.estado    = '';
    filtrosActivos.moneda    = 'USD';
    filtrosActivos.precioMin = '';
    filtrosActivos.precioMax = '';

    document.querySelectorAll('.filtro-tab').forEach(b => {
      const isAll = b.dataset.op === 'todos';
      b.classList.toggle('active', isAll);
      b.setAttribute('aria-selected', String(isAll));
    });

    const s = v => { if (v) v.value = ''; };
    s(document.getElementById('filtroTipo'));
    s(document.getElementById('filtroEstado'));
    s(document.getElementById('filtroMin'));
    s(document.getElementById('filtroMax'));
    const mon = document.getElementById('filtroMoneda');
    if (mon) mon.value = 'USD';

    aplicarFiltros();
  });

  // Toggle móvil
  const toggle = document.getElementById('filtrosToggle');
  const body   = document.getElementById('filtrosBody');
  if (toggle && body) {
    toggle.addEventListener('click', () => {
      const open = body.classList.toggle('open');
      toggle.classList.toggle('open', open);
      toggle.setAttribute('aria-expanded', String(open));
    });
  }
}

/* ── Formulario de contacto ───────────────────── */

function initContactForm() {
  const form = document.getElementById('contactForm');
  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = form.querySelector('[type="submit"]');
    btn.disabled    = true;
    btn.textContent = 'Enviando…';

    const datos = Object.fromEntries(new FormData(form));
    try { await enviarContacto(datos); } catch { /* demo: siempre muestra éxito */ }

    form.style.display = 'none';
    document.getElementById('formSuccess').classList.add('visible');
  });
}

/* Skeleton pulse */
const _styleEl = document.createElement('style');
_styleEl.textContent = '@keyframes pulse{0%,100%{opacity:1}50%{opacity:.45}}';
document.head.appendChild(_styleEl);
