# app/auth/__init__.py

from flask import Blueprint

# Création du blueprint "auth"
auth_bp = Blueprint('auth', __name__)

# Import des routes pour que Flask les enregistre
from . import routes
