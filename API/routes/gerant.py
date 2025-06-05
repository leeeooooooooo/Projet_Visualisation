from flask import Blueprint
bp = Blueprint('gerant', __name__, url_prefix='/gerant')


# Route pour la création d’un nouveau gérant
@bp.route('/creation/gerant', methods=['POST'])
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
