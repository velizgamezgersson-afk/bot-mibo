# 1. Empezar desde una imagen de Python oficial
FROM python:3.11-slim

# 2. Instalar FFmpeg (¡SOLO FFMPEG!)
RUN apt-get update && apt-get install -y ffmpeg

# 3. Preparar la carpeta de trabajo
WORKDIR /app

# 4. Copiar el archivo de requisitos
COPY requirements.txt .

# 5. Instalar las librerías de Python
RUN pip install -r requirements.txt

# 6. Copiar todo el resto del código del bot
COPY . .

# 6.5. Exponer el puerto para Render (EL TRUCO)
EXPOSE 10000

# 7. El comando para iniciar el bot
CMD ["python", "main.py"]