// Initialisation de l'application
document.addEventListener('DOMContentLoaded', () => {
    // Vérifier si un token existe
    const savedToken = localStorage.getItem('token');
    if (savedToken) {
        Auth.token = savedToken;
        Auth.getCurrentUser()
            .then(() => UI.updateUserInterface())
            .catch(() => Auth.logout());
    }

    // Gestionnaire de connexion
    document.getElementById('loginForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;

        try {
            await Auth.login(email, password);
            UI.showNotification('Connexion réussie');
            UI.updateUserInterface();
        } catch (error) {
            UI.showNotification(error.message, 'error');
        }
    });

    // Gestionnaire de déconnexion
    document.getElementById('logoutBtn').addEventListener('click', () => {
        Auth.logout();
        UI.updateUserInterface();
        UI.showNotification('Déconnexion réussie');
    });
});