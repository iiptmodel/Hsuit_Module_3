// Chat Application State
let currentSessionId = null;
let uploadedFile = null;
let sessionSocket = null;

// DOM Elements
const welcomeScreen = document.getElementById('welcomeScreen');
const chatScreen = document.getElementById('chatScreen');
const newSessionBtn = document.getElementById('newSessionBtn');
const quickStartBtn = document.getElementById('quickStartBtn');
const sessionList = document.getElementById('sessionList');
const messagesContainer = document.getElementById('messagesContainer');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const attachBtn = document.getElementById('attachBtn');
const fileInput = document.getElementById('fileInput');
const uploadedFiles = document.getElementById('uploadedFiles');
const clearChatBtn = document.getElementById('clearChatBtn');
const sessionTitle = document.getElementById('sessionTitle');
const audienceSelect = document.getElementById('audienceSelect');
const themeToggleBtn = document.getElementById('themeToggleBtn');

// Stats
const totalReportsEl = document.getElementById('total-reports');
const totalChatsEl = document.getElementById('total-chats');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadSessions();
    loadStats();
    setupEventListeners();
    initTheme();
});

function setupEventListeners() {
    // New session buttons
    newSessionBtn.addEventListener('click', createNewSession);
    quickStartBtn.addEventListener('click', createNewSession);
    
    // Message input
    messageInput.addEventListener('input', () => {
        adjustTextareaHeight();
        updateSendButtonState();
    });
    
    messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // Send button
    sendBtn.addEventListener('click', sendMessage);
    
    // File attachment
    attachBtn.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', handleFileSelect);
    
    // Clear chat
    clearChatBtn.addEventListener('click', clearCurrentSession);

    // Theme toggle
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => toggleTheme());
    }
}

/* Theme handling: toggles data-theme attribute on <html> and persists choice */
function initTheme() {
    try {
        const saved = localStorage.getItem('app-theme');
        if (saved === 'dark') {
            document.documentElement.setAttribute('data-theme', 'dark');
        } else {
            document.documentElement.removeAttribute('data-theme');
        }
    } catch (e) {
        // ignore storage errors
    }
}

function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme');
    if (current === 'dark') {
        document.documentElement.removeAttribute('data-theme');
        try { localStorage.setItem('app-theme', 'light'); } catch (e) {}
    } else {
        document.documentElement.setAttribute('data-theme', 'dark');
        try { localStorage.setItem('app-theme', 'dark'); } catch (e) {}
    }
}

// Session Management
async function loadSessions() {
    try {
        const response = await fetch('/api/v1/chat/sessions');
        const sessions = await response.json();
        
        sessionList.innerHTML = '';
        
        if (sessions.length === 0) {
            sessionList.innerHTML = `
                <div style="padding: 2rem; text-align: center; color: var(--text-secondary);">
                    <p>No chat sessions yet</p>
                    <p style="font-size: 0.9rem; margin-top: 0.5rem;">Create a new session to get started</p>
                </div>
            `;
            return;
        }
        
        sessions.forEach(session => {
            const sessionEl = createSessionElement(session);
            sessionList.appendChild(sessionEl);
        });
        
    } catch (error) {
        console.error('Error loading sessions:', error);
        showError('Failed to load chat sessions');
    }
}

function createSessionElement(session) {
    const div = document.createElement('div');
    div.className = 'session-item';
    if (session.id === currentSessionId) {
        div.classList.add('active');
    }
    
    const title = session.title || 'New Chat';
    const preview = session.messages && session.messages.length > 0 
        ? session.messages[session.messages.length - 1].content.substring(0, 50) + '...'
        : 'No messages yet';
    const time = new Date(session.created_at).toLocaleString();
    
    div.innerHTML = `
        <div class="session-title">${title}</div>
        <div class="session-preview">${preview}</div>
        <div class="session-time">${time}</div>
    `;
    
    div.addEventListener('click', () => loadSession(session.id));
    
    return div;
}

async function createNewSession() {
    try {
        const response = await fetch('/api/v1/chat/sessions', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title: 'New Medical Analysis Chat' })
        });
        
        const session = await response.json();
        currentSessionId = session.id;
        
        // Update UI
        welcomeScreen.style.display = 'none';
        chatScreen.style.display = 'flex';
        messagesContainer.innerHTML = '';
        sessionTitle.textContent = session.title;
    // Open websocket for realtime updates for this session
    setupWebsocket(currentSessionId);
        
        // Reload sessions list
        loadSessions();
        loadStats();
        
    } catch (error) {
        console.error('Error creating session:', error);
        showError('Failed to create new chat session');
    }
}

