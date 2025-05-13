from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db

# Association enseignant <-> matiere
class Enseigne(db.Model):
    __tablename__ = 'enseigne'
    id = db.Column(db.Integer, primary_key=True)
    enseignant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    matiere_id = db.Column(db.Integer, db.ForeignKey('matieres.id'), nullable=False)

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    users = db.relationship('User', backref='role', lazy=True)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    def set_admin(self):
        admin_role = Role.query.filter_by(name='ADMIN').first()
        if not admin_role:
            admin_role = Role(name='ADMIN')
            db.session.add(admin_role)
        self.roles.append(admin_role)

    
    # Relations
    etudiant = db.relationship('Etudiant', backref='user', uselist=False, cascade='all, delete-orphan')
    enseignant_matieres = db.relationship('Enseigne', backref='enseignant', lazy='select', cascade='all, delete-orphan')

class Classe(db.Model):
    __tablename__ = 'classes'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50), unique=True, nullable=False)
    etudiants = db.relationship('Etudiant', backref='classe', lazy=True)

class Etudiant(db.Model):
    __tablename__ = 'etudiants'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    matricule = db.Column(db.String(20), unique=True, nullable=False)
    classe_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    notes = db.relationship('Note', backref='etudiant', lazy=True, cascade='all, delete-orphan')

class Matiere(db.Model):
    __tablename__ = 'matieres'  # Nom corrigé
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False, unique=True)
    coeff = db.Column(db.Float, default=1.0, nullable=False)
    enseignants = db.relationship('Enseigne', backref='matiere', lazy='dynamic', cascade='all, delete-orphan')
    notes = db.relationship('Note', backref='matiere', lazy=True, cascade='all, delete-orphan')

class Note(db.Model):
    __tablename__ = 'notes'
    id = db.Column(db.Integer, primary_key=True)
    etudiant_id = db.Column(db.Integer, db.ForeignKey('etudiants.id'), nullable=False)
    matiere_id = db.Column(db.Integer, db.ForeignKey('matieres.id'), nullable=False)
    note = db.Column(db.Float, nullable=False)
    date_saisie = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    @property
    def appreciation(self):
        if self.note >= 12:
            return 'Excellent'
        elif self.note >= 10:
            return 'Bien'
        elif self.note >= 7:
            return 'Passable'
        return 'Insuffisant'
