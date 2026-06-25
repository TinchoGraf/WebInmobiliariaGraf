# Leonardograf Propiedades — Web Inmobiliaria

Sitio web completo para inmobiliaria con frontend HTML/CSS/JS puro y backend FastAPI + SQLite.

## Estructura

```
WebParaInmobiliariaGraf/
├── index.html          # Página principal (hero + listado + mapa + contacto)
├── propiedad.html      # Detalle de propiedad individual
├── admin/index.html    # Panel administrativo
├── css/
│   ├── style.css           # Variables globales e imports
│   └── components/         # CSS por sección
├── js/
│   ├── main.js     # Lógica principal y cards
│   ├── api.js      # Fetch al backend (con datos demo de fallback)
│   ├── mapa.js     # Leaflet / OpenStreetMap
│   └── utils.js    # Navbar, hamburgesa, formateo
├── backend/
│   ├── main.py         # API FastAPI
│   ├── models.py       # Modelos SQLAlchemy
│   ├── database.py     # Configuración DB
│   ├── seed.py         # Datos de ejemplo
│   └── requirements.txt
└── assets/images/      # Imágenes de propiedades
```

## Inicio rápido

### Frontend (sin backend)
Abrí `index.html` directamente en el navegador o usá Live Server en VS Code.
Los datos de demo se cargan automáticamente si el backend no está disponible.

### Backend (FastAPI)
```bash
cd backend
pip install -r requirements.txt
python seed.py          # Carga datos de ejemplo
uvicorn main:app --reload
```
La API queda en `http://localhost:8000` — docs en `/docs`.

## Tecnologías
- **Frontend**: HTML5, CSS3 (variables + grid + flexbox), JavaScript ES2022 — sin frameworks
- **Mapa**: Leaflet + OpenStreetMap (gratuito)
- **Backend**: FastAPI + SQLAlchemy async + SQLite (reemplazable por PostgreSQL)
- **Fuentes**: Inter via Google Fonts
