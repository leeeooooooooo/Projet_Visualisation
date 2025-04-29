import { createRouter, createWebHistory } from 'vue-router'
import authService from '@/services/authService'
import connexion from '@/views/connexion.vue'
import consommation from '@/views/consommation.vue'
import rapport from '@/views/rapport.vue'
import notification from '@/views/notification.vue'
import configuration from '@/views/configuration.vue'
import panneau from '@/views/panneau.vue'

const routes = [
  {
    path: '/',
    name: 'connexion',
    component: connexion
  },
  {
    path: '/consommation',
    name: 'consommation',
    component: consommation,
    meta: { requiresAuth: true }
  },
  {
    path: '/panneau',
    name: 'panneau',
    component: panneau,
    meta: { requiresAuth: true }
  },
  {
    path: '/rapport',
    name: 'rapport',
    component: rapport,
    meta: { requiresAuth: true }
  },
  {
    path: '/notification',
    name: 'notification',
    component: notification,
    meta: { requiresAuth: true }
  },
  {
    path: '/configuration',
    name: 'configuration',
    component: configuration,
    meta: { requiresAuth: true }
  },
  // Ajout d'une route pour la déconnexion
  {
    path: '/deconnexion',
    name: 'deconnexion',
    beforeEnter: (to, from, next) => {
      authService.logout()
      next('/')
    }
  },
  // Route pour gérer les chemins non définis
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

// Garde de navigation pour protéger les routes
router.beforeEach((to, from, next) => {
  // Initialiser l'authentification
  authService.initialize()
  
  // Vérifier si la route nécessite une authentification
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  
  if (requiresAuth) {
    // Vérifier si l'utilisateur est connecté
    if (authService.isAuthenticated()) {
      next() // Autoriser l'accès
    } else {
      // Rediriger vers la page de connexion avec le chemin de retour
      next({
        path: '/',
        replace: true, // Remplacer l'URL actuelle pour ne pas garder le paramètre `redirect`
        query: { redirect: to.fullPath }
      })
    }
  } else {
    // Route publique, continuer normalement
    next()
  }
})

export default router