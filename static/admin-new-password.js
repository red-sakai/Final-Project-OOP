function togglePassword(inputId, iconId) {
    const input = document.getElementById(inputId);
    const icon = document.getElementById(iconId);
    if (input.type === "password") {
        input.type = "text";
        icon.src = "/static/images/hide.png";
        icon.alt = "Hide Password";
    } else {
        input.type = "password";
        icon.src = "/static/images/visible.png";
        icon.alt = "Show Password";
    }
}

// Password validation and requirement checking
document.addEventListener('DOMContentLoaded', function() {
    const passwordInput = document.getElementById('admin-new-password');
    const confirmInput = document.getElementById('admin-confirm-password');
    const newPasswordError = document.getElementById('new-password-error');
    const confirmPasswordError = document.getElementById('confirm-password-error');
    const form = document.querySelector('.admin-reset-pass-form');
    
    // Requirement elements
    const reqLength = document.getElementById('req-length');
    const reqSymbols = document.getElementById('req-symbols');
    const reqCase = document.getElementById('req-case');

    function checkRequirement(element, condition) {
        if (condition) {
            element.style.color = '#2e7d32';
            element.querySelector('.check-image').style.opacity = '1';
        } else {
            element.style.color = '#d32f2f';
            element.querySelector('.check-image').style.opacity = '0.3';
        }
    }

    function validatePassword(password) {
        const minLength = password.length >= 8;
        const hasSymbol = /[^A-Za-z0-9]/.test(password);
        const hasLower = /[a-z]/.test(password);
        const hasUpper = /[A-Z]/.test(password);
        
        // Update visual indicators
        checkRequirement(reqLength, minLength);
        checkRequirement(reqSymbols, hasSymbol);
        checkRequirement(reqCase, hasLower && hasUpper);
        
        return minLength && hasSymbol && hasLower && hasUpper;
    }

    function checkPasswords() {
        let valid = true;
        
        // Validate new password
        if (!validatePassword(passwordInput.value)) {
            newPasswordError.style.display = 'block';
            passwordInput.classList.add('input-error');
            valid = false;
        } else {
            newPasswordError.style.display = 'none';
            passwordInput.classList.remove('input-error');
        }
        
        // Validate confirm password
        if (passwordInput.value !== confirmInput.value || !confirmInput.value) {
            confirmPasswordError.style.display = 'block';
            confirmInput.classList.add('input-error');
            valid = false;
        } else {
            confirmPasswordError.style.display = 'none';
            confirmInput.classList.remove('input-error');
        }
        
        return valid;
    }

    passwordInput.addEventListener('input', checkPasswords);
    confirmInput.addEventListener('input', checkPasswords);

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (!checkPasswords()) {
            return;
        }

        // Submit form data to update password
        const formData = new FormData(form);
        
        fetch('/admin-new-password', {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'application/json'
            },
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                showSuccessPopup();
            } else {
                showErrorPopup(data.message || 'Failed to update password');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showErrorPopup('An error occurred while updating the password: ' + error.message);
        });
    });

    function showSuccessPopup() {
        const popup = document.createElement('div');
        popup.className = 'popup-overlay';
        popup.innerHTML = `
            <div class="popup-content">
                <h2>Password Updated Successfully!</h2>
                <p>Your admin password has been changed successfully.</p>
                <button id="go-to-login-btn" onclick="window.location.href='/admin/login'">Go to Login</button>
            </div>
        `;
        document.body.appendChild(popup);
    }

    function showErrorPopup(message) {
        const popup = document.createElement('div');
        popup.className = 'popup-overlay';
        popup.innerHTML = `
            <div class="popup-content">
                <h2>Error</h2>
                <p>${message}</p>
                <button id="go-to-login-btn" onclick="this.parentElement.parentElement.remove()">Close</button>
            </div>
        `;
        document.body.appendChild(popup);
    }
});
