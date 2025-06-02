# Usa una imagen oficial con Python 3.12.3
FROM python:3.12.3-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos del proyecto
COPY . .

# Instala dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Comando por defecto para ejecutar tu script
CMD ["python", "idealista_monitor.py"]
