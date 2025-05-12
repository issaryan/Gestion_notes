from flask import Blueprint

# Création du blueprint en premier
matiere_bp = Blueprint(
    'matiere',
    __name__,
    url_prefix='/matieres',
    template_folder='templates'
)

# Import des routes APRÈS la création du blueprint pour éviter les dépendances circulaires
from . import routes

__all__ = ['matiere_bp']
