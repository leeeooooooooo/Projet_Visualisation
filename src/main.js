import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import axios from 'axios'
import authService from '@/services/authService'

// Création de l'application Vue
const app = createApp(App)


// Configuration globale d'axios
axios.defaults.baseURL = 'http://localhost:3005' // URL de base de votre API

// Intercepteur pour gérer les erreurs 401 (non autorisé)
axios.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      authService.logout() // Déconnecte l'utilisateur
      router.push('/connexion') // Redirige vers la page de connexion
    }
    return Promise.reject(error)
  }
)

// Injection du service d'authentification dans toute l'application
app.config.globalProperties.$auth = authService

// Initialisation de l'authentification au démarrage
// Utilisez bien la méthode initialize() et non initializeAuth()

// Application du router
app.use(router)

// Montage de l'application
app.mount('#app')

// Message de confirmation en développement
if (process.env.NODE_ENV === 'development') {
  console.log('Application initialisée avec succès')
}