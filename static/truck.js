document.querySelectorAll('.truck-card').forEach(card => {
    card.addEventListener('mouseenter', () => {
        card.classList.add('hovered');
    });
    card.addEventListener('mouseleave', () => {
        card.classList.remove('hovered');
    });
});

document.querySelectorAll('.book-btn').forEach(btn => {
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
        const popup = document.getElementById('loading-popup');
        popup.style.display = 'flex';
        // Optionally, you can change the message based on the truck type
        // setTimeout to simulate loading, then redirect
        setTimeout(() => {
            window.location.href = btn.getAttribute('href');
        }, 1800); // 1.8 seconds
    });
});