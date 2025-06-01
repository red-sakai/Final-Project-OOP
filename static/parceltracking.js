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
    // Make sure the map div exists
    var mapDiv = document.getElementById('map');
    if (!mapDiv) return;

    // Set map to fill container completely
    mapDiv.style.height = "100%";
    mapDiv.style.width = "100%";
    
    // Use orderData from Flask if available
    if (typeof orderData === 'undefined' || !orderData) {
        showNotification('No order data found for this tracking ID', 'error');
        return;
    }

    // Initialize the map with optimized settings
    var map = L.map('map', {
        zoomControl: false,
        scrollWheelZoom: true,
        attributionControl: false,
        dragging: true,
        tap: true
    }).setView([orderData.customerLatitude, orderData.customerLongitude], 12);
    
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

    // Only show the drop-off marker for this order
    setupMapWithOrderData(map, orderData);
}

function setupMapWithOrderData(map, orderData) {
    // Extract coordinates for this specific order
    const branchPoint = [orderData.branchLatitude, orderData.branchLongitude];
    const customerPoint = [orderData.customerLatitude, orderData.customerLongitude];
    
    // Add branch marker (drop-off point)
    const branchMarker = L.marker(branchPoint)
        .addTo(map)
        .bindPopup(`<b>${orderData.originBranch}</b><br>Branch Location`);
    
    // Draw the route line between customer and branch
    const routeLine = L.polyline([customerPoint, branchPoint], {
        color: '#03335E',
        weight: 4,
        opacity: 0.7,
        lineCap: 'round',
        dashArray: '1, 8',
        dashOffset: '1'
    }).addTo(map);
    
    animatePolyline(routeLine);
    
    // Create a parcel marker that will move along the route
    const parcelColor = getParcelColorByOrderType(orderData.orderItemId);
    const parcelMarker = L.circleMarker(customerPoint, {
        radius: 10,
        color: parcelColor,
        fillColor: parcelColor,
        fillOpacity: 0.8,
        weight: 2
    }).addTo(map)
    .bindPopup(`<b>Parcel ${orderData.orderItemId}</b><br>${orderData.deliveryStatus}`);
    
    parcelMarker.openPopup();
    
    // Set up animation for the parcel
    animateParcel(parcelMarker, customerPoint, branchPoint, 5000);
    
    // Fit map to these points with padding
    const bounds = L.latLngBounds([customerPoint, branchPoint]);
    map.fitBounds(bounds, {
        padding: [50, 50],
        maxZoom: 13
    });
    
    // Store references for later use (like refresh)
    window.mapObjects = {
        map: map,
        orderData: orderData,
        parcelMarker: parcelMarker,
        routePoints: [customerPoint, branchPoint]
    };
}

// Determine color based on order ID prefix
function getParcelColorByOrderType(orderId) {
    if (orderId.startsWith('MC')) return '#1976d2'; // Blue for Motorcycle
    if (orderId.startsWith('TK')) return '#4CAF50'; // Green for Truck
    if (orderId.startsWith('CR')) return '#FFC107'; // Yellow for Car
    return '#e91e63'; // Pink as default
}

// Animate parcel moving along the route
function animateParcel(marker, startPoint, endPoint, duration) {
    let startTime = null;
    
    function animate(timestamp) {
        if (!startTime) startTime = timestamp;
        const elapsed = timestamp - startTime;
        const t = Math.min(elapsed / duration, 1);
        const pos = interpolate(startPoint, endPoint, t);
        
        marker.setLatLng(pos);
        
        if (t < 1) {
            requestAnimationFrame(animate);
        } else {
            // Animation complete - the parcel has reached its destination
            marker.setLatLng(endPoint);
            marker.bindPopup(`<b>Parcel ${window.mapObjects.orderData.orderItemId}</b><br>Arrived at ${window.mapObjects.orderData.originBranch}`).openPopup();
        }
    }
    
    requestAnimationFrame(animate);
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
    if (!window.mapObjects) return;
    
    const { map, parcelMarker, routePoints } = window.mapObjects;
    
    // Update the parcel position (simulate movement)
    var progress = Math.min(0.9, 0.7 + Math.random() * 0.2); // Move a bit further along the route
    var newPosition = calculateCurrentPosition(routePoints, progress);
    
    parcelMarker.setLatLng(newPosition);
    
    // Add animation effect
    parcelMarker._path?.classList.add('marker-updated');
    setTimeout(() => {
        if (parcelMarker._path) {
            parcelMarker._path.classList.remove('marker-updated');
        }
    }, 1000);
    
    // Center the map on the new position
    map.panTo(newPosition);
}

function calculateCurrentPosition(route, progress) {
    // Simple linear interpolation between route points
    return interpolate(route[0], route[1], progress);
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