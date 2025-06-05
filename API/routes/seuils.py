from flask import Blueprint
bp = Blueprint('seuils', __name__, url_prefix='/seuils')

# Route permettant de créer des seuils de consommation (eau/électricité) pour un emplacement donné
# Méthode HTTP : POST
@bp.route('/seuils', methods=['POST'])
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
@bp.route('/seuils/<string:numero_emplacement>', methods=['PUT'])
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
