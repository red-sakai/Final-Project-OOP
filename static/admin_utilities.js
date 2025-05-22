document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const searchInput = document.getElementById('searchInput');
    const timeRangeFilter = document.getElementById('timeRangeFilter');
    const dataTypeFilter = document.getElementById('dataTypeFilter');
    const chartTabs = document.querySelectorAll('.chart-tabs .tab');
    const tableTabs = document.querySelectorAll('.tables-tabs .tab');
    const chartWrappers = document.querySelectorAll('.chart-wrapper');
    const tableContainers = document.querySelectorAll('.data-table-container');
    const generateReportBtn = document.querySelector('.generate-report-btn');
    const reportModal = document.getElementById('reportModal');
    const closeModal = document.querySelector('.close-modal');
    const reportForm = document.getElementById('reportForm');
    const cancelBtn = document.querySelector('.cancel-btn');
    const reportTimeRange = document.getElementById('reportTimeRange');
    const dateRangeInputs = document.querySelectorAll('.date-range');
    
    // Chart instances
    let salesChart = null;
    let vehiclesChart = null;
    let employeesChart = null;
    let customersChart = null;
    
    // Check if initialChartData is defined (coming from the backend)
    const chartData = typeof initialChartData !== 'undefined' ? initialChartData : {
        sales: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            datasets: [
                {
                    label: 'Revenue',
                    data: [18500, 22300, 19800, 24500, 28700, 32600, 31200, 35800, 34500, 36700, 39200, 42800],
                    borderColor: '#4361ee',
                    backgroundColor: 'rgba(67, 97, 238, 0.1)',
                    tension: 0.3
                },
                {
                    label: 'Costs',
                    data: [12200, 14500, 13800, 16200, 19500, 21400, 20800, 23600, 22300, 23800, 25600, 27900],
                    borderColor: '#f44336',
                    backgroundColor: 'rgba(244, 67, 54, 0.1)',
                    tension: 0.3
                },
                {
                    label: 'Profit',
                    data: [6300, 7800, 6000, 8300, 9200, 11200, 10400, 12200, 12200, 12900, 13600, 14900],
                    borderColor: '#4caf50',
                    backgroundColor: 'rgba(76, 175, 80, 0.1)',
                    tension: 0.3
                }
            ]
        },
        vehicles: {
            labels: ['Available', 'In Use', 'Maintenance'],
            datasets: [
                {
                    data: [42, 28, 12],
                    backgroundColor: [
                        'rgba(76, 175, 80, 0.7)',
                        'rgba(255, 152, 0, 0.7)',
                        'rgba(244, 67, 54, 0.7)'
                    ],
                    borderColor: [
                        'rgba(76, 175, 80, 1)',
                        'rgba(255, 152, 0, 1)',
                        'rgba(244, 67, 54, 1)'
                    ],
                    borderWidth: 1
                }
            ]
        },
        employees: {
            labels: ['Drivers', 'Warehouse', 'Admin', 'Support', 'Management'],
            datasets: [
                {
                    label: 'Performance Score',
                    data: [85, 78, 92, 88, 82],
                    backgroundColor: 'rgba(67, 97, 238, 0.7)',
                    borderColor: 'rgba(67, 97, 238, 1)',
                    borderWidth: 1
                }
            ]
        },
        customers: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            datasets: [
                {
                    label: 'New Customers',
                    data: [22, 28, 34, 42, 38, 45, 52, 48, 56, 61, 58, 64],
                    borderColor: '#4361ee',
                    backgroundColor: 'rgba(67, 97, 238, 0.1)',
                    tension: 0.3
                },
                {
                    label: 'Repeat Customers',
                    data: [48, 52, 58, 63, 67, 72, 76, 82, 85, 91, 95, 102],
                    borderColor: '#4caf50',
                    backgroundColor: 'rgba(76, 175, 80, 0.1)',
                    tension: 0.3
                }
            ]
        }
    };
    
    // Initialize charts
    function initCharts() {
        const salesChartCtx = document.getElementById('salesChart').getContext('2d');
        salesChart = new Chart(salesChartCtx, {
            type: 'line',
            data: chartData.sales,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    title: {
                        display: true,
                        text: 'Monthly Sales Performance'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '$' + value.toLocaleString();
                            }
                        }
                    }
                }
            }
        });
        
        const vehiclesChartCtx = document.getElementById('vehiclesChart').getContext('2d');
        vehiclesChart = new Chart(vehiclesChartCtx, {
            type: 'pie',
            data: chartData.vehicles,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    title: {
                        display: true,
                        text: 'Vehicle Status Distribution'
                    }
                }
            }
        });
        
        const employeesChartCtx = document.getElementById('employeesChart').getContext('2d');
        employeesChart = new Chart(employeesChartCtx, {
            type: 'bar',
            data: chartData.employees,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    title: {
                        display: true,
                        text: 'Employee Performance by Department'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    }
                }
            }
        });
        
        const customersChartCtx = document.getElementById('customersChart').getContext('2d');
        customersChart = new Chart(customersChartCtx, {
            type: 'line',
            data: chartData.customers,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    title: {
                        display: true,
                        text: 'Customer Growth Over Time'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
    
    function filterData() {
        const timeRange = timeRangeFilter.value;
        const dataType = dataTypeFilter.value;
        
        document.querySelectorAll('.chart-container').forEach(container => {
            container.classList.add('loading');
        });
        
        if (dataType === 'all' || dataType === 'sales') {
            fetch(`/api/utilities/chart-data?type=sales&timeRange=${timeRange}`)
                .then(response => response.json())
                .then(data => {
                    salesChart.data.labels = data.labels;
                    salesChart.data.datasets = data.datasets;
                    salesChart.update();
                    document.querySelector('#salesChartWrapper .chart-container').classList.remove('loading');
                })
                .catch(error => {
                    console.error('Error fetching sales data:', error);
                    document.querySelector('#salesChartWrapper .chart-container').classList.remove('loading');
                    fallbackFilterData(timeRange, 'sales');
                });
        }
        
        if (dataType === 'all' || dataType === 'vehicles') {
            fetch(`/api/utilities/chart-data?type=vehicles&timeRange=${timeRange}`)
                .then(response => response.json())
                .then(data => {
                    vehiclesChart.data.labels = data.labels;
                    vehiclesChart.data.datasets = data.datasets;
                    vehiclesChart.update();
                    document.querySelector('#vehiclesChartWrapper .chart-container').classList.remove('loading');
                })
                .catch(error => {
                    console.error('Error fetching vehicles data:', error);
                    document.querySelector('#vehiclesChartWrapper .chart-container').classList.remove('loading');
                    fallbackFilterData(timeRange, 'vehicles');
                });
        }
        
        if (dataType === 'all' || dataType === 'employees') {
            fetch(`/api/utilities/chart-data?type=employees&timeRange=${timeRange}`)
                .then(response => response.json())
                .then(data => {
                    employeesChart.data.labels = data.labels;
                    employeesChart.data.datasets = data.datasets;
                    employeesChart.update();
                    document.querySelector('#employeesChartWrapper .chart-container').classList.remove('loading');
                })
                .catch(error => {
                    console.error('Error fetching employees data:', error);
                    document.querySelector('#employeesChartWrapper .chart-container').classList.remove('loading');
                    fallbackFilterData(timeRange, 'employees');
                });
        }
        
        if (dataType === 'all' || dataType === 'customers') {
            fetch(`/api/utilities/chart-data?type=customers&timeRange=${timeRange}`)
                .then(response => response.json())
                .then(data => {
                    customersChart.data.labels = data.labels;
                    customersChart.data.datasets = data.datasets;
                    customersChart.update();
                    document.querySelector('#customersChartWrapper .chart-container').classList.remove('loading');
                })
                .catch(error => {
                    console.error('Error fetching customers data:', error);
                    document.querySelector('#customersChartWrapper .chart-container').classList.remove('loading');
                    fallbackFilterData(timeRange, 'customers');
                });
        }
    }
    
    function fallbackFilterData(timeRange, chartType) {
        console.log(`Using fallback filtering for ${chartType} chart with time range ${timeRange}`);
        
        const multiplier = {
            'week': 0.8,
            'month': 1,
            'quarter': 1.2,
            'year': 1.5
        }[timeRange];
        
        if (chartType === 'sales') {
            salesChart.data.datasets.forEach(dataset => {
                dataset.data = dataset.data.map(value => Math.round(value * multiplier));
            });
            salesChart.update();
        } else if (chartType === 'vehicles') {
            vehiclesChart.data.datasets[0].data = vehiclesChart.data.datasets[0].data.map(value => 
                Math.round(value * (0.9 + Math.random() * 0.2)));
            vehiclesChart.update();
        } else if (chartType === 'employees') {
            employeesChart.data.datasets[0].data = employeesChart.data.datasets[0].data.map(value => 
                Math.min(100, Math.round(value * (0.95 + Math.random() * 0.1))));
            employeesChart.update();
        } else if (chartType === 'customers') {
            customersChart.data.datasets.forEach(dataset => {
                dataset.data = dataset.data.map(value => Math.round(value * multiplier));
            });
            customersChart.update();
        }
    }
    
    reportForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        
        const submitBtn = this.querySelector('.save-btn');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Generating...';
        submitBtn.disabled = true;
        
        fetch('/api/utilities/generate-report', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alert(data.message);
                closeModal();
            } else {
                alert('Error: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error generating report:', error);
            alert('An error occurred while generating the report. Please try again.');
        })
        .finally(() => {
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
        });
    });
    
    initCharts();
    
    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        
        document.querySelectorAll('.data-table tbody tr').forEach(row => {
            let textContent = '';
            
            for (let i = 0; i < row.cells.length; i++) {
                textContent += row.cells[i].textContent + ' ';
            }
            
            textContent = textContent.toLowerCase();
            
            if (searchTerm && textContent.includes(searchTerm)) {
                row.style.backgroundColor = 'rgba(67, 97, 238, 0.1)';
            } else {
                row.style.backgroundColor = '';
            }
        });
    });
});
