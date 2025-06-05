from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy       # ORM pour interagir avec la base de données
from flask_bcrypt import Bcrypt               # Pour hasher les mots de passe
from flask_cors import CORS                   # Pour autoriser les requêtes cross-origin (ex: frontend ↔ backend)
from datetime import datetime
from flask import session
from flask_cors import cross_origin
from flask_mail import Mail, Message          # Pour envoyer des emails (ex : notifications)
import smtplib
import re
import logging                                # Pour le système de journalisation (logs)

app = Flask(__name__)
bcrypt = Bcrypt(app)  # Initialisation de bcrypt pour le hachage des mots de passe

# CORS : autorise l'accès à l'API depuis des domaines différents (ex : Vue.js sur localhost)
CORS(app, supports_credentials=True, origins=[
    "http://localhost:8080",         # pour le développement local (non-HTTPS)
    "https://localhost:8080",        # pour du HTTPS local (optionnel)
    "https://172.20.0.39",           # pour la version déployée en réseau local
])

# Configuration de la base de données MariaDB via SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://camping:camping@172.20.0.39/camping_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Désactive le suivi des modifications pour de meilleures performances

app.secret_key = 'votre_clé_secrète'  # Clé secrète pour sécuriser les sessions utilisateur (cookies, etc.)

# Configuration de l'envoi de mails via Flask-Mail (ex: pour envoyer des alertes ou confirmations)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'campingciel@gmail.com'     # adresse utilisée pour l'envoi
app.config['MAIL_PASSWORD'] = 'Camping11@'                # mot de passe de l’adresse (à ne jamais laisser en clair en prod !)

# Configuration du système de logs : permet d’enregistrer les événements dans un fichier et dans la console
logging.basicConfig(
    level=logging.INFO,  # Niveau de logs (INFO = standard, DEBUG = très détaillé)
    format='%(asctime)s [%(levelname)s] %(message)s',  # Format : date, niveau, message
    handlers=[
        logging.FileHandler("app.log"),       # Enregistrement dans le fichier app.log
        logging.StreamHandler()               # Affichage des logs aussi dans le terminal
    ]
)

logger = logging.getLogger(__name__)  # Création d’un logger spécifique pour ce fichier

# Initialisation de l’objet SQLAlchemy pour interagir avec la base de données
db = SQLAlchemy(app)

# ======================== Modèles ======================== #

class Gerant(db.Model):
    __tablename__ = 'Gerant'
    Id_Gerant = db.Column(db.Integer, primary_key=True)
    Identifiant = db.Column(db.String(50), unique=True, nullable=False)
    Mot_de_passe = db.Column(db.String(255), nullable=False)
    Email = db.Column(db.String(100))
    Telephone = db.Column(db.String(20))


class Campeur(db.Model):
    __tablename__ = 'Campeur'
    Id_Campeur = db.Column(db.Integer, primary_key=True)
    Identifiant = db.Column(db.String(50), unique=True, nullable=False)
    Mot_de_passe = db.Column(db.String(255), nullable=False)
    Date_Debut = db.Column(db.Date)
    Date_Fin = db.Column(db.Date)


class Emplacement(db.Model):
    __tablename__ = 'Emplacement'
    Id_Emplacement = db.Column(db.Integer, primary_key=True)
    Numero_Emplacement = db.Column(db.String(20), unique=True, nullable=False)
    Id_Campeur = db.Column(db.Integer, db.ForeignKey('Campeur.Id_Campeur'), nullable=True)  # Nullable car un emplacement peut être vide
    Id_Gerant = db.Column(db.Integer, db.ForeignKey('Gerant.Id_Gerant'), nullable=False)
    gerant = db.relationship('Gerant', backref='emplacements')

class ConsommationEau(db.Model):
    __tablename__ = 'Consommation_eau'

    Id_Consommation_eau = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Date_Heure = db.Column(db.DateTime, nullable=False)
    Quantite = db.Column(db.Float(precision=2), nullable=False)
    Id_Emplacement = db.Column(db.Integer, db.ForeignKey('Emplacement.Id_Emplacement'), nullable=False)

