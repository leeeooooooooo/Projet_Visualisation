from flask import Blueprint
bp = Blueprint('alerte', __name__, url_prefix='/alerte')

# Route pour traiter les alertes de dépassement des seuils de consommation
# Méthode HTTP : POST
@bp.route('/alerte/consommation', methods=['POST'])
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
