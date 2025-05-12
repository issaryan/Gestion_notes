from functools import wraps
from flask_jwt_extended import get_jwt, jwt_required
from flask import jsonify

def role_required(*allowed_roles):
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            if claims.get('role') not in allowed_roles:
                return jsonify({"message": "Accès non autorisé"}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator

admin_required = role_required('ADMIN')
teacher_required = role_required('ENSEIGNANT')
student_required = role_required('ETUDIANT')
