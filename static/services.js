document.addEventListener("DOMContentLoaded", () => {
    const sendBtn = document.getElementById("send-btn");
    const chatInput = document.getElementById("chat-input");
    const chatBody = document.getElementById("chatbox-body");
    const chatToggle = document.getElementById("chatbox-toggle");
    const chatContent = document.getElementById("chatbox-body-container");

    let isChatCollapsed = false;

    function sendMessage() {
        const message = chatInput.value.trim();
        if (message !== "") {
            const userMsg = document.createElement("div");
            userMsg.className = "chat-message user";
            userMsg.textContent = message;
            chatBody.appendChild(userMsg);
            chatInput.value = "";
            chatBody.scrollTop = chatBody.scrollHeight;

            setTimeout(() => {
                const botReply = document.createElement("div");
                botReply.className = "chat-message bot";
                botReply.textContent = "Thanks for your message! We'll get back to you soon.";
                chatBody.appendChild(botReply);
                chatBody.scrollTop = chatBody.scrollHeight;
            }, 1000);
        }
    }

    function toggleChat() {
        isChatCollapsed = !isChatCollapsed;
        if (isChatCollapsed) {
            chatContent.classList.add("collapsed");
        } else {
            chatContent.classList.remove("collapsed");
        }
    }

    sendBtn.addEventListener("click", sendMessage);
    chatInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") {
            sendMessage();
        }
    });

    chatToggle.addEventListener("click", toggleChat);
    chatContent.classList.remove("collapsed");
});
