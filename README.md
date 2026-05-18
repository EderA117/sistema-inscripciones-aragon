# Sistema de Inscripciones - FES Aragón 🏫💻

Este es un sistema robusto de gestión de inscripciones desarrollado con **Django** como framework de backend y **PostgreSQL** como motor de bases de datos, todo completamente contenedorizado utilizando **Docker** y **Docker Compose**.

## 🚀 Requisitos Previos

Antes de comenzar, asegúrate de tener instalado en tu computadora:
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) (con soporte para WSL2 en Windows).
* [Git](https://git-scm.com/).

---

## 🛠️ Pasos para Desplegar el Proyecto

Sigue estas instrucciones exactas para descargar, compilar y ejecutar todo el entorno de forma automática:

### 1. Clonar el repositorio
Abre una terminal en tu máquina local y clona este proyecto:
```bash
git clone https://github.com/EderA117/sistema-inscripciones-aragon.git
cd sistema-inscripciones-aragon
```

2. Construir y levantar los contenedores
Ejecuta el siguiente comando para compilar la imagen de Django e inicializar de forma limpia los volúmenes de las bases de datos transaccionales y de catálogos:
```bash
docker-compose up --build
```

3. Aplicar las migraciones del sistema
Una vez que veas en la terminal que los servidores están listos, abre una nueva terminal (sin apagar la anterior) y ejecuta las migraciones de Django para dibujar las tablas de administración internas:

```bash
docker-compose exec web python manage.py migrate
```

Accesos del Sistema
Una vez completados los pasos anteriores, podrás acceder a las siguientes plataformas locales:

Panel del Alumno (Inscripciones): http://localhost:8000/

Panel de Administración (Django Admin): http://localhost:8000/admin


Si deseas crear un administrador nuevo y personalizado, ejecuta:
```bash
docker-compose exec web python manage.py createsuperuser
```

Estructura de la Arquitectura Distribuida
El entorno levanta automáticamente tres servicios interconectados en una red virtual aislada:

web: Servidor de desarrollo Django (Puerto 8000).

db_default: Base de datos transaccional PostgreSQL para persistencia de inscripciones (Puerto 5432).

db_staging: Base de datos de catálogos y horarios escolares para lectura distribuida (Puerto 5433).
