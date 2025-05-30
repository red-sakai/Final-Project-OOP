// Auto-advance OTP boxes and basic animation
document.addEventListener('DOMContentLoaded', function() {
    const otpInputs = document.querySelectorAll('.otp-box');
    otpInputs.forEach((input, idx) => {
        input.addEventListener('input', function() {
            if (this.value.length === 1 && idx < otpInputs.length - 1) {
                otpInputs[idx + 1].focus();
            }
        });
        input.addEventListener('keydown', function(e) {
            if (e.key === "Backspace" && !this.value && idx > 0) {
                otpInputs[idx - 1].focus();
            }
        });
    });
});
