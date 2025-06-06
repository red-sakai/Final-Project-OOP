// Logout animation logic for admin support tickets page
document.addEventListener('DOMContentLoaded', function() {
    const logoutBtn = document.getElementById('logout-btn');
    const logoutOverlay = document.getElementById('logout-overlay');
    const logoutProgressBar = document.querySelector('.logout-progress-bar');
    const logoutMessage = document.getElementById('logout-message');
    const adminContainer = document.querySelector('.admin-container');

    if (logoutBtn && logoutOverlay) {
        const logoutMessages = [
            "Packing Up For The Day...",
            "Signing Out...",
            "Securing Your Session...",
            "Until Next Time...",
            "Logging Off Securely..."
        ];

        logoutBtn.addEventListener('click', function(e) {
            e.preventDefault();

            // Select random message
            const randomMessage = logoutMessages[Math.floor(Math.random() * logoutMessages.length)];
            logoutMessage.textContent = randomMessage;

            // Show logout overlay
            logoutOverlay.classList.add('active');
            if (adminContainer) adminContainer.classList.add('logging-out');

            // Animate progress bar
            setTimeout(() => {
                if (logoutProgressBar) logoutProgressBar.style.width = '100%';
            }, 100);

            // Redirect after animation completes
            setTimeout(() => {
                window.location.href = typeof logoutUrl !== 'undefined' ? logoutUrl : '/admin/login';
            }, 2500);
        });
    }
});