class ConsommationElectrique(db.Model):
    __tablename__ = 'Consommation_electrique'

    Id_Consommation_electrique = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Date_heure = db.Column(db.DateTime, nullable=False)
    Quantite = db.Column(db.Float(precision=2), nullable=False)
    Id_Emplacement = db.Column(db.Integer, db.ForeignKey('Emplacement.Id_Emplacement'), nullable=False)

class Seuil(db.Model):
    __tablename__ = 'Seuil'
    Id_Seuil = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Id_Emplacement = db.Column(db.Integer, db.ForeignKey('Emplacement.Id_Emplacement'), nullable=False)

    Seuil_Electricite_Matin = db.Column(db.Numeric(10, 2))
    Seuil_Electricite_Midi = db.Column(db.Numeric(10, 2))
    Seuil_Electricite_Soir = db.Column(db.Numeric(10, 2))
    Seuil_Electricite_Nuit = db.Column(db.Numeric(10, 2))

    Seuil_Eau_Matin = db.Column(db.Numeric(10, 2))
    Seuil_Eau_Midi = db.Column(db.Numeric(10, 2))
    Seuil_Eau_Soir = db.Column(db.Numeric(10, 2))
    Seuil_Eau_Nuit = db.Column(db.Numeric(10, 2))


def _tranche_horaire(heure):
    if 6 <= heure < 12:
        return "Matin"
    elif 12 <= heure < 17:
        return "Midi"
    elif 17 <= heure < 22:
        return "Soir"
    else:
        return "Nuit"

# ======================== Routes ======================== #

# Route pour la création d’un nouveau gérant
@app.route('/creation/gerant', methods=['POST'])
def creation_gerant():
    try:
        data = request.get_json()  # Récupération des données envoyées en JSON
        logger.info("Tentative de création d'un nouveau gérant avec les données : %s", data)

        identifiant = data.get('identifiant')
        mot_de_passe = data.get('mot_de_passe')
        email = data.get('email')
        telephone = data.get('telephone')

        # Vérifie que tous les champs sont remplis
        if not all([identifiant, mot_de_passe, email, telephone]):
            logger.warning("Champs manquants lors de la création du gérant.")
            return jsonify({'message': 'Tous les champs sont requis.'}), 400

        # Vérifie si l’identifiant est déjà utilisé
        if Gerant.query.filter_by(Identifiant=identifiant).first():
            logger.warning("Identifiant déjà utilisé : %s", identifiant)
            return jsonify({'message': 'Identifiant déjà utilisé.'}), 409

        # Hachage du mot de passe avec bcrypt
        hashed_pw = bcrypt.generate_password_hash(mot_de_passe).decode('utf-8')

        # Création d’un nouvel objet gérant
        new_gerant = Gerant(
            Identifiant=identifiant,
            Mot_de_passe=hashed_pw,
            Email=email,
            Telephone=telephone
        )

        db.session.add(new_gerant)  # Ajout du gérant à la session
        db.session.commit()         # Enregistrement dans la base de données

        logger.info("Gérant créé avec succès : Id_Gerant=%s, Identifiant=%s", new_gerant.Id_Gerant, new_gerant.Identifiant)

        # Réponse JSON avec les infos du nouveau gérant
        return jsonify({
            'message': 'Gérant créé avec succès',
            'Id_Gerant': new_gerant.Id_Gerant,
            'Identifiant': new_gerant.Identifiant
        }), 201

    except Exception as e:
        logger.exception("Erreur lors de la création du gérant.")
        return jsonify({'message': f'Erreur serveur : {str(e)}'}), 500


