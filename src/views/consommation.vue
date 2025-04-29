<template>
  <div class="consumption-container">
    <h1>Suivi des Consommations</h1>

    <!-- Bouton retour -->
    <button @click="goBack" class="back-button">Retour</button>

    <div class="controls">
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

    <div class="chart-row">
      <div v-if="chartType === 'water'" class="chart-box">
        <h2>Consommation d'eau (L)</h2>
        <canvas ref="waterChart"></canvas>
      </div>

      <div v-if="chartType === 'electricity'" class="chart-box">
        <h2>Consommation électrique (kWh)</h2>
        <canvas ref="electricityChart"></canvas>
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
      chartType: 'electricity',  // Par défaut, afficher l'électricité
      waterData: [],
      electricityData: [],
      waterChart: null,
      electricityChart: null
    };
  },
  mounted() {
    Chart.register(...registerables);
    this.fetchData();
  },
  methods: {
    async fetchData() {
      try {
        const token = localStorage.getItem('token');
        const config = { headers: { Authorization: `Bearer ${token}` } };
        
        const [waterRes, electricityRes] = await Promise.all([
          axios.get('http://172.20.0.39:5000/consommation/eau', config),
          axios.get('http://172.20.0.39:5000/consommation/electricite', config)
        ]);
        
        this.waterData = this.processData(waterRes.data);
        this.electricityData = this.processData(electricityRes.data);
        
        this.initCharts();
      } catch (error) {
        console.error("Erreur de chargement:", error);
      }
    },

    processData(rawData) {
      // Grouper les données selon la période sélectionnée
      const grouped = {};

      rawData.forEach(item => {
        const date = new Date(item.Date_Heure);
        let key;

        if (this.timeRange === 'day') {
          key = `${date.getHours()}h`;
        } else if (this.timeRange === 'week') {
          key = ['Dim', 'Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam'][date.getDay()];
        } else {
          key = date.toLocaleString('default', { month: 'short' });
        }

        grouped[key] = (grouped[key] || 0) + item.Quantite;
      });

      return {
        labels: Object.keys(grouped),
        values: Object.values(grouped)
      };
    },

    initCharts() {
      // Détruire les anciens graphiques s'ils existent
      if (this.waterChart) this.waterChart.destroy();
      if (this.electricityChart) this.electricityChart.destroy();

      // Créer le graphique d'eau si sélectionné
      if (this.chartType === 'water') {
        this.waterChart = new Chart(
          this.$refs.waterChart,
          this.getChartConfig('Eau', '#4dc9f6', this.waterData)
        );
      }

      // Créer le graphique d'électricité si sélectionné
      if (this.chartType === 'electricity') {
        this.electricityChart = new Chart(
          this.$refs.electricityChart,
          this.getChartConfig('Électricité', '#f67019', this.electricityData)
        );
      }
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
          scales: {
            y: {
              beginAtZero: true
            }
          }
        }
      };
    },

    updateCharts() {
      this.fetchData();
    },

    // Méthode pour rediriger vers le panneau
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

canvas {
  width: 100% !important;
  height: 500px !important;  /* Augmenter la hauteur ici */
}

.controls {
  margin-top: 20px;
  text-align: center;
}

select {
  padding: 8px 15px;
  border-radius: 4px;
  border: 1px solid #ddd;
  margin-right: 10px;
}

/* Style du bouton retour */
.back-button {
  background-color: #3498db;
  color: white;
  border: none;
  padding: 10px 20px;
  font-size: 1rem;
  cursor: pointer;
  margin-bottom: 20px;
  border-radius: 5px;
}

.back-button:hover {
  background-color: #2980b9;
}
</style>