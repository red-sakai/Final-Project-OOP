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

    // Editable Full Name
    const editNameBtn = document.getElementById('editNameBtn');
    const fullNameText = document.getElementById('fullNameText');
    const fullNameInput = document.getElementById('fullNameInput');
    
    if (editNameBtn) {
        editNameBtn.addEventListener('click', function(e) {
            e.preventDefault();
            fullNameText.style.display = 'none';
            fullNameInput.style.display = 'inline-block';
            fullNameInput.value = fullNameText.textContent;
            fullNameInput.focus();
        });
    }
    
    if (fullNameInput) {
        fullNameInput.addEventListener('blur', function() {
            fullNameText.textContent = fullNameInput.value || "Florence Shaw";
            fullNameText.style.display = 'inline';
            fullNameInput.style.display = 'none';
        });
        
        fullNameInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                fullNameInput.blur();
            }
        });
    }

    // Editable Email
    const editEmailBtn = document.getElementById('editEmailBtn');
    const emailText = document.getElementById('emailText');
    const emailInput = document.getElementById('emailInput');
    
    if (editEmailBtn) {
        editEmailBtn.addEventListener('click', function(e) {
            e.preventDefault();
            emailText.style.display = 'none';
            emailInput.style.display = 'inline-block';
            emailInput.value = emailText.textContent;
            emailInput.focus();
        });
    }
    
    if (emailInput) {
        emailInput.addEventListener('blur', function() {
            emailText.textContent = emailInput.value || "hi@florenceshaw.com";
            emailText.style.display = 'inline';
            emailInput.style.display = 'none';
        });
        
        emailInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                emailInput.blur();
            }
        });
    }

    // Editable Secondary Email
    const editSecondaryEmailBtn = document.getElementById('editSecondaryEmailBtn');
    const secondaryEmailText = document.getElementById('secondaryEmailText');
    const secondaryEmailInput = document.getElementById('secondaryEmailInput');
    
    if (editSecondaryEmailBtn) {
        editSecondaryEmailBtn.addEventListener('click', function(e) {
            e.preventDefault();
            secondaryEmailText.style.display = 'none';
            secondaryEmailInput.style.display = 'inline-block';
            secondaryEmailInput.value = secondaryEmailText.textContent;
            secondaryEmailInput.focus();
        });
    }
    
    if (secondaryEmailInput) {
        secondaryEmailInput.addEventListener('blur', function() {
            secondaryEmailText.textContent = secondaryEmailInput.value || "f.shaw@gmail.com";
            secondaryEmailText.style.display = 'inline';
            secondaryEmailInput.style.display = 'none';
        });
        
        secondaryEmailInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                secondaryEmailInput.blur();
            }
        });
    }

    // Avatar upload preview for a DIV
    const avatarInput = document.getElementById('avatarInput');
    const avatarDiv = document.getElementById('courierAvatarCircle');
    
    if (avatarInput && avatarDiv) {
        avatarInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    avatarDiv.style.backgroundImage = `url('${e.target.result}')`;
                    avatarDiv.style.backgroundSize = 'cover';
                    avatarDiv.style.backgroundPosition = 'center';
                }
                reader.readAsDataURL(this.files[0]);
            }
        });
    }

    // Logout button shows loading overlay
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function(e) {
            e.preventDefault();
            document.getElementById('logout-loading').style.display = 'flex';
            // Optionally, redirect after a delay:
            setTimeout(function() {
                window.location.href = "/login";  // Use the route instead of url_for in JS
            }, 2000); // 2 seconds
        });
    }

    // Back button goes to index
    const backBtn = document.getElementById('back-btn');
    if (backBtn) {
        backBtn.addEventListener('click', function() {
            window.location.href = "/";  // Use the route instead of url_for in JS
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
});
