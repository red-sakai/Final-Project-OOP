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

document.addEventListener('DOMContentLoaded', function() {
    // Animate cards on hover (optional, for extra smoothness)
    document.querySelectorAll('.dashboard-card').forEach(card => {
        card.addEventListener('mouseenter', () => card.classList.add('hovered'));
        card.addEventListener('mouseleave', () => card.classList.remove('hovered'));
    });

    // Optionally, reload graphs every X seconds for live updates
    setInterval(() => {
        document.getElementById('employees-graph').src = '/analytics/employee_statuses.png?' + new Date().getTime();
        document.getElementById('vehicles-graph').src = '/analytics/vehicles_deployed.png?' + new Date().getTime();
    }, 60000); // every 60 seconds
});