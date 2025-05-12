from marshmallow import Schema, fields, validate  # Ajout de l'import Schema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models import Classe
from ..extensions import db

class ClasseSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Classe
        load_instance = True
        include_fk = True

class ClasseCreateSchema(Schema):  # Utilise maintenant le Schema importé
    nom = fields.Str(required=True, validate=validate.Length(min=2, max=50))
    niveau = fields.Str(
        required=True,
        validate=validate.OneOf(["LICENCE", "MASTER", "DOCTORAT"])
    )
