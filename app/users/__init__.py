# app/users/__init__.py
from flask import Blueprint

users_bp = Blueprint('users', __name__, url_prefix='/users')

# Import après création du blueprint
from . import routes
