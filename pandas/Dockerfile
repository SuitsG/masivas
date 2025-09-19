FROM ubuntu

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt update && apt upgrade -y && \
    apt install -y python3 python3-pip python3-venv sudo && \
    apt clean && rm -rf /var/lib/apt/lists/*

# Crear usuario vscode para compatibilidad con devcontainer
RUN useradd -ms /bin/bash vscode && \
    usermod -aG sudo vscode && \
    echo 'vscode ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

# Cambiar a usuario vscode antes de instalar paquetes Python
USER vscode
WORKDIR /workspace

# Crear entorno virtual y instalar paquetes
RUN python3 -m venv /home/vscode/venv && \
    /home/vscode/venv/bin/pip install --upgrade pip && \
    /home/vscode/venv/bin/pip install jupyterlab ipykernel pandas numpy matplotlib seaborn sqlalchemy pymysql psycopg2-binary

# Asegurar que el entorno virtual esté en el PATH
ENV PATH="/home/vscode/venv/bin:$PATH"

# Copiar archivos del proyecto
COPY --chown=vscode:vscode conexiones /workspace/conexiones
COPY --chown=vscode:vscode functions /workspace/functions
COPY --chown=vscode:vscode notebooks /workspace/notebooks
COPY --chown=vscode:vscode data /workspace/data
COPY --chown=vscode:vscode src /workspace/src

# Configurar Jupyter
ENV JUPYTER_TOKEN=admin123

# Exponer puerto
EXPOSE 5020

# Comando por defecto
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=5020", "--no-browser", "--allow-root"]
