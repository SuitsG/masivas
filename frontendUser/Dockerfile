FROM ubuntu

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Python + venv
RUN apt update && apt upgrade -y && \
    apt install -y python3 python3-pip python3-venv && \
    apt clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 1) Copia primero requirements para usar caché
COPY requirements.txt .

# 2) Crea venv e instala deps dentro del venv
RUN python3 -m venv /app/venv && \
    /app/venv/bin/pip install --no-cache-dir -r requirements.txt

# 3) Asegura que 'python' y 'pip' usen el venv
ENV PATH="/app/venv/bin:${PATH}"

# 4) Copia el resto del código
COPY app.py .
COPY static ./static
COPY templates ./templates
COPY .env.example .env

EXPOSE 5000

# IMPORTANTE: tu app debe escuchar en 0.0.0.0 dentro del contenedor
# (en Flask: app.run(host="0.0.0.0", port=5000))
CMD ["python", "app.py"]
