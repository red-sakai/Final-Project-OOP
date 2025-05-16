window.addEventListener("DOMContentLoaded", function() {
    const urlParams = new URLSearchParams(window.location.search);
    const modal = document.getElementById("ticket-modal");
    const closeBtn = document.getElementById("close-modal-btn");
    if (urlParams.get("ticket_submitted") === "1" && modal) {
        modal.style.display = "flex";
    }
    if (closeBtn && modal) {
        closeBtn.onclick = function() {
            modal.style.display = "none";
            // Remove the query param from URL without reload
            if (window.history.replaceState) {
                const url = new URL(window.location);
                url.searchParams.delete("ticket_submitted");
                window.history.replaceState({}, document.title, url.pathname + url.search);
            }
        };
    }
    // Optional: close modal when clicking outside the box
    if (modal) {
        modal.onclick = function(e) {
            if (e.target === modal) {
                modal.style.display = "none";
                if (window.history.replaceState) {
                    const url = new URL(window.location);
                    url.searchParams.delete("ticket_submitted");
                    window.history.replaceState({}, document.title, url.pathname + url.search);
                }
            }
        };
    }
});