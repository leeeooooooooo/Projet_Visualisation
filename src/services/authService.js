const userTypeKey = 'userType'
const userIdKey = 'userId'

export default {
  getUserType() {
    return localStorage.getItem(userTypeKey)
  },
  setUserType(role) {
    if (role) localStorage.setItem(userTypeKey, role)
    else localStorage.removeItem(userTypeKey)
  },
  getUserId() {
    return localStorage.getItem(userIdKey)
  },
  setUserId(id) {
    if (id) localStorage.setItem(userIdKey, id)
    else localStorage.removeItem(userIdKey)
  },
  logout() {
    document.cookie = 'session_gerant=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;'
    document.cookie = 'session_campeur=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;'
    this.setUserType(null)
    this.setUserId(null)
  },

  // Ajout de la fonction debugCookies
  debugCookies() {
    console.log('Cookies actuels :', document.cookie)
  }
}
