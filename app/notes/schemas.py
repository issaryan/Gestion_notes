# app/notes/schemas.py

from marshmallow import fields, validate
from ..extensions import ma

class NoteSchema(ma.Schema):
    """
    Schéma pour la création, l'importation et la sérialisation de l'objet Note.
    Correspond au modèle :
    - Note (note: float, matiere_id: int, etudiant_id: int)
    - Relations via matricule (load_only)
    """

    # Champs en lecture seule (dump_only)
    id = fields.Int(dump_only=True, description="ID unique de la note")
    etudiant_id = fields.Int(
        dump_only=True, 
        description="ID de l'étudiant lié"
    )
    date_saisie = fields.DateTime(
        dump_only=True,
        format='iso',
        description="Date/heure de création (UTC)"
    )

    # Champs en écriture seule (load_only)
    matricule = fields.Str(
        load_only=True,
        required=True,
        validate=validate.Length(min=5, max=20),
        error_messages={
            "required": "Le matricule est obligatoire",
            "invalid": "Format de matricule invalide (5-20 caractères)"
        },
        description="Matricule étudiant pour association"
    )

    matiere_id = fields.Int(
        load_only=True,
        required=True,
        validate=validate.Range(min=1),
        error_messages={
            "required": "L'ID de la matière est obligatoire",
            "invalid": "ID matière doit être un entier positif"
        },
        description="ID de la matière évaluée"
    )

    note = fields.Float(
        load_only=True,
        required=True,
        validate=validate.Range(min=0, max=20),
        error_messages={
            "required": "La note est obligatoire",
            "invalid": "La note doit être entre 0 et 20"
        },
        description="Valeur numérique de la note"
    )

    # Métadonnées
    class Meta:
        ordered = True  # Garder l'ordre des champs
        additional = ("appreciation",)  # Champ calculé du modèle

# Instances pour sérialisation
note_schema = NoteSchema()
notes_schema = NoteSchema(many=True)