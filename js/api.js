class API {
    static async request(endpoint, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${Auth.token}`
            }
        };

        const response = await fetch(
            `${CONFIG.API_URL}${endpoint}`,
            { ...defaultOptions, ...options }
        );

        if (!response.ok) {
            throw new Error(`Erreur API: ${response.statusText}`);
        }

        return response.json();
    }

    // Méthodes pour les notes
    static async getNotes() {
        return this.request('/notes');
    }

    static async addNote(noteData) {
        return this.request('/notes', {
            method: 'POST',
            body: JSON.stringify(noteData)
        });
    }

    // Méthodes pour les classes
    static async getClasses() {
        return this.request('/classes');
    }

    static async addClass(classData) {
        return this.request('/classes', {
            method: 'POST',
            body: JSON.stringify(classData)
        });
    }

    // Méthodes pour les matières
    static async getMatieres() {
        return this.request('/matieres');
    }

    static async addMatiere(matiereData) {
        return this.request('/matieres', {
            method: 'POST',
            body: JSON.stringify(matiereData)
        });
    }

    // Méthodes pour les utilisateurs
    static async getUsers() {
        return this.request('/users');
    }

    static async addUser(userData) {
        return this.request('/users', {
            method: 'POST',
            body: JSON.stringify(userData)
        });
    }
}