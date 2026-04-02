/**
 * SCORAS ACADEMY CHATBOT - MODERN INTERFACE
 * ChatGPT-style frontend with Redis storage integration
 */

// =============================================================================
// CONFIGURATION
// =============================================================================

const CONFIG = {
    API_BASE_URL: window.API_BASE_URL || 'http://localhost:8003',
    MAX_MESSAGE_LENGTH: 2000,
    AUTO_RESIZE_MAX_HEIGHT: 120,
    TYPING_DELAY: 1000,
    STATUS_CHECK_INTERVAL: 30000
};

// =============================================================================
// GLOBAL STATE
// =============================================================================

let conversationId = null;
let messageCount = 0;
let isLoading = false;

// Inactivity timer variables
let inactivityTimer = null;
let warningTimer = null;
let inactivityWarningShown = false;

const INACTIVITY_WARNING_MS = 8 * 60 * 1000;  // 8 minutes
const INACTIVITY_CLOSE_MS = 10 * 60 * 1000;   // 10 minutes

// =============================================================================
// DOM ELEMENTS
// =============================================================================

const elements = {
    messagesWrapper: document.getElementById('messagesWrapper'),
    messageInput: document.getElementById('messageInput'),
    sendButton: document.getElementById('sendButton'),
    typingIndicator: document.getElementById('typingIndicator'),
    charCount: document.getElementById('charCount'),
    statusDot: document.querySelector('.status-dot'),
    statusText: document.querySelector('.status-text')
};

// =============================================================================
// INITIALIZATION
// =============================================================================

document.addEventListener('DOMContentLoaded', function() {
    initializeChat();
    setupEventListeners();
    checkApiStatus();

    // Focus input when page loads
    elements.messageInput.focus();

    console.log('🎓 Scoras Academy Chat Interface loaded');
});

function initializeChat() {
    // Try to restore existing conversation from localStorage
    const savedId = localStorage.getItem('scoras_conversation_id');
    if (savedId) {
        conversationId = savedId;
        console.log('Restored conversation ID:', conversationId);
    } else {
        conversationId = generateConversationId();
        localStorage.setItem('scoras_conversation_id', conversationId);
        console.log('New conversation ID:', conversationId);
    }

    // Start inactivity timer
    resetInactivityTimer();
}

function generateConversationId() {
    return 'user_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

// =============================================================================
// EVENT LISTENERS
// =============================================================================

function setupEventListeners() {
    // Message input events
    elements.messageInput.addEventListener('input', handleInputChange);
    elements.messageInput.addEventListener('keydown', handleKeyDown);

    // Send button
    elements.sendButton.addEventListener('click', sendMessage);

    // Prevent form submission
    document.addEventListener('submit', (e) => e.preventDefault());
}

function handleInputChange() {
    const message = elements.messageInput.value;
    const length = message.length;

    // Update character count
    elements.charCount.textContent = length;

    // Update character count color
    if (length > 1800) {
        elements.charCount.style.color = '#ef4444';
    } else if (length > 1500) {
        elements.charCount.style.color = '#f59e0b';
    } else {
        elements.charCount.style.color = 'var(--text-muted)';
    }

    // Update send button state
    elements.sendButton.disabled = !message.trim() || isLoading;

    // Auto-resize textarea
    autoResizeTextarea();
}

function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
}

function autoResizeTextarea() {
    const textarea = elements.messageInput;
    textarea.style.height = 'auto';
    const newHeight = Math.min(textarea.scrollHeight, CONFIG.AUTO_RESIZE_MAX_HEIGHT);
    textarea.style.height = newHeight + 'px';
}

// =============================================================================
// MESSAGE HANDLING
// =============================================================================

