document.addEventListener('DOMContentLoaded', function () {
    // Fee breakdown values (could be dynamic in real app)
    const baseFare = 200.00;
    const shippingFee = 79.00;
    const serviceFee = 20.00;

    function updateBreakdown() {
        document.getElementById('base-fare').textContent = `₱${baseFare.toFixed(2)}`;
        document.getElementById('shipping-fee').textContent = `₱${shippingFee.toFixed(2)}`;
        document.getElementById('service-fee').textContent = `₱${serviceFee.toFixed(2)}`;
        const total = baseFare + shippingFee + serviceFee;
        document.getElementById('amount-value').textContent = total.toFixed(2);
        return total.toFixed(2);
    }

    updateBreakdown();

    // Demo: get total from query param or use default
    function getTotalAmount() {
        // Always use the calculated breakdown for now
        return updateBreakdown();
    }

    document.getElementById('amount-value').textContent = getTotalAmount();

    // Modal creation
    function createModal(trackingId) {
        let modal = document.createElement('div');
        modal.className = 'order-modal';
        modal.innerHTML = `
            <div class="order-modal-content">
                <h2>Thank you for your order!</h2>
                <p>Your tracking ID is <span class="tracking-id">${trackingId}</span></p>
                <button id="okOrderBtn" class="order-ok-btn" disabled>OK (<span id="okOrderTimer">3</span>)</button>
            </div>
        `;
        Object.assign(modal.style, {
            position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh',
            background: 'rgba(3,51,94,0.18)', zIndex: 99999, display: 'flex',
            alignItems: 'center', justifyContent: 'center'
        });
        document.body.appendChild(modal);

        // Animate modal in
        setTimeout(() => {
            modal.querySelector('.order-modal-content').style.transform = 'scale(1)';
            modal.querySelector('.order-modal-content').style.opacity = '1';
        }, 10);

        // OK button cooldown
        let okBtn = document.getElementById('okOrderBtn');
        let okTimer = document.getElementById('okOrderTimer');
        let seconds = 3;
        okBtn.disabled = true;
        okBtn.classList.add('order-ok-btn-disabled');
        let interval = setInterval(() => {
            seconds--;
            okTimer.textContent = seconds;
            if (seconds <= 0) {
                clearInterval(interval);
                okBtn.disabled = false;
                okBtn.textContent = "OK";
                okBtn.classList.remove('order-ok-btn-disabled');
            }
        }, 1000);

        okBtn.onclick = function () {
            window.location.href = "index.html";
        };
    }

    // Generate random tracking ID: 4 digits + 2 lowercase letters
    function generateTrackingId() {
        const digits = Math.floor(1000 + Math.random() * 9000);
        const letters = String.fromCharCode(
            97 + Math.floor(Math.random() * 26),
            97 + Math.floor(Math.random() * 26)
        );
        return `${digits}${letters}`;
    }

    // Button enable/disable logic
    const methodCards = document.querySelectorAll('.pay-method-card');
    const creditFields = document.getElementById('credit-fields');
    const gcashFields = document.getElementById('gcash-fields');
    const paypalFields = document.getElementById('paypal-fields');
    const codFields = document.getElementById('cod-fields');
    const payBtn = document.getElementById('payBtn');
    const paymentForm = document.getElementById('paymentForm');

    function getSelectedMethod() {
        const selected = document.querySelector('.pay-method-card.selected input[type="radio"]');
        return selected ? selected.value : null;
    }

    function isFormValid() {
        const method = getSelectedMethod();
        if (!method) return false;
        if (method === 'credit') {
            // Check all credit fields are filled
            const inputs = creditFields.querySelectorAll('input');
            return Array.from(inputs).every(input => input.value.trim() !== '');
        }
        // For GCash, PayPal, COD: just need method selected
        return true;
    }

    function updatePayBtnState() {
        if (isFormValid()) {
            payBtn.disabled = false;
            payBtn.classList.remove('btn-disabled');
        } else {
            payBtn.disabled = true;
            payBtn.classList.add('btn-disabled');
        }
    }

    // Add .btn-disabled style if not present
    if (!document.querySelector('style[data-paywall-btn]')) {
        const style = document.createElement('style');
        style.dataset.paywallBtn = "1";
        style.innerHTML = `
            .btn-disabled, .order-ok-btn-disabled {
                background: #bfc8d1 !important;
                color: #7a869a !important;
                cursor: not-allowed !important;
                box-shadow: none !important;
                pointer-events: none;
                filter: grayscale(0.3);
            }
            .order-modal-content {
                background: #fff;
                border-radius: 18px;
                box-shadow: 0 8px 40px #03335e55, 0 2px 12px #b2dbf855;
                padding: 40px 32px 28px 32px;
                min-width: 280px;
                max-width: 90vw;
                display: flex;
                flex-direction: column;
                align-items: center;
                animation: popInModal 0.5s cubic-bezier(.4,2,.3,1);
                border: 2px solid #b2dbf8;
                position: relative;
                transform: scale(0.92);
                opacity: 0;
                transition: transform 0.25s, opacity 0.25s;
            }
            .order-modal-content h2 {
                color: #03335e;
                font-size: 1.5rem;
                margin: 0 0 12px 0;
                font-weight: 800;
                letter-spacing: 1px;
            }
            .order-modal-content .tracking-id {
                color: #095190;
                font-size: 1.2rem;
                font-weight: 700;
                background: #eaf6fb;
                border-radius: 8px;
                padding: 4px 16px;
                margin-left: 4px;
                letter-spacing: 2px;
            }
            .order-ok-btn {
                background: #b2dbf8;
                color: #03335e;
                border: none;
                border-radius: 10px;
                padding: 10px 32px;
                font-size: 1rem;
                font-weight: 700;
                cursor: pointer;
                box-shadow: 0 2px 8px #b2dbf8aa;
                transition: background 0.2s, color 0.2s, transform 0.15s;
                margin-top: 18px;
            }
            .order-ok-btn:enabled:hover {
                background: #095190;
                color: #fff;
                transform: scale(1.04);
            }
            @keyframes popInModal {
                0% { transform: scale(0.85) translateY(30px); opacity: 0; }
                100% { transform: scale(1) translateY(0); opacity: 1; }
            }
        `;
        document.head.appendChild(style);
    }

    // Payment method switching
    function showFields(method) {
        creditFields.style.display = method === 'credit' ? '' : 'none';
        gcashFields.style.display = method === 'gcash' ? '' : 'none';
        paypalFields.style.display = method === 'paypal' ? '' : 'none';
        codFields.style.display = method === 'cod' ? '' : 'none';
        payBtn.style.display = (method === 'paypal') ? 'none' : '';
        updatePayBtnState();
    }

    methodCards.forEach(card => {
        card.addEventListener('click', function () {
            methodCards.forEach(c => c.classList.remove('selected'));
            this.classList.add('selected');
            const radio = this.querySelector('input[type="radio"]');
            radio.checked = true;
            showFields(radio.value);
        });
    });

    // Initial state
    showFields(getSelectedMethod());

    // Listen for input changes to enable/disable Pay Now
    paymentForm.addEventListener('input', updatePayBtnState);

    // PayPal integration
    if (window.paypal) {
        paypal.Buttons({
            style: {
                layout: 'vertical',
                color:  'blue',
                shape:  'rect',
                label:  'paypal'
            },
            createOrder: function(data, actions) {
                return actions.order.create({
                    purchase_units: [{
                        amount: {
                            value: getTotalAmount(),
                            currency_code: 'PHP'
                        }
                    }]
                });
            },
            onApprove: function(data, actions) {
                return actions.order.capture().then(function(details) {
                    document.getElementById('paypal-button-container').innerHTML =
                        `<div class="paypal-success">Payment completed by ${details.payer.name.given_name}!</div>`;
                });
            }
        }).render('#paypal-button-container');
    }

    // Handle form submit for non-PayPal
    paymentForm.addEventListener('submit', function(e) {
        e.preventDefault();
        if (!isFormValid()) return;
        payBtn.textContent = "Processing...";
        payBtn.disabled = true;
        payBtn.classList.add('processing');
        setTimeout(() => {
            payBtn.textContent = "Paid!";
            payBtn.classList.remove('processing');
            payBtn.classList.add('paid');
            // Show modal
            createModal(generateTrackingId());
        }, 1200);
    });

    // Initial button state
    updatePayBtnState();
});
