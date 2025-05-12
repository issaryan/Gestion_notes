// Module de gestion de l'authentification
const Auth = {
    token: null,
    user: null,

    // Initialisation
    init() {
        this.token = localStorage.getItem('token');
        const userData = localStorage.getItem('user');
        if (userData) {
            this.user = JSON.parse(userData);
        }
    },

    // Récupération du token
    getToken() {
        return this.token;
    },

    // Connexion
    async login(email, password) {
        try {
            const response = await API.login({ email, password });
            this.token = response.access_token;
            localStorage.setItem('token', this.token);

            // Récupération des informations utilisateur
            await this.fetchUserInfo();
            return true;
        } catch (error) {
            console.error('Erreur de connexion:', error);
            throw new Error(CONFIG.MESSAGES.LOGIN_ERROR);
        }
    },

    // Récupération des informations utilisateur
    async fetchUserInfo() {
        try {
            this.user = await API.getCurrentUser();
            localStorage.setItem('user', JSON.stringify(this.user));
            return this.user;
        } catch (error) {
            this.logout();
            throw error;
        }
    },

    // Déconnexion
    logout() {
        this.token = null;
        this.user = null;
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.reload();
    },

    // Vérification de l'authentification
    isAuthenticated() {
        return !!this.token;
    },

    // Vérification du rôle
    hasRole(role) {
        return this.user && this.user.role === role;
    },

    // Vérification de l'expiration du token
    checkTokenExpiration() {
        const tokenData = this.parseJwt(this.token);
        if (tokenData && tokenData.exp) {
            const expirationTime = tokenData.exp * 1000;
            if (Date.now() >= expirationTime) {
                this.logout();
                UI.showNotification(CONFIG.MESSAGES.SESSION_EXPIRED, 'error');
                return false;
            }
        }
        return true;
    },

    // Décodage du token JWT
    parseJwt(token) {
        try {
            const base64Url = token.split('.')[1];
            const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
            return JSON.parse(window.atob(base64));
        } catch (error) {
            console.error('Erreur de décodage du token:', error);
            return null;
        }
    }
};