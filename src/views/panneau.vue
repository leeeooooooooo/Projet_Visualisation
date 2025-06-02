<template>
  <div class="dashboard">
    <header class="dashboard-header">
      <h1>Tableau de bord</h1>
      <div class="user-info">
        <span class="user-type">{{ userTypeDisplay }}</span>
        <button class="logout-btn" @click="logout" aria-label="Déconnexion">
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
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import authService from '@/services/authService'

const router = useRouter()

// Réactifs pour stocker rôle et id utilisateur récupérés
const userType = ref('campeur')  // valeur par défaut
const userId = ref(null)

// Affichage lisible du type utilisateur
const userTypeDisplay = computed(() => 
  userType.value === 'gerant' ? 'Espace Gérant' : 'Espace Campeur'
)

// Cartes accessibles (inchangé)
const allCards = [
  // ... mêmes cartes que dans ton code
]

// Filtrage des cartes visibles selon le type d'utilisateur
const filteredCards = computed(() => 
  allCards.filter(card => card.access.includes(userType.value))
)

onMounted(async () => {
  try {
    const res = await fetch('/user/role', {
      method: 'GET',
      credentials: 'include' // pour envoyer les cookies
    })

    if (res.ok) {
      const text = await res.text()
      console.log('Réponse brute du serveur :', text)

      let data
      try {
        data = JSON.parse(text)
      } catch (parseError) {
        console.error('Erreur de parsing JSON:', parseError)
        userType.value = 'inconnu'
        userId.value = null
        authService.setUserType(null)
        authService.setUserId(null)
        router.push('/')
        return
      }

      userType.value = data.role
      userId.value = data.id

      // Mise à jour dans authService
      authService.setUserType(data.role)
      authService.setUserId(data.id)

      console.log("Type d'utilisateur:", userType.value)
      console.log('ID utilisateur:', userId.value)
    } else {
      console.warn('Utilisateur inconnu, non connecté')
      userType.value = 'inconnu'
      userId.value = null
      authService.setUserType(null)
      authService.setUserId(null)
      router.push('/')
    }
  } catch (error) {
    console.error('Erreur lors de la récupération du rôle utilisateur:', error)
  }

  await nextTick()
  const cards = document.querySelectorAll('.dashboard-card')
  cards.forEach((card, index) => {
    setTimeout(() => {
      card.classList.add('show')
    }, 100 * (index + 1))
  })
})

const logout = () => {
  authService.logout()
  router.push('/')
}
</script>

<style>
/* Variables de couleur */
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

/* Reset */
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

/* Conteneur des cartes */
.cards-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 1.5rem;
  padding: 2rem;
  flex-grow: 1;
}

/* Carte */
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
  background-color: rgba(255, 255, 255, 0.4);
  color: #1e293b;
  border-radius: 50%;
  padding: 1rem;
  margin-bottom: 1rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.3s ease;
}

.dashboard-card:hover .card-icon {
  transform: scale(1.1) rotate(10deg);
}

.card-title {
  color: #1e293b;
  margin-bottom: 0.5rem;
  font-size: 1.5rem;
  font-weight: 600;
}

.card-description {
  color: rgba(30, 41, 59, 0.8);
  font-size: 1rem;
}

/* Couleurs */
.card-blue {
  background: var(--blue-gradient);
  color: var(--text-light);
}

.card-green {
  background: var(--green-gradient);
  color: var(--text-light);
}

.card-orange {
  background: var(--orange-gradient);
  color: var(--text-light);
}

.card-purple {
  background: var(--purple-gradient);
  color: var(--text-light);
}

/* Vague au survol */
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

/* Responsive */
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
    gap: 2rem;
    padding: 3rem 4rem;
  }
}
</style>
