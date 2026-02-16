# Sistema de Inventario - Django + Docker

Sistema completo de gestión de inventario construido con Django, Docker y tecnologías modernas.

## 🚀 Características

- **Gestión de Inventario**: Control completo de productos, categorías y stock
- **Reportes PDF**: Generación de reportes con ReportLab
- **API REST**: Backend con Django REST Framework
- **Documentación API**: Swagger/OpenAPI con drf-yasg
- **Tareas Asíncronas**: Celery + Redis para procesamiento en background
- **Exportación Excel**: Importación/exportación de datos con pandas y openpyxl
- **Interfaz Admin**: Panel de administración Django personalizado

## 🛠️ Tecnologías

- **Backend**: Django 4.2, Python 3.x
- **Base de Datos**: PostgreSQL
- **Cache/Tareas**: Redis + Celery
- **API**: Django REST Framework
- **Contenedores**: Docker + Docker Compose
- **Frontend**: Bootstrap 5 + Crispy Forms

## 📦 Estructura del Proyecto

```
SISTEMA-DE-INVENTARIO-DJANGO---DOCKER/
├── Dockerfile              # Imagen Docker de la app
├── docker-compose.yml       # Orquestación de servicios
├── entrypoint.sh           # Script de inicio
├── manage.py               # CLI de Django
├── requirements.txt        # Dependencias Python
├── .env.example            # Variables de entorno
└── [app Django]
```

## 🐳 Docker

### Servicios incluidos

- **web**: Aplicación Django
- **db**: PostgreSQL
- **redis**: Cache y broker de Celery
- **celery**: Worker de tareas asíncronas

### Comandos

```bash
# Iniciar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener servicios
docker-compose down
```

## 🔧 Configuración

1. Copiar `.env.example` a `.env`
2. Ajustar variables de entorno
3. Ejecutar `docker-compose up -d`

---

## 📄 Licencia

MIT — contribuciones bienvenidas 🚀

---

## 💻 Creado Por

🧑‍💻 Isaac Haro

Ingeniero en Sistemas · Full Stack · Automatización · Data

Isaac Esteban Haro Torres
- 📧 zackharo1@gmail.com
- 📱 098805517
- 💻 [GitHub](https://github.com/ieharo1)
