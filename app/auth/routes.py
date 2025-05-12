# app/auth/routes.py
from flask import request, jsonify, current_app
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    get_jwt,
    jwt_required
)
from datetime import timedelta
from functools import wraps
from sqlalchemy.exc import SQLAlchemyError 
import re

from . import auth_bp
from ..models import User, Role, Etudiant, Classe, Enseigne, Matiere
from ..extensions import db
from werkzeug.security import generate_password_hash

# Décorateur personnalisé pour vérifier les rôles
def check_roles(*allowed_roles):
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            if claims.get('role') not in allowed_roles:
                return jsonify({"message": "Action non autorisée pour ce rôle"}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Authentification d'un utilisateur
    """
    data = request.get_json() or {}
    
    # Validation des champs obligatoires
    if not data.get('email') or not data.get('password'):
        return jsonify({"message": "Email et mot de passe requis"}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({"message": "Email ou mot de passe incorrect"}), 401
    
    # Correction : Convertir l'identity en string
    access_token = create_access_token(
        identity=str(user.id),  # <-- Correction ici
        additional_claims={
            'id': user.id,
            'role': user.role.name,
            'nom': user.nom
        },
        expires_delta=timedelta(hours=8))

    return jsonify(access_token=access_token), 200

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Création d'un compte utilisateur avec gestion sécurisée des admins
    """
    try:
        data = request.get_json() or {}
        if not data:
            return jsonify({"message": "Aucune donnée fournie"}), 400

        # Vérification des champs obligatoires
        required_fields = ['nom', 'email', 'password']
        if missing := [field for field in required_fields if field not in data]:
            return jsonify({"message": f"Champs manquants: {', '.join(missing)}"}), 400

        # Validation de l'email
        if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", data['email']):
            return jsonify({"message": "Format d'email invalide"}), 400

        # Politique de mot de passe robuste
        password = data['password']
        if len(password) < 12 \
            or not re.search(r"\d", password) \
            or not re.search(r"[A-Z]", password) \
            or not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return jsonify({
                "message": "Le mot de passe doit contenir : 12+ caractères, 1 majuscule, 1 chiffre et 1 caractère spécial"
            }), 400

        # Vérification de l'unicité de l'email
        if User.query.filter_by(email=data['email'].lower().strip()).first():
            return jsonify({"message": "Cet email est déjà utilisé"}), 409

        # Gestion des permissions admin
        provided_key = request.headers.get('X-ADMIN-SECRET', '').strip()
        expected_key = current_app.config.get('ADMIN_SECRET_KEY', '').strip()
        is_admin = False

        if provided_key and provided_key == expected_key:
            role_name = 'ADMIN'
            admin_role = Role.query.filter_by(name=role_name).first()
            
            if not admin_role:
                admin_role = Role(name=role_name)
                db.session.add(admin_role)
                db.session.flush()
            
            role = admin_role
            is_admin = True
        else:
            role_name = data.get('role', 'ETUDIANT').upper()
            role = Role.query.filter_by(name=role_name).first()
                
            if not role:
                valid_roles = [r.name for r in Role.query.all()]
                return jsonify({
                    "message": f"Rôle invalide. Valides: {', '.join(valid_roles)}"
                }), 400
                    
            if role_name == 'ADMIN':
                return jsonify({"message": "Création admin non autorisée"}), 403

        # Création de l'utilisateur
        new_user = User(
            nom=data['nom'].strip(),
            email=data['email'].lower().strip(),
            role=role,
            password_hash=generate_password_hash(password)
        )
        db.session.add(new_user)
        db.session.flush()

        # Création des profils spécifiques (sauf pour admin)
        if not is_admin:
            try:
                if role.name == 'ETUDIANT':
                    create_etudiant_profile(new_user, data)
                elif role.name == 'ENSEIGNANT':
                    create_enseignant_profile(new_user, data)
            except ValueError as e:
                db.session.rollback()
                return jsonify({"message": str(e)}), 400

        db.session.commit()

        return jsonify({
            "id": new_user.id,
            "nom": new_user.nom,
            "email": new_user.email,
            "role": role.name,
            "message": "Administrateur créé" if is_admin else "Utilisateur créé"
        }), 201

    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Erreur DB: {str(e)}", exc_info=True)
        return jsonify({"message": "Erreur de création d'utilisateur"}), 500
        
    except Exception as e:
        current_app.logger.error(f"Erreur critique: {str(e)}", exc_info=True)
        return jsonify({"message": "Erreur interne du serveur"}), 500

def create_etudiant_profile(user, data):
    """Crée le profil étudiant"""
    required_fields = ['matricule', 'classe_id']
    if any(field not in data for field in required_fields):
        raise ValueError(f"Champs requis pour étudiant: {', '.join(required_fields)}")
    
    if Etudiant.query.filter_by(matricule=data['matricule']).first():
        raise ValueError("Ce matricule est déjà utilisé")
    
    if not Classe.query.get(data['classe_id']):
        raise ValueError("Classe introuvable")
    
    etudiant = Etudiant(
        user_id=user.id,
        matricule=data['matricule'],
        classe_id=data['classe_id']
    )
    db.session.add(etudiant)

def create_enseignant_profile(user, data):
    """Crée les associations enseignant-matières"""
    if 'matiere_ids' not in data or not isinstance(data['matiere_ids'], list):
        raise ValueError("Liste matiere_ids requise")
    
    valid_matiere_ids = [
        m.id for m in Matiere.query.filter(Matiere.id.in_(data['matiere_ids'])).all()
    ]
    if len(valid_matiere_ids) != len(data['matiere_ids']):
        raise ValueError("Un ou plusieurs matiere_ids invalides")
    
    for matiere_id in valid_matiere_ids:
        db.session.add(Enseigne(
            enseignant_id=user.id,
            matiere_id=matiere_id
        ))

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    Récupère les informations de l'utilisateur connecté
    """
    # Correction : Conversion de l'identity en int
    user_id = int(get_jwt_identity())  # <-- Correction ici
    claims = get_jwt()
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "Utilisateur non trouvé"}), 404
    
    response_data = {
        'id': user.id,
        'nom': user.nom,
        'email': user.email,
        'role': claims.get('role')
    }
    
    if claims.get('role') == 'ETUDIANT' and user.etudiant:
        response_data.update({
            'matricule': user.etudiant.matricule,
            'classe_id': user.etudiant.classe_id
        })
    elif claims.get('role') == 'ENSEIGNANT' and user.enseignant_matieres:
        response_data['matieres'] = [e.matiere_id for e in user.enseignant_matieres]
    
    return jsonify(response_data), 200
