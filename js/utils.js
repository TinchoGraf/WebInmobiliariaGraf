/* utils.js — helpers generales */

/**
 * Formatea un número como precio en pesos o dólares.
 * @param {number} valor
 * @param {string} moneda  'ARS' | 'USD'
 */
function formatearPrecio(valor, moneda = 'USD') {
  const opciones = {
    style: 'currency',
    currency: moneda,
    maximumFractionDigits: 0,
  };
  return new Intl.NumberFormat('es-AR', opciones).format(valor);
}

/**
 * Recorta un string a maxLen caracteres y agrega '…'.
 * @param {string} texto
 * @param {number} maxLen
 */
function truncar(texto, maxLen = 60) {
  if (!texto || texto.length <= maxLen) return texto;
  return texto.slice(0, maxLen).trimEnd() + '…';
}

/**
 * Debounce simple.
 * @param {Function} fn
 * @param {number} delay
 */
function debounce(fn, delay = 300) {
  let timer;
  return function (...args) {
    clearTimeout(timer);
    timer = setTimeout(() => fn.apply(this, args), delay);
  };
}

/**
 * Retorna un placeholder SVG en data-URI para imágenes faltantes.
 */
function imagenPlaceholder(width = 400, height = 280) {
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}">
    <rect width="${width}" height="${height}" fill="#F7F7F5"/>
    <path d="M${width/2-30} ${height/2+20}L${width/2} ${height/2-20}L${width/2+30} ${height/2+20}Z" fill="#CBD5E1"/>
    <rect x="${width/2-20}" y="${height/2+10}" width="40" height="10" fill="#CBD5E1"/>
  </svg>`;
  return `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`;
}

/**
 * Agrega la clase 'scrolled' al navbar cuando hay scroll vertical.
 */
function initNavbarScroll() {
  const navbar = document.getElementById('navbar');
  if (!navbar) return;
  const onScroll = () => {
    navbar.classList.toggle('scrolled', window.scrollY > 20);
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
}

/**
 * Inicializa el menú hamburguesa.
 */
function initHamburguesa() {
  const toggle = document.getElementById('navToggle');
  const menu   = document.getElementById('navMenu');
  if (!toggle || !menu) return;

  toggle.addEventListener('click', () => {
    const isOpen = toggle.classList.toggle('open');
    menu.classList.toggle('open', isOpen);
    toggle.setAttribute('aria-expanded', String(isOpen));
    toggle.setAttribute('aria-label', isOpen ? 'Cerrar menú' : 'Abrir menú');
    document.body.style.overflow = isOpen ? 'hidden' : '';
  });

  // Cerrar al hacer click en un link del menú
  menu.querySelectorAll('.navbar__link').forEach(link => {
    link.addEventListener('click', () => {
      toggle.classList.remove('open');
      menu.classList.remove('open');
      toggle.setAttribute('aria-expanded', 'false');
      toggle.setAttribute('aria-label', 'Abrir menú');
      document.body.style.overflow = '';
    });
  });

  // Cerrar con Escape
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && menu.classList.contains('open')) {
      toggle.click();
    }
  });
}

/**
 * Observa elementos .fade-up y agrega .visible cuando entran al viewport.
 */
function initScrollReveal() {
  const targets = document.querySelectorAll('.fade-up');
  if (!targets.length) return;

  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12 });

  targets.forEach(el => observer.observe(el));
}

/**
 * Anima números de 0 hasta el valor data-target cuando entran al viewport.
 * Elemento: <span class="count-up" data-target="150" data-prefix="+" data-suffix=""></span>
 */
function initCounters() {
  const counters = document.querySelectorAll('.count-up');
  if (!counters.length) return;

  const easeOut = t => 1 - Math.pow(1 - t, 3);

  const animate = (el) => {
    const target   = parseInt(el.dataset.target, 10);
    const duration = 1600;
    const start    = performance.now();
    const prefix   = el.dataset.prefix || '';
    const suffix   = el.dataset.suffix || '';

    const tick = (now) => {
      const elapsed  = now - start;
      const progress = Math.min(elapsed / duration, 1);
      const value    = Math.round(easeOut(progress) * target);
      el.textContent = prefix + value + suffix;
      if (progress < 1) requestAnimationFrame(tick);
    };

    requestAnimationFrame(tick);
  };

  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        animate(entry.target);
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.4 });

  counters.forEach(el => observer.observe(el));
}

/* ── WhatsApp ────────────────────────────────── */

const WPP_NUMERO = '5492284224338'; // reemplazá con el número real

/**
 * Genera un link de WhatsApp con mensaje pre-cargado para una propiedad.
 * @param {{ id: number, titulo: string }} propiedad
 */
function generarLinkWhatsApp(propiedad) {
  const linkPropiedad = `${window.location.origin}/propiedad.html?id=${propiedad.id}`;
  const mensaje = `Hola, me interesa la propiedad "${propiedad.titulo}" que vi en ${linkPropiedad}, quisiera más información.`;
  return `https://wa.me/${WPP_NUMERO}?text=${encodeURIComponent(mensaje)}`;
}

/**
 * Resalta el link activo según el scroll de secciones.
 */
function initActiveSections() {
  const sections = document.querySelectorAll('section[id]');
  const links    = document.querySelectorAll('.navbar__link[href^="#"]');
  if (!sections.length || !links.length) return;

  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      links.forEach(link => {
        const href = link.getAttribute('href').slice(1);
        link.classList.toggle('active', href === entry.target.id);
      });
    });
  }, { rootMargin: '-40% 0px -55% 0px' });

  sections.forEach(s => observer.observe(s));
}
