# app/reports/__init__.py

from flask import Blueprint

# Création du blueprint "reports"
reports_bp = Blueprint('reports', __name__)

# Import des routes pour que Flask les enregistre
from . import routes
