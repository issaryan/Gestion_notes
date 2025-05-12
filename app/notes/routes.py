# app/notes/routes.py

from flask import request, jsonify
from functools import wraps
import pandas as pd
from flask_jwt_extended import jwt_required, get_jwt

from . import notes_bp
from ..extensions import db
from ..models import Note, Etudiant, Matiere, Enseigne
from .schemas import NoteSchema

# Schémas
note_schema = NoteSchema()
notes_schema = NoteSchema(many=True)

# Décorateurs de rôle
def teacher_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        if claims.get('role') != 'ENSEIGNANT':
            return jsonify({'message': 'Accès réservé aux enseignants'}), 403
        return fn(*args, **kwargs)
    return wrapper

@notes_bp.route('', methods=['GET'])
@jwt_required()
def list_notes():
    """Liste les notes de l'étudiant connecté"""
    claims = get_jwt()
    
    if claims.get('role') != 'ÉTUDIANT':
        return jsonify({'message': 'Accès réservé aux étudiants'}), 403

    etu = Etudiant.query.filter_by(user_id=claims.get('sub')).first()
    if not etu:
        return jsonify({'message': 'Profil étudiant introuvable'}), 404

    notes = Note.query.filter_by(etudiant_id=etu.id).all()
    return jsonify(notes_schema.dump(notes)), 200

@notes_bp.route('', methods=['POST'])
@teacher_required
def add_note():
    """Saisie manuelle d'une note par un enseignant"""
    data = request.get_json() or {}
    errors = note_schema.validate(data)
    if errors:
        return jsonify(errors), 400

    # Vérifier l'étudiant
    etu = Etudiant.query.filter_by(matricule=data['matricule']).first()
    if not etu:
        return jsonify({'message': 'Matricule étudiant invalide'}), 404

    # Vérifier que l'enseignant a le droit de noter cette matière
    enseignant_id = get_jwt().get('sub')
    if not Enseigne.query.filter_by(
        enseignant_id=enseignant_id,
        matiere_id=data['matiere_id']
    ).first():
        return jsonify({'message': 'Vous ne pouvez pas noter cette matière'}), 403

    # Créer la note
    note = Note(
        etudiant_id=etu.id,
        matiere_id=data['matiere_id'],
        note=data['note']
    )
    db.session.add(note)
    db.session.commit()

    return jsonify(note_schema.dump(note)), 201

@notes_bp.route('/import', methods=['POST'])
@teacher_required
def import_notes():
    """Import de notes via fichier CSV/Excel"""
    if 'file' not in request.files:
        return jsonify({'message': 'Aucun fichier fourni'}), 400

    f = request.files['file']
    enseignant_id = get_jwt().get('sub')
    errors = []
    created = []

    try:
        # Lire le fichier
        df = pd.read_csv(f) if f.filename.endswith('.csv') else pd.read_excel(f)
        
        # Vérifier les colonnes obligatoires
        required_columns = {'matricule', 'matiere_id', 'note'}
        if not required_columns.issubset(df.columns):
            return jsonify({
                'message': f'Colonnes requises: {", ".join(required_columns)}'
            }), 400

        # Vérifier les droits par matière
        valid_matiere_ids = [
            m.matiere_id 
            for m in Enseigne.query.filter_by(enseignant_id=enseignant_id).all()
        ]

        for index, row in df.iterrows():
            # Validation des données
            if pd.isnull(row.get('matricule')) or pd.isnull(row.get('matiere_id')) or pd.isnull(row.get('note')):
                errors.append(f"Ligne {index+2}: Données manquantes")
                continue

            etu = Etudiant.query.filter_by(matricule=row['matricule']).first()
            if not etu:
                errors.append(f"Ligne {index+2}: Matricule invalide")
                continue

            if int(row['matiere_id']) not in valid_matiere_ids:
                errors.append(f"Ligne {index+2}: Matière non autorisée")
                continue

            try:
                note_value = float(row['note'])
                if not (0 <= note_value <= 20):
                    raise ValueError
            except:
                errors.append(f"Ligne {index+2}: Note invalide (0-20)")
                continue

            # Création de la note
            note = Note(
                etudiant_id=etu.id,
                matiere_id=int(row['matiere_id']),
                note=note_value
            )
            db.session.add(note)
            created.append(note)

        db.session.commit()

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'message': 'Erreur de traitement du fichier',
            'error': str(e)
        }), 400

    response = {
        'created': len(created),
        'errors': errors
    }
    return jsonify(response), 201