<template>
  <div id="app">
    <h1>Gestion du camping</h1>

    <div v-if="currentView === 'selection'">
      <h2>Que faire ?</h2>
      <button @click="showAccountForm">Créer un compte</button>
      <button @click="showThresholdForm">Configurer les seuils</button>
    </div>

    <div v-if="currentView === 'account'">
      <h2>Créer un compte</h2>

      <label>Type de compte :
        <select v-model="accountForm.userType" @change="handleUserTypeChange">
          <option value="campeur">Campeur</option>
          <option value="gerant">Gérant</option>
        </select>
      </label>

      <div v-if="accountForm.userType === 'campeur'">
        <label>Numéro d'emplacement :
          <input v-model.number="accountForm.Numero_Emplacement" type="number" />
        </label>
        <label>Mot de passe :
          <input v-model="accountForm.Mot_de_passe" type="password" />
        </label>
        <label>Date de début :
          <input v-model="accountForm.Date_Debut" type="date" />
        </label>
        <label>Date de fin :
          <input v-model="accountForm.Date_Fin" type="date" />
        </label>
      </div>

      <div v-if="accountForm.userType === 'gerant'">
        <label>Identifiant :
          <input v-model="accountForm.Identifiant" type="text" />
        </label>
        <label>Mot de passe :
          <input v-model="accountForm.Mot_de_passe" type="password" />
        </label>
        <label>Email :
          <input v-model="accountForm.Email" type="email" />
        </label>
        <label>Téléphone :
          <input v-model="accountForm.Telephone" type="tel" />
        </label>
      </div>

      <button @click="backToSelection">Retour</button>
      <button @click="switchToThresholds">Configurer les seuils</button>
      <button @click="submitForm">Valider</button>
    </div>

    <div v-if="currentView === 'threshold'">
      <h2>Configurer les seuils</h2>

      <label>Numéro d'emplacement :
        <input v-model.number="thresholdsForm.Numero_Emplacement" type="number" required />
      </label>

      <h3>Seuils d'eau</h3>
      <label>Matin :
        <input v-model.number="thresholdsForm.Seuil_Eau_Matin" type="number" />
      </label>
      <label>Midi :
        <input v-model.number="thresholdsForm.Seuil_Eau_Midi" type="number" />
      </label>
      <label>Soir :
        <input v-model.number="thresholdsForm.Seuil_Eau_Soir" type="number" />
      </label>
      <label>Nuit :
        <input v-model.number="thresholdsForm.Seuil_Eau_Nuit" type="number" />
      </label>

      <h3>Seuils électricité</h3>
      <label>Matin :
        <input v-model.number="thresholdsForm.Seuil_Electricite_Matin" type="number" />
      </label>
      <label>Midi :
        <input v-model.number="thresholdsForm.Seuil_Electricite_Midi" type="number" />
      </label>
      <label>Soir :
        <input v-model.number="thresholdsForm.Seuil_Electricite_Soir" type="number" />
      </label>
      <label>Nuit :
        <input v-model.number="thresholdsForm.Seuil_Electricite_Nuit" type="number" />
      </label>

      <button @click="backToSelection">Retour</button>
      <button @click="switchToAccounts">Créer un compte</button>
      <button @click="submitThresholds">Valider</button>
    </div>

    <button @click="goToPanneau">Retour au tableau de bord</button>
  </div>
</template>


<script>
import axios from 'axios';

