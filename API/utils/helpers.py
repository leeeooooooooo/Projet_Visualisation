def _tranche_horaire(heure):
    if 6 <= heure < 12:
        return "Matin"
    elif 12 <= heure < 17:
        return "Midi"
    elif 17 <= heure < 22:
        return "Soir"
    else:
        return "Nuit"
