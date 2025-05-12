# manage.py

from flask import Flask
from flask_migrate import Migrate
from app import create_app
from config import DevConfig
from app.extensions import db
from app import models
# Dans votre fichier app.py (configuration minimale sécurisée pour les tests)
import os


# Crée l'application avec la configuration de développement
app = create_app(DevConfig)
app.config['ADMIN_SECRET_KEY'] = os.getenv('ADMIN_SECRET_KEY', 'clé_temporaire_pour_dev_123')

# Configure la migration
migrate = Migrate(app, db)

if __name__ == '__main__':
    app.run()
