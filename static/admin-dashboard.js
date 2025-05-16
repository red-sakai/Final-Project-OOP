let eqCount = 0;
document.addEventListener('keydown', function(e) {
    // Ignore if user is typing in an input or textarea
    if (document.activeElement.tagName === 'INPUT' || document.activeElement.tagName === 'TEXTAREA') return;
    if (e.key === '=') {
        eqCount++;
        if (eqCount === 5) {
            window.location.href = adminDashboardUrl;
        }
    } else {
        eqCount = 0;
    }
});