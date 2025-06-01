document.addEventListener("DOMContentLoaded", function () {
    // Initialize the map based on the tracking ID
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
    var mapDiv = document.getElementById('map');
    if (!mapDiv) return;

    mapDiv.style.height = "100%";
    mapDiv.style.width = "100%";

    if (typeof orderData === 'undefined' || !orderData) {
        showNotification('No order data found for this tracking ID', 'error');
        return;
    }

    var map = L.map('map', {
        zoomControl: false,
        scrollWheelZoom: true,
        attributionControl: false,
        dragging: true,
        tap: true
    }).setView([orderData.customerLatitude, orderData.customerLongitude], 12);

    L.control.zoom({ position: 'topright' }).addTo(map);
    L.control.attribution({ position: 'bottomright' })
        .addAttribution('© OpenStreetMap, CARTO').addTo(map);

    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>',
        subdomains: 'abcd',
        maxZoom: 19
    }).addTo(map);

    setupMapWithOrderData(map, orderData);
}

function setupMapWithOrderData(map, orderData) {
    const branchPoint = [orderData.branchLatitude, orderData.branchLongitude];
    const customerPoint = [orderData.customerLatitude, orderData.customerLongitude];

    // Add branch marker (drop-off point)
    const branchMarker = L.marker(branchPoint)
        .addTo(map)
        .bindPopup(`<b>${orderData.originBranch}</b><br>Branch Location`);

    // Use Leaflet Routing Machine to get the route
    const routingControl = L.Routing.control({
        waypoints: [
            L.latLng(customerPoint[0], customerPoint[1]),
            L.latLng(branchPoint[0], branchPoint[1])
        ],
        routeWhileDragging: false,
        addWaypoints: false,
        draggableWaypoints: false,
        fitSelectedRoutes: true,
        show: false,
        lineOptions: {
            styles: [{ color: '#03335E', weight: 5, opacity: 0.8 }]
        },
        createMarker: function() { return null; }, // Don't add default markers
        router: L.Routing.osrmv1({
            serviceUrl: 'https://router.project-osrm.org/route/v1'
        })
    }).addTo(map);

    routingControl.on('routesfound', function(e) {
        const route = e.routes[0];
        const routeLine = route.coordinates.map(coord => [coord.lat, coord.lng]);

        // Animate the parcel marker along the route (at least 20 seconds)
        animateParcelAlongRoute(map, routeLine, orderData, 20000);
    });

    // Store for refresh
    window.mapObjects = {
        map: map,
        orderData: orderData,
        branchMarker: branchMarker,
        routingControl: routingControl
    };
}

// Animate the parcel marker along the route polyline, with a minimum duration
function animateParcelAlongRoute(map, routeLine, orderData, minDurationMs) {
    // Remove previous marker if any
    if (window.mapObjects.parcelMarker) {
        map.removeLayer(window.mapObjects.parcelMarker);
    }

    const parcelColor = getParcelColorByOrderType(orderData.orderItemId);
    let marker = L.circleMarker(routeLine[0], {
        radius: 10,
        color: parcelColor,
        fillColor: parcelColor,
        fillOpacity: 0.8,
        weight: 2
    }).addTo(map)
    .bindPopup(`<b>Parcel ${orderData.orderItemId}</b><br>${orderData.deliveryStatus}`);

    marker.openPopup();

    // Animation variables
    let i = 0;
    const totalPoints = routeLine.length;
    // Calculate the interval so that the animation takes at least minDurationMs
    const animationSpeed = Math.max(10, Math.ceil(minDurationMs / totalPoints));

    function moveMarker() {
        if (i < totalPoints) {
            marker.setLatLng(routeLine[i]);
            i++;
            setTimeout(moveMarker, animationSpeed);
        } else {
            marker.setLatLng(routeLine[totalPoints - 1]);
            marker.bindPopup(`<b>Parcel ${orderData.orderItemId}</b><br>Arrived at ${orderData.originBranch}`).openPopup();
        }
    }
    moveMarker();

    // Save marker for refresh
    window.mapObjects.parcelMarker = marker;
    window.mapObjects.routeLine = routeLine;
    window.mapObjects.animationSpeed = animationSpeed;
    window.mapObjects.minDurationMs = minDurationMs;
}

// Determine color based on order ID prefix
function getParcelColorByOrderType(orderId) {
    if (orderId.startsWith('MC')) return '#1976d2'; // Blue for Motorcycle
    if (orderId.startsWith('TK')) return '#4CAF50'; // Green for Truck
    if (orderId.startsWith('CR')) return '#FFC107'; // Yellow for Car
    return '#e91e63'; // Pink as default
}

// interpolate between two points
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

function updateMapData() {
    // On refresh, re-animate the parcel from current position to destination
    if (!window.mapObjects || !window.mapObjects.routeLine) return;
    const { map, orderData, routeLine, minDurationMs } = window.mapObjects;

    // Start animation from a random point along the route (simulate progress)
    let startIdx = Math.floor(routeLine.length * (0.7 + Math.random() * 0.2));
    let marker = window.mapObjects.parcelMarker;
    if (!marker) return;

    let i = startIdx;
    const totalPoints = routeLine.length;
    const animationSpeed = Math.max(10, Math.ceil((minDurationMs || 20000) / (totalPoints - startIdx)));

    function moveMarker() {
        if (i < totalPoints) {
            marker.setLatLng(routeLine[i]);
            i++;
            setTimeout(moveMarker, animationSpeed);
        } else {
            marker.setLatLng(routeLine[totalPoints - 1]);
            marker.bindPopup(`<b>Parcel ${orderData.orderItemId}</b><br>Arrived at ${orderData.originBranch}`).openPopup();
        }
    }
    moveMarker();

    // Center the map on the new position
    map.panTo(routeLine[startIdx]);
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

function updateProgressStatus() {
    // Set the progress bar to match the current status (e.g., 60%)
    const progressBar = document.querySelector('.progress-bar-fill');
    if (progressBar) {
        progressBar.style.width = '60%';
    }
}

function showNotification(message, type = 'success') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        background: ${type === 'error' ? '#f44336' : '#333'};
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
        
        // Ensure route points remain visible after resize
        if (window.mapObjects.routePoints) {
            var bounds = L.latLngBounds(window.mapObjects.routePoints);
            window.mapObjects.map.fitBounds(bounds, {
                padding: [50, 50],
                maxZoom: 13
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