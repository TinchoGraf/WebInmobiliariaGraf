/* main.js — punto de entrada principal */

document.addEventListener('DOMContentLoaded', () => {
  initNavbarScroll();
  initHamburguesa();
  initActiveSections();
  initScrollReveal();
  initCounters();
  initFiltros();
  initContactForm();
  initOnboarding();
  initMapaOficina();
  aplicarFiltros();
});

/* ── Estado de filtros ────────────────────────── */

const filtrosActivos = {
  operacion:  'todos',
  tipo:       '',
  antiguedad: '',
  moneda:     'USD',
  precioMin:  '',
  precioMax:  '',
};

/* ── Carga / filtrado ─────────────────────────── */

async function aplicarFiltros() {
  const grid = document.getElementById('propiedadesGrid');
  if (!grid) return;

  grid.innerHTML = skeletonCards(6);

  const items = await fetchPropiedades({ ...filtrosActivos });

  grid.innerHTML = '';

  if (items === null) {
    _actualizarContador(0);
    grid.innerHTML = `
      <div style="grid-column:1/-1;text-align:center;padding:3rem 1rem;color:var(--color-text-muted)">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="margin-bottom:1rem;opacity:.4"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
        <p style="font-size:1.125rem;font-weight:600;margin-bottom:.5rem">Error de conexión</p>
        <p>Hubo un problema al cargar las propiedades. Intentá de nuevo más tarde.</p>
      </div>`;
    actualizarMapa([]);
    return;
  }

  _actualizarContador(items.length);

  if (!items.length) {
    grid.innerHTML = `
      <div style="grid-column:1/-1;text-align:center;padding:3rem 1rem;color:var(--color-text-muted)">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="margin-bottom:1rem;opacity:.4"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
        <p style="font-size:1.125rem;font-weight:600;margin-bottom:.5rem">Sin resultados</p>
        <p>No encontramos propiedades con esos filtros. Probá cambiando los criterios de búsqueda.</p>
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
  comercial: 'Comercial', chacra_campo: 'Chacra / Campo', quinta: 'Quinta', ph: 'PH',
};
const ANTIGUEDAD_LABELS = {
  a_estrenar: 'A estrenar', '1_10': '1-10 años', '10_20': '10-20 años', mas_20: '+20 años',
};
const OP_LABELS = {
  venta: 'VENTA', alquiler: 'ALQUILER',
  alquiler_temp: 'ALQUILER TEMP.', alquiler_temporario: 'ALQUILER TEMP.',
};
const OP_CLASSES = {
  venta: '', alquiler: 'badge--alquiler',
  alquiler_temp: 'badge--temp', alquiler_temporario: 'badge--temp',
};

function crearCard(prop) {
  const precio    = formatearPrecio(prop.precio, prop.moneda || 'USD');
  const img       = (prop.imagenes && prop.imagenes[0]) || imagenPlaceholder(400, 260);
  const wppLink   = generarLinkWhatsApp(prop);
  const opLabel   = OP_LABELS[prop.operacion]  || prop.operacion.toUpperCase();
  const opClass   = OP_CLASSES[prop.operacion] || '';
  const tipoLabel       = TIPO_LABELS[prop.tipo]            || prop.tipo;
  const antiguedadLabel = prop.antiguedad
    ? (ANTIGUEDAD_LABELS[prop.antiguedad] || prop.antiguedad) : null;

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
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#A00000" stroke-width="2"><path d="M20.84 4.61a5.5 5.5 0 00-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 00-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 000-7.78z"/></svg>
      </button>
    </a>
    <div class="propiedad-card__body">
      <div class="propiedad-card__precio">${precio}</div>
      <h3 class="propiedad-card__titulo">${prop.titulo}</h3>
      <div class="propiedad-card__meta">
        <span class="card-tipo">${tipoLabel}</span>
        ${antiguedadLabel ? `<span class="card-estado card-estado--${prop.antiguedad}">${antiguedadLabel}</span>` : ''}
      </div>
      <div class="propiedad-card__ubicacion">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg>
        ${prop.direccion || '—'}
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
    btn.querySelector('svg').setAttribute('fill', saved ? 'none' : '#A00000');
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
      _actualizarMonedaPorOperacion(btn.dataset.op);
      aplicarFiltros();
    });
  });

  // Dropdowns y precio → sólo se aplican con "Buscar"
  document.getElementById('filtroTipo')?.addEventListener('change', e => { filtrosActivos.tipo = e.target.value; });
  document.getElementById('filtroMoneda')?.addEventListener('change', e => { filtrosActivos.moneda = e.target.value; });

  // Chips de antigüedad (multi-select)
  document.querySelectorAll('#filtroAntiguedad .chip').forEach(chip => {
    chip.addEventListener('click', () => {
      const val = chip.dataset.val;
      if (val === '') {
        document.querySelectorAll('#filtroAntiguedad .chip').forEach(c => c.classList.remove('active'));
        chip.classList.add('active');
        filtrosActivos.antiguedad = '';
      } else {
        document.querySelector('#filtroAntiguedad .chip[data-val=""]')?.classList.remove('active');
        chip.classList.toggle('active');
        const activos = [...document.querySelectorAll('#filtroAntiguedad .chip.active')]
          .map(c => c.dataset.val).filter(v => v !== '');
        if (activos.length === 0) {
          document.querySelector('#filtroAntiguedad .chip[data-val=""]')?.classList.add('active');
          filtrosActivos.antiguedad = '';
        } else {
          filtrosActivos.antiguedad = activos.join(',');
        }
      }
    });
  });

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
    filtrosActivos.operacion  = 'todos';
    filtrosActivos.tipo       = '';
    filtrosActivos.antiguedad = '';
    filtrosActivos.moneda     = 'USD';
    filtrosActivos.precioMin  = '';
    filtrosActivos.precioMax  = '';

    document.querySelectorAll('.filtro-tab').forEach(b => {
      const isAll = b.dataset.op === 'todos';
      b.classList.toggle('active', isAll);
      b.setAttribute('aria-selected', String(isAll));
    });

    const clr = v => { if (v) v.value = ''; };
    clr(document.getElementById('filtroTipo'));
    clr(document.getElementById('filtroMin'));
    clr(document.getElementById('filtroMax'));

    // Reset chips antigüedad → "Todos"
    document.querySelectorAll('#filtroAntiguedad .chip').forEach(c => c.classList.remove('active'));
    document.querySelector('#filtroAntiguedad .chip[data-val=""]')?.classList.add('active');

    // Reset moneda y desbloquear
    const mon = document.getElementById('filtroMoneda');
    if (mon) { mon.value = 'USD'; mon.disabled = false; mon.title = ''; }
    _actualizarMonedaPorOperacion('todos');

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

/* ── Moneda automática por operación ─────────── */

function _actualizarMonedaPorOperacion(op) {
  const sel = document.getElementById('filtroMoneda');
  if (!sel) return;
  if (op === 'venta') {
    sel.value    = 'USD';
    sel.disabled = true;
    sel.title    = 'Las ventas se publican en USD';
    filtrosActivos.moneda = 'USD';
  } else if (op === 'alquiler' || op === 'alquiler_temporario') {
    sel.value    = 'ARS';
    sel.disabled = true;
    sel.title    = 'Los alquileres se publican en ARS';
    filtrosActivos.moneda = 'ARS';
  } else {
    sel.disabled = false;
    sel.title    = '';
  }
}

/* ── Formulario de contacto ───────────────────── */

function initContactForm() {
  const form = document.getElementById('contactForm');
  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    // Ocultar error previo si estaba visible
    const errEl = document.getElementById('formError');
    if (errEl) errEl.classList.remove('visible');

    const btn = form.querySelector('[type="submit"]');
    btn.disabled  = true;
    btn.innerHTML = '<span class="form-spinner"></span> Enviando…';

    const datos = Object.fromEntries(new FormData(form));
    const payload = {
      nombre:   `${datos.nombre || ''} ${datos.apellido || ''}`.trim(),
      email:    datos.email,
      telefono: datos.telefono || null,
      mensaje:  datos.interes
        ? `[${datos.interes}] ${datos.mensaje}`
        : datos.mensaje,
    };

    try {
      await enviarMensaje(payload);
      form.style.display = 'none';
      document.getElementById('formSuccess').classList.add('visible');
    } catch {
      if (errEl) errEl.classList.add('visible');
      btn.disabled  = false;
      btn.textContent = 'Enviar mensaje';
    }
  });
}

/* ── Onboarding banner (primer scroll) ───────── */

function initOnboarding() {
  if (sessionStorage.getItem('lgraf_onboarding_seen')) return;
  const banner = document.getElementById('onboardingBanner');
  const closeBtn = document.getElementById('onboardingClose');
  if (!banner) return;

  const mostrar = () => {
    banner.classList.add('visible');
    window.removeEventListener('scroll', mostrar);
  };
  window.addEventListener('scroll', mostrar, { passive: true });

  closeBtn?.addEventListener('click', () => {
    banner.classList.remove('visible');
    sessionStorage.setItem('lgraf_onboarding_seen', '1');
  });
}

/* ── Mini mapa de la oficina ─────────────────── */

const OFICINA_LAT = -36.8866;
const OFICINA_LNG = -60.3210;

function initMapaOficina() {
  const el = document.getElementById('mapaOficina');
  if (!el || typeof L === 'undefined') return;

  const mapa = L.map('mapaOficina', {
    center:          [OFICINA_LAT, OFICINA_LNG],
    zoom:            16,
    zoomControl:     false,
    scrollWheelZoom: false,
    dragging:        false,
    doubleClickZoom: false,
    attributionControl: false,
  });

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap',
    maxZoom: 18,
  }).addTo(mapa);

  const iconOficina = L.divIcon({
    className: '',
    html: `<svg width="38" height="38" viewBox="0 0 38 38" xmlns="http://www.w3.org/2000/svg">
      <circle cx="19" cy="19" r="17" fill="#A00000" stroke="#fff" stroke-width="2.5"/>
      <text x="19" y="24" text-anchor="middle" font-family="Inter,sans-serif"
            font-size="12" font-weight="700" fill="#fff">LG</text>
    </svg>`,
    iconSize:    [38, 38],
    iconAnchor:  [19, 19],
    popupAnchor: [0, -22],
  });

  L.marker([OFICINA_LAT, OFICINA_LNG], { icon: iconOficina })
    .bindPopup('<b>Leonardograf Propiedades</b><br>Coronel Suárez 3131, Olavarría')
    .addTo(mapa);

  // "Ver en mapa" — desktop: scroll a busquedas + setView; mobile: Google Maps
  document.getElementById('btnVerEnMapa')?.addEventListener('click', () => {
    if (window.innerWidth < 768) {
      window.open(`https://maps.google.com/?q=${OFICINA_LAT},${OFICINA_LNG}`, '_blank', 'noopener');
    } else {
      document.getElementById('busquedas')?.scrollIntoView({ behavior: 'smooth' });
      setTimeout(() => {
        if (typeof mapaInstancia !== 'undefined' && mapaInstancia) {
          mapaInstancia.setView([OFICINA_LAT, OFICINA_LNG], 17);
        }
      }, 600);
    }
  });
}

/* Skeleton pulse */
const _styleEl = document.createElement('style');
_styleEl.textContent = '@keyframes pulse{0%,100%{opacity:1}50%{opacity:.45}}';
document.head.appendChild(_styleEl);