async function loadSession(sessionId) {
    try {
        const response = await fetch(`/api/v1/chat/sessions/${sessionId}`);
        const session = await response.json();
        
        currentSessionId = sessionId;
        sessionTitle.textContent = session.title;
        
        // Show chat screen
        welcomeScreen.style.display = 'none';
        chatScreen.style.display = 'flex';
        
        // Load messages
        messagesContainer.innerHTML = '';
        if (session.messages && session.messages.length > 0) {
            session.messages.forEach(msg => displayMessage(msg));
        }
        
        // Update session list
        loadSessions();
        
        // Scroll to bottom
        scrollToBottom();
    // Open websocket for realtime updates for this session
    setupWebsocket(currentSessionId);
        
    } catch (error) {
        console.error('Error loading session:', error);
        showError('Failed to load chat session');
    }
}

async function clearCurrentSession() {
    if (!currentSessionId) return;
    
    if (!confirm('Are you sure you want to delete this chat session?')) return;
    
    try {
        await fetch(`/api/v1/chat/sessions/${currentSessionId}`, {
            method: 'DELETE'
        });
        
        currentSessionId = null;
        welcomeScreen.style.display = 'flex';
        chatScreen.style.display = 'none';
        loadSessions();
        loadStats();
        
    } catch (error) {
        console.error('Error deleting session:', error);
        showError('Failed to delete chat session');
    }
}

// Message Handling
async function sendMessage() {
    if (!currentSessionId) {
        await createNewSession();
    }
    
    const content = messageInput.value.trim();
    
    if (!content && !uploadedFile) {
        return;
    }
    
    // Disable input
    sendBtn.disabled = true;
    messageInput.disabled = true;
    
    try {
        // Create FormData for multipart upload
        const formData = new FormData();
        formData.append('content', content || 'Please analyze this file');
        // Append audience (patient/doctor)
        const audience = audienceSelect ? audienceSelect.value : 'patient';
        formData.append('audience', audience);
        
        if (uploadedFile) {
            formData.append('file', uploadedFile);
        }
        
        // Display user message immediately
        const userMsg = {
            role: 'user',
            content: uploadedFile ? `📎 ${uploadedFile.name}\n\n${content}` : content,
            created_at: new Date().toISOString()
        };
        displayMessage(userMsg);
        
        // Clear input
        messageInput.value = '';
        clearUploadedFile();
        adjustTextareaHeight();
        
        // Show typing indicator
        showTypingIndicator();
        
        // Send message
        const response = await fetch(`/api/v1/chat/sessions/${currentSessionId}/messages`, {
            method: 'POST',
            body: formData
        });
        
        const aiMessage = await response.json();
        
        // Remove typing indicator
        removeTypingIndicator();
        
        // Display AI response
            if (!(sessionSocket && sessionSocket.readyState === WebSocket.OPEN)) {
                displayMessage(aiMessage);
            }
        
        // Update stats
        loadStats();
        loadSessions();
        
    } catch (error) {
        console.error('Error sending message:', error);
        removeTypingIndicator();
        showError('Failed to send message. Please try again.');
    } finally {
        sendBtn.disabled = false;
        messageInput.disabled = false;
        messageInput.focus();
        updateSendButtonState();
    }
}

function displayMessage(message) {
    const div = document.createElement('div');
    div.className = `message ${message.role}`;
    if (message.id) div.dataset.messageId = message.id;

    const avatar = message.role === 'user' ? '👤' : '🤖';
    const time = new Date(message.created_at).toLocaleTimeString();

    const audioHtml = message.audio_file_path ? `\n                <div class="message-audio"><audio controls src="/${message.audio_file_path}"></audio></div>` : '';

    // If message content looks like a dumped binary (e.g., Python bytes literal or raw PDF stream),
    // avoid rendering the raw blob in the UI and show a safe placeholder instead.
    let contentHtml = '';
    if (typeof message.content === 'string' && looksLikeBinary(message.content)) {
        contentHtml = `<div class="muted">[Uploaded file content omitted]</div>`;
    } else {
        contentHtml = formatMessageContent(message.content || '');
    }

    div.innerHTML = `
        <div class="message-avatar">${avatar}</div>
        <div class="message-content">
            ${contentHtml}
            ${audioHtml}
            <div class="message-time">${time}</div>
        </div>
    `;

    messagesContainer.appendChild(div);
    scrollToBottom();

    // For assistant messages without audio, poll for audio updates
    if (message.role === 'assistant' && message.id && !message.audio_file_path) {
        pollForAudio(message.id, div);
    }
}

