document.addEventListener("DOMContentLoaded", () => {
    // Call outs
    const trackingHeader = document.getElementById("tracking-header");
    const trackingSubheader = document.getElementById("tracking-subheader");
    const trackingSlogan = document.getElementById("tracking-slogan");

    // Animation for all elements
    if (trackingHeader) {       
        trackingHeader.style.opacity = "1";
        trackingHeader.style.visibility = "visible";
        // Re-trigger animation
        trackingHeader.classList.remove("fade-slide-right");
        setTimeout(() => {
            trackingHeader.classList.add("fade-slide-right");
        }, 10);
    }

    if (trackingSubheader) {       
        trackingSubheader.style.opacity = "1";
        trackingSubheader.style.visibility = "visible";
        // Re-trigger animation
        trackingSubheader.classList.remove("fade-slide-right");
        setTimeout(() => {
            trackingSubheader.classList.add("fade-slide-right");
        }, 10);
    }

    if (trackingSlogan) {       
        trackingSlogan.style.opacity = "1";
        trackingSlogan.style.visibility = "visible";
        // Re-trigger animation
        trackingSlogan.classList.remove("fade-slide-right");
        setTimeout(() => {
            trackingSlogan.classList.add("fade-slide-right");
        }, 10);
    }

    // --- Navigation Bar Toggle Animation ---
    const navToggle = document.getElementById('nav-toggle');
    const navLinksContainer = document.getElementById('nav-links-container');

    if (navToggle && navLinksContainer) {
        navToggle.addEventListener('click', function () {
            navLinksContainer.classList.toggle('expanded');
        });
    }
});