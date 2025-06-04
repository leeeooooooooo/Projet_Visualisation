<template>
  <div class="login-container">
    <div class="login-card">
      <h1 class="title">Connexion</h1>

      <!-- Sélection du type d'utilisateur -->
      <div class="user-type-selector">
        <button 
          @click="userType = 'campeur'" 
          :class="{ active: userType === 'campeur' }"
          class="type-button"
          :disabled="isLoading"
        >
          Campeur
        </button>
        <button 
          @click="userType = 'gerant'" 
          :class="{ active: userType === 'gerant' }"
          class="type-button"
          :disabled="isLoading"
        >
          Gérant
        </button>
      </div>

      <!-- Formulaire pour Campeur -->
      <form v-if="userType === 'campeur'" @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="emplacement">Numéro emplacement</label>
          <input 
            type="text" 
            id="emplacement" 
            v-model="campeur.numeroEmplacement" 
            required
            class="form-input"
            :disabled="isLoading"
          />
        </div>

        <div class="form-group">
          <label for="password-campeur">Mot de passe</label>
          <div class="password-wrapper">
            <input 
              :type="showPasswordCampeur ? 'text' : 'password'" 
              id="password-campeur" 
              v-model="campeur.motDePasse" 
              required
              class="form-input"
              :disabled="isLoading"
            />
            <button type="button" @click="showPasswordCampeur = !showPasswordCampeur" class="toggle-password">
              <span v-if="showPasswordCampeur">🔓</span>
              <span v-else>🔒</span>
            </button>
          </div>
        </div>

        <button type="submit" class="submit-button" :disabled="isLoading">
          <span v-if="isLoading">Connexion en cours...</span>
          <span v-else>Se connecter</span>
        </button>
      </form>

      <!-- Formulaire pour Gérant -->
      <form v-if="userType === 'gerant'" @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="identifiant">Identifiant</label>
          <input 
            type="text" 
            id="identifiant" 
            v-model="gerant.identifiant" 
            required
            class="form-input"
            :disabled="isLoading"
          />
        </div>

        <div class="form-group">
          <label for="password-gerant">Mot de passe</label>
          <div class="password-wrapper">
            <input 
              :type="showPasswordGerant ? 'text' : 'password'" 
              id="password-gerant" 
              v-model="gerant.motDePasse" 
              required
              class="form-input"
              :disabled="isLoading"
            />
            <button type="button" @click="showPasswordGerant = !showPasswordGerant" class="toggle-password">
              <span v-if="showPasswordGerant">🔓</span>
              <span v-else>🔒</span>
            </button>
          </div>
        </div>

        <button type="submit" class="submit-button" :disabled="isLoading">
          <span v-if="isLoading">Connexion en cours...</span>
          <span v-else>Se connecter</span>
        </button>
      </form>

      <!-- Message d'erreur -->
      <div v-if="errorMessage" class="error-message">
        {{ errorMessage }}
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import authService from '@/services/authService'; // AJOUT : Import de votre authService

