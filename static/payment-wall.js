document.addEventListener('DOMContentLoaded', function () {
    // Demo: get total from query param or use default
    function getTotalAmount() {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get('total') || '299.00';
    }
    document.getElementById('amount-value').textContent = getTotalAmount();

    // Payment method switching
    const methodCards = document.querySelectorAll('.pay-method-card');
    const creditFields = document.getElementById('credit-fields');
    const gcashFields = document.getElementById('gcash-fields');
    const paypalFields = document.getElementById('paypal-fields');
    const codFields = document.getElementById('cod-fields');
    const payBtn = document.getElementById('payBtn');

    function showFields(method) {
        creditFields.style.display = method === 'credit' ? '' : 'none';
        gcashFields.style.display = method === 'gcash' ? '' : 'none';
        paypalFields.style.display = method === 'paypal' ? '' : 'none';
        codFields.style.display = method === 'cod' ? '' : 'none';
        payBtn.style.display = (method === 'paypal') ? 'none' : '';
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
    showFields(document.querySelector('.pay-method-card.selected input[type="radio"]').value);

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

    // Demo: handle form submit for non-PayPal
    document.getElementById('paymentForm').addEventListener('submit', function(e) {
        e.preventDefault();
        const selected = document.querySelector('.pay-method-card.selected input[type="radio"]').value;
        payBtn.textContent = "Processing...";
        payBtn.disabled = true;
        payBtn.classList.add('processing');
        setTimeout(() => {
            payBtn.textContent = selected === 'cod' ? "Order Placed!" : "Paid!";
            payBtn.classList.remove('processing');
            payBtn.classList.add('paid');
        }, 1800);
    });
});
