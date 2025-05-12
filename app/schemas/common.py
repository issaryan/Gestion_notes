from marshmallow import Schema, fields

class ErrorResponseSchema(Schema):
    message = fields.Dict(required=True)

error_response_schema = ErrorResponseSchema()
