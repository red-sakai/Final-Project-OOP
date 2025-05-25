document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const searchInput = document.getElementById('searchInput');
    const segmentFilter = document.getElementById('segmentFilter');
    const cityFilter = document.getElementById('cityFilter');
    const tabs = document.querySelectorAll('.tab');
    const customerRows = document.querySelectorAll('.customer-row');
    const addCustomerBtn = document.querySelector('.add-customer-btn');
    const customerModal = document.getElementById('customerModal');
    const confirmationModal = document.getElementById('confirmationModal');
    const closeModals = document.querySelectorAll('.close-modal');
    const customerForm = document.getElementById('customerForm');
    const cancelBtns = document.querySelectorAll('.cancel-btn');
    const editBtns = document.querySelectorAll('.action-btn.edit');
    const deleteBtns = document.querySelectorAll('.action-btn.delete');
    const deleteConfirmBtn = document.querySelector('.delete-confirm-btn');
    
    let currentCustomerId = null;

    // Tab functionality
    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            // Remove active class from all tabs
            tabs.forEach(t => t.classList.remove('active'));
            
            // Add active class to clicked tab
            this.classList.add('active');
            
            // Filter table rows based on segment
            filterCustomers();
        });
    });
    
    // Filter functionality
    function filterCustomers() {
        const searchTerm = searchInput.value.toLowerCase();
        const segment = document.querySelector('.tab.active').getAttribute('data-segment');
        const cityValue = cityFilter.value;
        
        customerRows.forEach(row => {
            const rowSegment = row.getAttribute('data-segment');
            const rowCity = row.cells[2].textContent;
            let textContent = '';
            
            // Collect text content from all cells except the last one (actions)
            for (let i = 0; i < row.cells.length - 1; i++) {
                textContent += row.cells[i].textContent + ' ';
            }
            
            textContent = textContent.toLowerCase();
            
            // Check if row matches all filter criteria
            const matchesSearch = textContent.includes(searchTerm);
            const matchesSegment = segment === 'all' || rowSegment === segment;
            const matchesCity = cityValue === 'all' || rowCity === cityValue;
            
            if (matchesSearch && matchesSegment && matchesCity) {
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
        const visibleRows = document.querySelectorAll('.customer-row:not([style*="display: none"])');
        const total = visibleRows.length;
        
        // Count by segment
        let corporate = 0;
        let consumer = 0;
        let homeOffice = 0;
        
        // Count by city
        const cityCounts = {};
        
        visibleRows.forEach(row => {
            const segment = row.getAttribute('data-segment');
            const city = row.cells[2].textContent;
            
            if (segment === 'Corporate') corporate++;
            else if (segment === 'Consumer') consumer++;
            else if (segment === 'Home Office') homeOffice++;
            
            cityCounts[city] = (cityCounts[city] || 0) + 1;
        });
        
        // Find top city
        let topCity = '';
        let maxCount = 0;
        
        for (const city in cityCounts) {
            if (cityCounts[city] > maxCount) {
                maxCount = cityCounts[city];
                topCity = city;
            }
        }
        
        // Update stats in UI
        document.querySelector('.stat-card:nth-child(1) .count').textContent = total;
        document.querySelector('.stat-card:nth-child(2) .count').textContent = corporate;
        document.querySelector('.stat-card:nth-child(3) .count').textContent = consumer;
        document.querySelector('.stat-card:nth-child(4) .count').textContent = topCity || 'N/A';
    }
    
    // Attach event listeners to filters
    searchInput.addEventListener('input', filterCustomers);
    segmentFilter.addEventListener('change', filterCustomers);
    cityFilter.addEventListener('change', filterCustomers);
    
    // Modal functionality
    function openModal(modal) {
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden'; // Prevent scrolling
    }
    
    function closeAllModals() {
        customerModal.style.display = 'none';
        confirmationModal.style.display = 'none';
        document.body.style.overflow = ''; // Enable scrolling
    }
    
    // Add new customer
    addCustomerBtn.addEventListener('click', function() {
        // Reset form
        customerForm.reset();
        document.getElementById('modalTitle').textContent = 'Add New Customer';
        document.getElementById('customerId').value = '';
        
        // Set default country
        document.getElementById('country').value = 'Philippines';
        
        // Open modal
        openModal(customerModal);
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
        if (event.target === customerModal) {
            closeAllModals();
        }
        if (event.target === confirmationModal) {
            closeAllModals();
        }
    });
    
    // Edit customer
    editBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const row = this.closest('tr');
            const cells = row.cells;
            
            // Get values from table row
            const id = cells[0].textContent;
            const fullName = cells[1].textContent.trim();
            const nameParts = fullName.split(' ');
            const firstName = nameParts.shift(); // First element
            const lastName = nameParts.join(' '); // Rest joined back together
            const city = cells[2].textContent;
            const country = cells[3].textContent;
            const segment = cells[4].querySelector('.segment').textContent;
            const orderItemId = cells[5].textContent;
            
            // Set modal title
            document.getElementById('modalTitle').textContent = 'Edit Customer';
            
            // Populate form
            document.getElementById('customerId').value = id;
            document.getElementById('firstName').value = firstName;
            document.getElementById('lastName').value = lastName;
            document.getElementById('city').value = city;
            document.getElementById('country').value = country;
            document.getElementById('segment').value = segment;
            document.getElementById('orderItemId').value = orderItemId;
            
            // Open modal
            openModal(customerModal);
        });
    });
    
    // Delete customer
    deleteBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const row = this.closest('tr');
            const id = row.cells[0].textContent;
            currentCustomerId = id;
            document.getElementById('deleteCustomerId').value = id;
            
            // Open confirmation modal
            openModal(confirmationModal);
        });
    });
    
    // Confirm delete
    if (deleteConfirmBtn) {
        deleteConfirmBtn.addEventListener('click', function() {
            if (currentCustomerId) {
                // In a real app, this would be handled by the form submit
                // We're providing this for demonstration
                console.log(`Customer with ID ${currentCustomerId} deleted`);
                
                // Find and remove the row from the table
                const rows = document.querySelectorAll('.customer-row');
                for (let row of rows) {
                    if (row.cells[0].textContent === currentCustomerId) {
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
    
    // Save customer (add or update)
    customerForm.addEventListener('submit', function(e) {
        // In a real application, this form will be submitted to the server
        // For demonstration, we'll prevent the default and handle it in JS
        e.preventDefault();
        
        const id = document.getElementById('customerId').value;
        const firstName = document.getElementById('firstName').value;
        const lastName = document.getElementById('lastName').value;
        const city = document.getElementById('city').value;
        const country = document.getElementById('country').value;
        const segment = document.getElementById('segment').value;
        const orderItemId = document.getElementById('orderItemId').value;
        
        // Log the data that would be sent to the server
        console.log('Customer data:', {
            id, firstName, lastName, city, country, segment, orderItemId
        });
        
        if (id) {
            // Update existing customer in the table
            const rows = document.querySelectorAll('.customer-row');
            for (let row of rows) {
                if (row.cells[0].textContent === id) {
                    // Update row data
                    row.cells[1].textContent = `${firstName} ${lastName}`;
                    row.cells[2].textContent = city;
                    row.cells[3].textContent = country;
                    
                    const segmentSpan = row.cells[4].querySelector('.segment');
                    segmentSpan.textContent = segment;
                    segmentSpan.className = `segment ${segment.toLowerCase().replace(' ', '-')}`;
                    
                    row.cells[5].textContent = orderItemId;
                    
                    // Update row data attribute
                    row.setAttribute('data-segment', segment);
                    
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
            // Add new customer to the table
            const tbody = document.getElementById('customersTableBody');
            const newId = new Date().getTime().toString().slice(-8); // Generate a temporary ID
            
            const newRow = document.createElement('tr');
            newRow.className = 'customer-row';
            newRow.setAttribute('data-segment', segment);
            newRow.style.animation = 'slideUp 0.5s';
            
            newRow.innerHTML = `
                <td>${newId}</td>
                <td>${firstName} ${lastName}</td>
                <td>${city}</td>
                <td>${country}</td>
                <td><span class="segment ${segment.toLowerCase().replace(' ', '-')}">${segment}</span></td>
                <td>${orderItemId}</td>
                <td>
                    <button class="action-btn edit" data-id="${newId}"><i class="fas fa-edit"></i></button>
                    <button class="action-btn delete" data-id="${newId}"><i class="fas fa-trash"></i></button>
                </td>
            `;
            
            tbody.appendChild(newRow);
            
            // Add event listeners to new buttons
            const newEditBtn = newRow.querySelector('.action-btn.edit');
            const newDeleteBtn = newRow.querySelector('.action-btn.delete');
            
            newEditBtn.addEventListener('click', function() {
                const cells = newRow.cells;
                document.getElementById('modalTitle').textContent = 'Edit Customer';
                
                const fullName = cells[1].textContent.trim();
                const nameParts = fullName.split(' ');
                const firstName = nameParts.shift();
                const lastName = nameParts.join(' ');
                
                document.getElementById('customerId').value = newId;
                document.getElementById('firstName').value = firstName;
                document.getElementById('lastName').value = lastName;
                document.getElementById('city').value = city;
                document.getElementById('country').value = country;
                document.getElementById('segment').value = segment;
                document.getElementById('orderItemId').value = orderItemId;
                
                openModal(customerModal);
            });
            
            newDeleteBtn.addEventListener('click', function() {
                currentCustomerId = newId;
                document.getElementById('deleteCustomerId').value = newId;
                openModal(confirmationModal);
            });
        }
        
        // Update stats
        updateStats();
        
        // Close modal
        closeAllModals();
    });
    
    // Initial filter
    filterCustomers();
    
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
