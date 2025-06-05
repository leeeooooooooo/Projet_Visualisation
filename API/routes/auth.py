from flask import Blueprint
bp = Blueprint('auth', __name__, url_prefix='/auth')

# Route pour la connexion d’un gérant
@bp.route('/login/gerant', methods=['POST', 'OPTIONS'])
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

# Route pour connecter un campeur (authentification)
# Supporte aussi les requêtes OPTIONS pour le CORS (Cross-Origin Resource Sharing)
@bp.route('/login/campeur', methods=['POST', 'OPTIONS'])
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