# Route pour la connexion d’un gérant
@app.route('/login/gerant', methods=['POST', 'OPTIONS'])
def login_gerant():
    # Gestion de la requête OPTIONS pour le CORS (pré-vol)
    if request.method == 'OPTIONS':
        logger.info("Requête OPTIONS reçue sur /login/gerant.")
        return jsonify({'message': 'Preflight OK'}), 200

    try:
        data = request.get_json()  # Récupère les données d’identification
        logger.info("Tentative de connexion d'un gérant avec les données : %s", data)

        identifiant = data.get('identifiant')
        mot_de_passe = data.get('mot_de_passe')

        # Vérifie que les deux champs sont présents
        if not identifiant or not mot_de_passe:
            logger.warning("Identifiant ou mot de passe manquant.")
            return jsonify({'message': 'Identifiant et mot de passe sont requis.'}), 400

        # Recherche du gérant dans la base
        gerant = Gerant.query.filter_by(Identifiant=identifiant).first()

        # Vérifie si le mot de passe est correct
        if gerant and gerant.Mot_de_passe and bcrypt.check_password_hash(gerant.Mot_de_passe, mot_de_passe):
            logger.info("Connexion réussie pour le gérant : Id=%s, Identifiant=%s", gerant.Id_Gerant, gerant.Identifiant)

            # Création de la réponse avec un cookie sécurisé pour la session
            resp = make_response(jsonify({
                'message': 'Connexion réussie',
                'Id_Gerant': gerant.Id_Gerant,
                'Identifiant': gerant.Identifiant,
                'role': 'gerant'
            }), 200)

            resp.set_cookie(
                'session_gerant',          # nom du cookie
                str(gerant.Id_Gerant),     # contenu = id du gérant
                httponly=True,             # inaccessible via JavaScript
                secure=True,               # transmis seulement en HTTPS
                samesite='None',           # autorise les requêtes cross-site
                max_age=3600               # durée de validité = 1h
            )

            logger.info("Cookie sécurisé défini pour le gérant ID : %s", gerant.Id_Gerant)
            return resp

        # Si l'identifiant ou le mot de passe est incorrect
        logger.warning("Échec de connexion pour l'identifiant : %s", identifiant)
        return jsonify({'message': 'Identifiant ou mot de passe incorrect.'}), 401

    except Exception as e:
        logger.exception("Erreur serveur lors de la tentative de connexion du gérant.")
        return jsonify({'message': 'Erreur serveur interne.'}), 500



# Déclare une route Flask accessible en POST à l’URL '/creation/campeur'
# Cette route permet de créer ou configurer un campeur (mot de passe, dates, liaison à un emplacement)
@app.route('/creation/campeur', methods=['POST'])
def creation_campeur():
    try:
        data = request.json  # Récupère les données JSON envoyées dans le corps de la requête
        logger.info("Requête reçue pour la mise à jour d’un campeur : %s", data)

        # Extraction des données nécessaires depuis le JSON
        numero_emplacement = data.get('numero_emplacement')
        mot_de_passe = data.get('mot_de_passe')
        date_debut = data.get('date_debut')
        date_fin = data.get('date_fin')

        logger.debug(f"Extraction des données - numero_emplacement: {numero_emplacement}, mot_de_passe: {'***' if mot_de_passe else None}, date_debut: {date_debut}, date_fin: {date_fin}")

        # Vérifie que toutes les données requises sont présentes
        if not all([numero_emplacement, mot_de_passe, date_debut, date_fin]):
            logger.warning("Requête incomplète : champs manquants.")
            return jsonify({'message': 'Tous les champs sont requis.'}), 400

        # Recherche d’un campeur dans la base via l’identifiant (numéro d’emplacement ici)
        campeur = Campeur.query.filter_by(Identifiant=numero_emplacement).first()
        if not campeur:
            logger.warning(f"Campeur non trouvé avec identifiant : {numero_emplacement}")
            return jsonify({'message': f'Le campeur avec l’identifiant {numero_emplacement} n’existe pas.'}), 404
        logger.info(f"Campeur trouvé : Id_Campeur={campeur.Id_Campeur}")

        # Hachage du mot de passe pour la sécurité (jamais stocker en clair)
        hashed_pw = bcrypt.generate_password_hash(mot_de_passe).decode('utf-8')
        logger.debug("Mot de passe haché généré.")

        # Mise à jour des champs dans la table Campeur
        campeur.Mot_de_passe = hashed_pw
        campeur.Date_Debut = datetime.strptime(date_debut, '%Y-%m-%d').date()
        campeur.Date_Fin = datetime.strptime(date_fin, '%Y-%m-%d').date()
        logger.info(f"Champs du campeur mis à jour : Date_Debut={campeur.Date_Debut}, Date_Fin={campeur.Date_Fin}")

        # Recherche de l'emplacement dans la base
        emplacement = Emplacement.query.filter_by(Id_Emplacement=int(numero_emplacement)).first()
        if not emplacement:
            logger.warning(f"Emplacement non trouvé : Id_Emplacement={numero_emplacement}")
            return jsonify({'message': f"L'emplacement avec l'ID {numero_emplacement} n'existe pas."}), 404

        # Vérifie si l'emplacement est déjà occupé par un autre campeur
        if emplacement.Id_Campeur and emplacement.Id_Campeur != campeur.Id_Campeur:
            logger.warning(f"Emplacement {numero_emplacement} déjà occupé par campeur {emplacement.Id_Campeur}")
            return jsonify({'message': f"L'emplacement {numero_emplacement} est déjà occupé."}), 409

        # Lier le campeur à l’emplacement
        emplacement.Id_Campeur = campeur.Id_Campeur
        emplacement.Numero_Emplacement = numero_emplacement
        logger.info(f"Emplacement {numero_emplacement} lié au campeur {campeur.Id_Campeur}")

        # Valider les modifications dans la base de données
        db.session.commit()
        logger.info(f"Mise à jour en base réussie pour campeur {campeur.Id_Campeur} et emplacement {numero_emplacement}")

        # Répondre avec un message de succès et des infos utiles
        return jsonify({
            'message': 'Campeur mis à jour et lié à l’emplacement.',
            'Id_Campeur': campeur.Id_Campeur,
            'Identifiant': campeur.Identifiant,
            'Id_Emplacement': emplacement.Id_Emplacement
        }), 200

    except Exception as e:
        # Annule les modifications si erreur
        db.session.rollback()
        logger.exception("Erreur lors de la mise à jour du campeur et de l’emplacement.")
        return jsonify({'message': f'Erreur : {str(e)}'}), 500

