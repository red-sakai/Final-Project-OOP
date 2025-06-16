// Function to activate a section
function activateSection(section) {
    // Remove 'active' from all nav links and sections
    document.querySelectorAll('.sidebar-nav a').forEach(l => l.classList.remove('active'));
    document.querySelectorAll('.content-section').forEach(sec => {
        sec.classList.remove('active');
        sec.style.opacity = 0; // Reset opacity for animation
    });

    // Activate the correct nav link and section
    const navLink = document.querySelector('.sidebar-nav a[data-section="' + section + '"]');
    const sectionDiv = document.getElementById(section);
    
    if (navLink) navLink.classList.add('active');
    if (sectionDiv) {
        sectionDiv.classList.add('active');
        // Trigger animation by changing opacity after a short delay
        setTimeout(() => {
            sectionDiv.style.opacity = 1;
        }, 50);
    }

    // Load activities when activity section is activated
    if (section === 'activity') {
        setTimeout(() => {
            loadUserActivities();
        }, 100);
    }
}

// Load user activities function
function loadUserActivities() {
    const activityTimeline = document.getElementById('activity-timeline');
    const loadingMessage = document.getElementById('activity-loading');
    
    if (!activityTimeline) return;
    
    // Show loading message
    if (loadingMessage) {
        loadingMessage.style.display = 'block';
    }
    
    fetch('/api/user-activities')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error fetching activities:', data.error);
                displayNoActivities();
                return;
            }
            
            displayActivities(data.activities);
        })
        .catch(error => {
            console.error('Error fetching user activities:', error);
            displayNoActivities();
        })
        .finally(() => {
            // Hide loading message
            if (loadingMessage) {
                loadingMessage.style.display = 'none';
            }
        });
}

function displayActivities(activities) {
    const activityTimeline = document.getElementById('activity-timeline');
    if (!activityTimeline) return;
    
    // Clear existing content except loading message
    const loadingMessage = document.getElementById('activity-loading');
    activityTimeline.innerHTML = '';
    if (loadingMessage) {
        activityTimeline.appendChild(loadingMessage);
    }
    
    if (!activities || activities.length === 0) {
        displayNoActivities();
        return;
    }
    
    activities.forEach((activity, index) => {
        const timelineItem = document.createElement('div');
        timelineItem.className = 'timeline-item';
        timelineItem.style.opacity = '0';
        timelineItem.style.animationDelay = `${index * 0.1}s`;
        timelineItem.setAttribute('data-activity', activity.activity_type);
        
        const activityIcon = getActivityIcon(activity.activity_type);
        const activityDescription = formatActivityDescription(activity);
        
        // Create source indicator
        const sourceIndicator = activity.source === 'mysql' ? 
            '<span style="color: #22c55e; font-size: 12px;">●</span>' : 
            '<span style="color: #f59e0b; font-size: 12px;">●</span>';
        
        timelineItem.innerHTML = `
            <div class="timeline-avatar">
                ${activityIcon}
            </div>
            <div class="timeline-content">
                <div class="timeline-date">${activity.date} ${sourceIndicator}</div>
                <div class="timeline-time">${activity.time}</div>
                <div class="timeline-action">${activityDescription}</div>
                ${activity.ip_address ? `<div style="font-size: 12px; color: #888;">IP: ${activity.ip_address}</div>` : ''}
                <button class="timeline-btn" onclick="showActivityDetails('${activity.full_timestamp}', '${activity.activity_type}', '${activity.source}')">View Details</button>
            </div>
        `;
        
        activityTimeline.appendChild(timelineItem);
        
        // Trigger animation
        setTimeout(() => {
            timelineItem.style.opacity = '1';
            timelineItem.style.animation = 'slideInUp 0.5s ease-out forwards';
        }, index * 100);
    });
}

