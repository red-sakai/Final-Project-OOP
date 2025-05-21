document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const vehiclesContainer = document.getElementById('vehicles-container');
    const vehicleModal = document.getElementById('vehicle-modal');
    const vehicleDetailsModal = document.getElementById('vehicle-details-modal');
    const deleteConfirmationModal = document.getElementById('delete-confirmation-modal');
    const vehicleForm = document.getElementById('vehicle-form');
    const addVehicleBtn = document.getElementById('add-vehicle-btn');
    const vehicleSearch = document.getElementById('vehicle-search');
    const filterBtns = document.querySelectorAll('.filter-btn');
    const closeModalBtns = document.querySelectorAll('.close-modal');
    const cancelBtn = document.getElementById('cancel-btn');
    const deleteVehicleBtn = document.getElementById('delete-vehicle-btn');
    const cancelDeleteBtn = document.getElementById('cancel-delete-btn');
    const confirmDeleteBtn = document.getElementById('confirm-delete-btn');
    const prevPageBtn = document.getElementById('prev-page');
    const nextPageBtn = document.getElementById('next-page');
    const currentPageSpan = document.getElementById('current-page');
    const totalPagesSpan = document.getElementById('total-pages');

    // State Management
    let vehicles = [];
    let filteredVehicles = [];
    let currentVehicle = null;
    let currentFilter = {
        category: 'all',
        status: null
    };
    let currentPage = 1;
    let vehiclesPerPage = 6; // Vehicles per page for pagination
    
    // Vehicle Types Metadata - For easy access to available models by type
    const vehicleTypes = {
        motorcycle: {
            brands: ['Honda', 'Yamaha'],
            models: {
                'Honda': ['Click 125i'],
                'Yamaha': ['Mio Sporty', 'NMAX']
            },
            minWeight: 0,
            maxWeight: {
                'Click 125i': 150,
                'Mio Sporty': 130,
                'NMAX': 160
            }
        },
        car: {
            brands: ['Toyota', 'Honda', 'MG'],
            models: {
                'Toyota': ['Vios'],
                'Honda': ['Civic'],
                'MG': ['5']
            },
            minWeight: 150,
            maxWeight: {
                'Vios': 500,
                'Civic': 480,
                '5': 450
            }
        },
        truck: {
            brands: ['Isuzu', 'Fuso', 'Hino'],
            models: {
                'Isuzu': ['4 Wheeler'],
                'Fuso': ['6 Wheeler'],
                'Hino': ['10 Wheeler']
            },
            minWeight: {
                '4 Wheeler': 500,
                '6 Wheeler': 2000,
                '10 Wheeler': 4000
            },
            maxWeight: {
                '4 Wheeler': 2000,
                '6 Wheeler': 4000,
                '10 Wheeler': 8000
            }
        }
    };

    // Initialize
    fetchVehicles();

    // Event Listeners
    addVehicleBtn.addEventListener('click', showAddVehicleModal);
    vehicleForm.addEventListener('submit', handleFormSubmit);
    vehicleSearch.addEventListener('input', handleSearch);
    
    // Add event listeners for close buttons, filter buttons, etc.
    closeModalBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const modal = this.closest('.modal');
            hideModal(modal);
        });
    });
    
    cancelBtn.addEventListener('click', () => {
        hideModal(vehicleModal);
    });
    
    deleteVehicleBtn.addEventListener('click', () => {
        hideModal(vehicleDetailsModal);
        showModal(deleteConfirmationModal);
    });
    
    cancelDeleteBtn.addEventListener('click', () => {
        hideModal(deleteConfirmationModal);
    });
    
    confirmDeleteBtn.addEventListener('click', () => {
        deleteVehicle(currentVehicle.id);
    });
    
    // Filter buttons
    filterBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            if (btn.dataset.category) {
                document.querySelectorAll('.filter-btn[data-category]').forEach(b => 
                    b.classList.remove('active'));
                currentFilter.category = btn.dataset.category;
            } else if (btn.dataset.status) {
                document.querySelectorAll('.filter-btn[data-status]').forEach(b => 
                    b.classList.remove('active'));
                currentFilter.status = btn.dataset.status;
            }
            
            this.classList.add('active');
            currentPage = 1;
            applyFilters();
        });
    });
    
    // Pagination buttons
    prevPageBtn.addEventListener('click', goToPreviousPage);
    nextPageBtn.addEventListener('click', goToNextPage);

    // Vehicle type dropdown - populate brand and model dropdowns
    document.getElementById('unit-type').addEventListener('change', updateBrandModelOptions);
    document.getElementById('unit-brand').addEventListener('change', updateModelOptions);
    document.getElementById('unit-model').addEventListener('change', updateWeightDefaults);

    // Core Functions
    async function fetchVehicles() {
        showLoading();
        
        try {
            const response = await fetch('/api/vehicles');
            
            if (!response.ok) {
                throw new Error('Failed to fetch vehicles');
            }
            
            vehicles = await response.json();
            filteredVehicles = [...vehicles];
            
            renderVehicles();
            updatePagination();
        } catch (error) {
            console.error('Error fetching vehicles:', error);
            showError('Failed to load vehicles data. Please try again later.');
        }
    }
    
    function renderVehicles() {
        // Calculate pagination
        const startIndex = (currentPage - 1) * vehiclesPerPage;
        const endIndex = startIndex + vehiclesPerPage;
        const paginatedVehicles = filteredVehicles.slice(startIndex, endIndex);
        
        // Check if no vehicles after filtering
        if (filteredVehicles.length === 0) {
            showNoResults();
            return;
        }
        
        // Clear container and add vehicle cards
        vehiclesContainer.innerHTML = '';
        
        paginatedVehicles.forEach(vehicle => {
            const card = createVehicleCard(vehicle);
            vehiclesContainer.appendChild(card);
            
            // Add animations for staggered appearance
            setTimeout(() => {
                card.classList.add('visible');
            }, 50 * vehiclesContainer.children.length);
        });
        
        // Add event listeners for card buttons
        addCardEventListeners();
    }
    
    function createVehicleCard(vehicle) {
        const template = document.getElementById('vehicle-card-template');
        const card = document.importNode(template.content.cloneNode(true).querySelector('.vehicle-card'));
        
        // Set card data attributes
        card.setAttribute('data-id', vehicle.id);
        card.setAttribute('data-type', vehicle.unit_type);
        
        // Set vehicle details in the card
        card.querySelector('.vehicle-name').textContent = `${vehicle.unit_brand} ${vehicle.unit_model}`;
        card.querySelector('.brand').textContent = vehicle.unit_brand;
        card.querySelector('.model').textContent = vehicle.unit_model;
        card.querySelector('.distance').textContent = vehicle.distance.toLocaleString();
        card.querySelector('.max-weight').textContent = vehicle.max_weight.toLocaleString();
        
        // Set status with appropriate class
        const statusElem = card.querySelector('.vehicle-status');
        statusElem.textContent = formatStatus(vehicle.status);
        statusElem.classList.add(vehicle.status);
        
        return card;
    }
    
    function addCardEventListeners() {
        // View details button
        document.querySelectorAll('.view-details').forEach(btn => {
            btn.addEventListener('click', function() {
                const vehicleId = parseInt(this.closest('.vehicle-card').dataset.id);
                showVehicleDetails(vehicleId);
            });
        });
        
        // Edit button
        document.querySelectorAll('.edit-btn').forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                const vehicleId = parseInt(this.closest('.vehicle-card').dataset.id);
                showEditVehicleModal(vehicleId);
            });
        });
        
        // Delete button
        document.querySelectorAll('.delete-btn').forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                const vehicleId = parseInt(this.closest('.vehicle-card').dataset.id);
                const vehicle = vehicles.find(v => v.id === vehicleId);
                currentVehicle = vehicle;
                showModal(deleteConfirmationModal);
            });
        });
    }
    
    function showVehicleDetails(vehicleId) {
        const vehicle = vehicles.find(v => v.id === vehicleId);
        if (!vehicle) return;
        
        currentVehicle = vehicle;
        
        const detailsContainer = document.getElementById('vehicle-details');
        
        detailsContainer.innerHTML = `
            <div class="detail-section">
                <h3>Vehicle Information</h3>
                <div class="detail-row">
                    <div class="detail-label">Category</div>
                    <div class="detail-value">${formatVehicleType(vehicle.unit_type)}</div>
                </div>
                <div class="detail-row">
                    <div class="detail-label">Brand</div>
                    <div class="detail-value">${vehicle.unit_brand}</div>
                </div>
                <div class="detail-row">
                    <div class="detail-label">Model</div>
                    <div class="detail-value">${vehicle.unit_model}</div>
                </div>
                <div class="detail-row">
                    <div class="detail-label">Status</div>
                    <div class="detail-value">
                        <span class="status-badge ${vehicle.status}">${formatStatus(vehicle.status)}</span>
                    </div>
                </div>
                <div class="detail-row">
                    <div class="detail-label">Distance</div>
                    <div class="detail-value">${vehicle.distance.toLocaleString()} km</div>
                </div>
            </div>
            
            <div class="detail-section">
                <h3>Weight Capacity</h3>
                <div class="detail-row">
                    <div class="detail-label">Minimum Weight</div>
                    <div class="detail-value">${vehicle.min_weight.toLocaleString()} kg</div>
                </div>
                <div class="detail-row">
                    <div class="detail-label">Maximum Weight</div>
                    <div class="detail-value">${vehicle.max_weight.toLocaleString()} kg</div>
                </div>
            </div>
            
            <div class="detail-section">
                <h3>Driver Information</h3>
                <div class="detail-row">
                    <div class="detail-label">Driver ID</div>
                    <div class="detail-value">${vehicle.driver_id || 'Not assigned'}</div>
                </div>
                <div class="detail-row">
                    <div class="detail-label">License Expiry</div>
                    <div class="detail-value">${formatDate(vehicle.license_expiry)}</div>
                </div>
            </div>
            
            <div class="detail-section">
                <h3>Current Assignment</h3>
                <div class="detail-row">
                    <div class="detail-label">Order ID</div>
                    <div class="detail-value">${vehicle.order_id || 'No active order'}</div>
                </div>
            </div>
        `;
        
        // Setup edit button in details modal
        document.querySelector('#vehicle-details-modal .edit-vehicle-btn').addEventListener('click', function() {
            hideModal(vehicleDetailsModal);
            showEditVehicleModal(vehicle.id);
        });
        
        showModal(vehicleDetailsModal);
    }
    
    function showAddVehicleModal() {
        // Reset form
        vehicleForm.reset();
        document.getElementById('vehicle-id').value = '';
        document.getElementById('modal-title').textContent = 'Add New Vehicle';
        
        // Clear any previous error messages
        clearFormErrors();
        
        // Show modal
        showModal(vehicleModal);
    }
    
    function showEditVehicleModal(vehicleId) {
        const vehicle = vehicles.find(v => v.id === vehicleId);
        if (!vehicle) return;
        
        // Set form values
        document.getElementById('vehicle-id').value = vehicle.id;
        document.getElementById('unit-type').value = vehicle.unit_type;
        document.getElementById('unit-brand').value = vehicle.unit_brand;
        document.getElementById('unit-model').value = vehicle.unit_model;
        document.getElementById('distance').value = vehicle.distance;
        document.getElementById('driver-id').value = vehicle.driver_id || '';
        document.getElementById('license-expiry').value = formatDateForInput(vehicle.license_expiry);
        document.getElementById('order-id').value = vehicle.order_id || '';
        document.getElementById('min-weight').value = vehicle.min_weight;
        document.getElementById('max-weight').value = vehicle.max_weight;
        document.getElementById('status').value = vehicle.status;
        
        // Update title
        document.getElementById('modal-title').textContent = 'Edit Vehicle';
        
        // Clear any previous error messages
        clearFormErrors();
        
        // Update brand/model dropdowns
        updateBrandModelOptions();
        
        // Show modal
        showModal(vehicleModal);
    }
    
    function updateBrandModelOptions() {
        const unitType = document.getElementById('unit-type').value;
        const brandSelect = document.getElementById('unit-brand');
        
        // If no type selected or editing existing vehicle, no need to change anything
        if (!unitType) {
            return;
        }
        
        // Get the current value to preserve it if possible
        const currentBrand = brandSelect.value;
        
        // Get brands for this vehicle type
        const availableBrands = vehicleTypes[unitType]?.brands || [];
        
        // Update the brand field with datalist
        if (!document.getElementById('brand-list')) {
            const datalist = document.createElement('datalist');
            datalist.id = 'brand-list';
            document.body.appendChild(datalist);
            brandSelect.setAttribute('list', 'brand-list');
        }
        
        // Update datalist options
        const brandList = document.getElementById('brand-list');
        brandList.innerHTML = '';
        availableBrands.forEach(brand => {
            const option = document.createElement('option');
            option.value = brand;
            brandList.appendChild(option);
        });
        
        // After updating brands, update models
        updateModelOptions();
    }
    
    function updateModelOptions() {
        const unitType = document.getElementById('unit-type').value;
        const brandInput = document.getElementById('unit-brand').value;
        const modelInput = document.getElementById('unit-model');
        
        // If no type or brand selected, clear models
        if (!unitType || !brandInput) {
            return;
        }
        
        // Get models for this brand and type
        const availableModels = vehicleTypes[unitType]?.models[brandInput] || [];
        
        // Update the model field with datalist
        if (!document.getElementById('model-list')) {
            const datalist = document.createElement('datalist');
            datalist.id = 'model-list';
            document.body.appendChild(datalist);
            modelInput.setAttribute('list', 'model-list');
        }
        
        // Update datalist options
        const modelList = document.getElementById('model-list');
        modelList.innerHTML = '';
        availableModels.forEach(model => {
            const option = document.createElement('option');
            option.value = model;
            modelList.appendChild(option);
        });
        
        // After updating models, update weight defaults
        updateWeightDefaults();
    }
    
    function updateWeightDefaults() {
        const unitType = document.getElementById('unit-type').value;
        const brandInput = document.getElementById('unit-brand').value;
        const modelInput = document.getElementById('unit-model').value;
        
        // If no type, brand, or model selected, do nothing
        if (!unitType || !brandInput || !modelInput) {
            return;
        }
        
        // Get the min weight for this vehicle type
        let minWeight = 0;
        if (vehicleTypes[unitType]?.minWeight) {
            if (typeof vehicleTypes[unitType].minWeight === 'object') {
                minWeight = vehicleTypes[unitType].minWeight[modelInput] || 0;
            } else {
                minWeight = vehicleTypes[unitType].minWeight;
            }
        }
        
        // Get the max weight for this vehicle
        let maxWeight = 0;
        if (vehicleTypes[unitType]?.maxWeight) {
            if (typeof vehicleTypes[unitType].maxWeight === 'object') {
                maxWeight = vehicleTypes[unitType].maxWeight[modelInput] || 0;
            } else {
                maxWeight = vehicleTypes[unitType].maxWeight;
            }
        }
        
        // Only set if we're not editing an existing vehicle (id is empty)
        if (!document.getElementById('vehicle-id').value) {
            document.getElementById('min-weight').value = minWeight;
            document.getElementById('max-weight').value = maxWeight;
        }
    }
    
    async function handleFormSubmit(e) {
        e.preventDefault();
        
        // Get form data
        const vehicleId = document.getElementById('vehicle-id').value;
        const formData = {
            unit_type: document.getElementById('unit-type').value,
            unit_brand: document.getElementById('unit-brand').value,
            unit_model: document.getElementById('unit-model').value,
            distance: parseInt(document.getElementById('distance').value) || 0,
            driver_id: document.getElementById('driver-id').value || null,
            license_expiry: document.getElementById('license-expiry').value || null,
            order_id: document.getElementById('order-id').value || null,
            min_weight: parseInt(document.getElementById('min-weight').value) || 0,
            max_weight: parseInt(document.getElementById('max-weight').value) || 0,
            status: document.getElementById('status').value
        };
        
        try {
            let response;
            
            if (vehicleId) {
                // Update existing vehicle
                response = await fetch(`/api/vehicles/${vehicleId}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(formData)
                });
            } else {
                // Create new vehicle
                response = await fetch('/api/vehicles', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(formData)
                });
            }
            
            if (!response.ok) {
                throw new Error(`Failed to ${vehicleId ? 'update' : 'create'} vehicle`);
            }
            
            const updatedVehicle = await response.json();
            
            if (vehicleId) {
                // Update in local array
                const index = vehicles.findIndex(v => v.id == vehicleId);
                if (index !== -1) {
                    vehicles[index] = updatedVehicle;
                }
                
                showToast(`Vehicle ${formData.unit_brand} ${formData.unit_model} updated successfully`, 'success');
            } else {
                // Add to local array
                vehicles.push(updatedVehicle);
                
                showToast(`New vehicle ${formData.unit_brand} ${formData.unit_model} added successfully`, 'success');
            }
            
            // Close modal and refresh display
            hideModal(vehicleModal);
            applyFilters(); // Re-filter with the current filters
            updatePagination();
            
        } catch (error) {
            console.error('Error saving vehicle:', error);
            showToast(`Failed to ${vehicleId ? 'update' : 'add'} vehicle. Please try again.`, 'error');
        }
    }
    
    async function deleteVehicle(vehicleId) {
        try {
            const response = await fetch(`/api/vehicles/${vehicleId}`, {
                method: 'DELETE'
            });
            
            if (!response.ok) {
                throw new Error('Failed to delete vehicle');
            }
            
            // Remove from local array
            vehicles = vehicles.filter(v => v.id !== vehicleId);
            filteredVehicles = filteredVehicles.filter(v => v.id !== vehicleId);
            
            // Close modals
            hideModal(deleteConfirmationModal);
            hideModal(vehicleDetailsModal);
            
            // Show success message
            showToast('Vehicle deleted successfully', 'success');
            
            // Refresh display
            updatePagination();
            renderVehicles();
            
        } catch (error) {
            console.error('Error deleting vehicle:', error);
            hideModal(deleteConfirmationModal);
            showToast('Failed to delete vehicle. Please try again.', 'error');
        }
    }
    
    function handleSearch() {
        const searchTerm = vehicleSearch.value.toLowerCase();
        currentPage = 1; // Reset to first page
        applyFilters(searchTerm);
    }
    
    function applyFilters(searchTerm = null) {
        const searchQuery = searchTerm !== null ? searchTerm : vehicleSearch.value.toLowerCase();
        
        filteredVehicles = vehicles.filter(vehicle => {
            // Apply category filter
            if (currentFilter.category !== 'all' && vehicle.unit_type !== currentFilter.category) {
                return false;
            }
            
            // Apply status filter
            if (currentFilter.status && vehicle.status !== currentFilter.status) {
                return false;
            }
            
            // Apply search filter if there's a search term
            if (searchQuery) {
                const matchesBrand = vehicle.unit_brand.toLowerCase().includes(searchQuery);
                const matchesModel = vehicle.unit_model.toLowerCase().includes(searchQuery);
                const matchesType = vehicle.unit_type.toLowerCase().includes(searchQuery);
                const matchesStatus = vehicle.status.toLowerCase().includes(searchQuery);
                
                if (!(matchesBrand || matchesModel || matchesType || matchesStatus)) {
                    return false;
                }
            }
            
            return true;
        });
        
        updatePagination();
        renderVehicles();
    }
    
    function goToPreviousPage() {
        if (currentPage > 1) {
            currentPage--;
            renderVehicles();
            updatePagination();
        }
    }
    
    function goToNextPage() {
        const totalPages = Math.ceil(filteredVehicles.length / vehiclesPerPage) || 1;
        if (currentPage < totalPages) {
            currentPage++;
            renderVehicles();
            updatePagination();
        }
    }
    
    function updatePagination() {
        const totalPages = Math.ceil(filteredVehicles.length / vehiclesPerPage) || 1;
        
        currentPageSpan.textContent = currentPage;
        totalPagesSpan.textContent = totalPages;
        
        // Enable/disable buttons
        prevPageBtn.disabled = currentPage === 1;
        nextPageBtn.disabled = currentPage === totalPages;
    }
    
    // UI Helper Functions
    function showLoading() {
        vehiclesContainer.innerHTML = `
            <div class="loading-container">
                <div class="loading-spinner"></div>
                <p>Loading vehicles data...</p>
            </div>
        `;
    }
    
    function showError(message) {
        vehiclesContainer.innerHTML = `
            <div class="error-container">
                <i class="fas fa-exclamation-triangle"></i>
                <h3>Error Loading Data</h3>
                <p>${message}</p>
                <button class="primary-btn" onclick="location.reload()">
                    <i class="fas fa-sync"></i> Try Again
                </button>
            </div>
        `;
    }
    
    function showNoResults() {
        vehiclesContainer.innerHTML = `
            <div class="error-container">
                <i class="fas fa-search"></i>
                <h3>No Vehicles Found</h3>
                <p>No vehicles match your current search criteria.</p>
                <button class="primary-btn" onclick="resetFilters()">
                    <i class="fas fa-times"></i> Clear Filters
                </button>
            </div>
        `;
        
        // Add global resetFilters function
        window.resetFilters = function() {
            // Reset filter buttons
            document.querySelectorAll('.filter-btn[data-category]').forEach(btn => 
                btn.classList.remove('active'));
            document.querySelector('.filter-btn[data-category="all"]').classList.add('active');
            
            document.querySelectorAll('.filter-btn[data-status]').forEach(btn => 
                btn.classList.remove('active'));
            
            // Reset filter state
            currentFilter.category = 'all';
            currentFilter.status = null;
            
            // Clear search
            vehicleSearch.value = '';
            
            // Reset to page 1
            currentPage = 1;
            
            // Reapply filters (which will now show all)
            filteredVehicles = [...vehicles];
            updatePagination();
            renderVehicles();
        };
    }
    
    function showModal(modal) {
        modal.classList.add('show');
        document.body.style.overflow = 'hidden'; // Prevent scrolling while modal is open
    }
    
    function hideModal(modal) {
        modal.classList.remove('show');
        document.body.style.overflow = '';
    }
    
    function clearFormErrors() {
        // Remove any previous error messages
        const errorMessages = vehicleForm.querySelectorAll('.error-message');
        errorMessages.forEach(el => el.remove());
        
        // Remove error classes from inputs
        const inputs = vehicleForm.querySelectorAll('.error');
        inputs.forEach(input => input.classList.remove('error'));
    }
    
    function showToast(message, type = 'info') {
        // Create toast container if it doesn't exist
        let toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.className = 'toast-container';
            document.body.appendChild(toastContainer);
        }
        
        // Create toast element
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <div class="toast-content">
                <div class="toast-message">${message}</div>
            </div>
            <button class="toast-close">&times;</button>
        `;
        
        // Add close button functionality
        toast.querySelector('.toast-close').addEventListener('click', function() {
            toast.remove();
        });
        
        // Add to container
        toastContainer.appendChild(toast);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, 5000);
    }
    
    // Utility Functions
    function formatStatus(status) {
        switch (status) {
            case 'available': return 'Available';
            case 'in-use': return 'In Use';
            case 'maintenance': return 'Maintenance';
            default: return status.charAt(0).toUpperCase() + status.slice(1);
        }
    }
    
    function formatVehicleType(type) {
        switch (type) {
            case 'motorcycle': return 'Motorcycle';
            case 'car': return 'Car';
            case 'truck': return 'Truck';
            default: return type.charAt(0).toUpperCase() + type.slice(1);
        }
    }
    
    function formatDate(dateString) {
        if (!dateString) return 'Not set';
        
        const date = new Date(dateString);
        if (isNaN(date)) return 'Invalid date';
        
        return date.toLocaleDateString('en-US', { 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
        });
    }
    
    function formatDateForInput(dateString) {
        if (!dateString) return '';
        
        const date = new Date(dateString);
        if (isNaN(date)) return '';
        
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        
        return `${year}-${month}-${day}`;
    }
});
