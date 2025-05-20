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

// Animated Load Bar Sequence (one per card)
window.addEventListener('DOMContentLoaded', () => {
    function lerpColor(a, b, t) {
        return [
            Math.round(a[0] + (b[0] - a[0]) * t),
            Math.round(a[1] + (b[1] - a[1]) * t),
            Math.round(a[2] + (b[2] - a[2]) * t)
        ];
    }
    function rgbStr(arr) {
        return `rgb(${arr[0]},${arr[1]},${arr[2]})`;
    }

    const bars = [
        {
            el: document.getElementById('loadbar-light'),
            duration: 1000,
            target: 33,
            colorStops: [
                { pct: 0, color: [178,178,178] }, // gray
                { pct: 1, color: [60, 200, 120] } // green
            ]
        },
        {
            el: document.getElementById('loadbar-medium'),
            duration: 2000,
            target: 66,
            colorStops: [
                { pct: 0, color: [178,178,178] }, // gray
                { pct: 0.5, color: [60, 200, 120] }, // green
                { pct: 1, color: [255, 210, 60] } // yellow
            ]
        },
        {
            el: document.getElementById('loadbar-heavy'),
            duration: 3000,
            target: 100,
            colorStops: [
                { pct: 0, color: [178,178,178] }, // gray
                { pct: 0.66, color: [255, 210, 60] }, // yellow
                { pct: 1, color: [220, 50, 50] } // red
            ]
        }
    ];

    function animateBar(bar, cb) {
        const { el, duration, target, colorStops } = bar;
        let start = null;
        function getColor(pct) {
            for (let i = 1; i < colorStops.length; ++i) {
                if (pct <= colorStops[i].pct) {
                    const prev = colorStops[i-1];
                    const next = colorStops[i];
                    const t = (pct - prev.pct) / (next.pct - prev.pct);
                    return rgbStr(lerpColor(prev.color, next.color, t));
                }
            }
            return rgbStr(colorStops[colorStops.length-1].color);
        }
        function step(ts) {
            if (!start) start = ts;
            let elapsed = ts - start;
            let pct = Math.min(elapsed / duration, 1);
            let width = pct * target;
            el.style.width = width + '%';
            el.style.background = getColor(pct);
            if (pct < 1) {
                requestAnimationFrame(step);
            } else {
                el.style.width = target + '%';
                el.style.background = getColor(1);
                if (cb) setTimeout(cb, 150);
            }
        }
        el.style.width = '0%';
        el.style.background = getColor(0);
        requestAnimationFrame(step);
    }

    // Animate each bar independently, but staggered for effect
    animateBar(bars[0], () => {
        animateBar(bars[1], () => {
            animateBar(bars[2]);
        });
    });
});