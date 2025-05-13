# app/users/routes.py

from flask import request, jsonify
from functools import wraps
from flask_jwt_extended import jwt_required, get_jwt
from werkzeug.security import generate_password_hash

from . import users_bp
from ..extensions import db
from ..models import User, Role, Etudiant, Enseigne, Classe, Matiere
from .schemas import UserSchema

# Initialisation des schémas
user_schema = UserSchema()
users_schema = UserSchema(many=True)

# Décorateur pour accès administrateur uniquement
def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        if claims.get('role') != 'ADMIN':
            return jsonify({'message': 'Accès réservé aux administrateurs'}), 403
        return fn(*args, **kwargs)
    return wrapper

@users_bp.route('', methods=['GET'])
@admin_required
def list_users():
    """Liste tous les utilisateurs avec leurs détails"""
    users = User.query.options(
        db.joinedload(User.etudiant),
        db.joinedload(User.enseignant_matieres)
    ).all()
    return jsonify(users_schema.dump(users)), 200

@users_bp.route('/<int:user_id>', methods=['GET'])
@admin_required
def get_user(user_id):
    """Récupère un utilisateur par son ID"""
    user = User.query.options(
        db.joinedload(User.etudiant),
        db.joinedload(User.enseignant_matieres)
    ).get_or_404(user_id)
    return jsonify(user_schema.dump(user)), 200

@users_bp.route('', methods=['POST'])
@admin_required
def create_user():
    """
    Crée un nouvel utilisateur
    Exemple de payload:
    - Étudiant: {..., "role": "ÉTUDIANT", "matricule": "ETU123", "classe_id": 1}
    - Enseignant: {..., "role": "ENSEIGNANT", "matiere_ids": [1,2]}
    """
    data = request.get_json()
    errors = user_schema.validate(data)
    if errors:
        return jsonify(errors), 400

    # Vérification de l'unicité de l'email
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Cet email est déjà utilisé'}), 409

    # Validation du rôle
    role = Role.query.filter_by(name=data['role']).first()
    if not role:
        return jsonify({'message': 'Rôle invalide'}), 400

    # Création de l'utilisateur de base
    user = User(
        nom=data['nom'],
        email=data['email'],
        password_hash=generate_password_hash(data['password']),
        role_id=role.id
    )
    db.session.add(user)
    db.session.flush()  # Pour obtenir l'ID auto-généré

    # Création des relations spécifiques au rôle
    try:
        if data['role'] == 'ÉTUDIANT':
            _create_etudiant(user, data)  # <-- Correction: retirer 'self.'
        elif data['role'] == 'ENSEIGNANT':
            _create_enseignant(user, data)  # <-- Correction: retirer 'self.'
    except ValueError as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 400


    db.session.commit()
    return jsonify(user_schema.dump(user)), 201

def _create_etudiant(user, data):
    """Validation et création du profil étudiant"""
    if not data.get('matricule') or not data.get('classe_id'):
        raise ValueError('Matricule et classe_id requis pour un étudiant')
    
    if Etudiant.query.filter_by(matricule=data['matricule']).first():
        raise ValueError('Ce matricule est déjà utilisé')
    
    if not Classe.query.get(data['classe_id']):
        raise ValueError('Classe introuvable')
    
    etudiant = Etudiant(
        user_id=user.id,
        matricule=data['matricule'],
        classe_id=data['classe_id']
    )
    db.session.add(etudiant)

def _create_enseignant(user, data):
    """Validation et création des relations enseignant-matières"""
    matiere_ids = data.get('matiere_ids', [])
    if not isinstance(matiere_ids, list) or len(matiere_ids) == 0:
        raise ValueError('Liste de matiere_ids requise')
    
    for matiere_id in matiere_ids:
        if not Matiere.query.get(matiere_id):
            raise ValueError(f'Matière {matiere_id} introuvable')
        db.session.add(Enseigne(
            enseignant_id=user.id,
            matiere_id=matiere_id
        ))

@users_bp.route('/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    """Met à jour un utilisateur existant"""
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    errors = user_schema.validate(data, partial=True)
    if errors:
        return jsonify(errors), 400

    # Mise à jour des champs généraux
    if 'nom' in data:
        user.nom = data['nom']
    if 'email' in data and data['email'] != user.email:
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'message': 'Email déjà utilisé'}), 400
        user.email = data['email']
    if 'password' in data:
        user.password_hash = User.hash_password(data['password'])

    # Mise à jour des relations
    try:
        if user.role.name == 'ÉTUDIANT':
            _update_etudiant(user, data)  # <-- Correction: retirer 'self.'
        elif user.role.name == 'ENSEIGNANT':
            _update_enseignant(user, data)  # <-- Correction: retirer 'self.'
    except ValueError as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 400

    db.session.commit()
    return jsonify(user_schema.dump(user)), 200

def _update_etudiant(user, data):
    """Mise à jour du profil étudiant"""
    etudiant = user.etudiant
    if 'matricule' in data:
        if Etudiant.query.filter(Etudiant.matricule == data['matricule'], Etudiant.user_id != user.id).first():
            raise ValueError('Matricule déjà utilisé')
        etudiant.matricule = data['matricule']
    if 'classe_id' in data:
        if not Classe.query.get(data['classe_id']):
            raise ValueError('Classe introuvable')
        etudiant.classe_id = data['classe_id']

def _update_enseignant(user, data):
    """Mise à jour des matières enseignées"""
    if 'matiere_ids' in data:
        Enseigne.query.filter_by(enseignant_id=user.id).delete()
        for matiere_id in data['matiere_ids']:
            if not Matiere.query.get(matiere_id):
                raise ValueError(f'Matière {matiere_id} introuvable')
            db.session.add(Enseigne(
                enseignant_id=user.id,
                matiere_id=matiere_id
            ))

@users_bp.route('/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """Supprime un utilisateur et ses données associées"""
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'Utilisateur supprimé avec succès'}), 200