# Route pour connecter un campeur (authentification)
# Supporte aussi les requêtes OPTIONS pour le CORS (Cross-Origin Resource Sharing)
@app.route('/login/campeur', methods=['POST', 'OPTIONS'])
def login_campeur():
    # Gestion des requêtes de pré-vol (OPTIONS) pour le navigateur, utile avec le CORS
    if request.method == 'OPTIONS':
        logger.info("Requête OPTIONS reçue pour /login/campeur.")
        return '', 204  # Réponse vide avec code 204 (No Content)

    try:
        # Récupération des données d'identification envoyées en JSON
        data = request.get_json()
        logger.info("Tentative de connexion d’un campeur avec les données : %s", data)

        identifiant = data.get('identifiant')
        mot_de_passe = data.get('mot_de_passe')

        # Vérifie que les champs obligatoires sont fournis
        if not identifiant or not mot_de_passe:
            logger.warning("Champs manquants pour la connexion campeur.")
            return jsonify({'message': 'Identifiant et mot de passe sont requis.'}), 400

        # Recherche du campeur correspondant dans la base de données
        campeur = Campeur.query.filter_by(Identifiant=identifiant).first()
        if not campeur:
            logger.warning("Identifiant campeur non trouvé : %s", identifiant)
            return jsonify({'message': 'Identifiant non trouvé.'}), 401  # Unauthorized

        # Vérification sécurisée du mot de passe haché
        if not campeur.Mot_de_passe or not bcrypt.check_password_hash(campeur.Mot_de_passe, mot_de_passe):
            logger.warning("Mot de passe incorrect ou non défini pour l’identifiant : %s", identifiant)
            return jsonify({'message': 'Mot de passe incorrect.'}), 401

        # Stockage de l'ID du campeur dans la session Flask côté serveur
        session['campeur_id'] = campeur.Id_Campeur
        logger.info("Connexion réussie pour le campeur ID : %s", campeur.Id_Campeur)

        # Création d'un cookie sécurisé contenant l’ID du campeur
        resp = make_response(jsonify({'message': 'Connexion réussie'}), 200)
        resp.set_cookie(
            'session_campeur',             # Nom du cookie
            str(campeur.Id_Campeur),       # Contenu
            httponly=True,                 # Inaccessible en JavaScript (sécurité XSS)
            secure=True,                   # Envoyé uniquement en HTTPS
            samesite='None',               # Autorise les requêtes cross-origin
            max_age=3600                   # Expire après 1 heure
        )

        logger.info("Cookie sécurisé défini pour le campeur ID : %s", campeur.Id_Campeur)
        return resp

    except Exception as e:
        logger.exception("Erreur lors de la tentative de connexion campeur.")
        return jsonify({'message': 'Erreur serveur interne.'}), 500

