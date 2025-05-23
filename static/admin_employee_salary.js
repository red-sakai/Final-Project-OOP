document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const searchInput = document.getElementById('searchInput');
    const departmentFilter = document.getElementById('departmentFilter');
    const performanceFilter = document.getElementById('performanceFilter');
    const tabs = document.querySelectorAll('.tab');
    const salaryRows = document.querySelectorAll('.salary-row');
    const addSalaryBtn = document.querySelector('.add-salary-btn');
    const salaryModal = document.getElementById('salaryModal');
    const confirmationModal = document.getElementById('confirmationModal');
    const closeModal = document.querySelector('.close-modal');
    const salaryForm = document.getElementById('salaryForm');
    const cancelBtns = document.querySelectorAll('.cancel-btn');
    const editBtns = document.querySelectorAll('.action-btn.edit');
    const deleteBtns = document.querySelectorAll('.action-btn.delete');
    
    let currentEmployeeId = null;

    // Initialize Charts
    initCharts();

    // Tab functionality
    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            // Remove active class from all tabs
            tabs.forEach(t => t.classList.remove('active'));
            
            // Add active class to clicked tab
            this.classList.add('active');
            
            // Filter table rows based on category
            filterSalaries();
        });
    });
    
    // Filter functionality
    function filterSalaries() {
        const searchTerm = searchInput.value.toLowerCase();
        const department = document.querySelector('.tab.active').getAttribute('data-category');
        const performanceValue = performanceFilter.value;
        
        salaryRows.forEach(row => {
            const rowDepartment = row.getAttribute('data-department');
            const performanceStars = row.querySelector('.rating').querySelectorAll('.fa-star').length;
            let textContent = '';
            
            // Collect text content from all cells except the last one (actions)
            for (let i = 0; i < row.cells.length - 1; i++) {
                textContent += row.cells[i].textContent + ' ';
            }
            
            textContent = textContent.toLowerCase();
            
            // Check if row matches all filter criteria
            const matchesSearch = textContent.includes(searchTerm);
            const matchesDepartment = department === 'all' || rowDepartment === department;
            const matchesPerformance = performanceValue === 'all' || parseInt(performanceValue) === performanceStars;
            
            if (matchesSearch && matchesDepartment && matchesPerformance) {
                row.style.display = '';
                
                // Add animation for appearing rows
                row.style.animation = 'fadeIn 0.3s';
            } else {
                row.style.display = 'none';
            }
        });
    }
    
    // Attach event listeners to filters
    searchInput.addEventListener('input', filterSalaries);
    departmentFilter.addEventListener('change', filterSalaries);
    performanceFilter.addEventListener('change', filterSalaries);
    
    // Modal functionality
    function openModal(modal) {
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden'; // Prevent scrolling
    }
    
    function closeAllModals() {
        salaryModal.style.display = 'none';
        confirmationModal.style.display = 'none';
        document.body.style.overflow = ''; // Enable scrolling
    }
    
    // Add new salary record
    addSalaryBtn.addEventListener('click', function() {
        // Reset form
        salaryForm.reset();
        document.getElementById('modalTitle').textContent = 'Add New Salary Record';
        document.getElementById('employeeId').value = '';
        
        // Generate new employee ID
        const newEmployeeId = getNextEmployeeId();
        document.getElementById('employeeId').value = newEmployeeId;
        
        // Set today's date as default hire date
        const today = new Date();
        const formattedDate = `${today.getMonth() + 1}/${today.getDate()}/${today.getFullYear()}`;
        document.getElementById('hireDate').value = formattedDate;
        
        // Open modal
        openModal(salaryModal);
    });
    
    function getNextEmployeeId() {
        let maxId = 0;
        salaryRows.forEach(row => {
            const id = parseInt(row.cells[0].textContent);
            if (id > maxId) {
                maxId = id;
            }
        });
        return maxId + 1;
    }
    
    // Close modal events
    closeModal.addEventListener('click', closeAllModals);
    
    cancelBtns.forEach(btn => {
        btn.addEventListener('click', closeAllModals);
    });
    
    // Close modal when clicking outside
    window.addEventListener('click', function(event) {
        if (event.target === salaryModal) {
            closeAllModals();
        }
        if (event.target === confirmationModal) {
            closeAllModals();
        }
    });
    
    // Auto-calculate total compensation
    const salaryYearlyInput = document.getElementById('salaryYearly');
    const bonusAmountInput = document.getElementById('bonusAmount');
    const totalCompensationInput = document.getElementById('totalCompensation');
    
    function updateTotalCompensation() {
        const salaryYearly = parseFloat(salaryYearlyInput.value) || 0;
        const bonusAmount = parseFloat(bonusAmountInput.value) || 0;
        totalCompensationInput.value = (salaryYearly + bonusAmount).toFixed(2);
    }
    
    salaryYearlyInput.addEventListener('input', updateTotalCompensation);
    bonusAmountInput.addEventListener('input', updateTotalCompensation);
    
    // Auto-calculate monthly salary
    const salaryMonthlyInput = document.getElementById('salaryMonthly');
    
    salaryYearlyInput.addEventListener('input', function() {
        const salaryYearly = parseFloat(salaryYearlyInput.value) || 0;
        salaryMonthlyInput.value = (salaryYearly / 12).toFixed(2);
    });
    
    // Edit salary record
    editBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const row = this.closest('tr');
            const employeeId = row.cells[0].textContent;
            
            // Find the salary data
            const salary = salaryData.find(s => s.employee_id.toString() === employeeId);
            
            if (salary) {
                // Set modal title
                document.getElementById('modalTitle').textContent = 'Edit Salary Record';
                
                // Populate form
                document.getElementById('employeeId').value = salary.employee_id;
                document.getElementById('jobTitle').value = salary.job_title;
                document.getElementById('department').value = salary.department || '';
                document.getElementById('salaryYearly').value = salary.salary_yearly;
                document.getElementById('salaryMonthly').value = salary.salary_monthly;
                document.getElementById('hireDate').value = salary.hire_date;
                document.getElementById('yearsExperience').value = salary.years_of_experience;
                document.getElementById('yearsCompany').value = salary.years_of_experience_company;
                document.getElementById('performanceRating').value = salary.performance_rating;
                document.getElementById('bonusAmount').value = salary.bonus_amount;
                document.getElementById('totalCompensation').value = salary.total_compensation;
                
                // Update form action
                salaryForm.action = `${salaryForm.action.replace('/add', '')}/update`;
                
                // Open modal
                openModal(salaryModal);
            }
        });
    });
    
    // Delete salary record
    deleteBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const row = this.closest('tr');
            const employeeId = row.cells[0].textContent;
            currentEmployeeId = employeeId;
            
            // Set hidden input value
            document.getElementById('deleteEmployeeId').value = employeeId;
            
            // Open confirmation modal
            openModal(confirmationModal);
        });
    });
    
    // Initialize charts
    function initCharts() {
        // Department Chart
        const deptCtx = document.getElementById('departmentChart').getContext('2d');
        const deptLabels = Object.keys(departmentStats);
        const deptSalaries = deptLabels.map(dept => departmentStats[dept].avg_salary);
        
        const departmentChart = new Chart(deptCtx, {
            type: 'bar',
            data: {
                labels: deptLabels,
                datasets: [{
                    label: 'Average Salary',
                    data: deptSalaries,
                    backgroundColor: 'rgba(67, 97, 238, 0.7)',
                    borderColor: 'rgba(67, 97, 238, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '₱' + value.toLocaleString();
                            }
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return '₱' + context.parsed.y.toLocaleString();
                            }
                        }
                    }
                }
            }
        });
        
        // Performance Chart
        const perfCtx = document.getElementById('performanceChart').getContext('2d');
        const perfLabels = Object.keys(performanceStats).map(rating => '★'.repeat(rating));
        const perfBonuses = Object.keys(performanceStats).map(rating => performanceStats[rating].avg_bonus);
        
        const performanceChart = new Chart(perfCtx, {
            type: 'bar',
            data: {
                labels: perfLabels,
                datasets: [{
                    label: 'Average Bonus',
                    data: perfBonuses,
                    backgroundColor: 'rgba(76, 175, 80, 0.7)',
                    borderColor: 'rgba(76, 175, 80, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '₱' + value.toLocaleString();
                            }
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return '₱' + context.parsed.y.toLocaleString();
                            }
                        }
                    }
                }
            }
        });
    }
    
    // Initial filter
    filterSalaries();
});
