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

    // Add customer marker (origin point) with a different color (green)
    const customerIcon = L.icon({
        iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
        shadowSize: [41, 41],
        // Use a green marker icon (replace with your own if desired)
        // You can use a custom green icon URL or SVG here if you want a different style
        className: 'leaflet-marker-green'
    });

    const customerMarker = L.marker(customerPoint, { icon: customerIcon })
        .addTo(map)
        .bindPopup(`<b>Customer Location</b><br>${orderData.customerPlace || 'Pickup Point'}`);

    // Add CSS to tint the marker green
    const style = document.createElement('style');
    style.innerHTML = `
        .leaflet-marker-green {
            filter: hue-rotate(90deg) saturate(2);
        }
    `;
    document.head.appendChild(style);

    // Store for refresh
    window.mapObjects = {
        map: map,
        orderData: orderData,
        branchMarker: branchMarker,
        customerMarker: customerMarker
    };

    // --- Draw fallback straight line only, no arrow ---
    const directPath = L.polyline([customerPoint, branchPoint], {
        color: '#03335E',
        weight: 5,
        opacity: 0.5,
        dashArray: '10,10'
    }).addTo(map);

    window.mapObjects.directPath = directPath;

    // Animate the parcel marker along the straight line as initial fallback
    animateParcelAlongRoute(map, [customerPoint, branchPoint], orderData, 20000);

    // Store route points for proper resize handling
    window.mapObjects.routePoints = [customerPoint, branchPoint];

    // Ensure the map shows both points
    map.fitBounds(L.latLngBounds([customerPoint, branchPoint]), {
        padding: [50, 50],
        maxZoom: 13
    });

    // --- Try to get road-following route ---
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
            styles: [
                {color: '#03335E', opacity: 0.0, weight: 0} // Make the default route invisible
            ]
        },
        createMarker: function() { return null; },
        router: L.Routing.osrmv1({
            serviceUrl: 'https://router.project-osrm.org/route/v1',
            profile: 'driving',
            useHints: false,
            geometryOnly: false
        })
    }).addTo(map);

    routingControl.on('routesfound', function(e) {
        const route = e.routes[0];
        const routeLine = route.coordinates.map(coord => [coord.lat, coord.lng]);

        // Remove the fallback direct path and arrows
        if (window.mapObjects.directPath) {
            map.removeLayer(window.mapObjects.directPath);
            window.mapObjects.directPath = null;
        }
        if (window.mapObjects.arrowHead) {
            map.removeLayer(window.mapObjects.arrowHead);
            window.mapObjects.arrowHead = null;
        }

        // Create two layers for the route animation
        const routeBase = L.polyline(routeLine, {
            color: '#03335E',
            weight: 6,
            opacity: 0.7
        }).addTo(map);

        const routeOverlay = L.polyline(routeLine, {
            color: '#1976d2',
            weight: 3,
            opacity: 0.9,
            dashArray: '10, 10',
            dashOffset: '0'
        }).addTo(map);

        const arrows = L.polylineDecorator(routeLine, {
            patterns: [
                {offset: 25, repeat: 75, symbol: L.Symbol.arrowHead({
                    pixelSize: 12, 
                    polygon: false, 
                    pathOptions: {stroke: true, color: '#ffffff', weight: 2}
                })}
            ]
        }).addTo(map);

        window.mapObjects.routeLine = routeLine;
        window.mapObjects.routeBase = routeBase;
        window.mapObjects.routeOverlay = routeOverlay;
        window.mapObjects.routingControl = routingControl;
        window.mapObjects.arrows = arrows;

        animatePolyline(routeOverlay);
        animateParcelAlongRoute(map, routeLine, orderData, 20000);
        window.mapObjects.routePoints = routeLine;

        map.fitBounds(L.latLngBounds(routeLine), {
            padding: [50, 50],
            maxZoom: 13
        });
    });

    // If routing fails, keep the fallback line/arrows and do nothing else
    routingControl.on('routingerror', function() {
        // No action needed, fallback already shown
    });
}

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

    // --- Smooth animation between points ---
    let i = 0;
    const totalPoints = routeLine.length;
    const totalDuration = minDurationMs;
    const segmentDuration = totalDuration / (totalPoints - 1);
    let startTime = null;

    function animateStep(timestamp) {
        if (!startTime) startTime = timestamp;
        const elapsed = timestamp - startTime;
        // Determine which segment we are in
        let seg = Math.floor(elapsed / segmentDuration);
        if (seg >= totalPoints - 1) {
            marker.setLatLng(routeLine[totalPoints - 1]);
            marker.bindPopup(`<b>Parcel ${orderData.orderItemId}</b><br>Arrived at ${orderData.originBranch}`).openPopup();
            return;
        }
        // Interpolate between seg and seg+1
        const t = (elapsed % segmentDuration) / segmentDuration;
        const from = routeLine[seg];
        const to = routeLine[seg + 1];
        const pos = [
            from[0] + (to[0] - from[0]) * t,
            from[1] + (to[1] - from[1]) * t
        ];
        marker.setLatLng(pos);
        requestAnimationFrame(animateStep);
    }
    requestAnimationFrame(animateStep);

    // Save marker for refresh
    window.mapObjects.parcelMarker = marker;
    window.mapObjects.routeLine = routeLine;
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
    // Cancel any existing animation
    if (window.mapObjects && window.mapObjects.animationId) {
        cancelAnimationFrame(window.mapObjects.animationId);
    }
    
    // Set up the animation
    let dashOffset = 0;
    
    function animate() {
        // Update the dashOffset (negative for left-to-right flow)
        dashOffset -= 0.75; // Slightly faster animation
        line.setStyle({ dashOffset: dashOffset.toString() });
        
        // Continue the animation
        window.mapObjects.animationId = requestAnimationFrame(animate);
    }
    
    // Start the animation
    animate();
}

function updateMapData() {
    // On refresh, re-animate the parcel from current position to destination
    if (!window.mapObjects || !window.mapObjects.routeLine) return;
    const { map, orderData, routeLine, minDurationMs } = window.mapObjects;
    
    // Cancel any existing animation
    if (window.mapObjects.animationId) {
        cancelAnimationFrame(window.mapObjects.animationId);
    }

    // Re-create the route visualization
    if (window.mapObjects.routeOverlay) {
        map.removeLayer(window.mapObjects.routeOverlay);
    }
    
    if (window.mapObjects.arrows) {
        map.removeLayer(window.mapObjects.arrows);
    }
    
    // Create a new animated route overlay
    const routeOverlay = L.polyline(routeLine, {
        color: '#1976d2',
        weight: 3,
        opacity: 0.9,
        dashArray: '10, 10',
        dashOffset: '0'
    }).addTo(map);
    
    // Add arrows to show direction
    const arrows = L.polylineDecorator(routeLine, {
        patterns: [
            {offset: 25, repeat: 75, symbol: L.Symbol.arrowHead({
                pixelSize: 12, 
                polygon: false, 
                pathOptions: {stroke: true, color: '#ffffff', weight: 2}
            })}
        ]
    }).addTo(map);
    
    // Store the route path
    window.mapObjects.routeOverlay = routeOverlay;
    window.mapObjects.arrows = arrows;
    
    // Animate the polyline
    animatePolyline(routeOverlay);

    // Start animation from a random point along the route (simulate progress)
    let startIdx = Math.floor(routeLine.length * (0.3 + Math.random() * 0.4)); // More central position
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