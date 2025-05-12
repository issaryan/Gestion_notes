from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from functools import wraps

from ..extensions import db
from ..models import Classe, Matiere
from .schemas import ClasseSchema


# Blueprint pour les matières
matieres_bp = Blueprint('matieres', __name__)

# Schémas de sérialisation
classe_schema = ClasseSchema()
classes_schema = ClasseSchema(many=True)

# Décorateur pour restreindre l'accès aux administrateurs
def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        if claims.get('role') != 'ADMIN':
            return jsonify({'message': 'Accès refusé'}), 403
        return fn(*args, **kwargs)
    return wrapper

# === ROUTES POUR LES MATIÈRES ===

@matieres_bp.route('/matieres', methods=['GET'])
@jwt_required()
def get_matieres():
    """Récupère toutes les matières"""
    matieres = Matiere.query.all()
    out = [{"id": m.id, "nom": m.nom, "coeff": m.coeff} for m in matieres]
    return jsonify(out), 200

# === ROUTES POUR LES CLASSES ===

from . import classes_bp  # Ce blueprint doit déjà être défini dans __init__.py

@classes_bp.route('', methods=['GET'])
@admin_required
def list_classes():
    """Liste toutes les classes"""
    all_classes = Classe.query.all()
    return jsonify(classes_schema.dump(all_classes)), 200

@classes_bp.route('/<int:class_id>', methods=['GET'])
@admin_required
def get_class(class_id):
    """Récupère une classe par son ID"""
    classe = Classe.query.get_or_404(class_id)
    return jsonify(classe_schema.dump(classe)), 200

@classes_bp.route('', methods=['POST'])
@admin_required
def create_class():
    """Crée une nouvelle classe"""
    data = request.get_json() or {}
    errors = classe_schema.validate(data)
    if errors:
        return jsonify(errors), 400

    new_classe = Classe(**data)
    db.session.add(new_classe)
    db.session.commit()

    return jsonify(classe_schema.dump(new_classe)), 201

@classes_bp.route('/<int:class_id>', methods=['PUT'])
@admin_required
def update_class(class_id):
    """Met à jour une classe existante"""
    classe = Classe.query.get_or_404(class_id)
    data = request.get_json() or {}
    errors = classe_schema.validate(data, partial=True)
    if errors:
        return jsonify(errors), 400

    if 'nom' in data:
        classe.nom = data['nom']
    db.session.commit()

    return jsonify(classe_schema.dump(classe)), 200

@classes_bp.route('/<int:class_id>', methods=['DELETE'])
@admin_required
def delete_class(class_id):
    """Supprime une classe"""
    classe = Classe.query.get_or_404(class_id)
    db.session.delete(classe)
    db.session.commit()

    return jsonify({'message': 'Classe supprimée'}), 200
