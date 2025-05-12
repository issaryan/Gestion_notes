from flask import Flask
from .extensions import db, jwt, migrate
from .models import Role  # Import direct au niveau du module
from dotenv import load_dotenv
load_dotenv()
def create_app(config_class='config.Config'):
    """Factory d'application Flask avec configuration sécurisée"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialisation des extensions
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    # Contexte applicatif pour les opérations DB
    with app.app_context():
        # Import des modèles APRÈS initialisation des extensions
        from .models import (
            User,
            Etudiant,
            Classe,
            Matiere,
            Enseigne
        )
        
        # Création des tables si nécessaire
        db.create_all()

        # Initialisation des données système
        initialize_default_roles(app)

    # Enregistrement des blueprints
    register_blueprints(app)

    return app

def initialize_default_roles(app):
    """Initialise les rôles par défaut dans un contexte applicatif"""
    default_roles = ['ADMIN', 'ENSEIGNANT', 'ETUDIANT']
    
    try:
        with app.app_context():
            for role_name in default_roles:
                if not Role.query.filter_by(name=role_name).first():
                    db.session.add(Role(name=role_name))
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Erreur d'initialisation des rôles : {str(e)}")
        raise RuntimeError("Échec de l'initialisation des rôles") from e

def register_blueprints(app):
    """Enregistre les composants modulaires"""
    from .users.routes import users_bp
    from .classes.routes import classes_bp
    from .matieres.routes import matiere_bp
    from .auth.routes import auth_bp

    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(classes_bp, url_prefix='/api/classes')
    app.register_blueprint(matiere_bp, url_prefix='/api/matieres')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
