// Placeholder for main JavaScript functionalities
// This file can be used for:
// - Fetching data from backend APIs (MCP Server, AI Assistant Service)
// - Handling user interactions (e.g., button clicks, form submissions)
// - Dynamically updating the DOM with course content, AI messages, etc.

console.log("main.js loaded");

document.addEventListener('DOMContentLoaded', function() {
    const chatHistory = document.getElementById('chat-history');
    const studentInput = document.getElementById('student-input');
    const sendButton = document.getElementById('send-button');
    const startUrl = document.getElementById('start-activity-url') ? document.getElementById('start-activity-url').value : null;
    const interactUrl = document.getElementById('interact-activity-url') ? document.getElementById('interact-activity-url').value : null;
    const userId = document.getElementById('current-user-id') ? document.getElementById('current-user-id').value : 'guest';
    const activityKey = document.getElementById('current-activity-key') ? document.getElementById('current-activity-key').value : null;

    let sessionId = null;
    let conversationHistory = []; // To maintain history if needed on client side

    // Helper to append messages
    function appendMessage(sender, text, isError=false) {
        if (!chatHistory) return;
        const msgDiv = document.createElement('div');
        msgDiv.style.marginBottom = '10px';
        msgDiv.style.padding = '8px';
        msgDiv.style.borderRadius = '5px';

        if (sender === 'User') {
            msgDiv.style.backgroundColor = '#e1f5fe';
            msgDiv.style.textAlign = 'right';
            const strong = document.createElement('strong');
            strong.textContent = 'You: ';
            msgDiv.appendChild(strong);
            msgDiv.appendChild(document.createTextNode(text));
        } else {
            msgDiv.style.backgroundColor = isError ? '#ffebee' : '#f1f8e9';
            msgDiv.style.textAlign = 'left';
            const strong = document.createElement('strong');
            strong.textContent = sender + ': ';
            msgDiv.appendChild(strong);
            msgDiv.appendChild(document.createTextNode(text));
        }
        chatHistory.appendChild(msgDiv);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    // Start Activity
    if (startUrl && activityKey) {
        fetch(startUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: userId,
                activity_key: activityKey
            })
        })
        .then(response => response.json())
        .then(data => {
            console.log("Activity Started:", data);
            if (data.session_id) {
                sessionId = data.session_id;
            }
        })
        .catch(error => {
            console.error("Error starting activity:", error);
            appendMessage("System", "Failed to start AI session.", true);
        });
    }

    // Interact function
    function sendMessage() {
        const text = studentInput.value.trim();
        if (!text) return;

        appendMessage("User", text);
        studentInput.value = '';
        studentInput.disabled = true;
        sendButton.disabled = true;

        if (!interactUrl || !sessionId) {
            appendMessage("System", "Session not initialized or API unavailable.", true);
            studentInput.disabled = false;
            sendButton.disabled = false;
            return;
        }

        const payload = {
            session_id: sessionId,
            user_id: userId,
            user_utterance: text,
            ai_activity_key: activityKey,
            conversation_history: conversationHistory
        };

        fetch(interactUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                appendMessage("System", "Error: " + data.error, true);
            } else if (data.ai_messages && data.ai_messages.length > 0) {
                data.ai_messages.forEach(msg => {
                    appendMessage("AI Assistant", msg);
                    conversationHistory.push({role: "user", content: text});
                    conversationHistory.push({role: "assistant", content: msg});
                });
            } else {
                 appendMessage("System", "No response from AI.", true);
            }
        })
        .catch(error => {
            console.error("Error interacting:", error);
            appendMessage("System", "Error communicating with server.", true);
        })
        .finally(() => {
            studentInput.disabled = false;
            sendButton.disabled = false;
            studentInput.focus();
        });
    }

    if (sendButton) {
        sendButton.addEventListener('click', sendMessage);
    }

    if (studentInput) {
        studentInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    }
});
