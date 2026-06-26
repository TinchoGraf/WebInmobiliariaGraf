# Leonardograf Propiedades — Sitio web inmobiliario

Sitio web completo para **Leonardograf Propiedades**, Olavarría, Buenos Aires.  
Frontend estático (HTML / CSS / JS vanilla) + backend REST API (FastAPI + SQLite).

---

## Estructura del proyecto

```
WebParaInmobiliariaGraf/
├── index.html          # Página principal (hero, quiénes somos, búsquedas, contacto)
├── propiedad.html      # Detalle de propiedad (galería, mapa, WhatsApp)
├── admin/
│   └── index.html      # Panel de administración (login + CRUD completo)
├── css/
│   ├── style.css       # Variables globales, reset, utilidades
│   └── components/     # CSS por sección (navbar, hero, propiedades, etc.)
├── js/
│   ├── utils.js        # Helpers: formatearPrecio, generarLinkWhatsApp, etc.
│   ├── api.js          # Llamadas a la API REST (fetchPropiedades, fetchPropiedad)
│   ├── mapa.js         # Mapa Leaflet con marcadores por operación
│   └── main.js         # Punto de entrada: filtros, cards, contacto
├── assets/
│   └── images/         # Imágenes subidas desde el panel admin
└── backend/
    ├── main.py         # API FastAPI con 8 endpoints REST
    ├── models.py       # Modelo SQLAlchemy (tabla propiedades)
    ├── database.py     # Engine SQLite + sesión
    ├── seed.py         # Datos de ejemplo para desarrollo
    ├── requirements.txt
    └── .env.example    # Variables de entorno (usuario y contraseña admin)
```

---

## Cómo correr el proyecto localmente

### 1. Backend (FastAPI)

```bash
cd backend

# Crear entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows

# Instalar dependencias
pip install -r requirements.txt

# (Opcional) Copiar y editar variables de entorno
cp .env.example .env

# Cargar datos de ejemplo
python seed.py

# Iniciar servidor
uvicorn main:app --reload
```

La API queda disponible en `http://localhost:8000`.  
Documentación interactiva: `http://localhost:8000/docs`

### 2. Frontend

Abrí `index.html` directamente en el navegador **o** usá un servidor estático:

```bash
# Con Python
python -m http.server 5500

# Con Node.js
npx serve .

# Con VS Code: extensión "Live Server" → clic en "Go Live"
```

---

## Configuración rápida

### Número de WhatsApp

Editá la constante en **`js/utils.js`**, línea 161:

```js
const WPP_NUMERO = '5492284224338'; // formato: 54 + código área + número (sin 0 ni 15)
```

También actualizá los links `href="https://wa.me/5492284224338..."` en:
- `index.html` (navbar CTA, sección contacto, botón flotante)
- `propiedad.html` (botón flotante)
- `admin/index.html` (botón flotante)

### URL de la API (localhost → producción)

Editá **`js/api.js`**, línea 3:

```js
const API_BASE = 'http://localhost:8000'; // reemplazar con el dominio real al hacer deploy
```

### Datos del equipo

Editá directamente **`index.html`**, sección `#quienes-somos` (~líneas 185–240):
- Nombres, matrículas y fotos de los asesores
- Textos descriptivos de la agencia
- Links de LinkedIn

### Credenciales del panel admin

Creá el archivo **`backend/.env`** (basado en `.env.example`):

```env
ADMIN_USER=admin
ADMIN_PASSWORD=tu-contraseña-segura
DATABASE_URL=sqlite:///./inmobiliaria.db
```

---

## Panel de administración

Abrí `admin/index.html` con el backend corriendo.  
Credenciales por defecto: usuario `admin` / contraseña `cambiarme123`.

Funciones disponibles:
- Ver todas las propiedades (activas e inactivas)
- Crear, editar y eliminar propiedades
- Subida de fotos con drag & drop
- Selector de ubicación en mapa (Leaflet, centrado en Olavarría)
- Activar/pausar publicación con toggle
- Buscar por dirección, título o barrio

---

## Deploy

### Backend — Render.com (free tier)

1. Crear cuenta en [render.com](https://render.com)
2. **New → Web Service** → conectar repositorio GitHub
3. Configuración:
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. En **Environment Variables** agregar:
   - `ADMIN_USER` → tu usuario
   - `ADMIN_PASSWORD` → tu contraseña segura
5. Copiar la URL generada (ej: `https://lgraf-api.onrender.com`)
6. Actualizar `js/api.js`: `const API_BASE = 'https://lgraf-api.onrender.com'`

> El free tier de Render hiberna el servicio tras 15 min de inactividad. Para producción se recomienda un plan pago o VPS.

### Frontend — Netlify

1. Ir a [netlify.com](https://netlify.com) → **Sites → Add new site → Deploy manually**
2. Arrastrar la carpeta raíz del proyecto (todo menos la carpeta `backend/`)
3. El sitio queda publicado en `https://nombre-aleatorio.netlify.app`
4. Configurar dominio personalizado desde el panel de Netlify si se desea

---

## Endpoints de la API

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| GET | `/health` | No | Estado del servidor |
| GET | `/propiedades` | No | Listar propiedades activas (con filtros opcionales) |
| GET | `/propiedades?todas=true` | No | Incluye inactivas |
| GET | `/propiedades/{id}` | No | Detalle de una propiedad |
| POST | `/propiedades` | Sí | Crear propiedad |
| PUT | `/propiedades/{id}` | Sí | Editar propiedad |
| PATCH | `/propiedades/{id}/toggle` | Sí | Activar/pausar publicación |
| DELETE | `/propiedades/{id}` | Sí | Eliminar propiedad |
| POST | `/propiedades/{id}/imagenes` | Sí | Subir fotos |

Auth = HTTP Basic Authentication (usuario y contraseña definidos en `.env`)

---

## Tecnologías

- **Frontend**: HTML5, CSS3 (custom properties + grid + flexbox), JavaScript ES2022 — sin frameworks ni build tools
- **Mapa**: Leaflet.js 1.9.4 + OpenStreetMap (gratuito, sin API key)
- **Backend**: FastAPI + SQLAlchemy (sync) + SQLite
- **Fuentes**: Inter via Google Fonts
- **Deploy sugerido**: Render.com (backend) + Netlify (frontend)
