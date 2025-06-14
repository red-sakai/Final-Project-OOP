document.addEventListener("DOMContentLoaded", () => {
    // --- Animation for tracking page elements ---
    const trackingHeader = document.getElementById("tracking-header");
    const trackingSubheader = document.getElementById("tracking-subheader");
    const trackingSlogan = document.getElementById("tracking-slogan");
    const trackingCallout = document.getElementById("tracking-callout");
    const trackForm = document.getElementById("tracking-form");

    // Initialize animations with a slight delay between elements
    if (trackingHeader) {
        trackingHeader.classList.add("fade-slide-right");
    }
    
    setTimeout(() => {
        if (trackingSubheader) {
            trackingSubheader.classList.add("fade-slide-right");
        }
    }, 200);
    
    setTimeout(() => {
        if (trackingCallout) {
            trackingCallout.classList.add("fade-slide-right");
        }
    }, 400);
    
    setTimeout(() => {
        if (trackForm) {
            trackForm.classList.add("fade-slide-up");
        }
    }, 600);
    
    setTimeout(() => {
        if (trackingSlogan) {
            trackingSlogan.classList.add("fade-slide-up");
        }
    }, 1000);

    // --- Error message handling ---
    const errorDiv = document.getElementById("tracking-error");
    if (errorDiv && errorDiv.textContent.trim() !== "") {
        errorDiv.classList.add("visible");
    }

    // --- Input focus effects ---
    const trackingInput = document.getElementById("tracking-input");
    if (trackingInput) {
        trackingInput.addEventListener("focus", () => {
            trackingInput.parentElement.classList.add("input-focused");
        });
        
        trackingInput.addEventListener("blur", () => {
            trackingInput.parentElement.classList.remove("input-focused");
        });
    }

    // --- Form validation ---
    const trackingForm = document.getElementById("tracking-form");
    if (trackingForm) {
        trackingForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const input = document.getElementById('tracking-input').value.trim();
            const errorDiv = document.getElementById('tracking-error');
            errorDiv.textContent = '';
            errorDiv.classList.remove("visible");
            
            // Add loading state to button
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="loading-dots">Processing</span>';
            
            fetch('/validate-order-item-id', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({order_item_id: input})
            })
            .then(resp => resp.json())
            .then(data => {
                if (data.exists) {
                    // Submit the form as POST to /tracking
                    submitBtn.innerHTML = 'Redirecting...';
                    e.target.submit();
                } else {
                    errorDiv.textContent = 'Invalid Tracking ID. Please enter a valid Order Item Id.';
                    errorDiv.classList.add("visible");
                    submitBtn.disabled = false;
                    submitBtn.textContent = originalText;
                }
            })
            .catch(() => {
                errorDiv.textContent = 'Error validating Tracking ID. Please try again.';
                errorDiv.classList.add("visible");
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            });
        });
    }

    // --- Chatbox logic (copy from services.js) ---
    const sendBtn = document.getElementById("send-btn");
    const chatInput = document.getElementById("chat-input");
    const chatBody = document.getElementById("chatbox-body");
    const chatToggle = document.getElementById("chatbox-toggle");
    const chatContent = document.getElementById("chatbox-body-container");
    const chatboxContainer = document.getElementById("chatbox-container");

    let isChatCollapsed = false;

    function createMessageBubble(text, sender = "bot", isTyping = false) {
        const msg = document.createElement("div");
        msg.className = `chat-message ${sender}${isTyping ? " typing" : " pop"}`;
        msg.textContent = text;
        return msg;
    }

    // Language switcher logic
    const langToggle = document.getElementById("chatbox-lang-toggle");
    const langLabelEn = document.getElementById("lang-label-en");
    const langLabelTl = document.getElementById("lang-label-tl");
    let chatLang = "en";

    function updateLangLabels() {
        if (langToggle && langLabelEn && langLabelTl) {
            if (langToggle.checked) {
                chatLang = "tl";
                langLabelEn.classList.remove("active");
                langLabelTl.classList.add("active");
            } else {
                chatLang = "en";
                langLabelEn.classList.add("active");
                langLabelTl.classList.remove("active");
            }
        }
    }
    if (langToggle) {
        langToggle.addEventListener("change", updateLangLabels);
        // Set initial state
        updateLangLabels();
    }

    function sendMessage(messageText) {
        const message = (messageText !== undefined) ? messageText : chatInput.value.trim();
        if (message !== "") {
            const userMsg = createMessageBubble(message, "user");
            chatBody.appendChild(userMsg);
            chatBody.scrollTop = chatBody.scrollHeight;
            if (messageText === undefined) chatInput.value = "";

            const typingBubble = createMessageBubble("...", "bot", true);
            chatBody.appendChild(typingBubble);
            chatBody.scrollTop = chatBody.scrollHeight;

            fetch('/hexabot', {
                method: 'POST',
                body: new URLSearchParams({ question: message, lang: chatLang }),
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
                }, 700);
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

    function toggleChat() {
        isChatCollapsed = !isChatCollapsed;
        if (isChatCollapsed) {
            chatContent.classList.remove("expanded");
        } else {
            chatContent.classList.add("expanded");
        }
    }

    if (chatboxContainer && chatToggle) {
        chatToggle.addEventListener("click", () => {
            chatboxContainer.classList.toggle("collapsed");
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
                quickReplyToggle.innerHTML = 'Quick Replies &#9650;';
            } else {
                quickRepliesBox.classList.remove("expanded");
                quickReplyToggle.innerHTML = 'Quick Replies &#9660;';
            }
        });
        quickRepliesBox.classList.remove("expanded");
        quickReplyToggle.innerHTML = 'Quick Replies &#9660;';
    }

    const quickReplies = document.querySelectorAll('.quick-reply-btn');
    quickReplies.forEach(btn => {
        btn.addEventListener('click', () => {
            sendMessage(btn.textContent);
        });
    });

    if (sendBtn) {
        sendBtn.addEventListener("click", () => sendMessage());
    }

    if (chatInput) {
        chatInput.addEventListener("keypress", (e) => {
            if (e.key === "Enter") {
                e.preventDefault();
                sendMessage();
            }
        });
    }

    if (chatToggle) {
        chatToggle.addEventListener("click", toggleChat);
    }

    if (chatContent) {
        chatContent.classList.remove("collapsed");
    }

    // --- Sidebar logic (copy from services.js) ---
    const sidebar = document.getElementById("user-sidebar");
    const sidebarToggle = document.getElementById("sidebar-toggle");
    const sidebarClose = document.getElementById("sidebar-close");
    const logoutBtn = document.getElementById("logout-btn");
    const themeToggle = document.getElementById("theme-toggle");
    const themeLabel = document.getElementById("theme-label");
    const sidebarOverlay = document.getElementById("sidebar-overlay");

    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener("click", function(e) {
            e.preventDefault();
            sidebar.classList.add("open");
            sidebarOverlay.classList.add("active");
            document.body.style.overflow = "hidden";
        });
    }
    function closeSidebar() {
        sidebar.classList.remove("open");
        sidebarOverlay.classList.remove("active");
        document.body.style.overflow = "";
    }
    if (sidebarClose && sidebar) {
        sidebarClose.addEventListener("click", closeSidebar);
    }
    if (sidebarOverlay) {
        sidebarOverlay.addEventListener("click", closeSidebar);
    }

    document.querySelectorAll('.sidebar-section.dropdown').forEach(section => {
        const toggle = section.querySelector('.dropdown-toggle');
        toggle.addEventListener('click', (e) => {
            e.stopPropagation();
            document.querySelectorAll('.sidebar-section.dropdown').forEach(s => {
                if (s !== section) s.classList.remove('open');
            });
            section.classList.toggle('open');
        });
    });

    document.addEventListener('keydown', (e) => {
        if (e.key === "Escape" && sidebar.classList.contains("open")) {
            closeSidebar();
            document.querySelectorAll('.sidebar-section.dropdown').forEach(s => s.classList.remove('open'));
        }
    });

    // Logout button logic (modal)
    if (logoutBtn) {
        logoutBtn.addEventListener("click", () => {
            const logoutLoading = document.getElementById("logout-loading");
            if (logoutLoading) {
                logoutLoading.style.display = "flex";
                sidebar.classList.remove("open");
                sidebarOverlay.classList.remove("active");
                document.body.style.overflow = "hidden";
                setTimeout(() => {
                    window.location.href = "/user-login.html";
                }, 2500);
            } else {
                window.location.href = "/user-login.html";
            }
        });
    }
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
});