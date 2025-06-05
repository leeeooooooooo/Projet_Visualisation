from flask import Flask, request, jsonify
import jwt
import datetime
import os
from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Date, DECIMAL
from sqlalchemy.orm import relationship

app = Flask(__name__)

# Configuration de la base de données
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://camping:camping@172.20.0.39/camping_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Clé secrète pour le JWT
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'cle_secrete_temporaire_pour_developpement')

# Configuration CORS autorisant seulement le frontend (localhost:8080)
CORS(app, resources={r"/*": {"origins": "https://172.20.0.39"}}, supports_credentials=True)



db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# ======================== Modèles ======================== #

class Gerant(db.Model):
    __tablename__ = 'Gerant'
    Id_Gerant = db.Column(db.Integer, primary_key=True)
    Identifiant = db.Column(db.String(50), unique=True, nullable=False)
    Mot_de_passe = db.Column(db.String(255), nullable=False)
    Email = db.Column(db.String(100), nullable=False)
    Telephone = db.Column(db.String(20), nullable=False)

class Campeur(db.Model):
    __tablename__ = 'Campeur'
    Id_Campeur = db.Column(db.Integer, primary_key=True)
    Identifiant = db.Column(db.String(50), unique=True, nullable=False)
    Mot_de_passe = db.Column(db.String(255), nullable=False)
    Date_Debut = db.Column(db.Date, nullable=False)
    Date_Fin = db.Column(db.Date, nullable=False)

class ConsommationEau(db.Model):
    __tablename__ = 'Consommation_eau'
    Id_Consommation_eau = db.Column(db.Integer, primary_key=True)
    Date_Heure = db.Column(db.DateTime, nullable=False)
    Periode = db.Column(db.String(20), nullable=False)
    Quantite = db.Column(db.Float, nullable=False)
    Id_Emplacement = db.Column(db.Integer, nullable=False)

class ConsommationElectrique(db.Model):
    __tablename__ = 'Consommation_electrique'
    Id_Consommation_electrique = db.Column(db.Integer, primary_key=True)
    Date_Heure = db.Column(db.DateTime, nullable=False)
    Periode = db.Column(db.String(20), nullable=False)
    Quantite = db.Column(db.Float, nullable=False)
    Id_Emplacement = db.Column(db.Integer, nullable=False)

class Emplacement(db.Model):
    __tablename__ = 'Emplacement'
    Id_Emplacement = db.Column(db.Integer, primary_key=True)
    Numero_Emplacement = db.Column(db.String(20), unique=True, nullable=False)
    Id_Campeur = db.Column(db.Integer, db.ForeignKey('Campeur.Id_Campeur'), nullable=True)  # Nullable car un emplacement peut être vide
    Id_Gerant = db.Column(db.Integer, db.ForeignKey('Gerant.Id_Gerant'), nullable=False)

class Seuil(db.Model):
    __tablename__ = 'Seuil'

    Id_Seuil = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Seuils d'électricité
    Seuil_Electricite_Matin = db.Column(db.Float, nullable=False)
    Seuil_Electricite_Midi = db.Column(db.Float, nullable=False)
    Seuil_Electricite_Soir = db.Column(db.Float, nullable=False)

    # Seuils d'eau
    Seuil_Eau_Matin = db.Column(db.Float, nullable=False)
    Seuil_Eau_Midi = db.Column(db.Float, nullable=False)
    Seuil_Eau_Soir = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return (
            f"<Seuil(Id_Seuil={self.Id_Seuil}, "
            f"Seuil_Electricite_Matin={self.Seuil_Electricite_Matin}, "
            f"Seuil_Electricite_Midi={self.Seuil_Electricite_Midi}, "
            f"Seuil_Electricite_Soir={self.Seuil_Electricite_Soir}, "
            f"Seuil_Eau_Matin={self.Seuil_Eau_Matin}, "
            f"Seuil_Eau_Midi={self.Seuil_Eau_Midi}, "
            f"Seuil_Eau_Soir={self.Seuil_Eau_Soir})>"
        )


# Fonction pour générer un token JWT
def generate_token(user_id, user_type):
    # Durée de validité du token (par exemple, 24 heures)
    expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    
    # Créer le payload du token
    payload = {
        'user_id': user_id,
        'user_type': user_type,
        'exp': expiration
    }
    
    # Générer le token avec la clé secrète de l'application
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    
    return token

# Décorateur pour protéger les routes qui nécessitent une authentification
def token_required(f):
    from functools import wraps
    
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Vérifier si le token est dans l'en-tête Authorization
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'message': 'Token manquant!'}), 401
        
        try:
            # Décoder le token
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            
            # Récupérer l'utilisateur selon son type
            if data['user_type'] == 'campeur':
                current_user = Campeur.query.get(data['user_id'])
            else:
                current_user = Gerant.query.get(data['user_id'])
                
            if not current_user:
                return jsonify({'message': 'Utilisateur non trouvé!'}), 401
                
        except Exception as e:
            return jsonify({'message': 'Token invalide!', 'error': str(e)}), 401
            
        # Passer l'utilisateur à la fonction de la route
        return f(current_user, *args, **kwargs)
    
    return decorated

