document.addEventListener("DOMContentLoaded", () => {
    // Get DOM elements
    const sendBtn = document.getElementById("send-btn");
    const chatInput = document.getElementById("chat-input");
    const chatBody = document.getElementById("chatbox-body");
    const chatToggle = document.getElementById("chatbox-toggle");
    const chatContent = document.getElementById("chatbox-body-container");
    
    // Get title elements and fix visibility
    const servicesTitle = document.getElementById("services-title");
    const servicesSubtitle = document.getElementById("services-subtitle");
    
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
    
    // Chat state
    let isChatCollapsed = false;

    // Function to send messages
    function sendMessage() {
        const message = chatInput.value.trim();
        if (message !== "") {
            // Create and append user message
            const userMsg = document.createElement("div");
            userMsg.className = "chat-message user";
            userMsg.textContent = message;
            chatBody.appendChild(userMsg);
            
            // Clear input field
            chatInput.value = "";
            
            // Scroll to bottom
            chatBody.scrollTop = chatBody.scrollHeight;
            
            // Bot response
            setTimeout(() => {
                const botReply = document.createElement("div");
                botReply.className = "chat-message bot";
                botReply.textContent = "Thanks for your message! We'll get back to you soon.";
                chatBody.appendChild(botReply);
                chatBody.scrollTop = chatBody.scrollHeight;
            }, 1000);
        }
    }

    // Toggle chat visibility
    function toggleChat() {
        isChatCollapsed = !isChatCollapsed;
        if (isChatCollapsed) {
            chatContent.classList.add("collapsed");
        } else {
            chatContent.classList.remove("collapsed");
        }
    }

    // Event listeners
    if (sendBtn) {
        sendBtn.addEventListener("click", sendMessage);
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
});