export default {
  name: 'ConfigurationComponent',
  data() {
    return {
      currentView: 'selection', // 'selection', 'account', 'threshold'
      accountForm: {
        userType: 'campeur',
        Mot_de_passe: '',
        Numero_Emplacement: null,
        Date_Debut: '',
        Date_Fin: '',
        Identifiant: '', // Gardé dans le data mais pas utilisé pour les campeurs
        Email: '',
        Telephone: ''
      },
      thresholdsForm: {
        Numero_Emplacement: null,
        Seuil_Eau_Matin: null,
        Seuil_Eau_Midi: null,
        Seuil_Eau_Soir: null,
        Seuil_Eau_Nuit: null,
        Seuil_Electricite_Matin: null,
        Seuil_Electricite_Midi: null,
        Seuil_Electricite_Soir: null,
        Seuil_Electricite_Nuit: null,
      }
    };
  },
  methods: {
    showAccountForm() {
      this.currentView = 'account';
    },
    showThresholdForm() {
      this.currentView = 'threshold';
    },
    backToSelection() {
      this.currentView = 'selection';
    },
    switchToThresholds() {
      this.currentView = 'threshold';
    },
    switchToAccounts() {
      this.currentView = 'account';
    },
    handleUserTypeChange() {
      if (this.accountForm.userType === 'campeur') {
        this.accountForm.Email = '';
        this.accountForm.Telephone = '';
      } else {
        this.accountForm.Numero_Emplacement = null;
        this.accountForm.Date_Debut = '';
        this.accountForm.Date_Fin = '';
      }
    },
    async submitForm() {
      try {
        const url = this.accountForm.userType === 'campeur'
          ? 'http://172.20.0.39:5000/creation/campeur'
          : 'http://172.20.0.39:5000/creation/gerant';
          
        const formData = this.accountForm.userType === 'campeur'
          ? {
              // Identifiant supprimé de l'envoi pour les campeurs
              mot_de_passe: this.accountForm.Mot_de_passe,
              date_debut: this.accountForm.Date_Debut,
              date_fin: this.accountForm.Date_Fin,
              numero_emplacement: this.accountForm.Numero_Emplacement,
            }
          : {
              identifiant: this.accountForm.Identifiant,
              mot_de_passe: this.accountForm.Mot_de_passe,
              email: this.accountForm.Email,
              Telephone: this.accountForm.Telephone
            };
                                               
            const response = await axios.post(url, formData, {
            headers: { 'Content-Type': 'application/json' },
            withCredentials: true
        });

        console.log('Réponse du serveur:', response.data);
        alert('Compte créé avec succès !');
        this.resetForm();
      } catch (error) {
        console.error('Erreur lors de l\'envoi des données :', error);
        alert('Échec de la création du compte: ' + (error.response?.data?.message || error.message));
      }
    },
    async submitThresholds() {
      try {
        // Vérifier que le numéro d'emplacement est fourni
        if (!this.thresholdsForm.Numero_Emplacement) {
          alert('Veuillez saisir un numéro d\'emplacement.');
          return;
        }

        const url = 'https://172.20.0.39:5000/seuils';
        const response = await axios.post(url, this.thresholdsForm, {
        headers: { 'Content-Type': 'application/json' },
        withCredentials: true
        });

        console.log('Réponse du serveur:', response.data);
        alert('Seuils configurés avec succès !');
        this.resetThresholdsForm();
      } catch (error) {
        console.error('Erreur lors de l\'envoi des seuils :', error);
        alert('Échec de la configuration des seuils: ' + (error.response?.data?.message || error.message));
      }
    },
    resetForm() {
      this.accountForm = {
        userType: this.accountForm.userType,
        Mot_de_passe: '',
        Numero_Emplacement: null,
        Date_Debut: '',
        Date_Fin: '',
        Identifiant: '',
        Email: '',
        Telephone: ''
      };
    },
    resetThresholdsForm() {
      this.thresholdsForm = {
        Numero_Emplacement: null,
        Seuil_Eau_Matin: null,
        Seuil_Eau_Midi: null,
        Seuil_Eau_Soir: null,
        Seuil_Eau_Nuit: null,
        Seuil_Electricite_Matin: null,
        Seuil_Electricite_Midi: null,
        Seuil_Electricite_Soir: null,
        Seuil_Electricite_Nuit: null,
      };
    },
    goToPanneau() {
      this.$router.push({ name: 'panneau' });
    }
  }
};
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  height: 100%;
  font-family: 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background: linear-gradient(135deg, #c5e7f7, #e0c5f7);
  display: flex;
  justify-content: center;
  align-items: center;
}

/* Conteneur principal centré */
.app-container {
  background-color: white;
  padding: 3rem 4rem;
  border-radius: 20px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
  max-width: 800px;
  width: 100%;
}

/* Titres */
h1 {
  font-size: 2.5rem;
  color: #2c3e50;
  margin-bottom: 2rem;
  text-align: center;
}

h2 {
  font-size: 2rem;
  color: #2c3e50;
  margin-bottom: 1.5rem;
  text-align: center;
}

h3 {
  font-size: 1.5rem;
  color: #2c3e50;
  margin-top: 2rem;
  margin-bottom: 1rem;
  text-align: center;
}

/* Labels */
label {
  display: block;
  margin: 1rem 0;
  font-size: 1.2rem;
}

/* Inputs et selects */
input,
select {
  display: block;
  width: 100%;
  padding: 0.75rem;
  margin-top: 0.25rem;
  font-size: 1rem;
  border: 1px solid #ccc;
  border-radius: 10px;
}

/* Boutons */
button {
  margin: 1rem 0.5rem 0;
  padding: 0.8rem 1.5rem;
  font-size: 1.2rem;
  border: none;
  border-radius: 12px;
  background-color: #3498db;
  color: white;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

button:hover {
  background-color: #2980b9;
}

/* Centrage des boutons dans chaque section */
div[v-if] {
  text-align: center;
}
</style>