document.addEventListener("DOMContentLoaded", function () {
    // Initialize the map
    initializeMap();
    
    // Set up modal functionality
    setupModalInteractions();
    
    // Set up refresh button
    document.getElementById('refresh-map')?.addEventListener('click', function() {
        updateMapData();
        // Update the "last updated" time
        document.querySelector('.update-time').textContent = 'Last updated: Just now';
        
        // Show a brief notification
        showNotification('Map data refreshed successfully');
    });
    
    // Simulate progress based on the current status
    updateProgressStatus();
});

function initializeMap() {
    // Make sure the map div exists
    var mapDiv = document.getElementById('map');
    if (!mapDiv) return;

    // Set map to fill container completely
    mapDiv.style.height = "100%";
    mapDiv.style.width = "100%";
    
    // Initialize the map with optimized settings
    var map = L.map('map', {
        zoomControl: false,
        scrollWheelZoom: true,
        attributionControl: false,
        dragging: true,
        tap: true
    }).setView([14.5995, 120.9842], 10); // Slightly zoomed out for better fit
    
    // Add zoom control to top-right
    L.control.zoom({
        position: 'topright'
    }).addTo(map);
    
    // Add attribution to bottom-right
    L.control.attribution({
        position: 'bottomright'
    }).addAttribution('© OpenStreetMap, CARTO').addTo(map);
    
    // Use a cleaner map style
    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>',
        subdomains: 'abcd',
        maxZoom: 19
    }).addTo(map);

    // drop-off points in NCR - keep original points
    var dropOffPoints = [
        {lat: 14.6760, lng: 121.0437, name: "Quezon City (North)"},
        {lat: 14.6507, lng: 120.9667, name: "Caloocan (North)"},
        {lat: 14.5995, lng: 120.9842, name: "Manila (Center)"},
        {lat: 14.4793, lng: 121.0198, name: "Parañaque (South)"}
    ];

    // starting point (Manila Port)
    var startPoint = [14.6016, 120.9762];
    
    // Define destination point
    var endPoint = [14.5995, 120.9842]; // Sta. Mesa Manila

    // add drop-off points as markers
    dropOffPoints.forEach(function(point) {
        L.marker([point.lat, point.lng])
            .addTo(map)
            .bindPopup(point.name);
    });

    // parcel colors and labels - keep original styling
    var parcelColors = ['red', 'blue', 'green', 'orange'];
    var parcelLabels = ['Parcel 1', 'Parcel 2', 'Parcel 3', 'Parcel 4'];

    // Draw main route line
    var mainRoute = [startPoint, endPoint];
    var routeLine = L.polyline(mainRoute, {
        color: '#03335E',
        weight: 4,
        opacity: 0.7,
        lineCap: 'round',
        dashArray: '1, 8',
        dashOffset: '1'
    }).addTo(map);

    // Animate dash
    animatePolyline(routeLine);

    // animate each parcel - keep original animation logic
    dropOffPoints.forEach(function(point, idx) {
        // route: start -> drop-off
        var route = [startPoint, [point.lat, point.lng]];
        L.polyline(route, {color: parcelColors[idx], dashArray: '5, 10'}).addTo(map);

        // marker
        var marker = L.circleMarker(startPoint, {
            radius: 10,
            color: parcelColors[idx],
            fillColor: parcelColors[idx],
            fillOpacity: 0.8
        }).addTo(map).bindPopup(parcelLabels[idx]);

        marker.openPopup();

        // animation
        var duration = 5000 + idx * 1000; // ms, staggered
        var startTime = null;

        function animateParcel(ts) {
            if (!startTime) startTime = ts;
            var elapsed = ts - startTime;
            var t = Math.min(elapsed / duration, 1);
            var pos = interpolate(startPoint, [point.lat, point.lng], t);
            marker.setLatLng(pos);

            if (t < 1) {
                requestAnimationFrame(animateParcel);
            } else {
                marker.setLatLng([point.lat, point.lng]);
            }
        }
        setTimeout(function() {
            requestAnimationFrame(animateParcel);
        }, idx * 800); // stagger start
    });

    // Create a bounds object that includes all points
    var bounds = L.latLngBounds([startPoint]);
    dropOffPoints.forEach(function(point) {
        bounds.extend([point.lat, point.lng]);
    });
    
    // Fit map to these bounds with tighter padding to avoid unnecessary space
    map.fitBounds(bounds, {
        padding: [30, 30],
        maxZoom: 12 // Lower max zoom to ensure everything fits
    });
    
    // Store the map and points in window object for later access
    window.mapObjects = {
        map: map,
        dropOffPoints: dropOffPoints,
        startPoint: startPoint
    };
}

