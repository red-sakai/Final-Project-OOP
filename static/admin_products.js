document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const searchInput = document.getElementById('searchInput');
    const departmentFilter = document.getElementById('departmentFilter');
    const categoryFilter = document.getElementById('categoryFilter');
    const tabs = document.querySelectorAll('.tab');
    const productRows = document.querySelectorAll('.product-row');
    const addProductBtn = document.querySelector('.add-product-btn');
    const productModal = document.getElementById('productModal');
    const confirmationModal = document.getElementById('confirmationModal');
    const closeModal = document.querySelector('.close-modal');
    const productForm = document.getElementById('productForm');
    const cancelBtns = document.querySelectorAll('.cancel-btn');
    const editBtns = document.querySelectorAll('.action-btn.edit');
    const deleteBtns = document.querySelectorAll('.action-btn.delete');
    
    let currentProductId = null;

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
            filterProducts();
        });
    });
    
    // Filter functionality
    function filterProducts() {
        const searchTerm = searchInput.value.toLowerCase();
        const department = document.querySelector('.tab.active').getAttribute('data-category');
        const categoryValue = categoryFilter.value;
        
        productRows.forEach(row => {
            const rowDepartment = row.getAttribute('data-department');
            const rowCategory = row.cells[4].textContent;
            let textContent = '';
            
            // Collect text content from all cells except the last one (actions)
            for (let i = 0; i < row.cells.length - 1; i++) {
                textContent += row.cells[i].textContent + ' ';
            }
            
            textContent = textContent.toLowerCase();
            
            // Check if row matches all filter criteria
            const matchesSearch = textContent.includes(searchTerm);
            const matchesDepartment = department === 'all' || rowDepartment === department;
            const matchesCategory = categoryValue === 'all' || rowCategory === categoryValue;
            
            if (matchesSearch && matchesDepartment && matchesCategory) {
                row.style.display = '';
                
                // Add animation for appearing rows
                row.style.animation = 'fadeIn 0.3s';
            } else {
                row.style.display = 'none';
            }
        });
    }
    
    // Attach event listeners to filters
    searchInput.addEventListener('input', filterProducts);
    departmentFilter.addEventListener('change', filterProducts);
    categoryFilter.addEventListener('change', filterProducts);
    
    // Modal functionality
    function openModal(modal) {
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden'; // Prevent scrolling
    }
    
    function closeAllModals() {
        productModal.style.display = 'none';
        confirmationModal.style.display = 'none';
        document.body.style.overflow = ''; // Enable scrolling
    }
    
    // Add new product
    addProductBtn.addEventListener('click', function() {
        // Reset form
        productForm.reset();
        document.getElementById('modalTitle').textContent = 'Add New Product';
        document.getElementById('productId').value = '';
        
        // Open modal
        openModal(productModal);
    });
    
    // Close modal events
    closeModal.addEventListener('click', closeAllModals);
    
    cancelBtns.forEach(btn => {
        btn.addEventListener('click', closeAllModals);
    });
    
    // Close modal when clicking outside
    window.addEventListener('click', function(event) {
        if (event.target === productModal) {
            closeAllModals();
        }
        if (event.target === confirmationModal) {
            closeAllModals();
        }
    });
    
    // Edit product
    editBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const row = this.closest('tr');
            const productId = this.getAttribute('data-id');
            
            // Find the product data
            const product = productData.find(p => p.id.toString() === productId);
            
            if (product) {
                // Set modal title
                document.getElementById('modalTitle').textContent = 'Edit Product';
                
                // Populate form
                document.getElementById('productId').value = product.id;
                document.getElementById('productName').value = product.product_name;
                document.getElementById('orderItemId').value = product.order_item_id;
                document.getElementById('productCategoryId').value = product.product_category_id;
                document.getElementById('productCategoryName').value = product.product_category_name;
                document.getElementById('departmentId').value = product.department_id;
                document.getElementById('departmentName').value = product.department_name;
                
                // Update form action
                productForm.action = `${productForm.action.replace('/add', '')}/update`;
                
                // Open modal
                openModal(productModal);
            }
        });
    });
    
    // Delete product
    deleteBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const productId = this.getAttribute('data-id');
            currentProductId = productId;
            
            // Set hidden input value
            document.getElementById('deleteProductId').value = productId;
            
            // Open confirmation modal
            openModal(confirmationModal);
        });
    });
    
    // Initialize charts
    function initCharts() {
        // Department Chart
        const deptCtx = document.getElementById('departmentChart').getContext('2d');
        const deptLabels = Object.keys(departmentStats);
        const deptCounts = deptLabels.map(dept => departmentStats[dept].count);
        
        const departmentChart = new Chart(deptCtx, {
            type: 'bar',
            data: {
                labels: deptLabels,
                datasets: [{
                    label: 'Products Count',
                    data: deptCounts,
                    backgroundColor: 'rgba(67, 97, 238, 0.7)',
                    borderColor: 'rgba(67, 97, 238, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
        
        // Category Chart
        const catCtx = document.getElementById('categoryChart').getContext('2d');
        const catLabels = Object.keys(categoryStats).slice(0, 10); // Top 10 categories
        const catCounts = catLabels.map(cat => categoryStats[cat].count);
        
        const categoryChart = new Chart(catCtx, {
            type: 'pie',
            data: {
                labels: catLabels,
                datasets: [{
                    data: catCounts,
                    backgroundColor: [
                        'rgba(67, 97, 238, 0.7)',
                        'rgba(76, 175, 80, 0.7)',
                        'rgba(255, 152, 0, 0.7)',
                        'rgba(244, 67, 54, 0.7)',
                        'rgba(156, 39, 176, 0.7)',
                        'rgba(3, 169, 244, 0.7)',
                        'rgba(255, 87, 34, 0.7)',
                        'rgba(0, 150, 136, 0.7)',
                        'rgba(63, 81, 181, 0.7)',
                        'rgba(33, 150, 243, 0.7)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'right'
                    }
                }
            }
        });
    }
    
    // Initial filter
    filterProducts();
});
