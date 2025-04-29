<template>
  <div class="connexion-conteneur">
    <h1>Connexion au Camping</h1>

    <div class="selecteur-utilisateur">
      <button
        :class="{ actif: typeUtilisateur === 'campeur' }"
        @click="changerTypeUtilisateur('campeur')"
      >
        Campeur
      </button>
      <button
        :class="{ actif: typeUtilisateur === 'gerant' }"
        @click="changerTypeUtilisateur('gerant')"
      >
        Gérant
      </button>
    </div>

    <form @submit.prevent="soumettreFormulaire">
      <div class="groupe-champ">
        <label for="identifiant">Identifiant</label>
        <input
          type="text"
          id="identifiant"
          v-model="identifiants.Identifiant"
          required
        />
      </div>
      <div class="groupe-champ">
        <label for="mot-de-passe">Mot de passe</label>
        <div class="input-password">
          <input
            :type="montrerMotDePasse ? 'text' : 'password'"
            id="mot-de-passe"
            v-model="identifiants.Mot_de_passe"
            @input="validerMotDePasse"
            required
            :class="{ 'erreur-champ': erreurs.Mot_de_passe }"
          />
          <button
            type="button"
            class="toggle-password"
            @click="montrerMotDePasse = !montrerMotDePasse"
            :aria-label="
              montrerMotDePasse
                ? 'Cacher le mot de passe'
                : 'Montrer le mot de passe'
            "
          >
            {{ montrerMotDePasse ? '🔓' : '🔒' }}
          </button>
        </div>
        <span v-if="erreurs.Mot_de_passe" class="message-validation">
          {{ erreurs.Mot_de_passe }}
        </span>
        <div class="password-strength" v-if="identifiants.Mot_de_passe">
          Force du mot de passe:
          <span :class="niveauSecuriteMotDePasse.class">
            {{ niveauSecuriteMotDePasse.text }}
          </span>
        </div>
      </div>

      <button type="submit" :disabled="enChargement || !formulaireValide">
        {{ enChargement ? 'Connexion en cours...' : 'Se connecter' }}
      </button>

      <div v-if="enChargement" class="chargement"></div>
      <div v-if="messageErreur" class="message-erreur">{{ messageErreur }}</div>
    </form>
  </div>
</template>

<script>
import axios from 'axios'
import authService from '@/services/authService'

