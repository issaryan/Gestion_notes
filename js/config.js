// Configuration de l'application
const CONFIG = {
    // URL de base de l'API
    API_URL: 'http://localhost:5000/api',
    
    // Délai d'expiration du token en millisecondes (1 heure)
    TOKEN_EXPIRATION: 3600000,
    
    // Rôles utilisateur
    ROLES: {
        ADMIN: 'ADMIN',
        ENSEIGNANT: 'ENSEIGNANT',
        ETUDIANT: 'ETUDIANT'
    },
    
    // Messages d'erreur
    MESSAGES: {
        LOGIN_ERROR: 'Identifiants incorrects',
        SERVER_ERROR: 'Erreur serveur',
        NETWORK_ERROR: 'Erreur de connexion',
        SESSION_EXPIRED: 'Session expirée',
        UNAUTHORIZED: 'Accès non autorisé'
    }
};