# Route pour récupérer la consommation d’eau d’un campeur
# Accessible en GET avec l'identifiant en paramètre d’URL
@app.route('/consommation/eau/<identifiant>', methods=['GET'])
def consommation_eau_campeur(identifiant):
    logger.info("Requête reçue pour consulter la consommation d'eau du campeur avec identifiant : %s", identifiant)

    try:
        # Recherche de l'emplacement correspondant à l'identifiant fourni
        emplacement = Emplacement.query.filter_by(Numero_Emplacement=identifiant).first()

        if not emplacement:
            logger.warning("Aucun emplacement trouvé pour l’identifiant %s", identifiant)
            return jsonify({'message': 'Aucun emplacement trouvé pour ce campeur.'}), 404

        logger.info("Emplacement trouvé : ID %s pour identifiant %s", emplacement.Id_Emplacement, identifiant)

        # Récupère toutes les consommations d’eau liées à cet emplacement
        consommations = ConsommationEau.query.filter_by(Id_Emplacement=emplacement.Id_Emplacement).all()
        logger.info("Nombre de consommations trouvées : %d", len(consommations))

        # Mise en forme de la réponse JSON
        resultats = [
            {
                'Id_Consommation_eau': c.Id_Consommation_eau,
                'Quantite': c.Quantite,
                'Date_Heure': c.Date_Heure.strftime('%Y-%m-%d %H:%M:%S')
            } for c in consommations
        ]

        return jsonify({'consommations': resultats}), 200

    except Exception as e:
        logger.exception("Erreur lors de la récupération des consommations d'eau pour l’identifiant : %s", identifiant)
        return jsonify({'message': f'Erreur serveur : {str(e)}'}), 500


# Route pour récupérer la consommation d’électricité d’un campeur
# Accessible en GET, avec l’identifiant (numéro d’emplacement) passé en paramètre d’URL
@app.route('/consommation/electricite/<identifiant>', methods=['GET'])
def consommation_electricite_campeur(identifiant):
    # Log de réception de la requête avec l’identifiant concerné
    logger.info("Requête GET reçue pour la consommation électrique du campeur avec identifiant : %s", identifiant)

    try:
        # Recherche de l'emplacement correspondant à l’identifiant (numéro d’emplacement du campeur)
        emplacement = Emplacement.query.filter_by(Numero_Emplacement=identifiant).first()

        # Si aucun emplacement n’est trouvé, on retourne une erreur 404
        if not emplacement:
            logger.warning("Aucun emplacement trouvé pour l’identifiant %s", identifiant)
            return jsonify({'message': 'Aucun emplacement trouvé pour ce campeur.'}), 404

        logger.info("Emplacement trouvé : ID %s pour identifiant %s", emplacement.Id_Emplacement, identifiant)

        # Recherche des consommations électriques liées à l'emplacement trouvé
        consommations = ConsommationElectrique.query.filter_by(Id_Emplacement=emplacement.Id_Emplacement).all()
        logger.info("Nombre de consommations électriques trouvées : %d", len(consommations))

        # Mise en forme des données à retourner au format JSON
        resultats = [
            {
                'Id_Consommation_electrique': c.Id_Consommation_electrique,         # ID unique de la mesure
                'Quantite': c.Quantite,                                             # Quantité d’électricité consommée
                'Date_heure': c.Date_heure.strftime('%Y-%m-%d %H:%M:%S')            # Date et heure de la mesure
            } for c in consommations
        ]

        # Retour des données avec un code HTTP 200 (OK)
        return jsonify({'consommations': resultats}), 200

    except Exception as e:
        # En cas d’erreur, on log l’exception complète et on retourne une erreur 500
        logger.exception("Erreur lors de la récupération de la consommation électrique pour l’identifiant : %s", identifiant)
        return jsonify({'message': f'Erreur serveur : {str(e)}'}), 500




