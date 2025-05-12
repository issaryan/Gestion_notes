// Utilitaires généraux
const utils = {
    // Formatage de date
    formatDate(dateString) {
        return new Date(dateString).toLocaleDateString('fr-FR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    },

    // Validation d'email
    isValidEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    },

    // Validation de mot de passe
    isValidPassword(password) {
        return password.length >= 12 &&
               /[A-Z]/.test(password) &&
               /[0-9]/.test(password) &&
               /[!@#$%^&*(),.?":{}|<>]/.test(password);
    },

    // Échappement HTML
    escapeHtml(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    },

    // Création d'éléments HTML sécurisés
    createElement(tag, attributes = {}, content = '') {
        const element = document.createElement(tag);
        Object.entries(attributes).forEach(([key, value]) => {
            element.setAttribute(key, value);
        });
        if (content) {
            element.textContent = content;
        }
        return element;
    },

    // Gestion des erreurs API
    handleApiError(error) {
        console.error('Erreur API:', error);
        if (error.response) {
            switch (error.response.status) {
                case 401:
                    Auth.logout();
                    UI.showNotification(CONFIG.MESSAGES.SESSION_EXPIRED, 'error');
                    break;
                case 403:
                    UI.showNotification(CONFIG.MESSAGES.UNAUTHORIZED, 'error');
                    break;
                default:
                    UI.showNotification(CONFIG.MESSAGES.SERVER_ERROR, 'error');
            }
        } else {
            UI.showNotification(CONFIG.MESSAGES.NETWORK_ERROR, 'error');
        }
    }
};