function pollForAudio(messageId, messageElement) {
    let attempts = 0;
    const maxAttempts = 30; // Poll for up to 30 seconds
    const pollInterval = 1000; // Every 1 second

    const poll = async () => {
        if (attempts >= maxAttempts) return;

        try {
            const response = await fetch(`/api/v1/chat/sessions/${currentSessionId}/messages`);
            const messages = await response.json();
            const updatedMessage = messages.find(msg => msg.id === messageId);

            if (updatedMessage && updatedMessage.audio_file_path) {
                // Update the message element with audio
                const content = messageElement.querySelector('.message-content');
                if (content && !content.querySelector('audio')) {
                    const audioDiv = document.createElement('div');
                    audioDiv.className = 'message-audio';
                    audioDiv.innerHTML = `<audio controls src="/${updatedMessage.audio_file_path}"></audio>`;
                    const timeEl = content.querySelector('.message-time');
                    if (timeEl) content.insertBefore(audioDiv, timeEl);
                    else content.appendChild(audioDiv);
                    scrollToBottom();
                }
                return; // Stop polling
            }
        } catch (error) {
            console.warn('Error polling for audio:', error);
        }

        attempts++;
        setTimeout(poll, pollInterval);
    };

    setTimeout(poll, pollInterval);
}

function setupWebsocket(sessionId) {
    // Close existing socket if any
    try {
        if (sessionSocket) {
            sessionSocket.close();
            sessionSocket = null;
        }
    } catch (e) {
        console.warn('Error closing previous websocket', e);
    }

    if (!sessionId) return;

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const url = `${protocol}//${window.location.host}/api/v1/chat/ws/sessions/${sessionId}`;
    sessionSocket = new WebSocket(url);

    sessionSocket.onopen = () => {
        console.info('WebSocket connected for session', sessionId);
    };

    sessionSocket.onmessage = (ev) => {
        try {
            const data = JSON.parse(ev.data);
            if (data.type === 'audio_ready') {
                handleAudioReady(data);
            } else if (data.type === 'assistant_init') {
                handleAssistantInit(data);
            } else if (data.type === 'assistant_delta') {
                handleAssistantDelta(data);
            }
        } catch (e) {
            console.warn('Invalid websocket message', e);
        }
    };

    sessionSocket.onclose = () => {
        console.info('WebSocket closed for session', sessionId);
    };

    sessionSocket.onerror = (err) => {
        console.warn('WebSocket error', err);
    };
}

function handleAudioReady(payload) {
    try {
        const messageId = payload.message_id;
        const audioPath = payload.audio_file_path;
        const msgEl = messagesContainer.querySelector(`[data-message-id='${messageId}']`);
        if (msgEl) {
            // find .message-content and append audio if not present
            const content = msgEl.querySelector('.message-content');
            if (content && !content.querySelector('audio')) {
                const audioDiv = document.createElement('div');
                audioDiv.className = 'message-audio';
                audioDiv.innerHTML = `<audio controls src="/${audioPath}"></audio>`;
                // insert before message-time if exists
                const timeEl = content.querySelector('.message-time');
                if (timeEl) content.insertBefore(audioDiv, timeEl);
                else content.appendChild(audioDiv);
                scrollToBottom();
            }
        } else {
            // If message element not found, optionally reload messages for the session
            // Fallback: reload session messages to pick up audio path
            loadSession(currentSessionId);
        }
    } catch (e) {
        console.error('Failed to handle audio_ready websocket message', e);
    }
}
        function handleAssistantInit(payload) {
            try {
                const existing = messagesContainer.querySelector(`[data-message-id='${payload.message_id}']`);
                if (existing) return; // already present

                const msg = {
                    id: payload.message_id,
                    role: 'assistant',
                    content: payload.content || '',
                    created_at: new Date().toISOString()
                };
                displayMessage(msg);
            } catch (e) {
                console.error('Failed to handle assistant_init', e);
            }
        }

        function handleAssistantDelta(payload) {
            try {
                const messageId = payload.message_id;
                const content = payload.content || '';
                const msgEl = messagesContainer.querySelector(`[data-message-id='${messageId}']`);
                if (msgEl) {
                    const contentEl = msgEl.querySelector('.message-content');
                    if (contentEl) {
                        // Replace the inner HTML with formatted content (preserve audio if present)
                        const hasAudio = !!contentEl.querySelector('audio');
                        const timeEl = contentEl.querySelector('.message-time');
                        contentEl.innerHTML = formatMessageContent(content) + (hasAudio ? `\n                <div class="message-audio"><audio controls src=""></audio></div>` : '') + (timeEl ? timeEl.outerHTML : '');
                        scrollToBottom();
                    }
                } else {
                    // If not present, reload session to pick up the message
                    loadSession(currentSessionId);
                }
            } catch (e) {
                console.error('Failed to handle assistant_delta', e);
            }
        }

