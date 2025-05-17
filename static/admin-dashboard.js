let eqCount = 0;
document.addEventListener('keydown', function(e) {
    // ignore if user is typing in an input or text area
    if (document.activeElement.tagName === 'INPUT' || document.activeElement.tagName === 'TEXTAREA') return;
    if (e.key === '=') {
        eqCount++;
        if (eqCount === 5) {
            window.location.href = adminDashboardUrl;
        }
    } else {     // reset the counter if any other key is pressed
        eqCount = 0;
    }
});