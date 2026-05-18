# Usamos una imagen ligera de Python oficial
FROM python:3.10-slim

# Evita que Python escriba archivos .pyc y fuerza el búfer de salida
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Configura el directorio de trabajo dentro del contenedor
WORKDIR /app

# Instala las dependencias del sistema necesarias para compilar paquetes
RUN apt-get update && apt-get install -y --no-install-recommends gcc libc-dev && rm -rf /var/lib/apt/lists/*

# Copia e instala los requerimientos de Python
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo el código de tu proyecto de la FES Aragón
COPY . /app/

# Expone el puerto nativo de desarrollo de Django
EXPOSE 8000

# Comando por defecto para arrancar el servidor
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]