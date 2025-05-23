<template>
  <div class="consumption-container">
    <h1>Suivi des Consommations</h1>

    <!-- Bouton retour -->
    <button @click="goBack" class="back-button">Retour</button>

    <div class="controls">
      <!-- Saisie de l'emplacement par numéro -->
      <div class="location-input-group">
        <label for="locationInput">Numéro d'emplacement :</label>
        <input 
          id="locationInput"
          v-model="selectedLocation" 
          @keyup.enter="updateCharts"
          class="location-input" 
          type="text" 
          placeholder="Tapez le numéro d'emplacement"
          autocomplete="off"
        />
        <button @click="updateCharts" class="search-button">🔍</button>
      </div>

      <select v-model="chartType" @change="updateCharts">
        <option value="electricity">Consommation électrique (kWh)</option>
        <option value="water">Consommation d'eau (L)</option>
      </select>
      
      <select v-model="timeRange" @change="updateCharts">
        <option value="day">Journalier</option>
        <option value="week">Hebdomadaire</option>
        <option value="month">Mensuel</option>
      </select>
    </div>

    <!-- Affichage de l'emplacement sélectionné -->
    <div v-if="selectedLocation" class="location-info">
      <h3>📍 {{ getLocationName(selectedLocation) }} (N° {{ selectedLocation }})</h3>
    </div>
    <div v-else class="location-info warning">
      <h3>⚠️ Veuillez sélectionner un emplacement pour voir les données</h3>
    </div>

    <div class="chart-row">
      <div v-if="chartType === 'water'" class="chart-box">
        <h2>Consommation d'eau (L)</h2>
        <p v-if="!waterData.labels || waterData.labels.length === 0" class="no-data">
          Aucune donnée disponible pour cet emplacement
        </p>
        <canvas v-else ref="waterChart"></canvas>
      </div>

      <div v-if="chartType === 'electricity'" class="chart-box">
        <h2>Consommation électrique (kWh)</h2>
        <p v-if="!electricityData.labels || electricityData.labels.length === 0" class="no-data">
          Aucune donnée disponible pour cet emplacement
        </p>
        <canvas v-else ref="electricityChart"></canvas>
      </div>
    </div>

    <!-- Statistiques additionnelles -->
    <div v-if="selectedLocation" class="stats-row">
      <div class="stat-box">
        <h3>Statistiques</h3>
        <div v-if="chartType === 'water' && waterData.values">
          <p><strong>Consommation totale:</strong> {{ getTotalConsumption(waterData.values) }} L</p>
          <p><strong>Consommation moyenne:</strong> {{ getAverageConsumption(waterData.values) }} L</p>
        </div>
        <div v-if="chartType === 'electricity' && electricityData.values">
          <p><strong>Consommation totale:</strong> {{ getTotalConsumption(electricityData.values) }} kWh</p>
          <p><strong>Consommation moyenne:</strong> {{ getAverageConsumption(electricityData.values) }} kWh</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { Chart, registerables } from 'chart.js';