async function sendMessage() {
    const message = elements.messageInput.value.trim();
    if (!message || isLoading) return;

    // Set loading state
    setLoadingState(true);

    // Add user message to UI
    addMessageToUI(message, 'user');

    // Clear input
    elements.messageInput.value = '';
    elements.messageInput.style.height = 'auto';
    handleInputChange();

    // Show typing indicator
    showTypingIndicator();

    try {
        // Send to API
        const response = await fetch(`${CONFIG.API_BASE_URL}/chat-simple`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                user_id: conversationId,
                lead_type: 'academy'
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        // Hide typing indicator
        hideTypingIndicator();

        // Add bot response to UI
        addMessageToUI(data.response, 'assistant');

        messageCount++;

    } catch (error) {
        console.error('Error sending message:', error);
        hideTypingIndicator();

        // Show error message
        addMessageToUI(
            'Desculpe, ocorreu um erro ao processar sua mensagem. Tente novamente em alguns instantes.',
            'assistant',
            true
        );
    } finally {
        // Reset loading state
        setLoadingState(false);
        elements.messageInput.focus();

        // Reset inactivity timer after each message
        resetInactivityTimer();
    }
}

function addMessageToUI(text, sender, isError = false) {
    const messageGroup = document.createElement('div');
    messageGroup.className = `message-group ${sender}`;

    if (isError) {
        messageGroup.classList.add('error');
    }

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';

    if (sender === 'assistant') {
        avatar.innerHTML = '<img src="https://avatars.githubusercontent.com/u/181589263?s=280&v=4" alt="Scoras Academy">';
    } else {
        avatar.textContent = 'U';
    }

    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';

    const content = document.createElement('div');
    content.className = 'message-content';
    content.innerHTML = formatMessage(text);

    const time = document.createElement('div');
    time.className = 'message-time';
    time.textContent = new Date().toLocaleTimeString('pt-BR', {
        hour: '2-digit',
        minute: '2-digit'
    });

    bubble.appendChild(content);
    bubble.appendChild(time);
    messageGroup.appendChild(avatar);
    messageGroup.appendChild(bubble);

    elements.messagesWrapper.appendChild(messageGroup);
    scrollToBottom();
}

function formatMessage(text) {
    return text
        .replace(/\n/g, '<br>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>');
}

function showTypingIndicator() {
    elements.typingIndicator.classList.remove('hidden');
    scrollToBottom();
}

function hideTypingIndicator() {
    elements.typingIndicator.classList.add('hidden');
}

function scrollToBottom() {
    setTimeout(() => {
        elements.messagesWrapper.scrollTop = elements.messagesWrapper.scrollHeight;
    }, 100);
}

function setLoadingState(loading) {
    isLoading = loading;
    elements.messageInput.disabled = loading;
    elements.sendButton.disabled = loading || !elements.messageInput.value.trim();
}

// =============================================================================
// API STATUS
// =============================================================================

async function checkApiStatus() {
    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}/health`);

        if (response.ok) {
            setConnectionStatus('online');
        } else {
            setConnectionStatus('connecting');
        }
    } catch (error) {
        console.error('Error checking API status:', error);
        setConnectionStatus('offline');
    }
}

function setConnectionStatus(status) {
    elements.statusDot.className = `status-dot ${status}`;

    switch (status) {
        case 'online':
            elements.statusText.textContent = 'Online';
            break;
        case 'connecting':
            elements.statusText.textContent = 'Conectando...';
            break;
        case 'offline':
            elements.statusText.textContent = 'Offline';
            break;
    }
}

// =============================================================================
// ACTION FUNCTIONS
// =============================================================================

function clearMessages() {
    if (messageCount > 0 && confirm('Tem certeza que deseja limpar a conversa atual?')) {
        // Keep only the welcome message
        const welcomeMessage = elements.messagesWrapper.querySelector('.message-group.assistant');
        elements.messagesWrapper.innerHTML = '';
        if (welcomeMessage) {
            elements.messagesWrapper.appendChild(welcomeMessage);
        }
        messageCount = 0;
        scrollToBottom();
    }
}

function newConversation() {
    if (messageCount > 0 && confirm('Tem certeza que deseja iniciar uma nova conversa?')) {
        // Reset conversation
        conversationId = generateConversationId();
        localStorage.setItem('scoras_conversation_id', conversationId);
        messageCount = 0;

        // Clear messages
        const welcomeMessage = elements.messagesWrapper.querySelector('.message-group.assistant');
        elements.messagesWrapper.innerHTML = '';
        if (welcomeMessage) {
            elements.messagesWrapper.appendChild(welcomeMessage);
        }
        scrollToBottom();
        console.log('New conversation started with ID:', conversationId);
    }
}

// =============================================================================
// INACTIVITY TIMER
// =============================================================================

function resetInactivityTimer() {
    clearTimeout(inactivityTimer);
    clearTimeout(warningTimer);
    inactivityWarningShown = false;

    // Set 8-minute warning
    warningTimer = setTimeout(() => {
        if (messageCount > 0) {
            addMessageToUI(
                'Notei que você está ausente há alguns minutos. Precisa de mais alguma ajuda? Se não responder em 2 minutos, encerrarei nossa conversa.',
                'assistant'
            );
            inactivityWarningShown = true;
        }
    }, INACTIVITY_WARNING_MS);

    // Set 10-minute close
    inactivityTimer = setTimeout(() => {
        if (messageCount > 0) {
            addMessageToUI(
                'Como não houve resposta, vou encerrar nossa conversa por aqui. Foi um prazer atendê-lo! Se precisar de algo, é só enviar uma nova mensagem. 😊',
                'assistant'
            );
            // Start a new session
            conversationId = generateConversationId();
            localStorage.setItem('scoras_conversation_id', conversationId);
            messageCount = 0;
        }
    }, INACTIVITY_CLOSE_MS);
}

// =============================================================================
// PERIODIC STATUS CHECK
// =============================================================================

setInterval(checkApiStatus, CONFIG.STATUS_CHECK_INTERVAL);

// =============================================================================
// GLOBAL FUNCTIONS (for onclick handlers)
// =============================================================================

window.clearMessages = clearMessages;
window.newConversation = newConversation;

// =============================================================================
// DEBUG INFO
// =============================================================================

console.log('Scoras Academy Chat Configuration:', CONFIG);
console.log('Conversation ID:', conversationId);
