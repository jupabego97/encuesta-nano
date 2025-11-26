# Nanotronics Survey

Encuesta interactiva moderna para recopilar opiniones de clientes de Nanotronics.

## Características

- Interfaz moderna con diseño futurista
- 11 preguntas interactivas
- Soporte para dispositivos móviles (responsive)
- Navegación por teclado y gestos táctiles
- Backend Flask con API REST
- **Base de datos PostgreSQL** para persistencia
- Fallback a almacenamiento en archivos si no hay BD
- Listo para producción en Railway

## Requisitos

- Python 3.11+
- PostgreSQL (opcional, recomendado para producción)
- pip

## Instalación Local

1. Clonar el repositorio:
```bash
git clone https://github.com/jupabego97/encuesta-nano.git
cd encuesta-nano
```

2. Crear entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno:
```bash
# Copiar el archivo de ejemplo
cp env.example.txt .env

# Editar .env con tus valores
# Importante: configurar DATABASE_URL si usas PostgreSQL
```

5. Ejecutar en desarrollo:
```bash
python app.py
```

La aplicación estará disponible en `http://localhost:5000`

## Despliegue en Railway

### Paso 1: Crear el proyecto

1. Acceder a [Railway](https://railway.app)
2. Conectar tu cuenta de GitHub
3. Crear nuevo proyecto → Deploy from GitHub repo
4. Seleccionar el repositorio `encuesta-nano`

### Paso 2: Agregar PostgreSQL

1. En el proyecto de Railway, click en **"+ New"**
2. Seleccionar **"Database"** → **"Add PostgreSQL"**
3. Railway creará la base de datos y configurará automáticamente `DATABASE_URL`

### Paso 3: Conectar la aplicación a la base de datos

1. Click en tu servicio de la aplicación
2. Ir a **"Variables"**
3. Click en **"Add Reference"** → seleccionar la variable `DATABASE_URL` del servicio PostgreSQL
4. Railway conectará automáticamente la app con la BD

### Paso 4: Configurar variables adicionales (opcional)

| Variable | Descripción | Valor por defecto |
|----------|-------------|-------------------|
| `FLASK_ENV` | Ambiente de ejecución | `production` |
| `SECRET_KEY` | Clave secreta para sesiones | (generar una segura) |
| `ALLOWED_ORIGINS` | Orígenes CORS permitidos | `*` |
| `LOG_LEVEL` | Nivel de logging | `INFO` |

Para generar un SECRET_KEY seguro:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Usando Railway CLI

```bash
# Instalar Railway CLI
npm install -g @railway/cli

# Iniciar sesión
railway login

# Vincular proyecto
railway link

# Desplegar
railway up
```

## Base de Datos

### Esquema

La tabla `survey_responses` almacena todas las respuestas:

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | Integer | ID único autoincremental |
| created_at | DateTime | Fecha de creación |
| q1_time_known | String | Tiempo conociendo Nanotronics |
| q3_experience | String | Experiencia de compra |
| q6_staff_rating | Integer | Calificación del personal (1-5) |
| q10_trust | Integer | Nivel de confianza (1-5) |
| raw_data | Text | JSON completo de la respuesta |
| ... | ... | (más campos para cada pregunta) |

### Acceder a los datos

**Desde Railway:**
1. Click en el servicio PostgreSQL
2. Click en **"Data"** para ver las tablas
3. O usa **"Connect"** para obtener la cadena de conexión

**Desde la API:**
```bash
# Obtener todas las respuestas
curl https://tu-app.railway.app/api/responses

# Obtener estadísticas
curl https://tu-app.railway.app/api/stats
```

## API Endpoints

### Endpoints de Salud

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/health` | GET | Health check básico |
| `/health/ready` | GET | Verificación de preparación (incluye BD) |
| `/health/live` | GET | Verificación de vida |

### Endpoints de la Encuesta

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/` | GET | Página principal de la encuesta |
| `/api/submit` | POST | Enviar respuestas de la encuesta |
| `/api/responses` | GET | Obtener todas las respuestas |
| `/api/stats` | GET | Obtener estadísticas |
| `/api/info` | GET | Información de la aplicación |

### Ejemplo de Envío

```bash
curl -X POST https://tu-app.railway.app/api/submit \
  -H "Content-Type: application/json" \
  -d '{"q1": "1_6_meses", "q3": "excelente"}'
```

### Ejemplo de Respuesta

```json
{
  "success": true,
  "message": "¡Respuesta guardada correctamente!",
  "id": "42"
}
```

## Estructura del Proyecto

```
encuesta-nano/
├── app.py              # Aplicación Flask principal
├── config.py           # Configuración centralizada
├── models.py           # Modelos de base de datos (SQLAlchemy)
├── index.html          # Frontend de la encuesta
├── styles.css          # Estilos CSS
├── script.js           # Lógica JavaScript
├── requirements.txt    # Dependencias Python
├── Procfile           # Configuración para Railway
├── railway.json       # Configuración específica de Railway
├── runtime.txt        # Versión de Python
├── env.example.txt    # Ejemplo de variables de entorno
└── responses/         # Directorio de respuestas (fallback)
    └── .gitkeep
```

## Características de Producción

- **PostgreSQL**: Base de datos persistente
- **Health Checks**: Endpoints `/health`, `/health/ready`, `/health/live`
- **Logging Estructurado**: Formato JSON para mejor integración
- **Rate Limiting**: Protección contra abuso de API
- **Headers de Seguridad**: X-Content-Type-Options, X-Frame-Options
- **CORS Configurable**: Control de orígenes permitidos
- **Fallback Storage**: Si no hay BD, usa archivos (datos efímeros)

## Desarrollo Local con PostgreSQL

1. Instalar PostgreSQL localmente
2. Crear base de datos:
```bash
createdb encuesta_nano
```

3. Configurar `.env`:
```
DATABASE_URL=postgresql://usuario:password@localhost:5432/encuesta_nano
```

4. Ejecutar la aplicación:
```bash
python app.py
```

Las tablas se crearán automáticamente al iniciar.

## Licencia

MIT License

## Autor

Nanotronics Team