function formatMessageContent(content) {
    // Convert line breaks to <br>
    return content.replace(/\n/g, '<br>');
}

function looksLikeBinary(text) {
    if (!text || typeof text !== 'string') return false;
    // Heuristics:
    // - contains many '\x' hex escapes (Python bytes literal or hex dump)
    // - contains PDF stream markers like '%PDF', 'endstream', '%%EOF', 'startxref'
    const hexEscapes = (text.match(/\\x[0-9A-Fa-f]{2}/g) || []).length;
    if (hexEscapes > 8) return true;
    const lowered = text.toLowerCase();
    if (lowered.includes('%pdf') || lowered.includes('endstream') || lowered.includes('%%eof') || lowered.includes('startxref')) return true;
    // If the string has a high ratio of non-printable characters (rare in normal messages)
    const nonPrintable = (text.match(/[^\x20-\x7E\r\n\t]/g) || []).length;
    if (nonPrintable / Math.max(1, text.length) > 0.15) return true;
    return false;
}

function showTypingIndicator() {
    const div = document.createElement('div');
    div.className = 'message assistant typing-indicator-message';
    div.id = 'typingIndicator';
    
    div.innerHTML = `
        <div class="message-avatar">🤖</div>
        <div class="message-content">
            <div class="typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        </div>
    `;
    
    messagesContainer.appendChild(div);
    scrollToBottom();
}

function removeTypingIndicator() {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) {
        indicator.remove();
    }
}

// File Upload Handling
function handleFileSelect(e) {
    const file = e.target.files[0];
    if (!file) return;
    
    // Validate file type (allow images, documents and common audio formats)
    const validTypes = [
        'application/pdf',
        'image/png', 'image/jpeg', 'image/jpg', 'image/bmp', 'image/tiff',
        'audio/wav', 'audio/x-wav', 'audio/mpeg', 'audio/mp3', 'audio/ogg', 'audio/webm'
    ];
    if (!validTypes.includes(file.type)) {
        showError('Please upload a PDF, image file (PNG, JPG, BMP, TIFF) or audio (WAV/MP3/OGG)');
        return;
    }
    
    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
        showError('File size must be less than 10MB');
        return;
    }
    
    uploadedFile = file;
    displayUploadedFile(file);
    updateSendButtonState();
}

function displayUploadedFile(file) {
    const fileSize = formatFileSize(file.size);
    uploadedFiles.style.display = 'block';

    // If audio, show audio player
    if (file.type.startsWith('audio/')) {
        const audioURL = URL.createObjectURL(file);
        uploadedFiles.innerHTML = `
            <div class="file-preview">
                <div class="file-icon">🔊</div>
                <div class="file-info">
                    <div class="file-name">${file.name}</div>
                    <div class="file-size">${fileSize}</div>
                    <audio controls src="${audioURL}"></audio>
                </div>
                <button class="btn-remove-file" onclick="clearUploadedFile()">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                        <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                </button>
            </div>
        `;
        return;
    }

    // Image / document preview
    const fileType = file.type.startsWith('image/') ? '🖼️' : '📄';
    uploadedFiles.innerHTML = `
        <div class="file-preview">
            <div class="file-icon">${fileType}</div>
            <div class="file-info">
                <div class="file-name">${file.name}</div>
                <div class="file-size">${fileSize}</div>
            </div>
            <button class="btn-remove-file" onclick="clearUploadedFile()">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                    <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
            </button>
        </div>
    `;
}

function clearUploadedFile() {
    uploadedFile = null;
    uploadedFiles.style.display = 'none';
    uploadedFiles.innerHTML = '';
    fileInput.value = '';
    updateSendButtonState();
}

function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

// Stats
async function loadStats() {
    try {
        // Load reports count
        const reportsResponse = await fetch('/api/v1/reports/');
        const reports = await reportsResponse.json();
        totalReportsEl.textContent = reports.length || 0;
        
        // Load chats count
        const chatsResponse = await fetch('/api/v1/chat/sessions');
        const chats = await chatsResponse.json();
        totalChatsEl.textContent = chats.length || 0;
        
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// UI Helpers
function adjustTextareaHeight() {
    messageInput.style.height = 'auto';
    messageInput.style.height = Math.min(messageInput.scrollHeight, 150) + 'px';
}

function updateSendButtonState() {
    const hasContent = messageInput.value.trim().length > 0 || uploadedFile !== null;
    sendBtn.disabled = !hasContent;
}

function scrollToBottom() {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function showError(message) {
    // Simple error display - can be enhanced with a modal or toast
    alert('Error: ' + message);
}
