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
    // Initialize graph loading state
    const graphElements = {
        vehicles: {
            img: document.getElementById('vehicles-graph'),
            loading: document.getElementById('vehicles-loading')
        },
        employees: {
            img: document.getElementById('employees-graph'),
            loading: document.getElementById('employees-loading')
        }
    };
    
    // Function to refresh graphs with loading indicators
    function refreshGraphs() {
        Object.values(graphElements).forEach(element => {
            if (element.loading && element.img) {
                // Show loading indicator
                element.loading.classList.add('visible');
                
                // Create new image object to preload
                const newImg = new Image();
                const timestamp = new Date().getTime();
                const imgSrc = element.img.src.split('?')[0] + '?' + timestamp;
                
                newImg.onload = function() {
                    // When image loads, update source and hide loading indicator
                    element.img.src = imgSrc;
                    setTimeout(() => {
                        element.loading.classList.remove('visible');
                    }, 300);
                };
                
                newImg.onerror = function() {
                    // Handle error
                    element.loading.classList.remove('visible');
                    console.error('Failed to load graph image');
                };
                
                // Start loading the new image
                newImg.src = imgSrc;
            }
        });
    }
    
    // Initial load of graphs
    refreshGraphs();
    
    // Setup refresh button
    const refreshBtn = document.getElementById('refresh-graphs');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', function() {
            const btn = this;
            btn.disabled = true;
            btn.classList.add('rotating');
            
            refreshGraphs();
            
            // Re-enable button after animation
            setTimeout(() => {
                btn.disabled = false;
                btn.classList.remove('rotating');
            }, 1000);
        });
    }
    
    // Add tooltip hover behavior for cards
    const cards = document.querySelectorAll('.dashboard-card');
    cards.forEach(card => {
        // Create ripple effect on click
        card.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            ripple.classList.add('ripple');
            
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            
            ripple.style.width = ripple.style.height = `${size}px`;
            ripple.style.left = `${e.clientX - rect.left - size/2}px`;
            ripple.style.top = `${e.clientY - rect.top - size/2}px`;
            
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
    
    // Optionally, reload graphs every 2 minutes for live updates
    setInterval(refreshGraphs, 120000);
    
    // Add CSS class for ripple effects
    const style = document.createElement('style');
    style.textContent = `
        .dashboard-card {
            position: relative;
            overflow: hidden;
        }
        .ripple {
            position: absolute;
            background: rgba(255, 255, 255, 0.7);
            border-radius: 50%;
            transform: scale(0);
            animation: ripple 0.6s linear;
            pointer-events: none;
        }
        @keyframes ripple {
            to {
                transform: scale(4);
                opacity: 0;
            }
        }
        .rotating {
            animation: rotate 1s linear infinite;
        }
        @keyframes rotate {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
    `;
    document.head.appendChild(style);
});