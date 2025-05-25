let eqCount = 0;
document.addEventListener('keydown', function(e) {
    // ignore if user is typing in an input or text area
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

document.addEventListener('DOMContentLoaded', function() {
    // Animate stats on page load
    function animateCounter(element, finalValue, duration = 1500) {
        if (!element) return;
        
        const startValue = 0;
        const increment = finalValue / (duration / 16);
        let currentValue = startValue;
        
        const timer = setInterval(() => {
            currentValue += increment;
            if (currentValue >= finalValue) {
                clearInterval(timer);
                currentValue = finalValue;
            }
            
            // Format the value based on the element's data type
            let displayValue = Math.floor(currentValue);
            if (element.id === 'efficiency-rate' || element.id === 'uptime') {
                displayValue = Math.floor(currentValue) + '%';
            } else if (element.id === 'revenue') {
                displayValue = '$' + (currentValue / 1000).toFixed(1) + 'K';
            }
            
            element.textContent = displayValue;
        }, 16);
    }
    
    // Initialize counters with realistic values
    const counters = {
        'vehicle-count': 24,
        'employee-count': 48,
        'delivery-count': 186,
        'efficiency-rate': 94,
        'uptime': 99.8,
        'revenue': 12400
    };
    
    // Start counter animations with staggered delays
    Object.entries(counters).forEach(([id, value], index) => {
        setTimeout(() => {
            const element = document.getElementById(id);
            animateCounter(element, value);
        }, index * 200);
    });
    
    // Menu card hover effects
    const menuCards = document.querySelectorAll('.menu-card');
    menuCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            // Add subtle pulse effect to icon
            const icon = this.querySelector('.card-icon');
            if (icon) {
                icon.style.transform = 'scale(1.1) rotate(5deg)';
            }
            
            // Animate arrow
            const arrow = this.querySelector('.card-arrow');
            if (arrow) {
                arrow.style.transform = 'translateX(5px)';
            }
        });
        
        card.addEventListener('mouseleave', function() {
            const icon = this.querySelector('.card-icon');
            if (icon) {
                icon.style.transform = 'scale(1) rotate(0deg)';
            }
            
            const arrow = this.querySelector('.card-arrow');
            if (arrow) {
                arrow.style.transform = 'translateX(0px)';
            }
        });
        
        // Add click ripple effect
        card.addEventListener('click', function(e) {
            const ripple = document.createElement('div');
            ripple.style.position = 'absolute';
            ripple.style.borderRadius = '50%';
            ripple.style.background = 'rgba(21, 121, 192, 0.3)';
            ripple.style.transform = 'scale(0)';
            ripple.style.animation = 'ripple 0.6s linear';
            ripple.style.pointerEvents = 'none';
            
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = (e.clientX - rect.left - size / 2) + 'px';
            ripple.style.top = (e.clientY - rect.top - size / 2) + 'px';
            
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
    
    // Refresh analytics functionality
    const refreshBtn = document.getElementById('refresh-analytics');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', function() {
            const btn = this;
            btn.disabled = true;
            btn.classList.add('rotating');
            
            // Simulate data refresh
            setTimeout(() => {
                // Re-animate counters with slight variations
                const variations = {
                    'efficiency-rate': 94 + Math.floor(Math.random() * 6) - 3,
                    'uptime': 99.8 + (Math.random() * 0.4) - 0.2,
                    'revenue': 12400 + Math.floor(Math.random() * 2000) - 1000
                };
                
                Object.entries(variations).forEach(([id, value]) => {
                    const element = document.getElementById(id);
                    animateCounter(element, value, 800);
                });
                
                btn.disabled = false;
                btn.classList.remove('rotating');
            }, 1000);
        });
    }
    
    // Staggered animation for menu sections
    const sections = document.querySelectorAll('.menu-section');
    sections.forEach((section, index) => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(30px)';
        
        setTimeout(() => {
            section.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            section.style.opacity = '1';
            section.style.transform = 'translateY(0)';
        }, 200 + (index * 150));
    });
    
    // Quick stats hover effects
    const quickStats = document.querySelectorAll('.quick-stat');
    quickStats.forEach(stat => {
        stat.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-3px) scale(1.05)';
            this.style.boxShadow = 'var(--shadow-medium)';
        });
        
        stat.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
            this.style.boxShadow = 'var(--shadow-light)';
        });
    });
    
    // Add dynamic time-based updates
    function updateTimeBasedMetrics() {
        const now = new Date();
        const hour = now.getHours();
        
        // Simulate different metrics based on time of day
        let efficiencyMultiplier = 1;
        if (hour >= 9 && hour <= 17) {
            efficiencyMultiplier = 1.1; // Higher efficiency during business hours
        }
        
        const baseEfficiency = 90;
        const newEfficiency = Math.min(99, Math.floor(baseEfficiency * efficiencyMultiplier + Math.random() * 5));
        
        const efficiencyElement = document.getElementById('efficiency-rate');
        if (efficiencyElement) {
            animateCounter(efficiencyElement, newEfficiency, 1000);
        }
    }
    
    // Update metrics every 30 seconds
    setInterval(updateTimeBasedMetrics, 30000);
    
    // Add CSS for ripple animation if not already present
    if (!document.querySelector('#ripple-style')) {
        const style = document.createElement('style');
        style.id = 'ripple-style';
        style.textContent = `
            @keyframes ripple {
                to {
                    transform: scale(4);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
    }
});