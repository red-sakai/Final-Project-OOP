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
    
    // Load quick stats data with animation
    function loadQuickStats() {
        // Simulated data - in real app would fetch from server
        const stats = {
            'vehicle-count': { value: 24, prefix: '', suffix: '' },
            'employee-count': { value: 48, prefix: '', suffix: '' },
            'delivery-count': { value: 186, prefix: '', suffix: '' },
            'efficiency-rate': { value: 94, prefix: '', suffix: '%' }
        };
        
        // Animate the number counting up
        Object.entries(stats).forEach(([id, data]) => {
            const element = document.getElementById(id);
            if (!element) return;
            
            const { value, prefix, suffix } = data;
            const duration = 1500; // Animation duration in ms
            const frameRate = 60; // Animation frame rate
            const increment = value / (duration / 1000 * frameRate);
            
            let current = 0;
            const timer = setInterval(() => {
                current += increment;
                if (current >= value) {
                    clearInterval(timer);
                    current = value;
                }
                element.textContent = `${prefix}${Math.floor(current)}${suffix}`;
            }, 1000 / frameRate);
        });
    }
    
    // Initial load of graphs and stats
    refreshGraphs();
    loadQuickStats();
    
    // Setup refresh button
    const refreshBtn = document.getElementById('refresh-graphs');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', function() {
            const btn = this;
            btn.disabled = true;
            btn.classList.add('rotating');
            
            refreshGraphs();
            loadQuickStats();
            
            // Re-enable button after animation
            setTimeout(() => {
                btn.disabled = false;
                btn.classList.remove('rotating');
            }, 1000);
        });
    }
    
    // Add ripple effect to cards
    const cards = document.querySelectorAll('.dashboard-card, .stat-card');
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
    
    // Staggered animation for dashboard cards
    const staggeredElements = document.querySelectorAll('.dashboard-options .dashboard-card');
    staggeredElements.forEach((element, index) => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            element.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }, 300 + (index * 100));
    });
    
    // Hover effect for graph cards
    const graphCards = document.querySelectorAll('.graph-card');
    graphCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.querySelector('.graph-img').style.transform = 'scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.querySelector('.graph-img').style.transform = 'scale(1)';
        });
    });
    
    // Reload graphs every 2 minutes for live updates
    setInterval(refreshGraphs, 120000);
});