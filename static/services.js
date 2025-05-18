document.addEventListener("DOMContentLoaded", () => {
    // Get DOM elements
    const sendBtn = document.getElementById("send-btn");
    const chatInput = document.getElementById("chat-input");
    const chatBody = document.getElementById("chatbox-body");
    const chatToggle = document.getElementById("chatbox-toggle");
    const chatContent = document.getElementById("chatbox-body-container");
    const chatboxContainer = document.getElementById("chatbox-container");

    // Get title elements and fix visibility
    const servicesTitle = document.getElementById("services-title");
    const servicesSubtitle = document.getElementById("services-subtitle");
    const servicesSlogan = document.getElementById("services-slogan");

    // Ensure title animation works properly
    if (servicesTitle) {
        servicesTitle.style.opacity = "1";
        servicesTitle.style.visibility = "visible";
        // Re-trigger animation
        servicesTitle.classList.remove("fade-slide-down");
        setTimeout(() => {
            servicesTitle.classList.add("fade-slide-down");
        }, 10);
    }

    if (servicesSubtitle) {
        servicesSubtitle.style.opacity = "1";
        servicesSubtitle.style.visibility = "visible";
        // Re-trigger animation
        servicesSubtitle.classList.remove("fade-slide-down");
        setTimeout(() => {
            servicesSubtitle.classList.add("fade-slide-down");
        }, 10);
    }

    if (servicesSlogan) {
        servicesSlogan.style.opacity = "1";
        servicesSlogan.style.visibility = "visible";
        // Re-trigger animation
        servicesSlogan.classList.remove("fade-slide-up");
        setTimeout(() => {
            servicesSlogan.classList.add("fade-slide-up");
        }, 10);
    }

    // Chat state
    let isChatCollapsed = false;

    function createMessageBubble(text, sender = "bot", isTyping = false) {
        const msg = document.createElement("div");
        msg.className = `chat-message ${sender}${isTyping ? " typing" : " pop"}`;
        msg.textContent = text;
        return msg;
    }

    // Function to send messages (make it accessible to quick replies)
    function sendMessage(messageText) {
        const message = (messageText !== undefined) ? messageText : chatInput.value.trim();
        if (message !== "") {
            // User message with pop animation
            const userMsg = createMessageBubble(message, "user");
            chatBody.appendChild(userMsg);
            chatBody.scrollTop = chatBody.scrollHeight;
            if (messageText === undefined) chatInput.value = "";

            // Add typing indicator for bot
            const typingBubble = createMessageBubble("...", "bot", true);
            chatBody.appendChild(typingBubble);
            chatBody.scrollTop = chatBody.scrollHeight;

            // Simulate delay before bot responds
            fetch('/faq-bot', {
                method: 'POST',
                body: new URLSearchParams({ question: message }),
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            })
            .then(res => res.json())
            .then(data => {
                setTimeout(() => {
                    typingBubble.remove();
                    const botReply = createMessageBubble(data.answer, "bot");
                    chatBody.appendChild(botReply);
                    chatBody.scrollTop = chatBody.scrollHeight;
                }, 700); // 700ms delay for realism
            })
            .catch(() => {
                setTimeout(() => {
                    typingBubble.remove();
                    const botReply = createMessageBubble("Sorry, I couldn't process your question.", "bot");
                    chatBody.appendChild(botReply);
                    chatBody.scrollTop = chatBody.scrollHeight;
                }, 700);
            });
        }
    }

    // Toggle chat visibility with smooth animation
    function toggleChat() {
        isChatCollapsed = !isChatCollapsed;
        if (isChatCollapsed) {
            chatContent.classList.remove("expanded");
        } else {
            chatContent.classList.add("expanded");
        }
    }

    // Chatbox toggle
    if (chatboxContainer && chatToggle) {
        chatToggle.addEventListener("click", () => {
            chatboxContainer.classList.toggle("collapsed");
        });
    }

    // --- Navigation Bar Toggle Animation ---
    const navToggle = document.getElementById('nav-toggle');
    const navLinksContainer = document.getElementById('nav-links-container');

    if (navToggle && navLinksContainer) {
        navToggle.addEventListener('click', function () {
            navLinksContainer.classList.toggle('expanded');
        });
    }

    // Quick reply slider toggle
    const quickReplyToggle = document.getElementById("quick-reply-toggle");
    const quickRepliesBox = document.getElementById("chatbox-quick-replies");
    let quickRepliesExpanded = false;

    if (quickReplyToggle && quickRepliesBox) {
        quickReplyToggle.addEventListener("click", () => {
            quickRepliesExpanded = !quickRepliesExpanded;
            if (quickRepliesExpanded) {
                quickRepliesBox.classList.add("expanded");
                quickReplyToggle.innerHTML = 'Quick Replies &#9650;'; // Up arrow
            } else {
                quickRepliesBox.classList.remove("expanded");
                quickReplyToggle.innerHTML = 'Quick Replies &#9660;'; // Down arrow
            }
        });
        // Start collapsed
        quickRepliesBox.classList.remove("expanded");
        quickReplyToggle.innerHTML = 'Quick Replies &#9660;';
    }

    // Attach event listeners to quick reply buttons
    const quickReplies = document.querySelectorAll('.quick-reply-btn');
    quickReplies.forEach(btn => {
        btn.addEventListener('click', () => {
            sendMessage(btn.textContent);
        });
    });

    // Event listeners
    if (sendBtn) {
        sendBtn.addEventListener("click", () => sendMessage());
    }

    if (chatInput) {
        chatInput.addEventListener("keypress", (e) => {
            if (e.key === "Enter") {
                e.preventDefault(); // Prevent default form submission
                sendMessage();
            }
        });
    }

    if (chatToggle) {
        chatToggle.addEventListener("click", toggleChat);
    }

    // Ensure chat starts expanded
    if (chatContent) {
        chatContent.classList.remove("collapsed");
    }

    // --- Sidebar Toggle Logic ---
    // Sidebar elements
    const sidebar = document.getElementById("user-sidebar");
    const sidebarToggle = document.getElementById("sidebar-toggle");
    const sidebarClose = document.getElementById("sidebar-close");
    const logoutBtn = document.getElementById("logout-btn");
    const themeToggle = document.getElementById("theme-toggle");
    const themeLabel = document.getElementById("theme-label");
    const sidebarOverlay = document.getElementById("sidebar-overlay");

    // Open sidebar
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener("click", () => {
            sidebar.classList.add("open");
            sidebarOverlay.classList.add("active");
            document.body.style.overflow = "hidden"; // Prevent background scroll
        });
    }
    // Close sidebar
    function closeSidebar() {
        sidebar.classList.remove("open");
        sidebarOverlay.classList.remove("active");
        document.body.style.overflow = ""; // Restore scroll
    }
    if (sidebarClose && sidebar) {
        sidebarClose.addEventListener("click", closeSidebar);
    }
    if (sidebarOverlay) {
        sidebarOverlay.addEventListener("click", closeSidebar);
    }

    // Dropdown logic for sidebar (accordion style: only one open at a time)
    document.querySelectorAll('.sidebar-section.dropdown').forEach(section => {
        const toggle = section.querySelector('.dropdown-toggle');
        toggle.addEventListener('click', (e) => {
            e.stopPropagation();
            // Close all dropdowns except the one clicked
            document.querySelectorAll('.sidebar-section.dropdown').forEach(s => {
                if (s !== section) s.classList.remove('open');
            });
            // Toggle the clicked one
            section.classList.toggle('open');
        });
    });

    // Close sidebar and dropdowns on ESC key
    document.addEventListener('keydown', (e) => {
        if (e.key === "Escape" && sidebar.classList.contains("open")) {
            closeSidebar();
            document.querySelectorAll('.sidebar-section.dropdown').forEach(s => s.classList.remove('open'));
        }
    });

    // Logout button
    if (logoutBtn) {
        logoutBtn.addEventListener("click", () => {
            // Show the loading screen
            const logoutLoading = document.getElementById("logout-loading");
            if (logoutLoading) {
                logoutLoading.style.display = "flex";
                // Wait for animation, then redirect
                setTimeout(() => {
                    window.location.href = "/user-login.html";
                }, 2500); // Match the truck animation duration
            } else {
                // fallback
                window.location.href = "/user-login.html";
            }
        });
    }
    // Theme toggle
    if (themeToggle && themeLabel) {
        themeToggle.addEventListener("change", () => {
            if (themeToggle.checked) {
                document.body.style.background = "#222";
                document.body.style.color = "#fff";
                themeLabel.textContent = "Dark";
            } else {
                document.body.style.background = "";
                document.body.style.color = "";
                themeLabel.textContent = "Light";
            }
        });
    }

    // --- 3D Carousel Logic ---
    const cards = Array.from(document.querySelectorAll('.carousel-card'));
    const leftArrow = document.querySelector('.arrow-left');
    const rightArrow = document.querySelector('.arrow-right');
    let current = 0;

    function updateCarousel() {
        cards.forEach((card, idx) => {
            card.classList.remove('active', 'left', 'right');
            if (idx === current) {
                card.classList.add('active');
            } else if ((idx === (current + 1) % 3)) {
                card.classList.add('right');
            } else if ((idx === (current + 2) % 3)) {
                card.classList.add('left');
            }
        });
    }

    leftArrow.addEventListener('click', () => {
        current = (current + 2) % 3; // Move left
        updateCarousel();
    });

    rightArrow.addEventListener('click', () => {
        current = (current + 1) % 3; // Move right
        updateCarousel();
    });

    updateCarousel();
});