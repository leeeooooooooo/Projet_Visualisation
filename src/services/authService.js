export default {
  // Fonction d'initialisation
  initialize() {
    // Par exemple, initialiser des variables ou des configurations ici
    console.log("AuthService initialisé");
  },
  
  // Récupérer le type d'utilisateur depuis les cookies
  getUserType() {
    const userType = document.cookie.split('; ').find(row => row.startsWith('userType='));
    return userType ? userType.split('=')[1] : null;
  },
  
  // Fonction pour simuler un logout
  logout() {
    document.cookie = 'userType=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
  }
};
