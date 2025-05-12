class UI {
    static showNotification(message, type = 'success') {
        const notification = document.getElementById('notification');
        notification.textContent = message;
        notification.className = `notification ${type}`;
        notification.classList.remove('hidden');

        setTimeout(() => {
            notification.classList.add('hidden');
        }, 3000);
    }

    static showSection(sectionId) {
        document.querySelectorAll('.section').forEach(section => {
            section.classList.add('hidden');
        });
        document.getElementById(sectionId).classList.remove('hidden');
    }

    static updateUserInterface() {
        const mainSection = document.getElementById('main-section');
        const authSection = document.getElementById('auth-section');
        const userRole = Auth.getRole();

        if (Auth.isAuthenticated()) {
            authSection.classList.add('hidden');
            mainSection.classList.remove('hidden');

            // Afficher le dashboard correspondant au rôle
            document.querySelectorAll('.dashboard').forEach(dash => {
                dash.classList.add('hidden');
            });

            const dashboardId = `${userRole.toLowerCase()}-dashboard`;
            const dashboard = document.getElementById(dashboardId);
            if (dashboard) {
                dashboard.classList.remove('hidden');
            }

            // Mettre à jour les informations utilisateur
            document.getElementById('userName').textContent = Auth.user.nom;
        } else {
            mainSection.classList.add('hidden');
            authSection.classList.remove('hidden');
        }
    }
}