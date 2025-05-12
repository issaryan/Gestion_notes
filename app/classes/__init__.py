# app/classes/__init__.py

from flask import Blueprint

# Création du blueprint "classes"
classes_bp = Blueprint('classes', __name__)

# Import des routes après la création du blueprint pour éviter les dépendances circulaires
from . import routes