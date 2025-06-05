from flask import Blueprint
bp = Blueprint('user', __name__, url_prefix='/user')

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
