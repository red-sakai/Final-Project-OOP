document.addEventListener("DOMContentLoaded", function () {
    const bookingForm = document.getElementById('bookingForm');
    const confirmBtn = document.querySelector('.btn');
    const quantityInput = document.getElementById('quantity');
    const weightModal = document.getElementById('weightModal');
    const confirmWeightBtn = document.getElementById('confirmWeight');
    const cancelWeightBtn = document.getElementById('cancelWeight');
    
    let weightConfirmed = false;
    
    document.getElementById('bookingForm').addEventListener('submit', function(event) {
        event.preventDefault();
        // Store dropoff and schedule in sessionStorage for payment-wall
        sessionStorage.setItem('carbook_dropoff', document.getElementById('dropoff').value);
        sessionStorage.setItem('carbook_schedule', document.getElementById('schedule').value);
        if (this.checkValidity()) {
            openPopup();
        } else {
            this.reportValidity();
        }
    });

    function openPopup() {
        document.getElementById("popup").style.display = "block";
        document.querySelector('.book-container').classList.add('blurred');
        startOkTimer();
    }

    window.closePpopup = function() {
        document.getElementById("popup").style.display = "none";
        document.querySelector('.book-container').classList.remove('blurred');
        window.location.href = carHomeUrl;
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

    // Weight modal functionality
    quantityInput.addEventListener('blur', function() {
        if (this.value && !weightConfirmed) {
            showWeightModal();
        }
    });
    
    function showWeightModal() {
        weightModal.classList.add('active');
        // Only blur the form inside mobile-card, not the modal
        document.querySelector('.TypeBox').classList.add('blurred');
    }
    
    function hideWeightModal() {
        weightModal.classList.remove('active');
        document.querySelector('.TypeBox').classList.remove('blurred');
    }
    
    confirmWeightBtn.addEventListener('click', function() {
        weightConfirmed = true;
        hideWeightModal();
    });
    
    cancelWeightBtn.addEventListener('click', function() {
        quantityInput.value = '';
        hideWeightModal();
        quantityInput.focus();
    });

    // Disable button initially
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