export default {
  name: 'LoginForm',
  data() {
    return {
      userType: 'campeur',
      campeur: {
        numeroEmplacement: '',
        motDePasse: ''
      },
      gerant: {
        identifiant: '',
        motDePasse: ''
      },
      showPasswordCampeur: false,
      showPasswordGerant: false,
      errorMessage: '',
      isLoading: false
    };
  },
  
  // AJOUT : Nettoyage des anciennes sessions au chargement
  mounted() {
    console.log('=== NETTOYAGE AU CHARGEMENT DE LA PAGE LOGIN ===');
    authService.logout(); // Nettoie les anciennes sessions
    authService.debugCookies();
  },
  
  methods: {
    handleLogin() {
      this.errorMessage = '';

      if (this.userType === 'campeur') {
        if (!this.campeur.numeroEmplacement || !this.campeur.motDePasse) {
          this.errorMessage = 'Veuillez remplir tous les champs';
          return;
        }
        this.loginCampeur();
      } else {
        if (!this.gerant.identifiant || !this.gerant.motDePasse) {
          this.errorMessage = 'Veuillez remplir tous les champs';
          return;
        }
        this.loginGerant();
      }
    },

    loginCampeur() {
      this.isLoading = true;
      console.log('=== TENTATIVE DE CONNEXION CAMPEUR ===');

      // AJOUT : Nettoyage avant connexion
      authService.logout();

      axios.post('/login/campeur', {
        identifiant: this.campeur.numeroEmplacement,
        mot_de_passe: this.campeur.motDePasse
      }, {
        withCredentials: true
      })
        .then(response => {
          console.log('Connexion campeur réussie:', response.data);
          
          // AJOUT : Gestion côté frontend après succès
          if (response.data && response.data.id_campeur) {
            // Si le serveur renvoie l'ID, on l'utilise
            authService.setSession('campeur', response.data.id_campeur);
          } else {
            // Sinon on attend un peu que le serveur ait défini le cookie
            setTimeout(() => {
              console.log('Vérification des cookies après connexion campeur:');
              authService.debugCookies();
            }, 100);
          }
          
          this.$router.push('/panneau');
        })
        .catch(error => {
          console.error('Erreur de connexion campeur:', error);
          this.errorMessage = error.response?.data?.message || 'Erreur de connexion, veuillez réessayer';
        })
        .finally(() => {
          this.isLoading = false;
        });
    },

    loginGerant() {
      this.isLoading = true;
      console.log('=== TENTATIVE DE CONNEXION GÉRANT ===');

      // AJOUT : Nettoyage avant connexion
      authService.logout();

      axios.post('/login/gerant', {
        identifiant: this.gerant.identifiant,
        mot_de_passe: this.gerant.motDePasse
      }, {
        withCredentials: true
      })
        .then(response => {
          console.log('Connexion gérant réussie:', response.data);
          
          // AJOUT : Gestion côté frontend après succès
          if (response.data && response.data.id_gerant) {
            // Si le serveur renvoie l'ID, on l'utilise
            authService.setSession('gerant', response.data.id_gerant);
          } else {
            // Sinon on attend un peu que le serveur ait défini le cookie
            setTimeout(() => {
              console.log('Vérification des cookies après connexion gérant:');
              authService.debugCookies();
            }, 100);
          }
          
          this.$router.push('/panneau');
        })
        .catch(error => {
          console.error('Erreur de connexion gérant:', error);
          this.errorMessage = error.response?.data?.message || 'Erreur de connexion, veuillez réessayer';
        })
        .finally(() => {
          this.isLoading = false;
        });
    }
  }
};
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f5f5;
  font-family: Arial, sans-serif;
}

.login-card {
  width: 400px;
  padding: 2rem;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.title {
  text-align: center;
  color: #333;
  margin-bottom: 1.5rem;
}

.user-type-selector {
  display: flex;
  margin-bottom: 1.5rem;
  border-radius: 4px;
  overflow: hidden;
}

.type-button {
  flex: 1;
  padding: 0.75rem;
  background-color: #e0e0e0;
  border: none;
  cursor: pointer;
  transition: background-color 0.3s;
}

.type-button.active {
  background-color: #4caf50;
  color: white;
}

.login-form {
  display: flex;
  flex-direction: column;
}

.form-group {
  margin-bottom: 1rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  color: #555;
  font-weight: bold;
}

.form-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.password-wrapper {
  position: relative;
}

.toggle-password {
  position: absolute;
  top: 0%;
  right: 0.0rem;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.2rem;
}

.submit-button {
  padding: 0.75rem;
  background-color: #4caf50;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  margin-top: 1rem;
  transition: background-color 0.3s;
}

.submit-button:hover {
  background-color: #45a049;
}

.error-message {
  color: #f44336;
  margin-top: 1rem;
  text-align: center;
}
</style>