function displayNoActivities() {
    const activityTimeline = document.getElementById('activity-timeline');
    if (!activityTimeline) return;
    
    const loadingMessage = document.getElementById('activity-loading');
    activityTimeline.innerHTML = '';
    if (loadingMessage) {
        activityTimeline.appendChild(loadingMessage);
    }
    
    const noActivitiesMessage = document.createElement('div');
    noActivitiesMessage.className = 'no-activities-message';
    noActivitiesMessage.style.textAlign = 'center';
    noActivitiesMessage.style.padding = '40px';
    noActivitiesMessage.style.color = '#888';
    noActivitiesMessage.innerHTML = `
        <p style="font-size: 18px; margin-bottom: 8px;">No recent activity found</p>
        <p style="font-size: 14px;">Your login history will appear here</p>
    `;
    
    activityTimeline.appendChild(noActivitiesMessage);
}

function getActivityIcon(activityType) {
    switch(activityType) {
        case 'LOGIN':
            return `<svg width="24" height="24" fill="#22c55e" viewBox="0 0 24 24">
                <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>`;
        case 'LOGOUT':
            return `<svg width="24" height="24" fill="#ef4444" viewBox="0 0 24 24">
                <path d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
            </svg>`;
        case 'REGISTER':
            return `<svg width="24" height="24" fill="#3b82f6" viewBox="0 0 24 24">
                <path d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"/>
            </svg>`;
        case 'UPDATE_PROFILE':
            return `<svg width="24" height="24" fill="#8b5cf6" viewBox="0 0 24 24">
                <path d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
            </svg>`;
        default:
            return `<svg width="24" height="24" fill="#6b7280" viewBox="0 0 24 24">
                <path d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>`;
    }
}

function formatActivityDescription(activity) {
    switch(activity.activity_type) {
        case 'LOGIN':
            return 'Successfully logged in';
        case 'LOGOUT':
            return 'Logged out of account';
        case 'REGISTER':
            return 'Account created successfully';
        case 'UPDATE_PROFILE':
            return 'Profile information updated';
        default:
            return activity.description || 'Unknown activity';
    }
}

