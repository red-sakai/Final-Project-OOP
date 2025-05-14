document.addEventListener("DOMContentLoaded", () => {
    // Call outs
    const indexSlogan = document.getElementById("index-slogan");
    const indexText = document.getElementById("index-text");
    const zoomEl = document.getElementById("zoom-image");

    // Animation for all elements
    if (indexSlogan) {       
        indexSlogan.style.opacity = "1";
        indexSlogan.style.visibility = "visible";
        // Re-trigger animation
        indexSlogan.classList.remove("fade-slide-right");
        setTimeout(() => {
            indexSlogan.classList.add("fade-slide-right");
        }, 10);
    }
    
    if (indexText) {       
        indexText.style.opacity = "1";
        indexText.style.visibility = "visible";
        // Re-trigger animation
        indexText.classList.remove("fade-slide-left");
        setTimeout(() => {
            indexText.classList.add("fade-slide-left");
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