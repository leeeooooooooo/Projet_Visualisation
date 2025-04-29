// src/services/authService.js
import axios from 'axios'
import router from '@/router'

// Clés pour le stockage local (version sécurisée)
const STORAGE_KEYS = {
  TOKEN: 'campingAuth_v1',
  USER_TYPE: 'campingUserType_v1',
  USER_DATA: 'campingUserData_v1'
}

export default {
  /**
   * Enregistre les informations d'authentification
   * @param {string} token - JWT token
   * @param {string} userType - 'campeur' ou 'gerant'
   * @param {object} userData - Données utilisateur
   */
  login(token, userType, userData) {
    if (!token || !userType) {
      throw new Error('Token et type utilisateur sont requis')
    }
  
    try {
      this.saveToken(token)
      this.saveUserType(userType)
      this.saveUserData(userData)
      
      // Configure axios pour les requêtes futures
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
      
      // Redirection sécurisée avec vérification du router
      let redirectPath = this.isGerant() ? '/admin' : '/Consommation'
      
      if (router && router.currentRoute && router.currentRoute.query.redirect) {
        // Validation du chemin de redirection pour éviter les attaques
        const safePaths = ['/admin', '/Consommation', '/profile'] // Ajoutez les chemins autorisés
        const requestedPath = router.currentRoute.query.redirect
        
        if (safePaths.includes(requestedPath)) {
          redirectPath = requestedPath
        }
      }
      
      router.push(redirectPath)
  
    } catch (error) {
      console.error('Erreur lors de la connexion:', error)
      this.logout()
      throw new Error('Échec de la connexion. Veuillez réessayer.')
    }
  },

  /**
   * Déconnexion de l'utilisateur (version sécurisée)
   */
  logout() {
    try {
      // Nettoyage complet
      Object.values(STORAGE_KEYS).forEach(key => {
        localStorage.removeItem(key)
      })
      
      delete axios.defaults.headers.common['Authorization']
      
      // Redirection avec nettoyage de l'historique
      router.replace('/connexion')
    } catch (error) {
      console.error('Erreur lors de la déconnexion:', error)
    }
  },

  /**
   * Sauvegarde sécurisée du token
   */
  saveToken(token) {
    localStorage.setItem(STORAGE_KEYS.TOKEN, token)
  },

  getToken() {
    return localStorage.getItem(STORAGE_KEYS.TOKEN)
  },

  saveUserType(userType) {
    if (!['campeur', 'gerant'].includes(userType)) {
      throw new Error('Type utilisateur invalide')
    }
    localStorage.setItem(STORAGE_KEYS.USER_TYPE, userType)
  },

  getUserType() {
    return localStorage.getItem(STORAGE_KEYS.USER_TYPE)
  },

  saveUserData(userData) {
    if (userData) {
      localStorage.setItem(STORAGE_KEYS.USER_DATA, JSON.stringify(userData))
    }
  },

  getUserData() {
    try {
      const data = localStorage.getItem(STORAGE_KEYS.USER_DATA)
      return data ? JSON.parse(data) : null
    } catch (e) {
      console.error('Erreur parsing userData:', e)
      return null
    }
  },

  isAuthenticated() {
    return !!this.getToken()
  },

  isGerant() {
    return this.getUserType() === 'gerant'
  },

  isCampeur() {
    return this.getUserType() === 'campeur'
  },

  /**
   * Initialisation améliorée avec vérification
   */
  initialize() {
    try {
      const token = this.getToken()
      if (token) {
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
        
        // Vérification cohérence des données
        if (!this.getUserType()) {
          console.warn('Type utilisateur manquant')
          this.logout()
          return false
        }
        
        return true
      }
    } catch (error) {
      console.error('Erreur initialisation auth:', error)
    }
    return false
  },

  /**
   * Récupération sécurisée des infos
   */
  getAuthInfo() {
    return {
      token: this.getToken(),
      userType: this.getUserType(),
      userData: this.getUserData(),
      isAuthenticated: this.isAuthenticated(),
      isGerant: this.isGerant(),
      isCampeur: this.isCampeur(),
      timestamp: new Date().toISOString()
    }
  },

  /**
   * Nouvelle méthode : Vérifie la validité de la session
   */
  checkSessionValidity() {
    return this.isAuthenticated() && this.getUserType()
  }
}
