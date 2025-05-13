from flask import jsonify, request
from . import matiere_bp  # Import relatif du blueprint
from ..models import Matiere
from ..extensions import db

# Import différé des schémas dans les fonctions concernées
def get_schemas():
    """Charge les schémas Marshmallow uniquement quand nécessaire"""
    from ..schemas.common import error_response_schema
    from .schemas import matiere_schema
    return matiere_schema, error_response_schema

@matiere_bp.route('/', methods=['GET'])
def list_matieres():
    """Liste toutes les matières"""
    matieres = Matiere.query.all()
    return jsonify([{
        'id': m.id,
        'nom': m.nom,
        'coefficient': m.coeff
    } for m in matieres])

@matiere_bp.route('/', methods=['POST'])
def create_matiere():
    """Crée une nouvelle matière"""
    matiere_schema, error_schema = get_schemas()
    
    data = request.get_json()
    
    # Validation des données
    errors = matiere_schema.validate(data)
    if errors:
        return jsonify(error_schema.dump({'message': errors})), 400
    
    # Création de la matière
    nouvelle_matiere = Matiere(
        nom=data['nom'],
        coeff=data.get('coefficient', 1)
    )
    
    try:
        db.session.add(nouvelle_matiere)
        db.session.commit()
        return jsonify(matiere_schema.dump(nouvelle_matiere)), 201
    except Exception as e:
        db.session.rollback()
        return jsonify(error_schema.dump({'message': str(e)})), 500

@matiere_bp.route('/<int:id>', methods=['GET'])
def get_matiere(id):
    """Récupère une matière par son ID"""
    matiere = Matiere.query.get_or_404(id)
    return jsonify({
        'id': matiere.id,
        'nom': matiere.nom,
        'coefficient': matiere.coeff
    })

@matiere_bp.route('/<int:id>', methods=['PUT'])
def update_matiere(id):
    """Met à jour une matière existante"""
    matiere_schema, error_schema = get_schemas()
    
    matiere = Matiere.query.get_or_404(id)
    data = request.get_json()
    
    # Validation
    errors = matiere_schema.validate(data)
    if errors:
        return jsonify(error_schema.dump({'message': errors})), 400
    
    try:
        matiere.nom = data['nom']
        matiere.coeff = data.get('coefficient', matiere.coeff)
        db.session.commit()
        return jsonify(matiere_schema.dump(matiere))
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@matiere_bp.route('/<int:id>', methods=['DELETE'])
def delete_matiere(id):
    """Supprime une matière"""
    matiere = Matiere.query.get_or_404(id)

    # 🔒 Vérifie si un enseignant est lié à cette matière
    if matiere.enseignants.count() > 0:
        return jsonify({'message': 'Suppression impossible : des enseignants sont liés à cette matière.'}), 400

    # 🔒 Vérifie si des notes existent pour cette matière
    if len(matiere.notes) > 0:
        return jsonify({'message': 'Suppression impossible : des notes existent pour cette matière.'}), 400

    db.session.delete(matiere)
    db.session.commit()
    return jsonify({'message': 'Matière supprimée avec succès'}), 200

