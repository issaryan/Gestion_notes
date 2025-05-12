# app/notes/__init__.py

from flask import Blueprint

# Création du blueprint “notes”
notes_bp = Blueprint('notes', __name__)

# Import des routes pour que Flask les enregistre
from . import routes
