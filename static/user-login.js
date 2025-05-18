let isVisible = false;

function togglePassword() {
    const input = document.getElementById("user-password");
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

// Secret admin login shortcut: press "=" 5 times
let eqCount = 0;
document.addEventListener('keydown', function(e) {
    if (document.activeElement.tagName === 'INPUT' || document.activeElement.tagName === 'TEXTAREA') return;
    if (e.key === '=') {
        eqCount++;
        if (eqCount === 5) {
            window.location.href = adminLoginUrl;
        }
    } else {
        eqCount = 0;
    }
});