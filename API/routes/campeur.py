from flask import Blueprint
bp = Blueprint('campeur', __name__, url_prefix='/campeur')

# Déclare une route Flask accessible en POST à l’URL '/creation/campeur'
# Cette route permet de créer ou configurer un campeur (mot de passe, dates, liaison à un emplacement)
@bp.route('/creation/campeur', methods=['POST'])
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

