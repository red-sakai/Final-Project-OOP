window.addEventListener('DOMContentLoaded', () => {
    // Support both car and truck bar IDs
    const bars = [
        // Car bars
        {
            id: 'loadbar-light',
            target: 33,
            duration: 1000,
            colorStops: [
                { pct: 0, color: [178,178,178] },
                { pct: 33, color: [60, 200, 90] }
            ]
        },
        {
            id: 'loadbar-medium',
            target: 66,
            duration: 2000,
            colorStops: [
                { pct: 0, color: [178,178,178] },
                { pct: 33, color: [60, 200, 90] },
                { pct: 66, color: [255, 210, 60] }
            ]
        },
        {
            id: 'loadbar-heavy',
            target: 100,
            duration: 3000,
            colorStops: [
                { pct: 0, color: [178,178,178] },
                { pct: 66, color: [255, 210, 60] },
                { pct: 100, color: [220, 60, 60] }
            ]
        },
        // Truck bars
        {
            id: 'truckbar-light',
            target: 33,
            duration: 1000,
            colorStops: [
                { pct: 0, color: [178,178,178] },
                { pct: 33, color: [60, 200, 90] }
            ]
        },
        {
            id: 'truckbar-medium',
            target: 66,
            duration: 2000,
            colorStops: [
                { pct: 0, color: [178,178,178] },
                { pct: 33, color: [60, 200, 90] },
                { pct: 66, color: [255, 210, 60] }
            ]
        },
        {
            id: 'truckbar-heavy',
            target: 100,
            duration: 3000,
            colorStops: [
                { pct: 0, color: [178,178,178] },
                { pct: 66, color: [255, 210, 60] },
                { pct: 100, color: [220, 60, 60] }
            ]
        }
    ];

    function lerpColor(a, b, t) {
        return [
            Math.round(a[0] + (b[0] - a[0]) * t),
            Math.round(a[1] + (b[1] - a[1]) * t),
            Math.round(a[2] + (b[2] - a[2]) * t)
        ];
    }
    function getColor(stops, pct) {
        for (let i = 1; i < stops.length; i++) {
            if (pct <= stops[i].pct) {
                const prev = stops[i-1];
                const next = stops[i];
                const range = next.pct - prev.pct;
                const t = range === 0 ? 0 : (pct - prev.pct) / range;
                const color = lerpColor(prev.color, next.color, t);
                return `rgb(${color[0]},${color[1]},${color[2]})`;
            }
        }
        const last = stops[stops.length-1];
        return `rgb(${last.color[0]},${last.color[1]},${last.color[2]})`;
    }

    // Animate a single bar, then call next
    function animateBar(bar, cb) {
        const el = document.getElementById(bar.id);
        if (!el) { cb && cb(); return; }
        let start = null;
        function step(ts) {
            if (!start) start = ts;
            const elapsed = ts - start;
            let pct = Math.min(bar.target, (elapsed / bar.duration) * bar.target);
            el.style.width = pct + '%';
            el.style.background = getColor(bar.colorStops, pct);
            if (pct < bar.target) {
                requestAnimationFrame(step);
            } else {
                el.style.width = bar.target + '%';
                el.style.background = getColor(bar.colorStops, bar.target);
                cb && cb();
            }
        }
        requestAnimationFrame(step);
    }

    // Animate car bars in sequence, then truck bars in sequence
    function runBarSequence(barIds) {
        let idx = 0;
        function next() {
            if (idx >= barIds.length) return;
            animateBar(barIds[idx], next);
            idx++;
        }
        if (barIds.length > 0) next();
    }

    // Filter bars for car and truck
    const carBars = bars.filter(b => document.getElementById(b.id) && b.id.startsWith('loadbar'));
    const truckBars = bars.filter(b => document.getElementById(b.id) && b.id.startsWith('truckbar'));

    runBarSequence(carBars);
    runBarSequence(truckBars);
});
