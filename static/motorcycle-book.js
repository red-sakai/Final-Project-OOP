document.addEventListener("DOMContentLoaded", function () {
    document.getElementById('bookingForm').addEventListener('submit', function(event) {
        event.preventDefault();
        if (this.checkValidity()) {
            openPopup();
        } else {
            this.reportValidity();
        }
    });

    function openPopup() {
        document.getElementById("popup").classList.add("show");
        document.querySelector('.book-container').classList.add('blurred');
        startOkTimer();
    }

    window.closePpopup = function() {
        document.getElementById("popup").classList.remove("show");
        document.querySelector('.book-container').classList.remove('blurred');
        window.location.href = motorcycleHomeUrl;
    }

    function startOkTimer() {
        var okBtn = document.getElementById('okBtn');
        var okTimer = document.getElementById('okTimer');
        var seconds = 3;
        okBtn.disabled = true;
        okTimer.textContent = seconds;
        okBtn.textContent = `OK (${seconds})`;
        var interval = setInterval(function() {
            seconds--;
            okTimer.textContent = seconds;
            okBtn.textContent = `OK (${seconds})`;
            if (seconds <= 0) {
                clearInterval(interval);
                okBtn.disabled = false;
                okBtn.textContent = "OK";
            }
        }, 1000);
    }

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