# ======================== Routes ======================== #

@app.route('/')
def home():
    return "Bienvenue sur l'API de gestion de consommation !"

@app.route('/register/gerant', methods=['POST'])
def register_gerant():
    data = request.json

    identifiant = data.get('Identifiant')
    mot_de_passe = data.get('Mot_de_passe')
    email = data.get('Email')
    telephone = data.get('Telephone')

    if not identifiant or not mot_de_passe or not email or not telephone:
        return jsonify({'message': 'Tous les champs sont requis.'}), 400

    if Gerant.query.filter_by(Identifiant=identifiant).first():
        return jsonify({'message': 'L\'identifiant est déjà pris.'}), 400

    mot_de_passe_hache = bcrypt.generate_password_hash(mot_de_passe).decode('utf-8')

    nouveau_gerant = Gerant(
        Identifiant=identifiant,
        Mot_de_passe=mot_de_passe_hache,
        Email=email,
        Telephone=telephone
    )

    try:
        db.session.add(nouveau_gerant)
        db.session.commit()
        return jsonify({'message': 'Gérant enregistré avec succès !'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Erreur lors de l\'enregistrement du gérant'}),

# Route pour enregistrer un CAMPEUR
@app.route('/register/campeur', methods=['POST'])
def register_campeur():
    data = request.json

    # Récupérer les données envoyées dans la requête
    identifiant = data.get('Identifiant')
    mot_de_passe = data.get('Mot_de_passe')
    date_debut = data.get('Date_Debut')
    date_fin = data.get('Date_Fin')
    numero_emplacement = data.get('Numero_Emplacement')  # Numéro d'emplacement

    # Vérification des champs
    if not mot_de_passe or not date_debut or not date_fin or not numero_emplacement:
        return jsonify({'message': 'Tous les champs sont requis.'}), 400

    # Vérifier si l'emplacement est déjà pris
    emplacement = Emplacement.query.filter_by(Numero_Emplacement=numero_emplacement).first()

    if not emplacement:
        return jsonify({'message': 'Emplacement non trouvé.'}), 404

    if emplacement.Id_Campeur is not None:
        return jsonify({'message': 'Emplacement déjà occupé. Veuillez choisir un emplacement libre.'}), 400

    # Hacher le mot de passe
    mot_de_passe_hache = bcrypt.generate_password_hash(mot_de_passe).decode('utf-8')

    # Créer un nouvel enregistrement pour le campeur sans 'Nom' ni 'Identifiant'
    nouveau_campeur = Campeur(
	Identifiant=identifiant,
        Mot_de_passe=mot_de_passe_hache,
        Date_Debut=date_debut,
        Date_Fin=date_fin
    )

    try:
        # Ajouter le campeur et valider l'ajout
        db.session.add(nouveau_campeur)
        db.session.commit()

        # Récupérer l'ID du campeur après insertion
        id_campeur = nouveau_campeur.Id_Campeur

        # Mettre à jour l'emplacement avec l'ID du campeur
        emplacement.Id_Campeur = id_campeur
        db.session.commit()

        return jsonify({
            'message': 'Campeur enregistré avec succès et emplacement attribué !',
            'Id_Campeur': id_campeur,
            'Numero_Emplacement': numero_emplacement
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Erreur lors de l\'enregistrement', 'error': str(e)}), 500

@app.route('/login/gerant', methods=['POST', 'OPTIONS'])
def login_gerant():
    if request.method == 'OPTIONS':
        # Réponse préflight pour le CORS
        return jsonify({'message': 'Preflight OK'}), 200

    data = request.json
    identifiant = data.get('identifiant')
    mot_de_passe = data.get('mot_de_passe')

    if not identifiant or not mot_de_passe:
        return jsonify({'message': 'Identifiant et mot de passe sont requis.'}), 400

    gerant = Gerant.query.filter_by(Identifiant=identifiant).first()

    if gerant and bcrypt.check_password_hash(gerant.Mot_de_passe, mot_de_passe):
        token = generate_token(gerant.Id_Gerant, "gerant")
        return jsonify({
            'message': 'Connexion réussie',
            'Id_Gerant': gerant.Id_Gerant,
            'Identifiant': gerant.Identifiant,
            'token': token
        }), 200
    else:
        return jsonify({'message': 'Identifiant ou mot de passe incorrect'}), 401