// interpolate between two points - keep original function
function interpolate(start, end, t) {
    return [
        start[0] + (end[0] - start[0]) * t,
        start[1] + (end[1] - start[1]) * t
    ];
}

function animatePolyline(line) {
    var dashArray = '1, 8';
    var dashOffset = 0;
    
    function animate() {
        dashOffset -= 0.5;
        line.setStyle({ dashOffset: dashOffset.toString() });
        requestAnimationFrame(animate);
    }
    
    animate();
}

function calculateCurrentPosition(route, progress) {
    // Simple linear interpolation between route points
    var totalSegments = route.length - 1;
    var targetSegment = Math.floor(progress * totalSegments);
    
    var startPoint = route[targetSegment];
    var endPoint = route[targetSegment + 1];
    
    // Calculate how far along this segment
    var segmentProgress = (progress * totalSegments) % 1;
    
    return [
        startPoint[0] + segmentProgress * (endPoint[0] - startPoint[0]),
        startPoint[1] + segmentProgress * (endPoint[1] - startPoint[1])
    ];
}

function setupModalInteractions() {
    var modal = document.getElementById('employee-modal');
    if (!modal) return;
    
    // Get all buttons that should open the modal
    var btns = [
        document.querySelector('.call-btn'),
        document.getElementById('view-courier-details')
    ];
    
    btns.forEach(btn => {
        if (btn) {
            btn.addEventListener('click', function() {
                modal.style.display = 'block';
            });
        }
    });
    
    // Close button
    var closeBtn = document.getElementById('close-modal');
    if (closeBtn) {
        closeBtn.addEventListener('click', function() {
            modal.style.display = 'none';
        });
    }
    
    // Contact button in modal
    var contactBtn = document.getElementById('contact-courier');
    if (contactBtn) {
        contactBtn.addEventListener('click', function() {
            // Simulate call functionality
            showNotification('Initiating call with courier...');
            modal.style.display = 'none';
        });
    }
    
    // Close when clicking outside
    window.addEventListener('click', function(event) {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
}

function updateMapData() {
    if (!window.mapObjects) return;
    
    const { map, parcelMarker, routePoints } = window.mapObjects;
    
    // Update the parcel position (simulate movement)
    var progress = Math.min(0.7, 0.6 + Math.random() * 0.1); // Move a bit further along the route
    var newPosition = calculateCurrentPosition(routePoints, progress);
    
    parcelMarker.setLatLng(newPosition);
    
    // Animate the marker update
    parcelMarker._icon.classList.add('marker-updated');
    setTimeout(() => {
        if (parcelMarker._icon) {
            parcelMarker._icon.classList.remove('marker-updated');
        }
    }, 1000);
    
    // Center the map on the new position
    map.panTo(newPosition);
}

function updateProgressStatus() {
    // Set the progress bar to match the current status (e.g., 60%)
    const progressBar = document.querySelector('.progress-bar-fill');
    if (progressBar) {
        progressBar.style.width = '60%';
    }
}

function showNotification(message) {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        background: #333;
        color: white;
        padding: 12px 24px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        z-index: 1000;
        opacity: 0;
        transition: opacity 0.3s;
    `;
    
    document.body.appendChild(notification);
    
    // Fade in
    setTimeout(() => {
        notification.style.opacity = '1';
    }, 10);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// Make sure the map resizes properly when window changes
window.addEventListener('resize', function() {
    if (window.mapObjects && window.mapObjects.map) {
        window.mapObjects.map.invalidateSize();
        
        // If we have route points, make sure they're still visible after resize
        if (window.mapObjects.dropOffPoints) {
            var bounds = L.latLngBounds([window.mapObjects.startPoint]);
            window.mapObjects.dropOffPoints.forEach(function(point) {
                bounds.extend([point.lat, point.lng]);
            });
            window.mapObjects.map.fitBounds(bounds, {
                padding: [30, 30],
                maxZoom: 12
            });
        }
    }
});

// After document is fully loaded, force a resize event to properly size the map
document.addEventListener("DOMContentLoaded", function() {
    setTimeout(function() {
        window.dispatchEvent(new Event('resize'));
    }, 100);
});