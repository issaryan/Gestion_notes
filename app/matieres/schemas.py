from marshmallow import Schema, fields

class MatiereSchema(Schema):
    id = fields.Int(dump_only=True)
    nom = fields.Str(required=True)
    coefficient = fields.Float(required=True)

matiere_schema = MatiereSchema()