export default {
  name: 'ConnexionCamping',

  data() {
    return {
      typeUtilisateur: 'campeur',
      identifiants: {
        Identifiant: '',
        Mot_de_passe: ''
      },
      enChargement: false,
      messageErreur: '',
      montrerMotDePasse: false,
      erreurs: {
        Mot_de_passe: ''
      },
      delaiMinimum: 1000,
      tempsDebutChargement: 0
    }
  },

  created() {
    // Vérifier si l'utilisateur est déjà connecté
    if (authService.isAuthenticated()) {
      // S'il y a une redirection spécifiée dans l'URL, aller à cet endroit
      const redirectPath = this.$route.query.redirect || '/panneau'
      this.$router.push(redirectPath)
    }
  },

  computed: {
    formulaireValide() {
      return (
        this.identifiants.Identifiant &&
        this.identifiants.Mot_de_passe &&
        !this.erreurs.Mot_de_passe
      )
    },

    niveauSecuriteMotDePasse() {
      if (!this.identifiants.Mot_de_passe) return { text: '', class: '' }

      const password = this.identifiants.Mot_de_passe
      let score = 0

      if (password.length >= 6) score++
      if (password.length >= 12) score++
      if (/\d/.test(password)) score++
      if (/[a-z]/.test(password) && /[A-Z]/.test(password)) score++

      switch (score) {
        case 0:
        case 1:
          return { text: 'Faible', class: 'faible' }
        case 2:
        case 3:
          return { text: 'Moyen', class: 'moyen' }
        case 4:
          return { text: 'Fort', class: 'fort' }
        default:
          return { text: 'Très fort', class: 'fort' }
      }
    }
  },

  methods: {
    changerTypeUtilisateur(type) {
      this.typeUtilisateur = type
      this.identifiants = {
        Identifiant: '',
        Mot_de_passe: ''
      }
      this.messageErreur = ''
      this.erreurs = {
        Mot_de_passe: ''
      }
    },

    validerMotDePasse() {
      const motDePasse = this.identifiants.Mot_de_passe
      let erreurs = []

      if (motDePasse.length < 6) {
        erreurs.push("au moins 6 caractères")
      }

      if (!/[A-Z]/.test(motDePasse)) {
        erreurs.push("une lettre majuscule")
      }

      if (!/\d/.test(motDePasse)) {
        erreurs.push("un chiffre")
      }

      if (erreurs.length > 0) {
        this.erreurs.Mot_de_passe = "Le mot de passe doit contenir " + erreurs.join(", ")
      } else {
        this.erreurs.Mot_de_passe = ""
      }
    },

    async soumettreFormulaire() {
  this.validerMotDePasse();

  if (!this.formulaireValide) {
    this.messageErreur = 'Veuillez corriger les erreurs dans le formulaire';
    return;
  }

  this.messageErreur = '';
  this.enChargement = true;
  this.tempsDebutChargement = Date.now();

  try {
    const endpoint = this.typeUtilisateur === 'campeur' 
      ? 'http://172.20.0.39:5000/login/campeur' 
      : 'http://172.20.0.39:5000/login/gerant';

    // Envoi des identifiants via POST
    const response = await axios.post(endpoint, {
      identifiant: this.identifiants.Identifiant,
      mot_de_passe: this.identifiants.Mot_de_passe
    });

    const user = response.data;

    // Authentification réussie
    authService.saveToken(user.token);
    authService.saveUserType(this.typeUtilisateur);
    authService.saveUserData(user);

    // Redirection après connexion
    const redirectPath = this.$route.query.redirect || '/panneau';
    this.$router.push(redirectPath);

  } catch (erreur) {
    this.messageErreur = erreur.response?.data?.message || erreur.message || "Erreur de connexion";
    console.error("Erreur:", erreur);
  } finally {
    this.enChargement = false;
  }
}
  }
}
</script>

<style scoped>
.connexion-conteneur {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  padding: 30px;
  width: 350px;
  margin: 50px auto;
}

h1 {
  text-align: center;
  color: #2c3e50;
  margin-bottom: 25px;
}

.selecteur-utilisateur {
  margin-bottom: 20px;
  text-align: center;
}

.selecteur-utilisateur button {
  padding: 10px 15px;
  margin: 0 5px;
  background-color: #e0e0e0;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.selecteur-utilisateur button.actif {
  background-color: #3498db;
  color: white;
}

.groupe-champ {
  margin-bottom: 15px;
  position: relative;
}

label {
  display: block;
  margin-bottom: 5px;
  color: #555;
}

input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
}

.input-password {
  position: relative;
}

.toggle-password {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  font-size: 16px;
  padding: 0;
}

.message-validation {
  color: #e74c3c;
  font-size: 12px;
  display: block;
  margin-top: 5px;
}

.erreur-champ {
  border-color: #e74c3c !important;
}

.password-strength {
  font-size: 12px;
  margin-top: 5px;
}

.password-strength .faible {
  color: #e74c3c;
}

.password-strength .moyen {
  color: #f39c12;
}

.password-strength .fort {
  color: #2ecc71;
}

button[type='submit'] {
  width: 100%;
  padding: 12px;
  background-color: #2ecc71;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  margin-top: 15px;
}

button[type='submit']:hover:not(:disabled) {
  background-color: #27ae60;
}

button[type='submit']:disabled {
  background-color: #95a5a6;
  cursor: not-allowed;
}

.message-erreur {
  color: #e74c3c;
  font-size: 14px;
  margin-top: 15px;
  text-align: center;
}

.chargement {
  text-align: center;
  margin-top: 15px;
}

.chargement::after {
  content: '';
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #3498db;
  border-radius: 50%;
  animation: rotation 1s linear infinite;
}

@keyframes rotation {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>