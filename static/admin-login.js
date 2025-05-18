let isVisible = false;

function togglePassword() {
    const input = document.getElementById("admin-password");
    const icon = document.getElementById("show-password-icon");

    if (!input || !icon) {
        console.warn("Password input or icon not found");
        return;
    }

    isVisible = !isVisible;
    input.type = isVisible ? "text" : "password";
    icon.src = isVisible ? icon.getAttribute("data-hide") : icon.getAttribute("data-visible");
    icon.alt = isVisible ? "Hide Password" : "Show Password";
}