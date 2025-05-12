from marshmallow import Schema, fields, validate
from ..schemas.common import error_response_schema  # Import du schéma d'erreur commun

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True, validate=validate.Length(min=3, max=80))
    email = fields.Email(required=True)
    role = fields.Str(validate=validate.OneOf(["professeur", "etudiant", "admin"]))
    password = fields.Str(load_only=True, required=True, validate=validate.Length(min=6))

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))

# Instanciation des schémas
user_schema = UserSchema()
users_schema = UserSchema(many=True)
login_schema = LoginSchema()

__all__ = [
    'user_schema',
    'users_schema',
    'login_schema',
    'error_response_schema'  # Export du schéma d'erreur commun
]
