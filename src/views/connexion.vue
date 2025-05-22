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
          <input 
            type="password" 
            id="password-campeur" 
            v-model="campeur.motDePasse" 
            required
            class="form-input"
            :disabled="isLoading"
          />
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
          <input 
            type="password" 
            id="password-gerant" 
            v-model="gerant.motDePasse" 
            required
            class="form-input"
            :disabled="isLoading"
          />
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
import Cookies from 'js-cookie'
export default {
  name: 'LoginForm',
  data() {
    return {
      userType: 'campeur', // Type d'utilisateur par défaut
      campeur: {
        numeroEmplacement: '',
        motDePasse: ''
      },
      gerant: {
        identifiant: '',
        motDePasse: ''
      },
      errorMessage: '',
      isLoading: false
    }
  },
  methods: {
    handleLogin() {
      this.errorMessage = ''; // Réinitialiser le message d'erreur
      
      if (this.userType === 'campeur') {
        // Vérifier que les champs sont remplis
        if (!this.campeur.numeroEmplacement || !this.campeur.motDePasse) {
          this.errorMessage = 'Veuillez remplir tous les champs';
          return;
        }
        
        // Appeler l'API pour le campeur
        this.loginCampeur();
      } else {
        // Vérifier que les champs sont remplis
        if (!this.gerant.identifiant || !this.gerant.motDePasse) {
          this.errorMessage = 'Veuillez remplir tous les champs';
          return;
        }
        
        // Appeler l'API pour le gérant
        this.loginGerant();
      }
    },
    
    loginCampeur() {
      this.isLoading = true;

      // Appel à l'API de connexion des campeurs
      axios.post('http://172.20.0.39:5000/login/campeur', {
        identifiant: this.campeur.numeroEmplacement,
        mot_de_passe: this.campeur.motDePasse
      }, {
        withCredentials: true // Important pour que le cookie de session soit envoyé/reçu
      })
        .then(response => {
          // Gestion de la session réussie
          console.log('Connexion campeur réussie:', response.data);

          // Pas besoin de stocker les données de session côté client, le serveur gère la session via le cookie
          
          // Rediriger vers le panneau du campeur avec son numéro d'emplacement
          this.$router.push(`/configuration`);
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

      // Appel à l'API de connexion des gérants
      axios.post('http://172.20.0.39:5000/login/gerant', {
        identifiant: this.gerant.identifiant,
        mot_de_passe: this.gerant.motDePasse
      }, {
        withCredentials: true // Important pour que le cookie de session soit envoyé/reçu
      })
        .then(response => {
          // Gestion de la session réussie
          console.log('Connexion gérant réussie:', response.data);

          // Pas besoin de stocker les données de session côté client, le serveur gère la session via le cookie
          
          // Rediriger vers le panneau du gérant
          this.$router.push('/configuration');
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
}
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