# Route permettant de créer des seuils de consommation (eau/électricité) pour un emplacement donné
# Méthode HTTP : POST
@app.route('/seuils', methods=['POST'])
def creation_seuils():
    try:
        # Récupération des données JSON envoyées dans la requête
        data = request.get_json()
        logger.info("Requête POST reçue pour création de seuils : %s", data)

        # Extraction du numéro d’emplacement
        numero_emplacement = data.get('Numero_Emplacement')

        # Vérifie que le champ obligatoire Numero_Emplacement est présent
        if not numero_emplacement:
            logger.warning("Numero_Emplacement manquant dans la requête")
            return jsonify({'message': 'Numero_Emplacement est requis.'}), 400

        # Recherche dans la base de données de l'emplacement correspondant
        emplacement = Emplacement.query.filter_by(Numero_Emplacement=numero_emplacement).first()

        # Si l’emplacement n’existe pas, retourner une erreur 404
        if not emplacement:
            logger.warning("Emplacement introuvable pour Numero_Emplacement : %s", numero_emplacement)
            return jsonify({'message': 'Emplacement introuvable.'}), 404

        # Création d’un objet Seuil avec les valeurs fournies
        seuil = Seuil(
            Id_Emplacement=emplacement.Id_Emplacement,                               # Clé étrangère vers l’emplacement
            Seuil_Electricite_Matin=data.get('Seuil_Electricite_Matin'),            # Seuil matin électricité
            Seuil_Electricite_Midi=data.get('Seuil_Electricite_Midi'),              # Seuil midi électricité
            Seuil_Electricite_Soir=data.get('Seuil_Electricite_Soir'),              # Seuil soir électricité
            Seuil_Electricite_Nuit=data.get('Seuil_Electricite_Nuit'),              # Seuil nuit électricité
            Seuil_Eau_Matin=data.get('Seuil_Eau_Matin'),                            # Seuil matin eau
            Seuil_Eau_Midi=data.get('Seuil_Eau_Midi'),                              # Seuil midi eau
            Seuil_Eau_Soir=data.get('Seuil_Eau_Soir'),                              # Seuil soir eau
            Seuil_Eau_Nuit=data.get('Seuil_Eau_Nuit')                               # Seuil nuit eau
        )

        # Ajout à la session de base de données et validation (commit)
        db.session.add(seuil)
        db.session.commit()

        logger.info("Seuils créés avec succès pour emplacement ID : %s", emplacement.Id_Emplacement)
        # Retour d’un message de succès avec un code 201 (création réussie)
        return jsonify({'message': 'Seuils enregistrés avec succès.'}), 201

    except Exception as e:
        # En cas d’erreur, annuler les changements dans la base (rollback) et logger l’exception
        db.session.rollback()
        logger.exception("Erreur serveur lors de la création des seuils")
        # Retourner une erreur 500 (erreur serveur)
        return jsonify({'message': f'Erreur serveur : {str(e)}'}), 500


