import { createRouter, createWebHistory } from 'vue-router'
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
    component: consommation
  },
  {
    path: '/panneau',
    name: 'panneau',
    component: panneau
  },
  {
    path: '/rapport',
    name: 'rapport',
    component: rapport
  },
  {
    path: '/notification',
    name: 'notification',
    component: notification
  },
  {
    path: '/configuration',
    name: 'configuration',
    component: configuration
  },
  // Ajout d'une route pour la déconnexion
  {
    path: '/deconnexion',
    name: 'deconnexion',
    beforeEnter: (to, from, next) => {
      // Redirection sans gestion de token
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

export default router
