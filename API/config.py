# config.py

class Config:
    # Configuration de la base de données MariaDB via SQLAlchemy
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://camping:camping@172.20.0.39/camping_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Clé secrète pour les sessions Flask
    SECRET_KEY = 'votre_clé_secrète'  # À personnaliser et sécuriser en production

    # Configuration de Flask-Mail (envoi d’emails)
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'campingciel@gmail.com'
    MAIL_PASSWORD = 'Camping11@'  # ⚠️ À ne jamais exposer en clair en production

    # Origines autorisées pour les requêtes CORS (cross-domain)
    CORS_ORIGINS = [
        "http://localhost:8080",     # Développement local HTTP
        "https://localhost:8080",    # Développement local HTTPS
        "https://172.20.0.39"        # Adresse réseau local déployée
    ]

    # Configuration des logs
    LOG_LEVEL = 'INFO'               # Niveau de détail : DEBUG, INFO, WARNING, ERROR
    LOG_FILE = 'app.log'             # Nom du fichier de log à créer

