<template>
  <div class="dashboard">
    <header class="dashboard-header">
      <h1>Tableau de bord</h1>
      <div class="user-info">
        <span class="user-type">{{ userTypeDisplay }}</span>
        <button class="logout-btn" @click="logout">
          <LogOut size="18" />
          <span>Déconnexion</span>
        </button>
      </div>
    </header>
    
    <main class="cards-container">
      <router-link 
        v-for="card in filteredCards"
        :key="card.title"
        :to="card.route"
        class="dashboard-card"
        :class="card.colorClass"
      >
        <div class="card-content">
          <div class="card-icon">
            <component :is="card.icon" size="64" />
          </div>
          <h2 class="card-title">{{ card.title }}</h2>
          <p class="card-description">{{ card.description }}</p>
        </div>
        <div class="hover-wave"></div>
      </router-link>
    </main>
    
    <footer class="dashboard-footer">
      <p>Projet Maîtrise des consommations</p>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import authService from '@/services/authService';

// État initial
const isLoading = ref(true);
const campingInfo = ref(null);
const campingServices = ref([]);
const userType = computed(() => authService.getUserType()); // Utilisation de la méthode getUserType

// En fonction du type d'utilisateur, définissons les données à afficher
const userData = computed(() => {
  if (userType.value === 'campeur') {
    return {
      occupancy: 0,
      todayBookings: 0,
      pendingServices: 0
    };
  } else {
    return {
      occupancy: 75,
      todayBookings: 5,
      pendingServices: 3
    };
  }
});

// Récupération des données
const occupancy = computed(() => userData.value.occupancy);
const todayBookings = computed(() => userData.value.todayBookings);
const pendingServices = computed(() => userData.value.pendingServices);

// Récupérer les données nécessaires au chargement
onMounted(async () => {
  try {
    const userResponse = await authService.getCurrentUser();
    // Si la réponse est valide, mettre à jour les données
    isLoading.value = false;
  } catch (error) {
    console.error('Erreur lors du chargement des données:', error.message);
    // Rediriger vers la page de connexion en cas d'erreur
    window.location.href = '/login';
  }
});

// Fonctions pour les actions
function requestService(serviceId) {
  // Demander un service spécifique
  console.log(`Service ${serviceId} demandé`);
}

function viewAllCampers() {
  // Afficher tous les campeurs
  console.log('Affichage de tous les campeurs');
}

function manageServices() {
  // Gérer les services
  console.log('Gestion des services');
}

function manageBookings() {
  // Gérer les réservations
  console.log('Gestion des réservations');
}

// Formater les dates
function formatDate(dateString) {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString('fr-FR');
}
</script>


<style scoped>
/* Variables pour les couleurs */
:root {
  --blue-gradient: linear-gradient(135deg, #60a5fa, #3b82f6);
  --green-gradient: linear-gradient(135deg, #4ade80, #10b981);
  --orange-gradient: linear-gradient(135deg, #fb923c, #f97316);
  --purple-gradient: linear-gradient(135deg, #c084fc, #8b5cf6);
  --header-gradient: linear-gradient(90deg, #1e40af, #3b82f6);
  --text-primary: #1e293b;
  --text-secondary: #475569;
  --text-light: #f8fafc;
}

/* Reset et base */
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

.dashboard {
  min-height: 100vh;
  width: 100%;
  background-color: #f1f5f9;
  display: flex;
  flex-direction: column;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* En-tête */
.dashboard-header {
  background: var(--header-gradient);
  color: black;
  padding: 1.5rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.dashboard-header h1 {
  font-size: 1.75rem;
  font-weight: 600;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.user-type {
  font-weight: 600;
  padding: 0.5rem 1.25rem;
  background-color: rgba(255, 255, 255, 0.25);
  border-radius: 2rem;
  backdrop-filter: blur(5px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  text-transform: uppercase;
  font-size: 0.85rem;
  letter-spacing: 0.5px;
  color: black;
  border: 1px solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
}

.logout-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background-color: transparent;
  border: 1px solid rgba(255, 255, 255, 0.5);
  color: black;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.logout-btn:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

/* Conteneur principal pour les cartes */
.cards-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 1.5rem;
  padding: 2rem;
  flex-grow: 1;
}

/* Styles des cartes */
.dashboard-card {
  height: 260px;
  background-color: white;
  border-radius: 1rem;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  position: relative;
  text-decoration: none;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
  transform: translateY(40px);
  opacity: 0;
}

.dashboard-card.show {
  transform: translateY(0);
  opacity: 1;
}

.dashboard-card:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  z-index: 10;
}

.card-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 2rem;
  z-index: 2;
  transition: transform 0.5s ease;
}

.dashboard-card:hover .card-content {
  transform: translateY(-8px);
}

.card-icon {
  background-color: rgba(255, 255, 255, 0.4); /* éventuellement plus opaque */
  color: #1e293b; /* pour ressortir */
}

.dashboard-card:hover .card-icon {
  transform: scale(1.1) rotate(10deg);
}

.card-title {
  color: #1e293b; /* texte sombre */
}

.card-description {
  color: rgba(30, 41, 59, 0.8); /* un gris foncé */
}

/* Couleurs des cartes avec dégradés */
.card-blue {
  background: var(--blue-gradient);
}

.card-green {
  background: var(--green-gradient);
}

.card-orange {
  background: var(--orange-gradient);
}

.card-purple {
  background: var(--purple-gradient);
}

/* Effet de vague au survol */
.hover-wave {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: radial-gradient(circle at center, rgba(255, 255, 255, 0.4) 0%, rgba(255, 255, 255, 0) 70%);
  transform: scale(0);
  opacity: 0;
  transition: transform 1s ease-out, opacity 0.6s ease;
  z-index: 1;
}

.dashboard-card:hover .hover-wave {
  transform: scale(2);
  opacity: 0.8;
}

/* Pied de page */
.dashboard-footer {
  background-color: #0f172a;
  color: #94a3b8;
  text-align: center;
  padding: 1rem;
  font-size: 0.875rem;
}

/* Responsive design */
@media (max-width: 768px) {
  .dashboard-header {
    flex-direction: column;
    gap: 1rem;
    padding: 1rem;
  }
  
  .user-info {
    width: 100%;
    justify-content: space-between;
  }
  
  .cards-container {
    grid-template-columns: 1fr;
    padding: 1rem;
  }
  
  .dashboard-card {
    height: 220px;
  }
}

@media (min-width: 769px) and (max-width: 1024px) {
  .cards-container {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1800px) {
  .cards-container {
    grid-template-columns: repeat(4, 1fr);
    max-width: 1600px;
    margin: 0 auto;
  }
}
</style>