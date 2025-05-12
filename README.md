# Gestion des Notes Académiques - Backend Flask

Ce projet est une application web de gestion des notes académiques développée avec Flask (Python) et MySQL, utilisant une architecture RESTful.

## Structure du projet

```
mon_projet_backend/
├── app/
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── schemas.py
│   ├── classes/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── schemas.py
│   ├── notes/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── schemas.py
│   ├── reports/
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── users/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── schemas.py
│   ├── __init__.py
│   ├── extensions.py
│   └── models.py
├── config.py
├── manage.py
├── requirements.txt
├── .env
├── Dockerfile
├── .dockerignore
└── docker-compose.yml
```

## Configuration de l'environnement

Créez un fichier `.env` à la racine avec le contenu suivant :

```
# Flask settings
FLASK_ENV=development
FLASK_APP=run.py
SECRET_KEY=super-secret-key-change-this

# Database
DB_USER=root
DB_PASSWORD=yourpassword
DB_HOST=db
DB_PORT=3306
DB_NAME=gestion_notes

SQLALCHEMY_DATABASE_URI=mysql+pymysql://root:yourpassword@db:3306/gestion_notes
SQLALCHEMY_TRACK_MODIFICATIONS=False

# JWT
JWT_SECRET_KEY=another-secret-key-change-this
JWT_ACCESS_TOKEN_EXPIRES=3600
```

## Lancer le backend avec Docker

1. Construire et lancer les conteneurs :

   docker-compose up --build

2. Accéder à l'application Flask :

   [http://localhost:5000](http://localhost:5000)

3. Accéder à la base de données MySQL :

   * Hôte : localhost
   * Port : 3306
   * Utilisateur : root
   * Mot de passe : yourpassword

## Gérer la base de données

Pour créer toutes les tables avec Flask-Migrate (après démarrage) :

```
docker exec -it flask-backend flask db init
docker exec -it flask-backend flask db migrate -m "Initial migration."
docker exec -it flask-backend flask db upgrade
```

## API RESTful

L'application expose plusieurs routes REST pour :

* Authentification (JWT)
* Gestion des utilisateurs (admin)
* Gestion des classes (admin)
* Gestion des notes (enseignant)
* Consultation des notes (étudiant)
* Génération de rapports (PDF/Excel/CSV)

## Dépendances

Installées via `requirements.txt` et incluses dans le conteneur Docker :

```
flask
flask_sqlalchemy
flask_jwt_extended
flask_marshmallow
marshmallow
pymysql
python-dotenv
flask-migrate
pandas
openpyxl
xlrd
reportlab
```

## Conseils

* Ne jamais commiter le fichier `.env` sur un dépôt public.
* Utiliser des variables d'environnement sécurisées en production.
* Adapter le `Dockerfile` pour être plus optimisé en production (par exemple, utiliser gunicorn).

---

Pour toute question, ouvrez une issue ou contactez le mainteneur du projet.
