# Dockerfile pour le service AI
FROM python:3.11-slim

# Installer les dépendances système nécessaires pour rembg
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Créer le répertoire de travail
WORKDIR /app

# Copier les fichiers de requirements
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Installer PyTorch CPU (plus léger que CUDA)
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Installer rembg et ses dépendances
RUN pip install --no-cache-dir \
    rembg[cli] \
    onnxruntime \
    scikit-image \
    pymatting \
    pooch \
    jsonschema \
    opencv-python-headless

# Installer les autres dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY . .

# Créer un utilisateur non-root
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Exposer le port
EXPOSE 8000

# Commande de démarrage
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]