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

    // Tab switching logic
    const tabBtns = document.querySelectorAll('.tab-btn');
    const ticketRows = document.querySelectorAll('.ticket-row');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            tabBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            const status = this.getAttribute('data-status');
            ticketRows.forEach(row => {
                const detailRow = row.nextElementSibling;
                if (row.getAttribute('data-status') === status) {
                    row.style.display = '';
                    if (detailRow && detailRow.classList.contains('ticket-row-detail')) {
                        detailRow.style.display = '';
                    }
                } else {
                    row.style.display = 'none';
                    if (detailRow && detailRow.classList.contains('ticket-row-detail')) {
                        detailRow.style.display = 'none';
                    }
                }
            });
        });
    });

    // Done button logic
    document.querySelectorAll('.done-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const ticketId = this.getAttribute('data-ticket-id');
            if (!ticketId) return;
            btn.disabled = true;
            btn.textContent = 'Marking...';
            fetch(`/admin/support/ticket/done/${ticketId}`, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({})
            })
            .then(res => {
                if (res.ok) {
                    window.location.reload();
                } else {
                    btn.disabled = false;
                    btn.textContent = 'Done';
                    alert('Failed to mark as done.');
                }
            })
            .catch(() => {
                btn.disabled = false;
                btn.textContent = 'Done';
                alert('Failed to mark as done.');
            });
        });
    });
});