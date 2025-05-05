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
        Seuil_Eau_Matin: null,
        Seuil_Eau_Midi: null,
        Seuil_Eau_Soir: null,
        Seuil_Electricite_Matin: null,
        Seuil_Electricite_Midi: null,
        Seuil_Electricite_Soir: null,
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
        const url = 'http://172.20.0.39:5000/seuils/configurer';
        const response = await axios.post(url, this.thresholdsForm, {
        headers: { 'Content-Type': 'application/json' },
        withCredentials: true
        });

        console.log('Réponse du serveur:', response.data);
        alert('Seuils configurés avec succès !');
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
    goToPanneau() {
      this.$router.push({ name: 'panneau' });
    }
  }
};
</script>

<style scoped>
/* Style reset */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  height: 100%;
  margin: 0;
  font-family: 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.app-container {
  background: linear-gradient(135deg, #c5e7f7, #e0c5f7);
  min-height: 100vh;
  padding: 2rem;
  color: #333;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.header {
  color: #2c3e50;
  font-size: 2.5rem;
  margin-bottom: 2rem;
  text-align: center;
}

.sub-header {
  color: #2c3e50;
  font-size: 1.8rem;
  margin-bottom: 1.5rem;
  text-align: center;
}

.section-title {
  color: #2c3e50;
  font-size: 1.2rem;
  margin-bottom: 1rem;
  border-bottom: 1px solid #d1d1d1;
  padding-bottom: 0.5rem;
}

/* Selection screen styles */
.selection-container {
  background-color: rgba(255, 255, 255, 0.8);
  border-radius: 15px;
  padding: 2rem;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 600px;
  text-align: center;
}

.selection-buttons {
  display: flex;
  justify-content: space-around;
  margin-top: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.option-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1.5rem;
  border: none;
  border-radius: 12px;
  background-color: white;
  color: #333;
  font-size: 1.2rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  width: 200px;
}

.option-btn i {
  font-size: 2rem;
  margin-bottom: 1rem;
}

.account-btn {
  background-color: #6ab7ff;
  color: white;
}

.threshold-btn {
  background-color: #7e57c2;
  color: white;
}

.option-btn:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
}

/* Form styles */
.form-container {
  background-color: rgba(255, 255, 255, 0.8);
  border-radius: 15px;
  padding: 2rem;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 700px;
}

.form-section {
  width: 100%;
}

.form-group, .threshold-group {
  margin-bottom: 1.2rem;
}

.threshold-group {
  margin-bottom: 2rem;
}

label {
  display: block;
  font-weight: 500;
  margin-bottom: 0.5rem;
  color: #555;
}

.form-input {
  width: 100%;
  padding: 0.8rem;
  border-radius: 8px;
  border: 1px solid #ddd;
  background-color: #f9f9f9;
  transition: border-color 0.3s ease, box-shadow 0.3s ease;
}

.form-input:focus {
  border-color: #7e57c2;
  box-shadow: 0 0 0 2px rgba(126, 87, 194, 0.2);
  outline: none;
}

.form-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 2rem;
}

.action-buttons {
  display: flex;
  gap: 1rem;
}

.submit-btn, .back-btn, .switch-btn {
  padding: 0.7rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.submit-btn {
  background-color: #4caf50;
  color: white;
}

.back-btn {
  background-color: #f5f5f5;
  color: #555;
}

.switch-btn {
  background-color: #ff9800;
  color: white;
}

.submit-btn:hover {
  background-color: #43a047;
}

.back-btn:hover {
  background-color: #e0e0e0;
}

.switch-btn:hover {
  background-color: #f57c00;
}

.dashboard-btn {
  margin-top: 2rem;
  padding: 0.7rem 1.5rem;
  border: none;
  border-radius: 8px;
  background-color: #607d8b;
  color: white;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.dashboard-btn:hover {
  background-color: #546e7a;
}

/* Responsive styles */
@media (max-width: 768px) {
  .form-container {
    padding: 1.5rem;
  }
  
  .option-btn {
    width: 100%;
    margin-bottom: 1rem;
  }
  
  .selection-buttons {
    flex-direction: column;
  }
  
  .form-actions {
    flex-direction: column;
    gap: 1rem;
  }
  
  .action-buttons {
    width: 100%;
    justify-content: space-between;
  }
  
  .submit-btn {
    width: 100%;
  }
}
</style>