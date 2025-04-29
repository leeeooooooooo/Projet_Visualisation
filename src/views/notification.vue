<template>
  <div class="notification-page">
    <h1 class="page-title">Alertes de Consommation</h1>
    
    <div v-if="loading" class="loader">Chargement des alertes...</div>

    <div v-else-if="alerts.length === 0" class="no-alerts">
      ✅ Aucune alerte de consommation pour le moment.
    </div>

    <div v-else class="alert-list">
      <div 
        v-for="alert in alerts"
        :key="alert.id"
        class="alert-card"
        :class="{ critical: alert.niveau === 'critique', warning: alert.niveau === 'moyen' }"
      >
        <h2>{{ alert.emplacement }}</h2>
        <p><strong>Type :</strong> {{ alert.type }}</p>
        <p><strong>Quantité :</strong> {{ alert.quantite }} {{ alert.unite }}</p>
        <p><strong>Date :</strong> {{ formatDate(alert.date) }}</p>
        <p><strong>Niveau :</strong> {{ alert.niveau }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const alerts = ref([])
const loading = ref(true)

const fetchAlerts = async () => {
  try {
    const res = await axios.get('/api/alerts') // à adapter selon ton backend
    alerts.value = res.data
  } catch (error) {
    console.error('Erreur lors du chargement des alertes :', error)
  } finally {
    loading.value = false
  }
}

const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  return date.toLocaleString('fr-FR')
}

onMounted(fetchAlerts)
</script>

<style scoped>
.notification-page {
  padding: 2rem;
}

.page-title {
  font-size: 2rem;
  margin-bottom: 1.5rem;
}

.loader, .no-alerts {
  font-size: 1.2rem;
  color: #64748b;
}

.alert-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 1.5rem;
}

.alert-card {
  background: white;
  padding: 1.5rem;
  border-radius: 1rem;
  box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
  transition: 0.3s ease;
  border-left: 6px solid #3b82f6;
}

.alert-card.critical {
  border-left-color: #ef4444;
  background: #fef2f2;
}

.alert-card.warning {
  border-left-color: #facc15;
  background: #fffbeb;
}

.alert-card h2 {
  margin-bottom: 0.5rem;
}

.alert-card p {
  margin: 0.25rem 0;
}
</style>