# 🔐 Route de connexion pour les CAMPEURS
@app.route('/login/campeur', methods=['POST', 'OPTIONS'])
def login_campeur():
    if request.method == 'OPTIONS':
        # Réponse préflight pour le CORS
        return jsonify({'message': 'Preflight OK'}), 200

    data = request.json
    numeroEmplacement = data.get('identifiant')
    mot_de_passe = data.get('mot_de_passe')

    if not numeroEmplacement or not mot_de_passe:
        return jsonify({'message': 'Identifiant et mot de passe sont requis.'}), 400

    campeur = Campeur.query.filter_by(Numero_Emplacement=numeroEmplacement).first()

    if campeur and bcrypt.check_password_hash(campeur.Mot_de_passe, mot_de_passe):
        # Créer un cookie sécurisé avec l'ID de l'utilisateur
        resp = make_response(jsonify({
            'message': 'Connexion réussie',
            'Id_Campeur': campeur.Id_Campeur,
            'Identifiant': campeur.Numero_Emplacement
        }), 200)
        
        # Exemple de cookie sécurisé
        resp.set_cookie('campeur_id', str(campeur.Id_Campeur), secure=True, httponly=False, samesite='Strict')

        return resp
    else:
        return jsonify({'message': 'Identifiant ou mot de passe incorrect'}), 401


# 📊 Route pour récupérer la consommation d'eau
@app.route('/consommation/eau', methods=['GET'])
def get_consommation_eau():
    try:

        consommations = ConsommationEau.query.all()  # Récupérer toutes les consommations d'eau

        return jsonify([{
            'Id_Consommation_eau': c.Id_Consommation_eau,
            'Date_Heure': c.Date_Heure.strftime('%Y-%m-%d %H:%M:%S'),
            'Periode': c.Periode,
            'Quantite': float(c.Quantite),
            'Id_Emplacement': c.Id_Emplacement
        } for c in consommations]), 200

    except Exception as e:
        return jsonify({'message': 'Erreur lors de la récupération des données', 'error': str(e)}), 500

# Route pour récupérer la consommation d'électricité
@app.route('/consommation/electricite', methods=['GET'])
def get_consommation_electricite():
    try:

        consommations = ConsommationElectrique.query.all()  # Récupérer toutes les consommations d'électricité

        return jsonify([{
            'Id_Consommation_electrique': c.Id_Consommation_electrique,
            'Date_Heure': c.Date_Heure.strftime('%Y-%m-%d %H:%M:%S'),
            'Periode': c.Periode,
            'Quantite': float(c.Quantite),
            'Id_Emplacement': c.Id_Emplacement
        } for c in consommations]), 200

    except Exception as e:
        return jsonify({'message': 'Erreur lors de la récupération des données', 'error': str(e)}), 500

          
@app.route('/seuils/configurer', methods=['POST'])
def ajouter_seuil():
    data = request.get_json()
    print("Données reçues :", data)  # Log des données reçues

    if not data.get('Seuil_Electricite_Matin') or not data.get('Seuil_Electricite_Midi') or not data.get('Seuil_Electricite_Soir'):
        return jsonify({'message': 'Les seuils d\'électricité sont nécessaires.'}), 400

    if not data.get('Seuil_Eau_Matin') or not data.get('Seuil_Eau_Midi') or not data.get('Seuil_Eau_Soir'):
        return jsonify({'message': 'Les seuils d\'eau sont nécessaires.'}), 400

    try:
        seuil = Seuil(
            Seuil_Electricite_Matin = data.get('Seuil_Electricite_Matin'),
            Seuil_Electricite_Midi  = data.get('Seuil_Electricite_Midi'),
            Seuil_Electricite_Soir  = data.get('Seuil_Electricite_Soir'),
            Seuil_Eau_Matin = data.get('Seuil_Eau_Matin'),
            Seuil_Eau_Midi  = data.get('Seuil_Eau_Midi'),
            Seuil_Eau_Soir  = data.get('Seuil_Eau_Soir')
        )

        db.session.add(seuil)
        db.session.commit()

        return jsonify({'message': 'Seuil ajouté avec succès.'}), 201

    except Exception as e:
        db.session.rollback()
        print(f"Erreur lors de l'ajout du seuil: {e}")  # Log de l'exception
        return jsonify({'message': 'Erreur lors de l\'ajout du seuil.', 'error': str(e)}), 500


            

# Route protégée d'exemple pour accéder au panneau de bord
@app.route('/panneau', methods=['GET'])
@token_required
def panneau(current_user):
    if hasattr(current_user, 'Id_Campeur'):
        # C'est un campeur
        return jsonify({
            'message': f'Bienvenue {current_user.Identifiant}!',
            'type': 'campeur',
            'id': current_user.Id_Campeur
        })
    else:
        # C'est un gérant
        return jsonify({
            'message': f'Bienvenue Gérant {current_user.Identifiant}!',
            'type': 'gerant',
            'id': current_user.Id_Gerant
        })

# ======================== Lancement du serveur ======================== #

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
