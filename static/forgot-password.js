// Example: Animate button on submit (can be expanded as needed)
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('forgot-password-form');
    if (form) {
        form.addEventListener('submit', function() {
            form.querySelector('button[type="submit"]').disabled = true;
            form.querySelector('button[type="submit"]').textContent = "Sending...";
        });
    }
});
