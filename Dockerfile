# Imagen base de Python
FROM python:3.12-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos del proyecto
COPY . .

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto del microservicio Flask
EXPOSE 5000

# Ejecuta el microservicio
CMD ["python", "app.py"]