# Route permettant de modifier les seuils d'un emplacement spécifique
# Méthode HTTP : PUT
@app.route('/seuils/<string:numero_emplacement>', methods=['PUT'])
def modifier_seuils(numero_emplacement):
    try:
        # Récupération des données JSON envoyées dans la requête
        data = request.get_json()
        logger.info("Requête PUT reçue pour modifier seuils de l'emplacement %s : %s", numero_emplacement, data)

        # Recherche de l'emplacement à partir de son numéro
        emplacement = Emplacement.query.filter_by(Numero_Emplacement=numero_emplacement).first()

        # Si l’emplacement n’existe pas, on retourne une erreur 404
        if not emplacement:
            logger.warning("Emplacement introuvable pour Numero_Emplacement : %s", numero_emplacement)
            return jsonify({'message': 'Emplacement introuvable.'}), 404

        # Recherche des seuils déjà enregistrés pour cet emplacement
        seuil = Seuil.query.filter_by(Id_Emplacement=emplacement.Id_Emplacement).first()

        # Si aucun seuil n'est trouvé, retourner une erreur 404
        if not seuil:
            logger.warning("Aucun seuil trouvé pour emplacement ID : %s", emplacement.Id_Emplacement)
            return jsonify({'message': 'Aucun seuil trouvé pour cet emplacement.'}), 404

        # Mise à jour des champs avec les valeurs fournies dans la requête (ou conservation de l'ancienne valeur si absente)
        seuil.Seuil_Electricite_Matin = data.get('Seuil_Electricite_Matin', seuil.Seuil_Electricite_Matin)
        seuil.Seuil_Electricite_Midi = data.get('Seuil_Electricite_Midi', seuil.Seuil_Electricite_Midi)
        seuil.Seuil_Electricite_Soir = data.get('Seuil_Electricite_Soir', seuil.Seuil_Electricite_Soir)
        seuil.Seuil_Electricite_Nuit = data.get('Seuil_Electricite_Nuit', seuil.Seuil_Electricite_Nuit)
        seuil.Seuil_Eau_Matin = data.get('Seuil_Eau_Matin', seuil.Seuil_Eau_Matin)
        seuil.Seuil_Eau_Midi = data.get('Seuil_Eau_Midi', seuil.Seuil_Eau_Midi)
        seuil.Seuil_Eau_Soir = data.get('Seuil_Eau_Soir', seuil.Seuil_Eau_Soir)
        seuil.Seuil_Eau_Nuit = data.get('Seuil_Eau_Nuit', seuil.Seuil_Eau_Nuit)

        # Validation des modifications en base
        db.session.commit()
        logger.info("Seuils mis à jour avec succès pour emplacement ID : %s", emplacement.Id_Emplacement)

        # Retour d’un message de succès avec un code 200
        return jsonify({'message': 'Seuils mis à jour avec succès.'}), 200

    except Exception as e:
        # En cas d’erreur, annuler les changements (rollback) et logger l’exception
        db.session.rollback()
        logger.exception("Erreur serveur lors de la modification des seuils pour emplacement %s", numero_emplacement)
        # Retourner une erreur 500 (erreur serveur)
        return jsonify({'message': f'Erreur serveur : {str(e)}'}), 500


