La base de données est structurée autour de plusieurs tables interconnectées pour assurer une gestion efficace des consommations dans un camping.
La table campeur enregistre les informations des campeurs, comme leurs identifiants et la période de leur séjour.
La table gerant stocke les identifiants et coordonnées des gérants. chaque emplacement du camping est associé à un campeur et à un gérant, et identifié par un numéro unique.
Les consommations d’eau et d’électricité sont enregistrées respectivement dans les tables consommation_eau et consommation_electrique, avec la date et la quantité mesurée.
La table rapport permet de regrouper les consommations par période en indiquant les totaux et moyennes par emplacement.
La table seuil contient les limites de consommation personnalisées selon les moments de la journée pour chaque emplacement.
La table alerte définit les préférences de notification (site, mail, sms) du gérant en cas de dépassement de seuil.
L’ensemble de ces tables est relié par des clés étrangères pour garantir la cohérence et l’intégrité des données.
