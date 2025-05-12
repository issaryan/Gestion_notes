# app/auth/schemas.py

from marshmallow import fields, validate, Schema
from ..extensions import ma

class LoginSchema(ma.Schema):
    """
    Schéma de validation pour la requête de connexion.
    Attend un JSON avec :
      - email    : adresse email valide, requise
      - password : chaîne de caractères non vide, requise
    """
    email = fields.Email(required=True, error_messages={
        "required": "L'email est requis.",
        "invalid": "L'email n'est pas valide."
    })
    password = fields.String(required=True, validate=validate.Length(min=1), error_messages={
        "required": "Le mot de passe est requis.",
        "invalid": "Le mot de passe doit être une chaîne de caractères."
    })

class UserSchema(ma.Schema):
    """
    Schéma pour sérialiser les informations retournées par /me.
    """
    user_id = fields.Int(required=True)
    role = fields.String(required=True)

# Instances des schémas pour usage direct
login_schema = LoginSchema()
user_schema  = UserSchema()
