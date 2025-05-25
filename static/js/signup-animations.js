document.addEventListener('DOMContentLoaded', () => {
    // Define keyframes for animations
    document.head.insertAdjacentHTML('beforeend', `
        <style>
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            
            @keyframes slideUp {
                from { 
                    opacity: 0;
                    transform: translateY(20px); 
                }
                to { 
                    opacity: 1;
                    transform: translateY(0); 
                }
            }
            
            @keyframes slideRight {
                from { 
                    opacity: 0;
                    transform: translateX(-30px); 
                }
                to { 
                    opacity: 1;
                    transform: translateX(0); 
                }
            }
            
            @keyframes pulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.05); }
                100% { transform: scale(1); }
            }
        </style>
    `);

    // Form validation and interactive effects
    const formInputs = document.querySelectorAll('.user-input');
    const signupButton = document.querySelector('.signin-button');

    // Input focus effects
    formInputs.forEach(input => {
        input.addEventListener('focus', () => {
            input.parentElement.querySelector('.input-icon').style.color = '#1579c0';
        });

        input.addEventListener('blur', () => {
            input.parentElement.querySelector('.input-icon').style.color = '';
            
            // Simple validation feedback
            if (input.value.trim() !== '') {
                if (input.type === 'email' && !validateEmail(input.value)) {
                    showInputError(input, 'Please enter a valid email');
                } else if (input.getAttribute('placeholder') === 'Confirm Password') {
                    const password = document.querySelector('input[placeholder="Password"]').value;
                    if (input.value !== password) {
                        showInputError(input, 'Passwords do not match');
                    } else {
                        showInputSuccess(input);
                    }
                } else {
                    showInputSuccess(input);
                }
            }
        });
    });

    // Button hover animation
    signupButton.addEventListener('mouseover', () => {
        signupButton.style.animation = 'pulse 0.8s infinite';
    });

    signupButton.addEventListener('mouseout', () => {
        signupButton.style.animation = '';
    });

    // Form submission animation
    document.querySelector('.user-signin-form').addEventListener('submit', (e) => {
        e.preventDefault();
        
        // Validate form
        let isValid = true;
        formInputs.forEach(input => {
            if (input.value.trim() === '') {
                isValid = false;
            }
        });

        if (isValid) {
            signupButton.textContent = 'Processing...';
            signupButton.disabled = true;
            
            // Add success animation
            signupButton.classList.add('animate-success');
            
            // Submit form after animation (simulating)
            setTimeout(() => {
                e.target.submit();
            }, 1500);
        } else {
            // Shake animation for the form
            const form = document.querySelector('.user-signin-form');
            form.style.animation = 'shake 0.5s ease';
            setTimeout(() => {
                form.style.animation = '';
            }, 500);
        }
    });

    // Helper functions
    function validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }

    function showInputError(input, message) {
        input.style.borderColor = '#ff3860';
        
        // Remove existing error message if any
        const existingError = input.parentElement.querySelector('.error-message');
        if (existingError) {
            existingError.remove();
        }
        
        // Add error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.style.color = '#ff3860';
        errorDiv.style.fontSize = '12px';
        errorDiv.style.marginTop = '5px';
        errorDiv.textContent = message;
        
        input.parentElement.appendChild(errorDiv);
    }

    function showInputSuccess(input) {
        input.style.borderColor = '#23d160';
        
        // Remove existing error message if any
        const existingError = input.parentElement.querySelector('.error-message');
        if (existingError) {
            existingError.remove();
        }
    }

    // Add shake keyframe dynamically
    document.head.insertAdjacentHTML('beforeend', `
        <style>
            @keyframes shake {
                0%, 100% { transform: translateX(0); }
                10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
                20%, 40%, 60%, 80% { transform: translateX(5px); }
            }
            
            @keyframes animate-success {
                0% { background-color: var(--primary-color); }
                100% { background-color: #23d160; }
            }
        </style>
    `);
});
