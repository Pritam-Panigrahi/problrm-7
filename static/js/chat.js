let autoSpeak = false;
let lastAIResponse = '';
let currentLanguage = document.documentElement.lang || 'en';

async function sendMessage() {
    const input = document.getElementById('userInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    addMessageToChat('user', message);
    input.value = '';
    
    try {
        const response = await fetch('/worker/chat/message', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({message})
        });
        
        const data = await response.json();
        
        if (response.ok) {
            addMessageToChat('ai', data.response);
            lastAIResponse = data.response;
            
            if (autoSpeak && typeof speakText === 'function') {
                speakText(data.response, currentLanguage);
            }
            
            if (data.is_complete) {
                setTimeout(() => {
                    window.location.href = '/worker/resume/preview';
                }, 2000);
            }
        } else {
            addMessageToChat('ai', 'Sorry, I encountered an error. Please try again.');
        }
    } catch (error) {
        addMessageToChat('ai', 'Connection error. Please check your internet and try again.');
    }
}

function addMessageToChat(role, message) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}-message`;
    
    const p = document.createElement('p');
    p.textContent = message;
    messageDiv.appendChild(p);
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function toggleSpeaker() {
    if (typeof stopSpeaking === 'function' && typeof isSpeaking !== 'undefined' && isSpeaking) {
        stopSpeaking();
        autoSpeak = false;
    } else if (autoSpeak) {
        autoSpeak = false;
        if (typeof stopSpeaking === 'function') {
            stopSpeaking();
        }
        updateSpeakerButton(false);
    } else {
        autoSpeak = true;
        if (lastAIResponse && typeof speakText === 'function') {
            speakText(lastAIResponse, currentLanguage);
        }
    }
}

document.getElementById('userInput').addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});
