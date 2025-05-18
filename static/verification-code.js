// Countdown Timer and Resend Code Logic
let timeLeft = 180;
let countdownEl = document.getElementById("countdown");
const resendBlue = document.getElementById("blue");

function updateTimer() {
    const minutes = String(Math.floor(timeLeft / 60)).padStart(2, '0');
    const seconds = String(timeLeft % 60).padStart(2, '0');
    countdownEl.textContent = `${minutes}:${seconds}`;
    if (timeLeft > 0) {
        timeLeft--;
        setTimeout(updateTimer, 1000);
    } else {
        makeResendClickable();
    }
}

function makeResendClickable() {
    resendBlue.innerHTML = `<a href="#" id="resend-link" style="color:#095190; text-decoration:underline; cursor:pointer;">Resend the code</a>`;
    document.getElementById("resend-link").addEventListener("click", function(e) {
        e.preventDefault();
        sendVerificationCode();
    });
}

function sendVerificationCode() {
    resendBlue.innerHTML = `Resend the code in <span class="timer" id="countdown">03:00</span>`;
    timeLeft = 180;
    countdownEl = document.getElementById("countdown");
    updateTimer();
}

updateTimer();

const errorMessage = document.getElementById("otp-error-message");
const resetBtn = document.getElementById("reset-password-btn");
const otpInputs = document.querySelectorAll(".otp-input");

// Function to get user code
function getUserCode() {
    let userCode = "";
    otpInputs.forEach(input => userCode += input.value);
    return userCode;
}

// Enable/disable button as user types
otpInputs.forEach(input => {
    input.addEventListener("input", function() {
        if (getUserCode() === systemCode) {
            resetBtn.disabled = false;
        } else {
            resetBtn.disabled = true;
        }
        // Do NOT show/hide error message here
    });
});

resetBtn.addEventListener("click", function(e) {
    e.preventDefault();
    if (getUserCode() === systemCode) {
        errorMessage.classList.remove("visible"); // Hide error if previously shown
        window.location.href = "admin-new-password.html?email=" + encodeURIComponent(email);
    } else {
        errorMessage.classList.add("visible"); // Show error only on invalid code and click
    }
});