// DOM content loaded event handler
document.addEventListener('DOMContentLoaded', function() {
    // On nav click
    document.querySelectorAll('.sidebar-nav a').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const section = this.dataset.section;
            window.location.hash = section; // Update the URL hash
            activateSection(section);
        });
    });

    // On page load and hash change
    function handleHash() {
        let section = window.location.hash.replace('#','') || 'profile';
        activateSection(section);
    }
    
    handleHash();
    window.addEventListener('hashchange', handleHash);

    // Editable Email
    const editEmailBtn = document.getElementById('editEmailBtn');
    const emailText = document.getElementById('emailText');
    const emailInput = document.getElementById('emailInput');
    const saveEmailBtn = document.getElementById('saveEmailBtn');
    const emailUpdateStatus = document.getElementById('emailUpdateStatus');

    if (editEmailBtn && emailInput && saveEmailBtn && emailText) {
        editEmailBtn.addEventListener('click', function(e) {
            e.preventDefault();
            emailText.style.display = 'none';
            emailInput.style.display = '';
            saveEmailBtn.style.display = '';
            editEmailBtn.style.display = 'none';
            emailInput.value = emailText.textContent;
            emailInput.focus();
        });

        saveEmailBtn.addEventListener('click', function(e) {
            e.preventDefault();
            const newEmail = emailInput.value.trim();
            if (!newEmail) return;
            fetch('/update_email', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({ email: newEmail })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    emailText.textContent = newEmail;
                    emailUpdateStatus.style.display = '';
                    setTimeout(() => { emailUpdateStatus.style.display = 'none'; }, 1200);
                } else {
                    alert(data.message || 'Failed to update email');
                }
            })
            .catch(() => alert('Error updating email'))
            .finally(() => {
                emailInput.style.display = 'none';
                saveEmailBtn.style.display = 'none';
                emailText.style.display = '';
                editEmailBtn.style.display = '';
            });
        });

        emailInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                saveEmailBtn.click();
            }
        });

        emailInput.addEventListener('blur', function() {
            saveEmailBtn.click();
        });
    }

    // Avatar upload preview for a DIV and update for IMG
    const avatarInput = document.getElementById('avatarInput');
    const avatarImg = document.getElementById('courierAvatarCircle');

    if (avatarInput && avatarImg) {
        avatarInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    // Update the <img> src for preview
                    avatarImg.src = e.target.result;
                }
                reader.readAsDataURL(this.files[0]);
            }
            // Also trigger upload to server
            if (this.files && this.files[0]) {
                const file = this.files[0];
                const formData = new FormData();
                formData.append('profile_image', file);

                fetch('/upload-profile-image', {
                    method: 'POST',
                    body: formData,
                    credentials: 'same-origin'
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success && data.image_url) {
                        // Update all profile images instantly
                        document.querySelectorAll('img.sidebar-profile-img').forEach(img => {
                            img.src = data.image_url + '?t=' + new Date().getTime(); // cache bust
                        });
                        // Update the big avatar
                        if (avatarImg) {
                            avatarImg.src = data.image_url + '?t=' + new Date().getTime();
                        }
                    } else {
                        alert(data.message || 'Upload failed');
                    }
                })
                .catch(() => alert('Upload failed'));
            }
        });
    }

    // Logout button shows loading overlay
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function(e) {
            e.preventDefault();
            const logoutLoading = document.getElementById("logout-loading");
            if (logoutLoading) {
                logoutLoading.style.display = "flex";
                // Hide any other overlays while showing loading
                document.body.style.overflow = "hidden";
                setTimeout(() => {
                    window.location.href = "/logout";
                }, 2500); // Match the truck animation duration
            } else {
                window.location.href = "/logout";
            }
        });
    }

    // Back button goes to index
    const backBtn = document.getElementById('back-btn');
    if (backBtn) {
        backBtn.addEventListener('click', function() {
            window.location.href = "/index.html";  // Redirect to index.html
        });
    }

    // Animation for profile image click
    const profileImg = document.querySelector('.sidebar-profile-img');
    if (profileImg) {
        profileImg.addEventListener('click', function() {
            this.style.animation = 'bounce 0.7s ease';
            this.addEventListener('animationend', function() {
                this.style.animation = '';
            });
        });
    }

    // Populate user email in the hidden field for the ticket form
    const userEmailElement = document.querySelector('.sidebar-profile-email');
    const hiddenEmailField = document.getElementById('user_email');

    if (userEmailElement && hiddenEmailField) {
        hiddenEmailField.value = userEmailElement.textContent.trim();
    }

    // Character count for ticket title
    const ticketTitle = document.getElementById('ticket-title');
    const ticketCharCount = document.getElementById('ticketCharCount');

    if (ticketTitle && ticketCharCount) {
        ticketTitle.addEventListener('input', function() {
            ticketCharCount.textContent = `${this.value.length}/100`;
        });
    }

    // File upload display
    const fileInput = document.querySelector('input[name="attachments"]');
    const uploadBtn = document.querySelector('.ticket-upload-btn');

    if (fileInput && uploadBtn) {
        fileInput.addEventListener('change', function() {
            if (this.files.length > 0) {
                uploadBtn.textContent = `${this.files.length} file(s) selected`;
            } else {
                uploadBtn.textContent = 'Upload Files';
            }
        });
        
        // Add drag and drop functionality
        const uploadArea = document.querySelector('.ticket-upload');
        if (uploadArea) {
            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                uploadArea.addEventListener(eventName, preventDefaults, false);
            });
            
            function preventDefaults(e) {
                e.preventDefault();
                e.stopPropagation();
            }
            
            ['dragenter', 'dragover'].forEach(eventName => {
                uploadArea.addEventListener(eventName, highlight, false);
            });
            
            ['dragleave', 'drop'].forEach(eventName => {
                uploadArea.addEventListener(eventName, unhighlight, false);
            });
            
            function highlight() {
                uploadArea.classList.add('highlight');
            }
            
            function unhighlight() {
                uploadArea.classList.remove('highlight');
            }
            
            uploadArea.addEventListener('drop', handleDrop, false);
            
            function handleDrop(e) {
                const dt = e.dataTransfer;
                const files = dt.files;
                fileInput.files = files;
                
                if (files.length > 0) {
                    uploadBtn.textContent = `${files.length} file(s) selected`;
                }
            }
        }
    }
    
    // Function to update user profile in the database/CSV
    function updateUserProfile(field, value) {
        // Create an AJAX request to update the user profile
        const xhr = new XMLHttpRequest();
        xhr.open('POST', '/update-profile', true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        
        xhr.onload = function() {
            if (xhr.status === 200) {
                const response = JSON.parse(xhr.responseText);
                if (response.success) {
                    showNotification('Profile updated successfully!', 'success');
                } else {
                    showNotification('Failed to update profile: ' + response.message, 'error');
                }
            } else {
                showNotification('Error updating profile', 'error');
            }
        };
        
        xhr.onerror = function() {
            showNotification('Connection error', 'error');
        };
        
        xhr.send(JSON.stringify({
            field: field,
            value: value
        }));
    }
    
    // Show notification function
    function showNotification(message, type) {
        // Check if notification container exists, if not create one
        let notificationContainer = document.getElementById('notification-container');
        if (!notificationContainer) {
            notificationContainer = document.createElement('div');
            notificationContainer.id = 'notification-container';
            notificationContainer.style.position = 'fixed';
            notificationContainer.style.top = '20px';
            notificationContainer.style.right = '20px';
            notificationContainer.style.zIndex = '1000';
            document.body.appendChild(notificationContainer);
        }
        
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.style.padding = '12px 24px';
        notification.style.marginBottom = '10px';
        notification.style.borderRadius = '4px';
        notification.style.backgroundColor = type === 'success' ? '#dff0d8' : '#f2dede';
        notification.style.color = type === 'success' ? '#3c763d' : '#a94442';
        notification.style.boxShadow = '0 2px 10px rgba(0,0,0,0.1)';
        notification.style.transition = 'all 0.5s ease-in-out';
        notification.style.animation = 'fadeInRight 0.5s';
        notification.textContent = message;
        
        // Add notification to container
        notificationContainer.appendChild(notification);
        
        // Remove notification after 3 seconds
        setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => {
                notificationContainer.removeChild(notification);
            }, 500);
        }, 3000);
    }
});

