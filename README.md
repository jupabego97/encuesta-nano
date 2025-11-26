# Nanotronics Survey

Encuesta interactiva moderna para recopilar opiniones de clientes de Nanotronics.

## Características

- Interfaz moderna con diseño futurista
- 11 preguntas interactivas
- Soporte para dispositivos móviles (responsive)
- Navegación por teclado y gestos táctiles
- Backend Flask con API REST
- Almacenamiento de respuestas en JSON y CSV
- Listo para producción en Railway

## Requisitos

- Python 3.11+
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
```

5. Ejecutar en desarrollo:
```bash
python app.py
```

La aplicación estará disponible en `http://localhost:5000`

## Despliegue en Railway

### Opción 1: Desde GitHub

1. Acceder a [Railway](https://railway.app)
2. Conectar tu cuenta de GitHub
3. Crear nuevo proyecto → Deploy from GitHub repo
4. Seleccionar el repositorio `encuesta-nano`
5. Railway detectará automáticamente la configuración

### Opción 2: Usando Railway CLI

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

### Variables de Entorno en Railway

Configurar las siguientes variables en el panel de Railway:

| Variable | Descripción | Valor por defecto |
|----------|-------------|-------------------|
| `FLASK_ENV` | Ambiente de ejecución | `production` |
| `SECRET_KEY` | Clave secreta para sesiones | (generar una segura) |
| `ALLOWED_ORIGINS` | Orígenes CORS permitidos | `*` |
| `LOG_LEVEL` | Nivel de logging | `INFO` |
| `RATE_LIMIT_ENABLED` | Habilitar rate limiting | `true` |

Para generar un SECRET_KEY seguro:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## API Endpoints

### Endpoints de Salud

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/health` | GET | Health check básico |
| `/health/ready` | GET | Verificación de preparación |
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

## Estructura del Proyecto

```
encuesta-nano/
├── app.py              # Aplicación Flask principal
├── config.py           # Configuración centralizada
├── index.html          # Frontend de la encuesta
├── styles.css          # Estilos CSS
├── script.js           # Lógica JavaScript
├── requirements.txt    # Dependencias Python
├── Procfile           # Configuración para Heroku/Railway
├── railway.json       # Configuración específica de Railway
├── nixpacks.toml      # Configuración de build
├── runtime.txt        # Versión de Python
├── env.example.txt    # Ejemplo de variables de entorno
└── responses/         # Directorio de respuestas (no versionado)
    └── .gitkeep
```

## Características de Producción

- **Health Checks**: Endpoints `/health`, `/health/ready`, `/health/live`
- **Logging Estructurado**: Formato JSON para mejor integración con sistemas de monitoreo
- **Rate Limiting**: Protección contra abuso de API
- **Headers de Seguridad**: X-Content-Type-Options, X-Frame-Options, X-XSS-Protection
- **CORS Configurable**: Control de orígenes permitidos
- **Graceful Shutdown**: Apagado limpio de workers
- **Gunicorn Optimizado**: Workers multi-hilo para mejor rendimiento

## Desarrollo

### Ejecutar en modo desarrollo

```bash
FLASK_ENV=development python app.py
```

### Ejecutar con Gunicorn (simular producción)

```bash
gunicorn app:app --bind 0.0.0.0:5000 --workers 2 --threads 4
```

## Licencia

MIT License

## Autor

Nanotronics Team

