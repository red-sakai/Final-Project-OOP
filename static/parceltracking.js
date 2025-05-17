document.addEventListener("DOMContentLoaded", function () {
    // drop-off points in NCR
    var dropOffPoints = [
        {lat: 14.6760, lng: 121.0437, name: "Quezon City (North)"},
        {lat: 14.6507, lng: 120.9667, name: "Caloocan (North)"},
        {lat: 14.5995, lng: 120.9842, name: "Manila (Center)"},
        {lat: 14.4793, lng: 121.0198, name: "Parañaque (South)"}
    ];

    // starting point (Manila Port)
    var startPoint = [14.6016, 120.9762];

    // Make sure the map div exists
    var mapDiv = document.getElementById('map');
    if (!mapDiv) return;

    // Set map height/width to fill the .map-container
    mapDiv.style.height = "400px";
    mapDiv.style.width = "100%";

    var map = L.map('map').setView([14.5995, 120.9842], 11);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    // add drop-off points as markers
    dropOffPoints.forEach(function(point) {
        L.marker([point.lat, point.lng])
            .addTo(map)
            .bindPopup(point.name);
    });

    // parcel colors and labels
    var parcelColors = ['red', 'blue', 'green', 'orange'];
    var parcelLabels = ['Parcel 1', 'Parcel 2', 'Parcel 3', 'Parcel 4'];

    // interpolate between two points
    function interpolate(start, end, t) {
        return [
            start[0] + (end[0] - start[0]) * t,
            start[1] + (end[1] - start[1]) * t
        ];
    }

    // animate each parcel
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

    // Modal logic for employee details
    var callBtn = document.querySelector('.call-btn');
    var modal = document.getElementById('employee-modal');
    var closeModal = document.getElementById('close-modal');

    if (callBtn && modal && closeModal) {
        callBtn.addEventListener('click', function() {
            modal.style.display = 'block';
        });
        closeModal.addEventListener('click', function() {
            modal.style.display = 'none';
        });
        window.addEventListener('click', function(event) {
            if (event.target === modal) {
                modal.style.display = 'none';
            }
        });
    }
});