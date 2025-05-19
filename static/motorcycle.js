document.querySelectorAll('.motorcycle-card').forEach(card => {
    card.addEventListener('mouseenter', () => {
        card.classList.add('hovered');
    });
    card.addEventListener('mouseleave', () => {
        card.classList.remove('hovered');
    });
});

document.querySelectorAll('.motorcycle-book-btn').forEach(btn => {
    btn.addEventListener('mousedown', () => {
        btn.style.transform = 'scale(0.96)';
    });
    btn.addEventListener('mouseup', () => {
        btn.style.transform = '';
    });
    btn.addEventListener('mouseleave', () => {
        btn.style.transform = '';
    });

    btn.addEventListener('click', function(e) {
        e.preventDefault();
        const popup = document.getElementById('motorcycle-loading-popup');
        popup.style.display = 'flex';
        setTimeout(() => {
            window.location.href = btn.getAttribute('href');
        }, 1800); // 1.8 seconds
    });
});