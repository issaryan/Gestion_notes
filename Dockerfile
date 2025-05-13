# Étape 1 : image de base
FROM python:3.11-slim

# Étape 2 : définition du répertoire de travail
WORKDIR /app

# Étape 3 : copier les fichiers dans le conteneur
COPY . /app

# Étape 4 : installer les dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    libmariadb-dev \
    libmariadb-dev-compat \
    && rm -rf /var/lib/apt/lists/*

# Étape 5 : installer les dépendances Python
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Étape 6 : exposer le port (par défaut Flask = 5001)
EXPOSE 5001

# Étape 7 : définir la variable d'environnement pour Flask
ENV FLASK_APP=run.py
ENV FLASK_ENV=production

# Étape 8 : point d'entrée (commande par défaut)
CMD ["gunicorn", "-b", "0.0.0.0:5001", "manage:app"]
