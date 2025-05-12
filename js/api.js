// Module de gestion des appels API
const API = {
    // Configuration par défaut des requêtes
    async request(endpoint, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${Auth.getToken()}`
            }
        };

        try {
            const response = await fetch(
                `${CONFIG.API_URL}${endpoint}`,
                { ...defaultOptions, ...options }
            );

            if (!response.ok) {
                throw new Error(`Erreur HTTP: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            utils.handleApiError(error);
            throw error;
        }
    },

    // Authentification
    async login(credentials) {
        return this.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify(credentials)
        });
    },

    async getCurrentUser() {
        return this.request('/auth/me');
    },

    // Gestion des notes
    async getNotes() {
        return this.request('/notes');
    },

    async addNote(noteData) {
        return this.request('/notes', {
            method: 'POST',
            body: JSON.stringify(noteData)
        });
    },

    async importNotes(formData) {
        return this.request('/notes/import', {
            method: 'POST',
            body: formData,
            headers: {
                'Authorization': `Bearer ${Auth.getToken()}`
            }
        });
    },

    // Gestion des classes
    async getClasses() {
        return this.request('/classes');
    },

    async addClass(classData) {
        return this.request('/classes', {
            method: 'POST',
            body: JSON.stringify(classData)
        });
    },

    // Gestion des matières
    async getMatieres() {
        return this.request('/matieres');
    },

    async addMatiere(matiereData) {
        return this.request('/matieres', {
            method: 'POST',
            body: JSON.stringify(matiereData)
        });
    },

    // Gestion des utilisateurs
    async getUsers() {
        return this.request('/users');
    },

    async addUser(userData) {
        return this.request('/users', {
            method: 'POST',
            body: JSON.stringify(userData)
        });
    },

    // Rapports
    async downloadReport(format) {
        const response = await fetch(
            `${CONFIG.API_URL}/reports/notes/${format}`,
            {
                headers: {
                    'Authorization': `Bearer ${Auth.getToken()}`
                }
            }
        );

        if (!response.ok) {
            throw new Error('Erreur lors du téléchargement');
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `notes_${format}_${new Date().toISOString()}.${format}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    }
};