export default {
  name: 'ConsommationCharts',
  data() {
    return {
      timeRange: 'week',
      chartType: 'electricity',
      selectedLocation: '', // Maintenant c'est le numéro d'emplacement saisi
      locations: [], // Liste des emplacements disponibles (pour référence)
      waterData: { labels: [], values: [] },
      electricityData: { labels: [], values: [] },
      waterChart: null,
      electricityChart: null,
      searchTimeout: null // Pour la temporisation de recherche
    };
  },
  mounted() {
    Chart.register(...registerables);
    this.fetchLocations();
  },
  methods: {
    async fetchLocations() {
      try {
        // Récupérer la liste des emplacements
        const response = await axios.get('http://172.20.0.39:5000/emplacements');
        this.locations = response.data;
        console.log("Emplacements chargés:", this.locations); // Debug
        
        // Ne pas sélectionner automatiquement - laisser l'utilisateur choisir
        // if (this.locations.length > 0) {
        //   this.selectedLocation = this.locations[0].Numero_Emplacement;
        //   this.fetchData();
        // }
      } catch (error) {
        console.error("Erreur de chargement des emplacements:", error);
      }
    },

    async fetchData() {
      // Ne charger les données que si un emplacement est saisi
      if (!this.selectedLocation || this.selectedLocation.trim() === '') {
        console.log("Aucun emplacement saisi"); // Debug
        this.waterData = { labels: [], values: [] };
        this.electricityData = { labels: [], values: [] };
        this.initCharts();
        return;
      }

      console.log("Chargement des données pour l'emplacement:", this.selectedLocation.trim()); // Debug

      try {
        const locationNumber = this.selectedLocation.trim();
        // Utiliser les nouvelles APIs avec l'identifiant en paramètre
        const [waterRes, electricityRes] = await Promise.all([
          axios.get(`http://172.20.0.39:5000/consommation/eau/${locationNumber}`),
          axios.get(`http://172.20.0.39:5000/consommation/electricite/${locationNumber}`)
        ]);
        
        console.log("Données eau reçues:", waterRes.data); // Debug
        console.log("Données électricité reçues:", electricityRes.data); // Debug
        
        // Traiter les données avec le nouveau format
        this.waterData = this.processNewApiData(waterRes.data.consommations, 'eau');
        this.electricityData = this.processNewApiData(electricityRes.data.consommations, 'electricite');
        
        this.initCharts();
      } catch (error) {
        console.error("Erreur de chargement des données:", error);
        // Réinitialiser les données en cas d'erreur
        this.waterData = { labels: [], values: [] };
        this.electricityData = { labels: [], values: [] };
        this.initCharts();
      }
    },

    processNewApiData(rawData, type) {
  if (!rawData || rawData.length === 0) {
    return { labels: [], values: [] };
  }

  // Adapter ici aux vrais noms de champs de ta réponse JSON
  const convertedData = rawData.map(item => ({
    Date_heure: item.Date_heure,
    Quantite: item.Quantite
  }));

  return this.processData(convertedData);
    },

    processData(rawData) {
      if (!rawData || rawData.length === 0) {
        return { labels: [], values: [] };
      }

      // Grouper les données selon la période sélectionnée
      const grouped = {};

      rawData.forEach(item => {
        const date = new Date(item.Date_heure);
        let key;

        if (this.timeRange === 'day') {
          key = `${date.getHours()}h`;
        } else if (this.timeRange === 'week') {
          key = ['Dim', 'Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam'][date.getDay()];
        } else {
          key = date.toLocaleString('default', { month: 'short' });
        }

        const quantite = item.Quantite || item.Quantite_Eau || item.Quantite_Electricite || 0;
        grouped[key] = (grouped[key] || 0) + quantite;
      });

      return {
        labels: Object.keys(grouped),
        values: Object.values(grouped)
      };
    },

    initCharts() {
      // Détruire les anciens graphiques s'ils existent
      if (this.waterChart) {
        this.waterChart.destroy();
        this.waterChart = null;
      }
      if (this.electricityChart) {
        this.electricityChart.destroy();
        this.electricityChart = null;
      }

      // Attendre le prochain tick pour que les refs soient disponibles
      this.$nextTick(() => {
        // Créer le graphique d'eau si sélectionné et si des données existent
        if (this.chartType === 'water' && this.$refs.waterChart && this.waterData.labels.length > 0) {
          this.waterChart = new Chart(
            this.$refs.waterChart,
            this.getChartConfig('Eau (L)', '#4dc9f6', this.waterData)
          );
        }

        // Créer le graphique d'électricité si sélectionné et si des données existent
        if (this.chartType === 'electricity' && this.$refs.electricityChart && this.electricityData.labels.length > 0) {
          this.electricityChart = new Chart(
            this.$refs.electricityChart,
            this.getChartConfig('Électricité (kWh)', '#f67019', this.electricityData)
          );
        }
      });
    },

    getChartConfig(label, color, data) {
      return {
        type: 'bar',
        data: {
          labels: data.labels,
          datasets: [{
            label: label,
            data: data.values,
            backgroundColor: color,
            borderColor: color,
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true
            }
          },
          plugins: {
            legend: {
              display: true,
              position: 'top'
            }
          }
        }
      };
    },

    updateCharts() {
      console.log("Emplacement sélectionné:", this.selectedLocation); // Debug
        this.fetchData();
    },

    getLocationName(locationNumber) {
      const location = this.locations.find(loc => loc.Numero_Emplacement == locationNumber);
      return location ? location.nom : `Emplacement N°${locationNumber}`;
    },

    getTotalConsumption(values) {
      if (!values || values.length === 0) return 0;
      return values.reduce((sum, val) => sum + val, 0).toFixed(2);
    },

    getAverageConsumption(values) {
      if (!values || values.length === 0) return 0;
      const total = values.reduce((sum, val) => sum + val, 0);
      return (total / values.length).toFixed(2);
    },

    goBack() {
      this.$router.push('/panneau');
    }
  }
};
</script>

<style scoped>
.consumption-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.chart-row {
  display: flex;
  gap: 20px;
  margin-top: 30px;
}

.chart-box {
  flex: 1;
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  min-height: 400px;
}

.stats-row {
  display: flex;
  gap: 20px;
  margin-top: 20px;
}

.stat-box {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  flex: 1;
}

.location-info.warning {
  background: #fff3cd;
  border-left: 4px solid #ffc107;
  color: #856404;
}

.location-info {
  text-align: center;
  margin: 20px 0;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #3498db;
}

.location-info h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.1em;
}

.no-data {
  text-align: center;
  color: #7f8c8d;
  font-style: italic;
  padding: 40px;
}

h1 {
  color: #2c3e50;
  text-align: center;
}

h2 {
  color: #34495e;
  margin-top: 0;
  font-size: 1.2em;
}

h3 {
  color: #34495e;
  font-size: 1.1em;
}

canvas {
  width: 100% !important;
  height: 350px !important;
}

.controls {
  margin-top: 20px;
  text-align: center;
  display: flex;
  justify-content: center;
  gap: 15px;
  flex-wrap: wrap;
}

.location-input-group {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.location-input-group label {
  font-weight: 500;
  color: #2c3e50;
  white-space: nowrap;
}

.location-input {
  padding: 8px 15px;
  border-radius: 4px;
  border: 2px solid #3498db;
  font-size: 14px;
  min-width: 200px;
  background-color: #e8f4fd;
  font-weight: 500;
}

.location-input:focus {
  outline: none;
  border-color: #2980b9;
  box-shadow: 0 0 5px rgba(52, 152, 219, 0.3);
}

.search-button {
  background-color: #3498db;
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.3s;
}

.search-button:hover {
  background-color: #2980b9;
}

select {
  padding: 8px 15px;
  border-radius: 4px;
  border: 1px solid #ddd;
  font-size: 14px;
  min-width: 150px;
}

.back-button {
  background-color: #3498db;
  color: white;
  border: none;
  padding: 10px 20px;
  font-size: 1rem;
  cursor: pointer;
  margin-bottom: 20px;
  border-radius: 5px;
  transition: background-color 0.3s;
}

.back-button:hover {
  background-color: #2980b9;
}

/* Responsive */
@media (max-width: 768px) {
  .controls {
    flex-direction: column;
    align-items: center;
  }
  
  .chart-row {
    flex-direction: column;
  }
  
  select {
    min-width: 200px;
  }
}
</style>