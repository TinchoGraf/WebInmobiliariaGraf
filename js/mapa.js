/* mapa.js — mapa Leaflet centrado en Olavarría, Buenos Aires */

let mapaInstancia      = null;
const marcadoresPorId  = {};   // { [propId]: L.Marker }

/* ── Íconos ──────────────────────────────────── */

function _colorPorOperacion(operacion) {
  return (operacion === 'alquiler')                                              ? '#A00000'
       : (operacion === 'alquiler_temp' || operacion === 'alquiler_temporario') ? '#B71C1C'
       : '#EAB308';
}

function _iconoNormal(operacion) {
  const c = _colorPorOperacion(operacion);
  return L.divIcon({
    className: '',
    html: `<div style="
      background:${c};width:30px;height:30px;
      border-radius:50% 50% 50% 0;transform:rotate(-45deg);
      border:2.5px solid #fff;box-shadow:0 2px 8px rgba(0,0,0,0.28);
    "></div>`,
    iconSize:    [30, 30],
    iconAnchor:  [15, 30],
    popupAnchor: [0, -34],
  });
}

function _iconoResaltado(operacion) {
  const c = (operacion === 'alquiler')                                              ? '#C62828'
           : (operacion === 'alquiler_temp' || operacion === 'alquiler_temporario') ? '#D32F2F'
           : '#F9A825';
  return L.divIcon({
    className: '',
    html: `<div style="
      background:${c};width:40px;height:40px;
      border-radius:50% 50% 50% 0;transform:rotate(-45deg);
      border:3px solid #fff;box-shadow:0 4px 18px rgba(0,0,0,0.38);
    "></div>`,
    iconSize:    [40, 40],
    iconAnchor:  [20, 40],
    popupAnchor: [0, -44],
  });
}

/* ── Popup ───────────────────────────────────── */

function _crearPopupHtml(prop) {
  const precio    = formatearPrecio(prop.precio, prop.moneda || 'USD');
  const opLabels  = { venta: 'VENTA', alquiler: 'ALQUILER', alquiler_temp: 'TEMP.', alquiler_temporario: 'TEMP.' };
  const opClasses = { venta: '', alquiler: 'badge--alquiler', alquiler_temp: 'badge--temp', alquiler_temporario: 'badge--temp' };
  const opLabel   = opLabels[prop.operacion] || prop.operacion.toUpperCase();
  const opClass   = opClasses[prop.operacion] || '';
  const img       = (prop.imagenes && prop.imagenes[0]) || imagenPlaceholder(240, 140);
  const wppLink   = typeof generarLinkWhatsApp === 'function' ? generarLinkWhatsApp(prop) : '#';

  return `
    <div class="map-popup">
      <img class="map-popup__img" src="${img}" alt="${prop.titulo}" />
      <div class="map-popup__body">
        <span class="propiedad-card__badge ${opClass}" style="position:static;display:inline-block;margin-bottom:6px;font-size:10px">${opLabel}</span>
        <div class="map-popup__precio">${precio}</div>
        <div class="map-popup__dir">${prop.direccion || ''}</div>
        <div class="map-popup__actions">
          <a class="map-popup__btn" href="propiedad.html?id=${prop.id}">Ver más</a>
          <a class="map-popup__btn map-popup__btn--wpp"
             href="${wppLink}" target="_blank" rel="noopener noreferrer"
             aria-label="Consultar por WhatsApp">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>
          </a>
        </div>
      </div>
    </div>`;
}

/* ── Leyenda ─────────────────────────────────── */

function _agregarLeyenda() {
  const ctrl = L.control({ position: 'bottomleft' });
  ctrl.onAdd = function () {
    const div = L.DomUtil.create('div', 'mapa-leyenda');
    div.innerHTML =
      '<div class="mapa-leyenda__item"><span class="mapa-leyenda__dot" style="background:#A00000"></span>Alquiler</div>' +
      '<div class="mapa-leyenda__item"><span class="mapa-leyenda__dot" style="background:#EAB308"></span>Venta</div>';
    return div;
  };
  ctrl.addTo(mapaInstancia);
}

/* ── API pública ─────────────────────────────── */

function initMapa(propiedades = []) {
  if (!document.getElementById('map')) return;
  if (typeof L === 'undefined') { console.warn('Leaflet no cargó aún'); return; }

  mapaInstancia = L.map('map', {
    center:      [-36.8927, -60.3224],  // Olavarría, BA
    zoom:        13,
    zoomControl: true,
  });

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    maxZoom: 18,
  }).addTo(mapaInstancia);

  agregarMarcadores(propiedades);
  _agregarLeyenda();
}

function agregarMarcadores(propiedades) {
  if (!mapaInstancia) return;

  // Limpiar marcadores anteriores
  Object.values(marcadoresPorId).forEach(m => mapaInstancia.removeLayer(m));
  Object.keys(marcadoresPorId).forEach(k => delete marcadoresPorId[k]);

  propiedades.forEach(prop => {
    if (prop.lat == null || prop.lng == null) return;

    const marcador = L.marker([prop.lat, prop.lng], {
      icon: _iconoNormal(prop.operacion),
    })
      .bindPopup(_crearPopupHtml(prop), { maxWidth: 250, className: 'popup-custom' })
      .addTo(mapaInstancia);

    marcador._propOperacion = prop.operacion;
    marcadoresPorId[prop.id] = marcador;
  });

  const lista = Object.values(marcadoresPorId);
  if (lista.length === 1) {
    const p = propiedades.find(p => p.lat != null);
    if (p) mapaInstancia.setView([p.lat, p.lng], 15);
  } else if (lista.length > 1) {
    mapaInstancia.fitBounds(L.featureGroup(lista).getBounds().pad(0.18));
  } else {
    // Sin resultados: volver a Olavarría
    mapaInstancia.setView([-36.8927, -60.3224], 13);
  }
}

function resaltarMarcador(id) {
  const m = marcadoresPorId[id];
  if (!m) return;
  m.setIcon(_iconoResaltado(m._propOperacion));
  m.setZIndexOffset(500);
}

function limpiarResaltado() {
  Object.values(marcadoresPorId).forEach(m => {
    m.setIcon(_iconoNormal(m._propOperacion));
    m.setZIndexOffset(0);
  });
}

function actualizarMapa(propiedades) {
  if (!mapaInstancia) {
    initMapa(propiedades);
  } else {
    agregarMarcadores(propiedades);
  }
}
