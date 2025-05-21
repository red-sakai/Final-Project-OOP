document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const searchInput = document.getElementById('searchInput');
    const categoryFilter = document.getElementById('categoryFilter');
    const statusFilter = document.getElementById('statusFilter');
    const tabs = document.querySelectorAll('.tab');
    const vehicleRows = document.querySelectorAll('.vehicle-row');
    const addVehicleBtn = document.querySelector('.add-vehicle-btn');
    const vehicleModal = document.getElementById('vehicleModal');
    const confirmationModal = document.getElementById('confirmationModal');
    const closeModal = document.querySelector('.close-modal');
    const vehicleForm = document.getElementById('vehicleForm');
    const cancelBtns = document.querySelectorAll('.cancel-btn');
    const editBtns = document.querySelectorAll('.action-btn.edit');
    const deleteBtns = document.querySelectorAll('.action-btn.delete');
    const deleteConfirmBtn = document.querySelector('.delete-confirm-btn');
    
    let currentVehicleId = null;

    // Tab functionality
    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            // Remove active class from all tabs
            tabs.forEach(t => t.classList.remove('active'));
            
            // Add active class to clicked tab
            this.classList.add('active');
            
            const category = this.getAttribute('data-category');
            
            // Filter table rows based on category
            filterVehicles();
        });
    });
    
    // Filter functionality
    function filterVehicles() {
        const searchTerm = searchInput.value.toLowerCase();
        const category = document.querySelector('.tab.active').getAttribute('data-category');
        const statusValue = statusFilter.value;
        
        vehicleRows.forEach(row => {
            const rowCategory = row.getAttribute('data-category');
            const rowStatus = row.querySelector('.status').textContent.toLowerCase();
            let textContent = '';
            
            // Collect text content from all cells except the last one (actions)
            for (let i = 0; i < row.cells.length - 1; i++) {
                textContent += row.cells[i].textContent + ' ';
            }
            
            textContent = textContent.toLowerCase();
            
            // Check if row matches all filter criteria
            const matchesSearch = textContent.includes(searchTerm);
            const matchesCategory = category === 'all' || rowCategory === category;
            const matchesStatus = statusValue === 'all' || rowStatus === statusValue.toLowerCase();
            
            if (matchesSearch && matchesCategory && matchesStatus) {
                row.style.display = '';
                
                // Add animation for appearing rows
                row.style.animation = 'fadeIn 0.3s';
            } else {
                row.style.display = 'none';
            }
        });
    }
    
    // Attach event listeners to filters
    searchInput.addEventListener('input', filterVehicles);
    categoryFilter.addEventListener('change', filterVehicles);
    statusFilter.addEventListener('change', filterVehicles);
    
    // Modal functionality
    function openModal(modal) {
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden'; // Prevent scrolling
    }
    
    function closeAllModals() {
        vehicleModal.style.display = 'none';
        confirmationModal.style.display = 'none';
        document.body.style.overflow = ''; // Enable scrolling
    }
    
    // Add new vehicle
    addVehicleBtn.addEventListener('click', function() {
        // Reset form
        vehicleForm.reset();
        document.getElementById('modalTitle').textContent = 'Add New Vehicle';
        document.getElementById('vehicleId').value = '';
        
        // Open modal
        openModal(vehicleModal);
    });
    
    // Close modal events
    closeModal.addEventListener('click', closeAllModals);
    
    cancelBtns.forEach(btn => {
        btn.addEventListener('click', closeAllModals);
    });
    
    // Close modal when clicking outside
    window.addEventListener('click', function(event) {
        if (event.target === vehicleModal) {
            closeAllModals();
        }
        if (event.target === confirmationModal) {
            closeAllModals();
        }
    });
    
    // Edit vehicle
    editBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const row = this.closest('tr');
            const cells = row.cells;
            
            // Get values from table row
            const id = cells[0].textContent;
            const brand = cells[1].textContent;
            const model = cells[2].textContent;
            const type = cells[3].textContent;
            const distance = parseInt(cells[4].textContent);
            const driverId = cells[5].textContent !== '-' ? cells[5].textContent : '';
            const licenseExpiry = cells[6].textContent !== '-' ? cells[6].textContent : '';
            const orderId = cells[7].textContent !== '-' ? cells[7].textContent : '';
            const maxWeight = parseInt(cells[8].textContent);
            const status = cells[9].querySelector('.status').textContent;
            
            // Set modal title
            document.getElementById('modalTitle').textContent = 'Edit Vehicle';
            
            // Populate form
            document.getElementById('vehicleId').value = id;
            document.getElementById('brand').value = brand;
            document.getElementById('model').value = model;
            document.getElementById('type').value = type;
            document.getElementById('distance').value = distance || 0;
            document.getElementById('driverId').value = driverId;
            document.getElementById('maxWeight').value = maxWeight || 0;
            document.getElementById('status').value = status;
            
            // Get category from row data attribute
            const category = row.getAttribute('data-category');
            document.getElementById('category').value = category;
            
            // Open modal
            openModal(vehicleModal);
        });
    });
    
    // Delete vehicle
    deleteBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const row = this.closest('tr');
            const id = row.cells[0].textContent;
            currentVehicleId = id;
            
            // Open confirmation modal
            openModal(confirmationModal);
        });
    });
    
    // Confirm delete
    deleteConfirmBtn.addEventListener('click', function() {
        if (currentVehicleId) {
            // In a real app, send AJAX request to delete the vehicle
            console.log(`Vehicle with ID ${currentVehicleId} deleted`);
            
            // Find and remove the row from the table
            const rowToDelete = document.querySelector(`tr td:first-child:contains('${currentVehicleId}')`).closest('tr');
            if (rowToDelete) {
                rowToDelete.style.animation = 'fadeOut 0.3s';
                setTimeout(() => {
                    rowToDelete.remove();
                    updateStats();
                }, 300);
            }
            
            // Close modal
            closeAllModals();
        }
    });
    
    // Save vehicle (add or update)
    vehicleForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const id = document.getElementById('vehicleId').value;
        const brand = document.getElementById('brand').value;
        const model = document.getElementById('model').value;
        const category = document.getElementById('category').value;
        const type = document.getElementById('type').value;
        const distance = document.getElementById('distance').value;
        const driverId = document.getElementById('driverId').value;
        const licenseExpiry = document.getElementById('licenseExpiry').value;
        const orderId = document.getElementById('orderId').value;
        const maxWeight = document.getElementById('maxWeight').value;
        const minWeight = document.getElementById('minWeight').value;
        const status = document.getElementById('status').value;
        
        // In a real app, send AJAX request to save the data
        console.log('Vehicle data:', {
            id, brand, model, category, type, distance, driverId, 
            licenseExpiry, orderId, maxWeight, minWeight, status
        });
        
        if (id) {
            console.log(`Updating vehicle with ID ${id}`);
            // Update existing vehicle in the table
            const row = document.querySelector(`tr td:first-child:contains('${id}')`).closest('tr');
            if (row) {
                row.cells[1].textContent = brand;
                row.cells[2].textContent = model;
                row.cells[3].textContent = type;
                row.cells[4].textContent = `${distance} km`;
                row.cells[5].textContent = driverId || '-';
                row.cells[6].textContent = licenseExpiry || '-';
                row.cells[7].textContent = orderId || '-';
                row.cells[8].textContent = `${maxWeight} kg`;
                
                const statusSpan = row.cells[9].querySelector('.status');
                statusSpan.textContent = status;
                statusSpan.className = 'status';
                
                if (status === 'Available') {
                    statusSpan.classList.add('available');
                } else if (status === 'In Use') {
                    statusSpan.classList.add('in-use');
                } else if (status === 'Maintenance') {
                    statusSpan.classList.add('maintenance');
                }
                
                // Update row data attribute
                row.setAttribute('data-category', category);
                
                // Highlight row to indicate update
                row.style.animation = 'none';
                setTimeout(() => {
                    row.style.animation = 'slideUp 0.5s';
                    row.style.backgroundColor = 'rgba(67, 97, 238, 0.1)';
                    setTimeout(() => {
                        row.style.backgroundColor = '';
                    }, 2000);
                }, 10);
            }
        } else {
            console.log('Adding new vehicle');
            // Add new vehicle to the table
            const tbody = document.getElementById('vehiclesTableBody');
            const newId = tbody.children.length + 1;
            
            const newRow = document.createElement('tr');
            newRow.className = 'vehicle-row';
            newRow.setAttribute('data-category', category);
            newRow.style.animation = 'slideUp 0.5s';
            
            newRow.innerHTML = `
                <td>${newId}</td>
                <td>${brand}</td>
                <td>${model}</td>
                <td>${type}</td>
                <td>${distance} km</td>
                <td>${driverId || '-'}</td>
                <td>${licenseExpiry || '-'}</td>
                <td>${orderId || '-'}</td>
                <td>${maxWeight} kg</td>
                <td><span class="status ${status.toLowerCase().replace(' ', '-')}">${status}</span></td>
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
                // Same as edit logic above
            });
            
            newDeleteBtn.addEventListener('click', function() {
                currentVehicleId = newId;
                openModal(confirmationModal);
            });
        }
        
        // Update stats
        updateStats();
        
        // Close modal
        closeAllModals();
    });
    
    // Update stats
    function updateStats() {
        const motorcycles = document.querySelectorAll('tr[data-category="Motorcycle"]:not([style*="display: none"])').length;
        const cars = document.querySelectorAll('tr[data-category="Car"]:not([style*="display: none"])').length;
        const trucks = document.querySelectorAll('tr[data-category="Truck"]:not([style*="display: none"])').length;
        const available = document.querySelectorAll('.status.available').length;
        
        document.querySelector('.stat-card:nth-child(1) .count').textContent = motorcycles;
        document.querySelector('.stat-card:nth-child(2) .count').textContent = cars;
        document.querySelector('.stat-card:nth-child(3) .count').textContent = trucks;
        document.querySelector('.stat-card:nth-child(4) .count').textContent = available;
    }
    
    // Helper function for finding elements by text content
    Element.prototype.contains = function(text) {
        return this.textContent.includes(text);
    };
    
    // Initial filter
    filterVehicles();
});
