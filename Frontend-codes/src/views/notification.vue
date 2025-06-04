<template>
  <div class="notification">
    <h2>Alertes consommation</h2>
    <button @click="chargerAlertes" :disabled="loading">
      {{ loading ? "Chargement..." : "Vérifier les alertes" }}
    </button>

    <div v-if="error" class="error">
      Erreur : {{ error }}
    </div>

    <div v-if="message" class="message">
      {{ message }}
    </div>

    <ul v-if="alertes.length > 0" class="alert-list">
      <li v-for="(alerte, index) in alertes" :key="index">
        🚨 {{ alerte }}
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  data() {
    return {
      alertes: [],
      message: '',
      error: '',
      loading: false,
    };
  },
  methods: {
    async chargerAlertes() {
      this.loading = true;
      this.error = '';
      this.message = '';
      this.alertes = [];

      try {
        const response = await fetch('https://172.20.0.39:5000/alerte/consommation', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({}), // tu peux envoyer des données si besoin
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status} - ${response.statusText}`);
        }

        const data = await response.json();

        if (data.message) {
          // Si message simple (aucun dépassement)
          this.message = data.message;
        }

        // Si alertes détaillées (ex: details, email, telephone)
        if (data.details) {
          // Je sépare les lignes d'alerte pour afficher chacune dans la liste
          this.alertes = data.details.split('\n').filter(line => line.trim() !== '');
        }
      } catch (err) {
        this.error = err.message || 'Erreur lors de la récupération des alertes';
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>

<style scoped>
.notification {
  max-width: 400px;
  margin: 20px auto;
  font-family: Arial, sans-serif;
}
button {
  padding: 10px 15px;
  cursor: pointer;
}
.error {
  color: red;
  margin-top: 10px;
}
.message {
  margin-top: 10px;
  font-weight: bold;
}
.alert-list {
  margin-top: 15px;
  list-style-type: none;
  padding-left: 0;
}
.alert-list li {
  background: #ffdddd;
  border: 1px solid red;
  padding: 8px;
  margin-bottom: 5px;
  border-radius: 4px;
}
</style>
