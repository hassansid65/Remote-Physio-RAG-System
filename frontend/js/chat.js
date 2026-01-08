const API_URL = 'http://localhost:8002';

let currentUserId = null;
let currentUserEmail = null;

// Check if user is already logged in
window.onload = function() {
    const savedUserId = localStorage.getItem('userId');
    const savedEmail = localStorage.getItem('userEmail');
    
    if (savedUserId && savedEmail) {
        currentUserId = savedUserId;
        currentUserEmail = savedEmail;
        showChatSection();
        loadChatHistory();
    }
};

async function login() {
    const email = document.getElementById('emailInput').value.trim();
    
    if (!email) {
        alert('Please enter your email');
        return;
    }
    
    if (!isValidEmail(email)) {
        alert('Please enter a valid email address');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentUserId = data.user_id;
            currentUserEmail = data.email;
            
            localStorage.setItem('userId', currentUserId);
            localStorage.setItem('userEmail', currentUserEmail);
            
            showChatSection();
            startChat();
        } else {
            alert('Error logging in. Please try again.');
        }
    } catch (error) {
        console.error('Login error:', error);
        alert('Connection error. Please check if the backend is running.');
    }
}

function logout() {
    localStorage.removeItem('userId');
    localStorage.removeItem('userEmail');
    currentUserId = null;
    currentUserEmail = null;
    
    document.getElementById('loginSection').classList.remove('hidden');
    document.getElementById('chatSection').classList.add('hidden');
    document.getElementById('chatContainer').innerHTML = '';
}

function showChatSection() {
    document.getElementById('loginSection').classList.add('hidden');
    document.getElementById('chatSection').classList.remove('hidden');
    document.getElementById('userEmail').textContent = currentUserEmail;
}

async function startChat() {
    try {
        const response = await fetch(`${API_URL}/chat/start/${currentUserId}`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            addMessage('assistant', data.greeting);
        }
    } catch (error) {
        console.error('Start chat error:', error);
    }
}

async function loadChatHistory() {
    try {
        const response = await fetch(`${API_URL}/chat/active/${currentUserId}`);
        const data = await response.json();
        
        if (data.active_chat && data.active_chat.messages) {
            document.getElementById('chatContainer').innerHTML = '';
            
            data.active_chat.messages.forEach(msg => {
                addMessage(msg.role, msg.content, false);
            });
            
            scrollToBottom();
        } else {
            startChat();
        }
    } catch (error) {
        console.error('Load history error:', error);
        startChat();
    }
}

async function sendMessage() {
    const input = document.getElementById('messageInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    addMessage('user', message);
    input.value = '';
    
    try {
        const response = await fetch(`${API_URL}/chat/message`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: currentUserId,
                message: message
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            addMessage('assistant', data.response, data.is_summary);
        } else {
            addMessage('assistant', 'Sorry, there was an error processing your message.');
        }
    } catch (error) {
        console.error('Send message error:', error);
        addMessage('assistant', 'Connection error. Please try again.');
    }
}

function addMessage(role, content, isSummary = false) {
    const chatContainer = document.getElementById('chatContainer');
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = `message-content ${isSummary ? 'summary' : ''}`;
    
    // Convert markdown-like formatting to HTML
    let formattedContent = content
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n/g, '<br>');
    
    contentDiv.innerHTML = formattedContent;
    
    const timestamp = document.createElement('div');
    timestamp.className = 'timestamp';
    timestamp.textContent = new Date().toLocaleTimeString();
    
    messageDiv.appendChild(contentDiv);
    messageDiv.appendChild(timestamp);
    chatContainer.appendChild(messageDiv);
    
    scrollToBottom();
}

function scrollToBottom() {
    const chatContainer = document.getElementById('chatContainer');
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function handleKeyPress(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}

function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}