// Global function for activity details (enhanced version)
function showActivityDetails(timestamp, activityType, source) {
    const sourceText = source === 'mysql' ? 'Database' : 'CSV Backup';
    const sourceColor = source === 'mysql' ? '#22c55e' : '#f59e0b';
    
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed; top: 0; left: 0; right: 0; bottom: 0; 
        background: rgba(0,0,0,0.5); z-index: 10000; 
        display: flex; align-items: center; justify-content: center;
    `;
    
    modal.innerHTML = `
        <div style="background: white; padding: 24px; border-radius: 12px; max-width: 500px; width: 90%;">
            <h3 style="margin: 0 0 16px 0; color: #333;">Activity Details</h3>
            <p><strong>Type:</strong> ${activityType}</p>
            <p><strong>Timestamp:</strong> ${timestamp}</p>
            <p><strong>Data Source:</strong> <span style="color: ${sourceColor};">${sourceText}</span></p>
            <div style="margin-top: 20px; text-align: right;">
                <button onclick="this.closest('.modal').remove()" 
                        style="background: #4a7ca7; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer;">
                    Close
                </button>
            </div>
        </div>
    `;
    
    modal.className = 'modal';
    modal.onclick = (e) => {
        if (e.target === modal) modal.remove();
    };
    
    document.body.appendChild(modal);
}
