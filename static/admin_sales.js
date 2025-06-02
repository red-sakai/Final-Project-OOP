document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const searchInput = document.getElementById('searchInput');
    const typeFilter = document.getElementById('typeFilter');
    const dateFilter = document.getElementById('dateFilter');
    const tabs = document.querySelectorAll('.tab');
    const saleRows = document.querySelectorAll('.sale-row');
    const addSaleBtn = document.querySelector('.add-sale-btn');
    const saleModal = document.getElementById('saleModal');
    const confirmationModal = document.getElementById('confirmationModal');
    const closeModals = document.querySelectorAll('.close-modal');
    const saleForm = document.getElementById('saleForm');
    const cancelBtns = document.querySelectorAll('.cancel-btn');
    const editBtns = document.querySelectorAll('.action-btn.edit');
    const deleteBtns = document.querySelectorAll('.action-btn.delete');
    const deleteConfirmBtn = document.querySelector('.delete-confirm-btn');
    
    let currentSaleId = null;

    // Tab functionality
    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            // Remove active class from all tabs
            tabs.forEach(t => t.classList.remove('active'));
            
            // Add active class to clicked tab
            this.classList.add('active');
            
            const type = this.getAttribute('data-type');
            
            // Filter table rows based on payment type
            filterSales();
        });
    });
    
    // Filter functionality
    function filterSales() {
        const searchTerm = searchInput.value.toLowerCase();
        const type = document.querySelector('.tab.active').getAttribute('data-type');
        const dateValue = dateFilter.value;
        
        // Calculate date threshold if dateValue is not 'all'
        let dateThreshold = null;
        if (dateValue !== 'all') {
            const days = parseInt(dateValue);
            dateThreshold = new Date();
            dateThreshold.setDate(dateThreshold.getDate() - days);
        }
        
        saleRows.forEach(row => {
            const rowType = row.getAttribute('data-type');
            let textContent = '';
            
            // Collect text content from all cells except the last one (actions)
            for (let i = 0; i < row.cells.length - 1; i++) {
                textContent += row.cells[i].textContent + ' ';
            }
            
            textContent = textContent.toLowerCase();
            
            // Extract date from the row (assuming date is in the 4th column with format YYYY-MM-DD)
            const dateStr = row.cells[3].textContent;
            const rowDate = new Date(dateStr);
            
            // Check if row matches all filter criteria
            const matchesSearch = textContent.includes(searchTerm);
            const matchesType = type === 'all' || rowType === type;
            const matchesDate = !dateThreshold || rowDate >= dateThreshold;
            
            if (matchesSearch && matchesType && matchesDate) {
                row.style.display = '';
                
                // Add animation for appearing rows
                row.style.animation = 'fadeIn 0.3s';
            } else {
                row.style.display = 'none';
            }
        });
        
        // Update stats based on filtered data
        updateStats();
    }
    
    // Update stats based on visible rows
    function updateStats() {
        const visibleRows = document.querySelectorAll('.sale-row:not([style*="display: none"])');
        
        let totalRevenue = 0;
        let totalProfit = 0;
        
        visibleRows.forEach(row => {
            // Parse revenue value (assuming it's in the 7th column, index 6)
            const revenueStr = row.cells[6].textContent.replace('₱', '').replace(/,/g, '');
            const revenue = parseFloat(revenueStr);

            // Parse profit value (assuming it's in the 8th column, index 7)
            const profitStr = row.cells[7].textContent.replace('₱', '').replace(/,/g, '');
            const profit = parseFloat(profitStr);

            if (!isNaN(revenue)) totalRevenue += revenue;
            if (!isNaN(profit)) totalProfit += profit;
        });

        // Update stats in the UI
        document.querySelector('.stat-card:nth-child(1) .count').textContent = '₱' + totalRevenue.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
        document.querySelector('.stat-card:nth-child(2) .count').textContent = '₱' + totalProfit.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
        document.querySelector('.stat-card:nth-child(3) .count').textContent = visibleRows.length;

        // Calculate profit margin
        const profitMargin = totalRevenue > 0 ? (totalProfit / totalRevenue * 100) : 0;
        document.querySelector('.stat-card:nth-child(4) .count').textContent = profitMargin.toFixed(1) + '%';
    }
    
    // Attach event listeners to filters
    searchInput.addEventListener('input', filterSales);
    typeFilter.addEventListener('change', filterSales);
    dateFilter.addEventListener('change', filterSales);
    
    // Modal functionality
    function openModal(modal) {
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden'; // Prevent scrolling
    }
    
    function closeAllModals() {
        saleModal.style.display = 'none';
        if(confirmationModal) confirmationModal.style.display = 'none';
        document.body.style.overflow = ''; // Enable scrolling
    }
    
    // Add new sale
    addSaleBtn.addEventListener('click', function() {
        // Reset form
        saleForm.reset();
        document.getElementById('modalTitle').textContent = 'Add New Sale';
        document.getElementById('saleId').value = '';
        
        // Set current date as default
        const today = new Date().toISOString().split('T')[0];
        document.getElementById('orderDate').value = today;
        
        // Open modal
        openModal(saleModal);
    });
    
    // Close modal events
    closeModals.forEach(closeBtn => {
        closeBtn.addEventListener('click', closeAllModals);
    });
    
    cancelBtns.forEach(btn => {
        btn.addEventListener('click', closeAllModals);
    });
    
    // Close modal when clicking outside
    window.addEventListener('click', function(event) {
        if (event.target === saleModal) {
            closeAllModals();
        }
        if (event.target === confirmationModal) {
            closeAllModals();
        }
    });
    
    // Edit sale
    editBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const row = this.closest('tr');
            const cells = row.cells;
            
            // Get values from table row
            const id = cells[0].textContent;
            const orderItemId = cells[1].textContent;
            const paymentType = cells[2].textContent;
            const orderDate = cells[3].textContent;
            
            // Extract numeric values, removing "$" and "," 
            const productPrice = parseFloat(cells[4].textContent.replace('$', '').replace(/,/g, ''));
            const discountRate = parseFloat(cells[5].textContent.replace('%', ''));
            const quantity = parseInt(cells[6].textContent);
            const profitRatio = parseFloat(cells[9].querySelector('.status').textContent === 'Profitable' ? 0.3 : -0.1);
            
            // Set modal title
            document.getElementById('modalTitle').textContent = 'Edit Sale';
            
            // Populate form
            document.getElementById('saleId').value = id;
            document.getElementById('orderItemId').value = orderItemId;
            document.getElementById('paymentType').value = paymentType;
            document.getElementById('orderDate').value = orderDate;
            document.getElementById('productPrice').value = productPrice;
            document.getElementById('discountRate').value = discountRate;
            document.getElementById('quantity').value = quantity;
            document.getElementById('profitRatio').value = profitRatio;
            
            // Open modal
            openModal(saleModal);
        });
    });
    
    // Delete sale
    deleteBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const row = this.closest('tr');
            const id = row.cells[0].textContent;
            currentSaleId = id;
            
            // Open confirmation modal
            openModal(confirmationModal);
        });
    });
    
    // Confirm delete
    if (deleteConfirmBtn) {
        deleteConfirmBtn.addEventListener('click', function() {
            if (currentSaleId) {
                // In a real app, send AJAX request to delete the sale
                console.log(`Sale with ID ${currentSaleId} deleted`);
                
                // Find and remove the row from the table
                const rows = document.querySelectorAll('.sale-row');
                for (let row of rows) {
                    if (row.cells[0].textContent === currentSaleId) {
                        row.style.animation = 'fadeOut 0.3s';
                        setTimeout(() => {
                            row.remove();
                            updateStats();
                        }, 300);
                        break;
                    }
                }
                
                // Close modal
                closeAllModals();
            }
        });
    }
    
    // Save sale (add or update)
    saleForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const id = document.getElementById('saleId').value;
        const orderItemId = document.getElementById('orderItemId').value;
        const paymentType = document.getElementById('paymentType').value;
        const orderDate = document.getElementById('orderDate').value;
        const productPrice = parseFloat(document.getElementById('productPrice').value);
        const discountRate = parseFloat(document.getElementById('discountRate').value);
        const quantity = parseInt(document.getElementById('quantity').value);
        const profitRatio = parseFloat(document.getElementById('profitRatio').value);
        
        // Calculate derived values
        const total = productPrice * quantity * (1 - discountRate / 100);
        const profit = total * profitRatio;
        const isProfit = profit > 0;
        
        console.log('Sale data:', {
            id, orderItemId, paymentType, orderDate, productPrice, 
            discountRate, quantity, profitRatio, total, profit
        });
        
        if (id) {
            // Update existing sale in the table
            const rows = document.querySelectorAll('.sale-row');
            for (let row of rows) {
                if (row.cells[0].textContent === id) {
                    // Update row data
                    row.cells[1].textContent = orderItemId;
                    row.cells[2].textContent = paymentType;
                    row.cells[3].textContent = orderDate;
                    row.cells[4].textContent = '$' + productPrice.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
                    row.cells[5].textContent = discountRate.toFixed(1) + '%';
                    row.cells[6].textContent = quantity;
                    row.cells[7].textContent = '$' + total.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
                    row.cells[8].textContent = '$' + profit.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
                    
                    // Update status
                    const statusSpan = row.cells[9].querySelector('.status');
                    statusSpan.textContent = isProfit ? 'Profitable' : 'Loss';
                    statusSpan.className = 'status ' + (isProfit ? 'profitable' : 'loss');
                    
                    // Update row data attribute
                    row.setAttribute('data-type', paymentType);
                    
                    // Highlight row to indicate update
                    row.style.animation = 'none';
                    setTimeout(() => {
                        row.style.animation = 'slideUp 0.5s';
                        row.style.backgroundColor = 'rgba(67, 97, 238, 0.1)';
                        setTimeout(() => {
                            row.style.backgroundColor = '';
                        }, 2000);
                    }, 10);
                    
                    break;
                }
            }
        } else {
            // Add new sale to the table
            const tbody = document.getElementById('salesTableBody');
            const newId = new Date().getTime().toString().slice(-8); // Generate a temporary ID
            
            const newRow = document.createElement('tr');
            newRow.className = 'sale-row';
            newRow.setAttribute('data-type', paymentType);
            newRow.style.animation = 'slideUp 0.5s';
            
            newRow.innerHTML = `
                <td>${newId}</td>
                <td>${orderItemId}</td>
                <td>${paymentType}</td>
                <td>${orderDate}</td>
                <td>$${productPrice.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
                <td>${discountRate.toFixed(1)}%</td>
                <td>${quantity}</td>
                <td>$${total.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
                <td>$${profit.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
                <td><span class="status ${isProfit ? 'profitable' : 'loss'}">${isProfit ? 'Profitable' : 'Loss'}</span></td>
                <td>
                    <button class="action-btn edit"><i class="fas fa-edit"></i></button>
                    <button class="action-btn delete"><i class="fas fa-trash"></i></button>
                </td>
            `;
            
            tbody.appendChild(newRow);
            
            // Add event listeners to new buttons
            const newEditBtn = newRow.querySelector('.action-btn.edit');
            const newDeleteBtn = newRow.querySelector('.action-btn.delete');
            
            newEditBtn.addEventListener('click', function() {
                // Reuse the edit logic from above
                const cells = newRow.cells;
                document.getElementById('modalTitle').textContent = 'Edit Sale';
                document.getElementById('saleId').value = newId;
                document.getElementById('orderItemId').value = orderItemId;
                document.getElementById('paymentType').value = paymentType;
                document.getElementById('orderDate').value = orderDate;
                document.getElementById('productPrice').value = productPrice;
                document.getElementById('discountRate').value = discountRate;
                document.getElementById('quantity').value = quantity;
                document.getElementById('profitRatio').value = profitRatio;
                openModal(saleModal);
            });
            
            newDeleteBtn.addEventListener('click', function() {
                currentSaleId = newId;
                openModal(confirmationModal);
            });
        }
        
        // Update stats
        updateStats();
        
        // Close modal
        closeAllModals();
    });

    // Run initial filtering
    filterSales();

    // Add keyframe animation for fadeOut if not present
    if (!document.querySelector('style#fadeOut-animation')) {
        const style = document.createElement('style');
        style.id = 'fadeOut-animation';
        style.innerHTML = `
            @keyframes fadeOut {
                from { opacity: 1; }
                to { opacity: 0; }
            }
        `;
        document.head.appendChild(style);
    }
});
