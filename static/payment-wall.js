document.addEventListener('DOMContentLoaded', function () {
    // Get pricing from data attributes embedded by Flask
    const baseFare = parseFloat(document.getElementById('fee-breakdown').dataset.baseFare || 200.00);
    const shippingFee = parseFloat(document.getElementById('fee-breakdown').dataset.shippingFee || 79.00);
    const serviceFee = parseFloat(document.getElementById('fee-breakdown').dataset.serviceFee || 20.00);
    const vehicleType = document.getElementById('fee-breakdown').dataset.vehicleType || 'default';

    function updateBreakdown() {
        document.getElementById('base-fare').textContent = `₱${baseFare.toFixed(2)}`;
        document.getElementById('shipping-fee').textContent = `₱${shippingFee.toFixed(2)}`;
        document.getElementById('service-fee').textContent = `₱${serviceFee.toFixed(2)}`;
        const total = baseFare + shippingFee + serviceFee;
        document.getElementById('amount-value').textContent = total.toFixed(2);
        return total.toFixed(2);
    }

    updateBreakdown();

    // Get vehicle icon based on type
    function getVehicleEmoji() {
        switch(vehicleType) {
            case 'motorcycle': return '🏍️';
            case 'car': return '🚗';
            case 'truck': return '🚚';
            default: return '🚚';
        }
    }

    // Update vehicle icon in the first fee row
    const firstFeeRow = document.querySelector('.fee-row:nth-child(1) span:first-child');
    if (firstFeeRow && firstFeeRow.dataset.updateIcon !== 'false') {
        const feeIcon = firstFeeRow.querySelector('.fee-icon');
        if (feeIcon) {
            feeIcon.textContent = getVehicleEmoji();
        }
    }

    // Demo: get total from query param or use default
    function getTotalAmount() {
        // Always use the calculated breakdown for now
        return updateBreakdown();
    }

    document.getElementById('amount-value').textContent = getTotalAmount();

    // Use vehicle type to customize UI
    document.documentElement.dataset.vehicleType = vehicleType;
    const container = document.querySelector('.payment-wall-container');
    if (container) {
        container.classList.add(`vehicle-${vehicleType}`);
    }

    // Modal creation
    function createModal(orderNumber) {
        let modal = document.createElement('div');
        modal.className = 'order-modal';
        modal.innerHTML = `
            <div class="order-modal-content">
                <div class="modal-icon">✅</div>
                <h2>Thank you for your order!</h2>
                <p>Your Order # is <span class="order-number">#${orderNumber}</span></p>
                <button id="okOrderBtn" class="order-ok-btn" disabled>OK (<span id="okOrderTimer">3</span>)</button>
            </div>
        `;
        Object.assign(modal.style, {
            position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh',
            background: 'rgba(3,51,94,0.6)', backdropFilter: 'blur(5px)', zIndex: 99999, display: 'flex',
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
            window.location.href = "/index.html";
        };
    }

    // Get the order number from the DOM (matches the one rendered by Flask)
    function getOrderNumberFromDOM() {
        const orderIdElem = document.querySelector('.order-id');
        if (orderIdElem) {
            // Extract the order id after the '#' (e.g., "Order #CR1234567")
            const match = orderIdElem.textContent.match(/#([A-Z]{2}\d{6,7})/i);
            if (match) return match[1];
        }
        return null;
    }

    // Generate random order number (6 digits)
    function generateOrderNumber() {
        return Math.floor(100000 + Math.random() * 900000).toString();
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
        
        if (method === 'credit' && creditFields && creditFields.style.display !== 'none') {
            const cardName = document.getElementById('card-name');
            const cardNumber = document.getElementById('card-number');
            const cardExp = document.getElementById('card-exp');
            const cardCvv = document.getElementById('card-cvv');
            const address = document.getElementById('credit-address1');
            
            return cardName && cardName.value.trim() !== '' &&
                cardNumber && cardNumber.value.trim().replace(/\s/g, '').length >= 16 &&
                cardExp && /^\d{2}\/\d{2}$/.test(cardExp.value.trim()) &&
                cardCvv && cardCvv.value.trim().length >= 3 &&
                address && address.value.trim() !== '';
        }
        
        if (method === 'gcash' && gcashFields && gcashFields.style.display !== 'none') {
            const refnum = document.getElementById('gcash-refnum');
            const address = document.getElementById('gcash-address1');
            return refnum && /^\d{13}$/.test(refnum.value.trim()) &&
                address && address.value.trim() !== '';
        }
        
        if (method === 'paypal' && paypalFields && paypalFields.style.display !== 'none') {
            const address = document.getElementById('paypal-address1');
            return address && address.value.trim() !== '';
        }
        
        if (method === 'cod' && codFields && codFields.style.display !== 'none') {
            const addr1 = document.getElementById('cod-address1');
            const phone = document.getElementById('cod-phone');
            return addr1 && addr1.value.trim() !== '' && 
                phone && phone.value.trim() !== '';
        }
        
        return false;
    }

    function updatePayBtnState() {
        const method = getSelectedMethod();
        if (!payBtn) return;

        // Update button text based on payment method
        const btnText = payBtn.querySelector('.btn-text');
        if (btnText) {
            if (method === 'cod') {
                btnText.textContent = "Order Now";
            } else {
                btnText.textContent = "Pay Now";
            }
        }

        // Toggle PayPal button visibility
        if (method === 'paypal') {
            payBtn.style.display = 'none';
            if (window.renderPayPalButton) window.renderPayPalButton();
        } else {
            payBtn.style.display = '';
        }

        // Enable/disable button based on form validity (only if not PayPal)
        if (method !== 'paypal') {
            if (isFormValid()) {
                payBtn.disabled = false;
                payBtn.classList.remove('btn-disabled', 'disabled');
            } else {
                payBtn.disabled = true;
                payBtn.classList.add('btn-disabled', 'disabled');
            }
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

    // Helper to set required attributes only for visible fields
    function updateRequiredFields(method) {
        // Credit Card
        if (creditFields) {
            creditFields.querySelectorAll('input').forEach(input => {
                input.required = (method === 'credit');
            });
        }
        // GCash
        if (gcashFields) {
            gcashFields.querySelectorAll('input').forEach(input => {
                input.required = (method === 'gcash');
            });
        }
        // PayPal
        if (paypalFields) {
            paypalFields.querySelectorAll('input').forEach(input => {
                input.required = (method === 'paypal');
            });
        }
        // COD
        if (codFields) {
            codFields.querySelectorAll('input').forEach(input => {
                // Only require address1 and phone for COD
                if (input.id === 'cod-address1' || input.id === 'cod-phone') {
                    input.required = (method === 'cod');
                } else {
                    input.required = false;
                }
            });
        }
    }

    // Payment method switching
    function showFields(method) {
        if (creditFields) creditFields.style.display = method === 'credit' ? '' : 'none';
        if (gcashFields) gcashFields.style.display = method === 'gcash' ? '' : 'none';
        if (paypalFields) paypalFields.style.display = method === 'paypal' ? '' : 'none';
        if (codFields) codFields.style.display = method === 'cod' ? '' : 'none';
        updateRequiredFields(method);
        updatePayBtnState();
    }

    methodCards.forEach(card => {
        card.addEventListener('click', function () {
            methodCards.forEach(c => c.classList.remove('selected'));
            this.classList.add('selected');
            const radio = this.querySelector('input[type="radio"]');
            if (radio) {
                radio.checked = true;
                showFields(radio.value);
            }
        });
    });

    // Initial state
    showFields(getSelectedMethod());

    // Listen for input changes to enable/disable Pay Now/Order Now
    if (paymentForm) {
        paymentForm.addEventListener('input', updatePayBtnState);
    }

    // Add animation to the total amount
    const totalAmount = document.getElementById('total-amount');
    if (totalAmount) {
        totalAmount.addEventListener('mouseover', function() {
            this.classList.add('pulse-animation');
            setTimeout(() => this.classList.remove('pulse-animation'), 1000);
        });
    }

    // Enhanced payment success animation
    if (paymentForm) {
        paymentForm.addEventListener('submit', function(e) {
            e.preventDefault();
            console.log('Form submitted');
            
            // Double check form validation
            if (!isFormValid()) {
                console.log('Form validation failed');
                alert("Please fill in all required fields correctly.");
                return;
            }
            
            const method = getSelectedMethod();
            console.log('Processing payment for method:', method);
            
            // Show processing animation
            const btnText = payBtn.querySelector('.btn-text');
            if (btnText) {
                btnText.textContent = method === 'cod' ? "Processing Order..." : "Processing Payment...";
            }
            payBtn.disabled = true;
            payBtn.classList.add('processing');
            
            // Add progress animation to payment card
            const paymentCard = document.querySelector('.payment-wall-card');
            if (paymentCard) {
                paymentCard.classList.add('processing-payment');
            }
            
            setTimeout(() => {
                if (btnText) {
                    btnText.textContent = method === 'cod' ? "Order Confirmed!" : "Payment Successful!";
                }
                payBtn.classList.remove('processing');
                payBtn.classList.add('paid');
                if (paymentCard) {
                    paymentCard.classList.remove('processing-payment');
                    paymentCard.classList.add('payment-success');
                }
                
                // Show modal with success animation and order number from DOM
                const orderNumber = getOrderNumberFromDOM();
                createModal(orderNumber || generateOrderNumber());
            }, 1500);
        });
    }

    // Force re-validation on input changes
    document.querySelectorAll('.pay-fields input').forEach(input => {
        input.addEventListener('input', updatePayBtnState);
    });

    // Add direct click handler to the button
    if (payBtn) {
        payBtn.addEventListener('click', function(e) {
            console.log('Button clicked, disabled state:', this.disabled);
            if (this.disabled) {
                e.preventDefault();
                e.stopPropagation();
                alert("Please fill in all required fields correctly.");
            }
        });
    }

    // --- Address Geocoding Helper ---
    async function geocodeAddress(address) {
        // Use Nominatim OpenStreetMap API for demonstration (no API key required)
        const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(address)}`;
        try {
            const resp = await fetch(url, {
                headers: { 'Accept-Language': 'en' }
            });
            if (!resp.ok) return null;
            const data = await resp.json();
            if (data && data.length > 0) {
                // Return the best match
                return {
                    lat: data[0].lat,
                    lon: data[0].lon,
                    display_name: data[0].display_name,
                    confidence: data[0].importance || 0
                };
            }
            return null;
        } catch (e) {
            return null;
        }
    }

    // Show geocode warning or coordinates below the input
    function showGeocodeWarning(input, message) {
        let warn = input.parentNode.querySelector('.geocode-warning');
        if (!warn) {
            warn = document.createElement('div');
            warn.className = 'geocode-warning';
            warn.style.color = '#e74c3c';
            warn.style.fontSize = '0.92em';
            warn.style.margin = '4px 0 0 0';
            input.parentNode.appendChild(warn);
        }
        warn.textContent = message;
    }

    // Show geocode coordinates below the input
    function showGeocodeCoords(input, lat, lon) {
        let coords = input.parentNode.querySelector('.geocode-coords');
        if (!coords) {
            coords = document.createElement('div');
            coords.className = 'geocode-coords';
            coords.style.color = '#1579c0';
            coords.style.fontSize = '0.92em';
            coords.style.margin = '2px 0 0 0';
            input.parentNode.appendChild(coords);
        }
        coords.textContent = `📍 Latitude: ${lat}, Longitude: ${lon}`;
    }

    function clearGeocodeWarning(input) {
        let warn = input.parentNode.querySelector('.geocode-warning');
        if (warn) warn.remove();
        let coords = input.parentNode.querySelector('.geocode-coords');
        if (coords) coords.remove();
    }

    // Attach geocoding to all Address Line 1 fields
    function attachAddressGeocoding(inputId) {
        const input = document.getElementById(inputId);
        if (!input) return;
        input.addEventListener('blur', async function() {
            const val = input.value.trim();
            clearGeocodeWarning(input);
            if (val.length < 5) return; // Ignore too-short addresses
            input.dataset.geocodeStatus = 'pending';
            const result = await geocodeAddress(val);
            if (!result) {
                showGeocodeWarning(input, "⚠️ Address not found. Please check for typos or be more specific.");
                input.dataset.geocodeStatus = 'fail';
            } else {
                // Optionally, show the resolved address
                if (result.confidence < 0.2) {
                    showGeocodeWarning(input, "⚠️ Address found, but confidence is low. Please double-check.");
                } else {
                    clearGeocodeWarning(input);
                }
                input.dataset.geocodeStatus = 'ok';
                input.dataset.geocodeLat = result.lat;
                input.dataset.geocodeLon = result.lon;
                input.dataset.geocodeDisplay = result.display_name;
                showGeocodeCoords(input, result.lat, result.lon);
            }
        });
    }
    ['credit-address1', 'gcash-address1', 'paypal-address1', 'cod-address1'].forEach(attachAddressGeocoding);

    // On submit, geocode if not already done
    if (paymentForm) {
        paymentForm.addEventListener('submit', async function(e) {
            // ...existing code...
            // Before processing payment, check geocode for the selected address
            const method = getSelectedMethod();
            let addrInput = null;
            if (method === 'credit') addrInput = document.getElementById('credit-address1');
            if (method === 'gcash') addrInput = document.getElementById('gcash-address1');
            if (method === 'paypal') addrInput = document.getElementById('paypal-address1');
            if (method === 'cod') addrInput = document.getElementById('cod-address1');
            if (addrInput && addrInput.value.trim().length >= 5) {
                if (!addrInput.dataset.geocodeStatus || addrInput.dataset.geocodeStatus === 'pending') {
                    // Try geocoding now
                    clearGeocodeWarning(addrInput);
                    const result = await geocodeAddress(addrInput.value.trim());
                    if (!result) {
                        showGeocodeWarning(addrInput, "⚠️ Address not found. Please check for typos or be more specific.");
                        // Allow submission, but warn
                    } else if (result.confidence < 0.2) {
                        showGeocodeWarning(addrInput, "⚠️ Address found, but confidence is low. Please double-check.");
                        showGeocodeCoords(addrInput, result.lat, result.lon);
                    } else {
                        clearGeocodeWarning(addrInput);
                        showGeocodeCoords(addrInput, result.lat, result.lon);
                    }
                    addrInput.dataset.geocodeStatus = result ? 'ok' : 'fail';
                }
            }
            // ...existing code...
        });
    }
});