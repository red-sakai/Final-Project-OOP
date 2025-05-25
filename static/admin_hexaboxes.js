document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const searchInput = document.getElementById('searchInput');
    const sizeFilter = document.getElementById('sizeFilter');
    const statusFilter = document.getElementById('statusFilter');
    const tabs = document.querySelectorAll('.tab');
    const packageRows = document.querySelectorAll('.package-row');
    const addPackageBtn = document.querySelector('.add-package-btn');
    const packageModal = document.getElementById('packageModal');
    const confirmationModal = document.getElementById('confirmationModal');
    const closeModal = document.querySelector('.close-modal');
    const packageForm = document.getElementById('packageForm');
    const cancelBtns = document.querySelectorAll('.cancel-btn');
    const editBtns = document.querySelectorAll('.action-btn.edit');
    const deleteBtns = document.querySelectorAll('.action-btn.delete');
    const deleteConfirmBtn = document.querySelector('.delete-confirm-btn');
    
    let currentPackageId = null;
    const packageData = []; // Assuming packageData is defined elsewhere or fetched dynamically

    // Tab functionality
    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            // Remove active class from all tabs
            tabs.forEach(t => t.classList.remove('active'));
            
            // Add active class to clicked tab
            this.classList.add('active');
            
            const status = this.getAttribute('data-status');
            
            // Filter table rows based on status
            filterPackages();
        });
    });
    
    // Filter functionality
    function filterPackages() {
        const searchTerm = searchInput.value.toLowerCase();
        const status = document.querySelector('.tab.active').getAttribute('data-status');
        const sizeValue = sizeFilter.value;
        const statusValue = statusFilter.value;
        
        packageRows.forEach(row => {
            const rowStatus = row.getAttribute('data-status');
            const rowSize = row.cells[5].textContent.trim();
            let textContent = '';
            
            // Collect text content from all cells except the last one (actions)
            for (let i = 0; i < row.cells.length - 1; i++) {
                textContent += row.cells[i].textContent + ' ';
            }
            
            textContent = textContent.toLowerCase();
            
            // Check if row matches all filter criteria
            const matchesSearch = textContent.includes(searchTerm);
            const matchesStatus = status === 'all' || rowStatus === status;
            const matchesSize = sizeValue === 'all' || rowSize === sizeValue;
            const matchesStatusFilter = statusValue === 'all' || rowStatus === statusValue;
            
            if (matchesSearch && matchesStatus && matchesSize && matchesStatusFilter) {
                row.style.display = '';
                
                // Add animation for appearing rows
                row.style.animation = 'fadeIn 0.3s';
            } else {
                row.style.display = 'none';
            }
        });
        
        // Update stats
        updateStats();
    }
    
    // Attach event listeners to filters
    searchInput.addEventListener('input', filterPackages);
    sizeFilter.addEventListener('change', filterPackages);
    statusFilter.addEventListener('change', filterPackages);
    
    // Modal functionality
    function openModal(modal) {
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden'; // Prevent scrolling
    }
    
    function closeAllModals() {
        packageModal.style.display = 'none';
        confirmationModal.style.display = 'none';
        document.body.style.overflow = ''; // Enable scrolling
    }
    
    // Add new package
    addPackageBtn.addEventListener('click', function() {
        // Reset form
        packageForm.reset();
        document.getElementById('modalTitle').textContent = 'Add New Package';
        document.getElementById('trackingId').value = generateTrackingId();
        document.getElementById('trackingId').readOnly = false;
        
        // Set default dates to today and today+3 days
        const today = new Date();
        const eta = new Date();
        eta.setDate(today.getDate() + 3);
        
        document.getElementById('dateShipped').value = today.toISOString().split('T')[0];
        document.getElementById('eta').value = eta.toISOString().split('T')[0];
        
        // Open modal
        openModal(packageModal);
    });
    
    // Generate random tracking ID
    function generateTrackingId() {
        const prefix = 'HX-';
        const numbers = Math.floor(10000000 + Math.random() * 90000000);
        return prefix + numbers;
    }
    
    // Close modal events
    closeModal.addEventListener('click', closeAllModals);
    
    cancelBtns.forEach(btn => {
        btn.addEventListener('click', closeAllModals);
    });
    
    // Close modal when clicking outside
    window.addEventListener('click', function(event) {
        if (event.target === packageModal) {
            closeAllModals();
        }
        if (event.target === confirmationModal) {
            closeAllModals();
        }
    });
    
    // Edit package
    editBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const row = this.closest('tr');
            const cells = row.cells;
            
            // Get values from table row
            const displayTrackingId = cells[0].textContent;
            
            // Find the original tracking ID from packageData
            const packageInfo = packageData.find(p => p.tracking_id === displayTrackingId);
            const originalTrackingId = packageInfo ? packageInfo.original_tracking_id : displayTrackingId;
            
            const sender = cells[1].textContent;
            const recipient = cells[2].textContent;
            const origin = cells[3].textContent;
            const destination = cells[4].textContent;
            const size = cells[5].textContent;
            const weight = cells[6].textContent;
            const dateShipped = cells[7].textContent;
            const eta = cells[8].textContent;
            const vehicle = cells[9].textContent;
            const status = row.getAttribute('data-status');
            
            // Set modal title
            document.getElementById('modalTitle').textContent = 'Edit Package';
            
            // Populate form
            document.getElementById('trackingId').value = originalTrackingId;
            document.getElementById('trackingId').readOnly = true; // Can't edit tracking ID
            document.getElementById('sender').value = sender;
            document.getElementById('recipient').value = recipient;
            document.getElementById('origin').value = origin;
            document.getElementById('destination').value = destination;
            document.getElementById('size').value = size;
            document.getElementById('weight').value = weight;
            
            // Format dates if needed
            try {
                // Try to parse and format the date if it's not already in YYYY-MM-DD format
                const shipDateParts = dateShipped.split('-');
                if (shipDateParts.length === 3) {
                    document.getElementById('dateShipped').value = dateShipped;
                }
            } catch (e) {
                // Default to today if parsing fails
                const today = new Date();
                document.getElementById('dateShipped').value = today.toISOString().split('T')[0];
            }
            
            try {
                // Try to parse and format the ETA date
                const etaDateParts = eta.split('-');
                if (etaDateParts.length === 3) {
                    document.getElementById('eta').value = eta;
                }
            } catch (e) {
                // Default to today+3 if parsing fails
                const etaDate = new Date();
                etaDate.setDate(etaDate.getDate() + 3);
                document.getElementById('eta').value = etaDate.toISOString().split('T')[0];
            }
            
            // Handle assigned vehicle
            document.getElementById('assignedVehicleText').value = vehicle;
            document.getElementById('status').value = status;
            
            // Change form action to update instead of add
            packageForm.action = '/update_package';
            
            // Open modal
            openModal(packageModal);
        });
    });
    
    // Delete package
    deleteBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const id = this.getAttribute('data-id');
            
            // Find the original tracking ID
            const packageInfo = packageData.find(p => p.tracking_id === id);
            const originalTrackingId = packageInfo ? packageInfo.original_tracking_id : id;
            
            document.getElementById('deleteTrackingId').value = originalTrackingId;
            currentPackageId = id;
            
            // Open confirmation modal
            openModal(confirmationModal);
        });
    });
    
    // Confirm delete
    deleteConfirmBtn.addEventListener('click', function() {
        if (currentPackageId) {
            // Find and remove the row from the table
            const rowToDelete = document.querySelector(`tr td:first-child:contains('${currentPackageId}')`).closest('tr');
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
    
    // Save package (add or update)
    packageForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Get selected vehicle option text
        const vehicleSelect = document.getElementById('assignedVehicle');
        const selectedIndex = vehicleSelect.selectedIndex;
        
        // Set the text value in the hidden field
        if (selectedIndex > 0) {
            document.getElementById('assignedVehicleText').value = vehicleSelect.options[selectedIndex].text;
        } else {
            document.getElementById('assignedVehicleText').value = 'Not Assigned';
        }
        
        const trackingId = document.getElementById('trackingId').value;
        const sender = document.getElementById('sender').value;
        const recipient = document.getElementById('recipient').value;
        const origin = document.getElementById('origin').value;
        const destination = document.getElementById('destination').value;
        const size = document.getElementById('size').value;
        const weight = document.getElementById('weight').value;
        const dateShipped = document.getElementById('dateShipped').value;
        const eta = document.getElementById('eta').value;
        const assignedVehicleId = document.getElementById('assignedVehicle').value;
        const status = document.getElementById('status').value;
        
        // Get vehicle text
        let assignedVehicleText = 'Not Assigned';
        if (assignedVehicleId) {
            const vehicleOption = document.getElementById('assignedVehicle').options[document.getElementById('assignedVehicle').selectedIndex];
            assignedVehicleText = vehicleOption.text;
        }
        
        // Check if we're editing or adding
        const isEditing = document.getElementById('trackingId').readOnly;
        
        if (isEditing) {
            // Update existing package in the table
            const row = document.querySelector(`tr td:first-child:contains('${trackingId}')`).closest('tr');
            if (row) {
                row.cells[1].textContent = sender;
                row.cells[2].textContent = recipient;
                row.cells[3].textContent = origin;
                row.cells[4].textContent = destination;
                row.cells[5].textContent = size;
                row.cells[6].textContent = weight;
                row.cells[7].textContent = dateShipped;
                row.cells[8].textContent = eta;
                row.cells[9].textContent = assignedVehicleText;
                
                // Update status
                row.setAttribute('data-status', status);
                const statusSpan = row.cells[10].querySelector('.status');
                statusSpan.textContent = status;
                statusSpan.className = 'status';
                statusSpan.classList.add(status.toLowerCase().replace(' ', '-'));
                
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
            // Add new package to the table
            const tbody = document.querySelector('#packagesTableBody');
            
            const newRow = document.createElement('tr');
            newRow.className = 'package-row';
            newRow.setAttribute('data-status', status);
            newRow.style.animation = 'slideUp 0.5s';
            
            newRow.innerHTML = `
                <td>${trackingId}</td>
                <td>${sender}</td>
                <td>${recipient}</td>
                <td>${origin}</td>
                <td>${destination}</td>
                <td>${size}</td>
                <td>${weight}</td>
                <td>${dateShipped}</td>
                <td>${eta}</td>
                <td>${assignedVehicleText}</td>
                <td><span class="status ${status.toLowerCase().replace(' ', '-')}">${status}</span></td>
                <td>
                    <button class="action-btn edit" data-id="${trackingId}"><i class="fas fa-edit"></i></button>
                    <button class="action-btn delete" data-id="${trackingId}"><i class="fas fa-trash"></i></button>
                </td>
            `;
            
            tbody.appendChild(newRow);
            
            // Add event listeners to new buttons
            const newEditBtn = newRow.querySelector('.action-btn.edit');
            const newDeleteBtn = newRow.querySelector('.action-btn.delete');
            
            newEditBtn.addEventListener('click', function() {
                // Reuse existing editBtns click handler logic
                const row = this.closest('tr');
                const cells = row.cells;
                // ...rest of edit logic
            });
            
            newDeleteBtn.addEventListener('click', function() {
                currentPackageId = trackingId;
                openModal(confirmationModal);
            });
        }
        
        // Update stats
        updateStats();
        
        // Close modal
        closeAllModals();
    });
    
    // Update stats based on visible rows
    function updateStats() {
        const totalCount = document.querySelectorAll('tr.package-row:not([style*="display: none"])').length;
        const pendingCount = document.querySelectorAll('tr.package-row[data-status="Pending"]:not([style*="display: none"])').length;
        const inTransitCount = document.querySelectorAll('tr.package-row[data-status="In Transit"]:not([style*="display: none"])').length;
        const deliveredCount = document.querySelectorAll('tr.package-row[data-status="Delivered"]:not([style*="display: none"])').length;
        
        document.querySelector('.stat-card:nth-child(1) .count').textContent = totalCount;
        document.querySelector('.stat-card:nth-child(2) .count').textContent = inTransitCount;
        document.querySelector('.stat-card:nth-child(3) .count').textContent = deliveredCount;
        document.querySelector('.stat-card:nth-child(4) .count').textContent = pendingCount;
    }
    
    // Helper function for finding elements by text content
    Element.prototype.contains = function(text) {
        return this.textContent.includes(text);
    };
    
    // Initial filter and stats update
    filterPackages();
    updateStats();
});
