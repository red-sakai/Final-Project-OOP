document.addEventListener('DOMContentLoaded', function() {
    // Animate reply button on click
    const replyForm = document.querySelector('.reply-form');
    if (replyForm) {
        replyForm.addEventListener('submit', function(e) {
            const btn = replyForm.querySelector('button[type="submit"]');
            if (btn) {
                btn.disabled = true;
                btn.textContent = "Sending...";
                btn.classList.add('sending');
            }
        });
    }
    // Animate textarea focus
    const textarea = document.querySelector('.reply-form textarea');
    if (textarea) {
        textarea.addEventListener('focus', function() {
            textarea.style.boxShadow = '0 0 0 2px #1579c055';
        });
        textarea.addEventListener('blur', function() {
            textarea.style.boxShadow = '';
        });
    }
});
