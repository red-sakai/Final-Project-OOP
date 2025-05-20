document.addEventListener("DOMContentLoaded", function () {
    document.getElementById('bookingForm').addEventListener('submit', function(event) {
        event.preventDefault();
        if (this.checkValidity()) {
            window.location.href = paymentWallUrl;
        } else {
            this.reportValidity();
        }
    });

    // Disable button initially
    const bookingForm = document.getElementById('bookingForm');
    const confirmBtn = document.querySelector('.btn');

    function checkFormValidity() {
        if (bookingForm.checkValidity()) {
            confirmBtn.disabled = false;
            confirmBtn.classList.remove('btn-disabled');
        } else {
            confirmBtn.disabled = true;
            confirmBtn.classList.add('btn-disabled');
        }
    }

    bookingForm.addEventListener('input', checkFormValidity);
    checkFormValidity();
});