# Route pour traiter les alertes de dépassement des seuils de consommation
# Méthode HTTP : POST
@app.route('/alerte/consommation', methods=['POST'])
def alerte_seuil():
    try:
        # Récupération des données JSON envoyées (si besoin d’infos supplémentaires)
        data = request.get_json()
        logger.info("Début traitement alerte consommation, données reçues : %s", data)

        # On fixe la date limite au début de la journée (00:00:00)
        date_limite = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        logger.info("Date limite pour filtrage consommations : %s", date_limite)

        # Listes pour stocker les consommations qui dépassent les seuils
        depassements_eau = []
        depassements_elec = []

        # Récupération des consommations d'eau depuis la date limite
        consommations_eau = ConsommationEau.query.filter(ConsommationEau.Date_Heure >= date_limite).all()
        logger.info("Consommations eau récupérées : %d", len(consommations_eau))

        # Parcours des consommations d'eau pour vérifier les dépassements
        for c in consommations_eau:
            # Récupération des seuils associés à l'emplacement de la consommation
            seuil = Seuil.query.filter_by(Id_Emplacement=c.Id_Emplacement).first()
            if seuil:
                # Détermination de la tranche horaire selon l'heure de consommation
                heure = c.Date_Heure.hour
                tranche = _tranche_horaire(heure)
                # Récupération du seuil d'eau pour cette tranche horaire
                seuil_eau = getattr(seuil, f"Seuil_Eau_{tranche}")
                # Vérification si la consommation dépasse le seuil
                if seuil_eau is not None and c.Quantite > seuil_eau:
                    logger.info("Dépassement eau détecté : Consommation %s > Seuil %s à l'emplacement %s",
                                c.Quantite, seuil_eau, c.Id_Emplacement)
                    depassements_eau.append(c)

        # Récupération des consommations électriques depuis la date limite
        consommations_elec = ConsommationElectrique.query.filter(ConsommationElectrique.Date_heure >= date_limite).all()
        logger.info("Consommations électricité récupérées : %d", len(consommations_elec))

        # Parcours des consommations électriques pour vérifier les dépassements
        for c in consommations_elec:
            seuil = Seuil.query.filter_by(Id_Emplacement=c.Id_Emplacement).first()
            if seuil:
                heure = c.Date_heure.hour
                tranche = _tranche_horaire(heure)
                seuil_elec = getattr(seuil, f"Seuil_Electricite_{tranche}")
                if seuil_elec is not None and c.Quantite > seuil_elec:
                    logger.info("Dépassement électricité détecté : Consommation %s > Seuil %s à l'emplacement %s",
                                c.Quantite, seuil_elec, c.Id_Emplacement)
                    depassements_elec.append(c)

        # Si aucun dépassement n'est détecté, retourner un message OK
        if not depassements_eau and not depassements_elec:
            logger.info("Aucun dépassement détecté aujourd'hui.")
            return jsonify({'message': 'Aucun dépassement détecté.'}), 200

        # Recherche du gérant à notifier : on prend le gérant du premier dépassement trouvé
        gerant = None
        if depassements_eau:
            gerant = Emplacement.query.get(depassements_eau[0].Id_Emplacement).gerant
        elif depassements_elec:
            gerant = Emplacement.query.get(depassements_elec[0].Id_Emplacement).gerant

        # Si aucun gérant n'est trouvé, retourner une erreur 404
        if not gerant:
            logger.warning("Aucun gérant trouvé pour ces consommations dépassant les seuils.")
            return jsonify({'message': 'Aucun gérant trouvé pour ces consommations.'}), 404

        # Construction du message d’alerte
        message_alerte = "Alerte de consommation :\n"
        if depassements_eau:
            message_alerte += f"- {len(depassements_eau)} dépassement(s) d'eau\n"
        if depassements_elec:
            message_alerte += f"- {len(depassements_elec)} dépassement(s) électrique\n"

        # Envoi de l'alerte par email au gérant
        logger.info("Envoi de l'alerte par email au gérant : %s", gerant.Email)
        msg = Message("Alerte consommation camping", sender=app.config['MAIL_USERNAME'], recipients=[gerant.Email])
        msg.body = message_alerte
        mail.send(msg)
        logger.info("Email envoyé avec succès.")

        # Envoi de l'alerte par SMS au gérant
        logger.info("Envoi de l'alerte par SMS au numéro : %s", gerant.Telephone)
        envoyer_sms(gerant.Telephone, message_alerte)
        logger.info("SMS envoyé avec succès.")

        # Retour d’un message de succès
        return jsonify({'message': 'Alertes envoyées.'}), 200

    except Exception as e:
        # Gestion des erreurs : rollback et logging
        logger.exception("Erreur serveur lors du traitement des alertes de consommation")
        return jsonify({'message': f'Erreur serveur : {str(e)}'}), 500

# Route pour récupérer le rôle de l'utilisateur connecté via les cookies de session
@app.route('/user/role', methods=['GET'])
def get_user_role():
    # Lecture du cookie de session pour un gérant (s'il existe)
    gerant_id = request.cookies.get('session_gerant')
    # Lecture du cookie de session pour un campeur (s'il existe)
    campeur_id = request.cookies.get('session_campeur')

    # Si on trouve un cookie de gérant, on renvoie le rôle 'gerant' avec son id
    if gerant_id:
        return jsonify({'role': 'gerant', 'id': gerant_id}), 200
    # Sinon, si on trouve un cookie de campeur, on renvoie le rôle 'campeur' avec son id
    elif campeur_id:
        return jsonify({'role': 'campeur', 'id': campeur_id}), 200
    # Si aucun cookie n'est trouvé, on renvoie un rôle inconnu et un code 401 (non autorisé)
    else:
        return jsonify({'role': 'inconnu'}), 401



# ======================== Lancement ======================== #
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000,ssl_context=('cert.pem', 'key.pem'))
