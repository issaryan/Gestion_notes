class Auth {
    static token = null;
    static user = null;

    static async login(email, password) {
        try {
            const response = await fetch(`${CONFIG.API_URL}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email, password })
            });

            if (!response.ok) {
                throw new Error('Identifiants invalides');
            }

            const data = await response.json();
            this.token = data.access_token;
            localStorage.setItem('token', this.token);

            await this.getCurrentUser();
            return true;
        } catch (error) {
            console.error('Erreur de connexion:', error);
            throw error;
        }
    }

    static async getCurrentUser() {
        try {
            const response = await fetch(`${CONFIG.API_URL}/auth/me`, {
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });

            if (!response.ok) {
                throw new Error('Erreur lors de la récupération du profil');
            }

            this.user = await response.json();
            return this.user;
        } catch (error) {
            console.error('Erreur profil:', error);
            throw error;
        }
    }

    static logout() {
        this.token = null;
        this.user = null;
        localStorage.removeItem('token');
    }

    static isAuthenticated() {
        return !!this.token;
    }

    static getRole() {
        return this.user?.role;
    }
}