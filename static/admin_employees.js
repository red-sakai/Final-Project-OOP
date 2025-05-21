document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const searchInput = document.getElementById('searchInput');
    const departmentFilter = document.getElementById('departmentFilter');
    const roleFilter = document.getElementById('roleFilter');
    const tabs = document.querySelectorAll('.tab');
    const employeeRows = document.querySelectorAll('.employee-row');
    const addEmployeeBtn = document.querySelector('.add-employee-btn');
    const employeeModal = document.getElementById('employeeModal');
    const confirmationModal = document.getElementById('confirmationModal');
    const closeModal = document.querySelector('.close-modal');
    const employeeForm = document.getElementById('employeeForm');
    const cancelBtns = document.querySelectorAll('.cancel-btn');
    const editBtns = document.querySelectorAll('.action-btn.edit');
    const deleteBtns = document.querySelectorAll('.action-btn.delete');
    const deleteConfirmBtn = document.querySelector('.delete-confirm-btn');
    const roleSelect = document.getElementById('role');
    const driverFields = document.querySelectorAll('.driver-field');
    
    let currentEmployeeId = null;

    // Handle driver-specific fields visibility
    function toggleDriverFields() {
        const isDriver = roleSelect.value === 'Driver';
        driverFields.forEach(field => {
            field.style.display = isDriver ? 'block' : 'none';
        });
    }
    
    // Listen for role changes
    if (roleSelect) {
        roleSelect.addEventListener('change', toggleDriverFields);
        // Initial toggle
        toggleDriverFields();
    }

    // Tab functionality
    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            // Remove active class from all tabs
            tabs.forEach(t => t.classList.remove('active'));
            
            // Add active class to clicked tab
            this.classList.add('active');
            
            const role = this.getAttribute('data-role');
            
            // Filter table rows based on role
            filterEmployees();
        });
    });
    
    // Filter functionality
    function filterEmployees() {
        const searchTerm = searchInput.value.toLowerCase();
        const role = document.querySelector('.tab.active').getAttribute('data-role');
        const departmentValue = departmentFilter.value;
        const roleValue = roleFilter.value;
        
        employeeRows.forEach(row => {
            const rowRole = row.getAttribute('data-role');
            const rowDepartment = row.cells[4].textContent.toLowerCase();
            const rowRoleText = row.cells[5].textContent.toLowerCase();
            let textContent = '';
            
            // Collect text content from all cells except the last one (actions)
            for (let i = 0; i < row.cells.length - 1; i++) {
                textContent += row.cells[i].textContent + ' ';
            }
            
            textContent = textContent.toLowerCase();
            
            // Check if row matches all filter criteria
            const matchesSearch = textContent.includes(searchTerm);
            const matchesRole = role === 'all' || rowRole === role;
            const matchesDepartment = departmentValue === 'all' || rowDepartment === departmentValue.toLowerCase();
            const matchesRoleFilter = roleValue === 'all' || rowRoleText === roleValue.toLowerCase();
            
            if (matchesSearch && matchesRole && matchesDepartment && matchesRoleFilter) {
                row.style.display = '';
                
                // Add animation for appearing rows
                row.style.animation = 'fadeIn 0.3s';
            } else {
                row.style.display = 'none';
            }
        });
    }
    
    // Attach event listeners to filters
    searchInput.addEventListener('input', filterEmployees);
    departmentFilter.addEventListener('change', filterEmployees);
    roleFilter.addEventListener('change', filterEmployees);
    
    // Modal functionality
    function openModal(modal) {
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden'; // Prevent scrolling
    }
    
    function closeAllModals() {
        employeeModal.style.display = 'none';
        confirmationModal.style.display = 'none';
        document.body.style.overflow = ''; // Enable scrolling
    }
    
    // Add new employee
    addEmployeeBtn.addEventListener('click', function() {
        // Reset form
        employeeForm.reset();
        document.getElementById('modalTitle').textContent = 'Add New Employee';
        document.getElementById('employeeId').value = '';
        
        // Set default date to today
        const today = new Date().toISOString().split('T')[0];
        document.getElementById('hireDate').value = today;
        
        // Toggle driver fields based on selected role
        toggleDriverFields();
        
        // Open modal
        openModal(employeeModal);
    });
    
    // Close modal events
    closeModal.addEventListener('click', closeAllModals);
    
    cancelBtns.forEach(btn => {
        btn.addEventListener('click', closeAllModals);
    });
    
    // Close modal when clicking outside
    window.addEventListener('click', function(event) {
        if (event.target === employeeModal) {
            closeAllModals();
        }
        if (event.target === confirmationModal) {
            closeAllModals();
        }
    });
    
    // Edit employee
    editBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const row = this.closest('tr');
            const id = this.getAttribute('data-id');
            
            // Find employee data from stored JSON
            const employee = employeeData.find(emp => emp.id.toString() === id);
            
            if (employee) {
                // Set modal title
                document.getElementById('modalTitle').textContent = 'Edit Employee';
                
                // Populate form
                document.getElementById('employeeId').value = employee.id;
                document.getElementById('firstName').value = employee.first_name;
                document.getElementById('lastName').value = employee.last_name;
                document.getElementById('email').value = employee.email;
                document.getElementById('phone').value = employee.phone_number;
                document.getElementById('department').value = employee.department;
                document.getElementById('role').value = employee.role;
                document.getElementById('hireDate').value = employee.hire_date;
                document.getElementById('status').value = employee.status;
                
                // Driver-specific fields
                if (employee.license_number) {
                    document.getElementById('licenseNumber').value = employee.license_number;
                }
                if (employee.license_expiry) {
                    document.getElementById('licenseExpiry').value = employee.license_expiry;
                }
                if (employee.assigned_vehicle) {
                    document.getElementById('assignedVehicle').value = employee.assigned_vehicle;
                }
                
                // Toggle driver fields
                toggleDriverFields();
                
                // Open modal
                openModal(employeeModal);
            }
        });
    });
    
    // Delete employee
    deleteBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const id = this.getAttribute('data-id');
            currentEmployeeId = id;
            
            // Set the hidden input for the delete form
            document.getElementById('deleteEmployeeId').value = id;
            
            // Open confirmation modal
            openModal(confirmationModal);
        });
    });
    
    // Update stats
    function updateStats() {
        const totalCount = document.querySelectorAll('tr.employee-row:not([style*="display: none"])').length;
        const managerCount = document.querySelectorAll('tr.employee-row[data-role="Manager"]:not([style*="display: none"])').length;
        const driverCount = document.querySelectorAll('tr.employee-row[data-role="Driver"]:not([style*="display: none"])').length;
        const activeCount = document.querySelectorAll('tr.employee-row .status.active').length;
        
        document.querySelector('.stat-card:nth-child(1) .count').textContent = totalCount;
        document.querySelector('.stat-card:nth-child(2) .count').textContent = managerCount;
        document.querySelector('.stat-card:nth-child(3) .count').textContent = driverCount;
        document.querySelector('.stat-card:nth-child(4) .count').textContent = activeCount;
    }
    
    // Initial filter
    filterEmployees();
});
