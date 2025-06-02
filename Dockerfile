#only for fly.io

# Usa una imagen oficial de Python 3.12
FROM python:3.12-slim

# Establece directorio de trabajo
WORKDIR /app

# Copia requirements e instala dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto de los archivos del proyecto
COPY . .

# Expón el puerto (opcional si no usas web)
EXPOSE 8080

# Comando por defecto
CMD ["python", "idealista_monitor.py"]
