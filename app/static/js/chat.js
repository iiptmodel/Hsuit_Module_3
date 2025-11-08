// Chat Application State
let currentSessionId = null;
let uploadedFile = null;
let sessionSocket = null;
let sessionSocketPing = null; // keepalive interval id

// Track streaming state per assistant message
const streamState = {
    // [messageId]: { lastText: '', final: false }
};

// DOM Elements (will be initialized on DOMContentLoaded)
let welcomeScreen;
let chatScreen;
let newSessionBtn;
let quickStartBtn;
let sessionList;
let messagesContainer;
let messageInput;
let sendBtn;
let attachBtn;
let fileInput;
let uploadedFiles;
let clearChatBtn;
let sessionTitle;
let audienceSelect;
let themeToggleBtn;
let filesToggleBtn;
let filesPanel;
let filesPanelClose;
let filesPanelContent;
let renameChatBtn;
let fileChip;
let fileChipName;
let fileChipRemove;

// Stats
const totalReportsEl = document.getElementById('total-reports');
const totalChatsEl = document.getElementById('total-chats');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Initialize DOM element references now that the DOM is ready
    initDomElements();

    loadSessions();
    loadStats();
    setupEventListeners();
    initTheme();
});

function initDomElements() {
    welcomeScreen = document.getElementById('welcomeScreen');
    chatScreen = document.getElementById('chatScreen');
    newSessionBtn = document.getElementById('newSessionBtn');
    quickStartBtn = document.getElementById('quickStartBtn');
    sessionList = document.getElementById('sessionList');
    messagesContainer = document.getElementById('messagesContainer');
    messageInput = document.getElementById('messageInput');
    sendBtn = document.getElementById('sendBtn');
    attachBtn = document.getElementById('attachBtn');
    fileInput = document.getElementById('fileInput');
    uploadedFiles = document.getElementById('uploadedFiles');
    clearChatBtn = document.getElementById('clearChatBtn');
    sessionTitle = document.getElementById('sessionTitle');
    audienceSelect = document.getElementById('audienceSelect');
    themeToggleBtn = document.getElementById('themeToggleBtn');
    filesToggleBtn = document.getElementById('filesToggleBtn');
    filesPanel = document.getElementById('filesPanel');
    filesPanelClose = document.getElementById('filesPanelClose');
    filesPanelContent = document.getElementById('filesPanelContent');
    renameChatBtn = document.getElementById('renameChatBtn');
    fileChip = document.getElementById('fileChip');
    fileChipName = document.getElementById('fileChipName');
    fileChipRemove = document.getElementById('fileChipRemove');
}

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
    if (fileChipRemove) fileChipRemove.addEventListener('click', () => clearUploadedFile());
    
    // Clear chat
    clearChatBtn.addEventListener('click', clearCurrentSession);

    // Theme toggle
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => toggleTheme());
    }

    // Rename chat button
    if (renameChatBtn) {
        renameChatBtn.addEventListener('click', () => renameChat());
    }

    // Files panel toggle
    if (filesToggleBtn && filesPanel) {
        filesToggleBtn.addEventListener('click', () => toggleFilesPanel());
    }
    if (filesPanelClose && filesPanel) {
        filesPanelClose.addEventListener('click', () => closeFilesPanel());
    }
}

// Ensure websocket is connected for the active session before sending a message
function ensureWebsocketForCurrentSession() {
    if (!currentSessionId) return;
    if (!(sessionSocket && sessionSocket.readyState === WebSocket.OPEN)) {
        setupWebsocket(currentSessionId);
    }
}

/* Theme handling: toggles data-theme attribute on <html> and persists choice */
function initTheme() {
    try {
        const saved = localStorage.getItem('app-theme');
        if (saved === 'dark') {
            document.documentElement.setAttribute('data-theme', 'dark');
            if (themeToggleBtn) {
                themeToggleBtn.setAttribute('aria-pressed', 'true');
                themeToggleBtn.classList.add('is-dark');
            }
        } else {
            document.documentElement.removeAttribute('data-theme');
            if (themeToggleBtn) {
                themeToggleBtn.setAttribute('aria-pressed', 'false');
                themeToggleBtn.classList.remove('is-dark');
            }
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
        if (themeToggleBtn) {
            themeToggleBtn.setAttribute('aria-pressed', 'false');
            themeToggleBtn.classList.remove('is-dark');
        }
    } else {
        document.documentElement.setAttribute('data-theme', 'dark');
        try { localStorage.setItem('app-theme', 'dark'); } catch (e) {}
        if (themeToggleBtn) {
            themeToggleBtn.setAttribute('aria-pressed', 'true');
            themeToggleBtn.classList.add('is-dark');
        }
    }
}

async function renameChat() {
    if (!currentSessionId) {
        showError('No active session to rename');
        return;
    }
    const oldTitle = sessionTitle ? sessionTitle.textContent : '';
    const newTitle = prompt('Enter a new title for this chat', oldTitle || '');
    if (!newTitle || newTitle.trim().length === 0) return;
    try {
        // optimistic UI
        sessionTitle.textContent = newTitle;
        const resp = await fetch(`/api/v1/chat/sessions/${currentSessionId}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title: newTitle })
        });
        if (!resp.ok) {
            const txt = await resp.text();
            console.warn('Rename API failed', resp.status, txt);
            showError('Failed to rename chat on server');
        } else {
            // reload session list to reflect title change
            loadSessions();
        }
    } catch (e) {
        console.error('Rename failed', e);
        showError('Rename failed');
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
            // update currentSessionId and UI
            currentSessionId = sessionId;
            if (session.title) sessionTitle.textContent = session.title;
        
        // Show chat screen
        welcomeScreen.style.display = 'none';
        chatScreen.style.display = 'flex';
        
        // Load messages
        messagesContainer.innerHTML = '';
        if (session.messages && session.messages.length > 0) {
            session.messages.forEach(msg => displayMessage(msg));
        }
        // Render reports (uploaded files) for the session
        if (typeof renderReports === 'function') {
            renderReports(session.reports || []);
        }
        
        // Update session list
        loadSessions();
        
        // Scroll to bottom
        scrollToBottom();
    // Open websocket for realtime updates for this session
    setupWebsocket(currentSessionId);

    // Heuristic: if the latest assistant message may still be streaming, start a short polling fallback
    try {
        const lastMsg = (session.messages || []).slice(-1)[0];
        if (lastMsg && lastMsg.role === 'assistant') {
            // Initialize stream state if not present
            streamState[lastMsg.id] = streamState[lastMsg.id] || { lastText: lastMsg.content || '', final: false };
            // Poll for a brief window to catch up if we refreshed mid-stream
            startMessagePollFallback(lastMsg.id, 10000, 1000);
        }
    } catch (e) {
        // ignore
    }
        
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
    // Make sure websocket is up before sending to maximize chance to receive early deltas
    ensureWebsocketForCurrentSession();
    
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
        
        // Display AI response if websocket didn't render it (DOM absence check), regardless of socket state
        const maybeExisting = messagesContainer.querySelector(`[data-message-id='${aiMessage.id}']`);
        if (!maybeExisting) {
            displayMessage(aiMessage);
        }

        // Mark stream state as final if server already finished
        streamState[aiMessage.id] = streamState[aiMessage.id] || { lastText: '', final: true };
        streamState[aiMessage.id].final = true;
        
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

    // If this is a user message starting with a paperclip line, render a compact attachment card
    if (message.role === 'user' && typeof message.content === 'string' && message.content.startsWith('📎')) {
        const firstLine = message.content.split('\n')[0];
        const rawName = firstLine.replace('📎','').trim();
        const cleanName = sanitizeFilename(rawName);
        const card = `<div class=\"attachment-card\">📎 <span class=\"attachment-name\" title=\"${cleanName}\">${truncateFilename(cleanName)}</span></div>`;
        const rest = message.content.split('\n').slice(2).join('\n');
        contentHtml = card + (rest ? '<div class=\"attachment-user-text\">' + formatMessageContent(rest) + '</div>' : '');
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

    // If content was replaced due to being binary-like, offer a quick action to open files panel
    if (looksLikeBinary(message.content) && message.session_id) {
        const actionBtn = document.createElement('button');
        actionBtn.className = 'btn-primary';
        actionBtn.style.marginTop = '0.5rem';
        actionBtn.textContent = 'View Files';
        actionBtn.addEventListener('click', () => {
            openFilesPanel();
        });
        const contentEl = div.querySelector('.message-content');
        if (contentEl) contentEl.appendChild(actionBtn);
    }

    // For assistant messages without audio, poll for audio updates
    if (message.role === 'assistant' && message.id && !message.audio_file_path) {
        pollForAudio(message.id, div);
    }
}

function pollForAudio(messageId, messageElement) {
    let attempts = 0;
    const maxAttempts = 30; // Poll for up to 30 seconds
    const pollInterval = 2000; // Every 2 seconds to reduce server load

    const poll = async () => {
        if (attempts >= maxAttempts) return;

        try {
            const response = await fetch(`/api/v1/chat/sessions/${currentSessionId}/messages`);
            const messages = await response.json();
            const updatedMessage = messages.find(msg => msg.id === messageId);

            if (updatedMessage) {
                // Update content if it's longer (in case WebSocket deltas were missed)
                const currentContent = messageElement.querySelector('.message-content');
                if (currentContent) {
                    const currentText = currentContent.textContent || '';
                    const serverText = updatedMessage.content || '';
                    if (serverText.length > currentText.length) {
                        // Preserve existing audio div if present
                        const existingAudio = currentContent.querySelector('.message-audio');
                        const audioHtml = existingAudio ? existingAudio.outerHTML : '';
                        const timeEl = currentContent.querySelector('.message-time');
                        currentContent.innerHTML = formatMessageContent(serverText) + audioHtml + (timeEl ? timeEl.outerHTML : '');
                        scrollToBottom();
                    }
                }

                if (updatedMessage.audio_file_path) {
                    // Update the message element with audio
                    const content = messageElement.querySelector('.message-content');
                    if (content && !content.querySelector('audio')) {
                        const audioDiv = document.createElement('div');
                        audioDiv.className = 'message-audio';
                        const cacheBust = Date.now();
                        audioDiv.innerHTML = `<audio controls src="/${updatedMessage.audio_file_path}?v=${cacheBust}"></audio>`;
                        const timeEl = content.querySelector('.message-time');
                        if (timeEl) content.insertBefore(audioDiv, timeEl);
                        else content.appendChild(audioDiv);
                        scrollToBottom();
                    }
                    return; // Stop polling
                }
            }
        } catch (error) {
            console.warn('Error polling for updates:', error);
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
        // keepalive ping every 25s so server receive loop stays healthy through proxies
        if (sessionSocketPing) clearInterval(sessionSocketPing);
        sessionSocketPing = setInterval(() => {
            try { sessionSocket && sessionSocket.readyState === WebSocket.OPEN && sessionSocket.send('ping'); } catch (_) {}
        }, 25000);
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

    let wsRetryAttempts = 0;
    sessionSocket.onclose = (event) => {
        console.info('WebSocket closed for session', sessionId, 'code:', event.code, 'reason:', event.reason);
        if (sessionSocketPing) { clearInterval(sessionSocketPing); sessionSocketPing = null; }
        if (currentSessionId !== sessionId || event.wasClean) return;
        wsRetryAttempts = Math.min(wsRetryAttempts + 1, 6);
        const backoff = Math.min(30000, 1000 * Math.pow(2, wsRetryAttempts));
        console.info(`Reconnecting WebSocket in ${Math.round(backoff/1000)}s (attempt ${wsRetryAttempts})...`);
        setTimeout(() => { if (currentSessionId === sessionId) setupWebsocket(sessionId); }, backoff);
    };

    sessionSocket.onerror = (err) => {
        console.warn('WebSocket error', err);
        // Note: onclose will handle reconnection
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
                const cacheBust = Date.now();
                audioDiv.innerHTML = `<audio controls src="/${audioPath}?v=${cacheBust}"></audio>`;
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
                streamState[payload.message_id] = { lastText: payload.content || '', final: false };
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
                        // Incremental update: append only the new tail to avoid flicker
                        const st = streamState[messageId] = streamState[messageId] || { lastText: '', final: false };
                        const prev = st.lastText || '';
                        let newTail = '';
                        if (content.startsWith(prev)) {
                            newTail = content.slice(prev.length);
                        } else {
                            // Fallback: server sent full text but prefix mismatch, replace fully
                            newTail = null;
                        }

                        const timeEl = contentEl.querySelector('.message-time');
                        const existingAudio = contentEl.querySelector('.message-audio');
                        if (newTail !== null) {
                            // Find the text container (everything before audio/time)
                            const shadow = document.createElement('div');
                            shadow.innerHTML = formatMessageContent(newTail);
                            // Insert before audio/time
                            if (timeEl) contentEl.insertBefore(shadow, timeEl);
                            else contentEl.appendChild(shadow);
                        } else {
                            // Replace content fully if divergence detected
                            const audioHtml = existingAudio ? existingAudio.outerHTML : '';
                            contentEl.innerHTML = formatMessageContent(content) + audioHtml + (timeEl ? timeEl.outerHTML : '');
                        }
                        st.lastText = content;
                        if (payload.final) {
                            st.final = true;
                            // add completion indicator once
                            const existingIndicator = contentEl.querySelector('.completion-indicator');
                            if (!existingIndicator) {
                                const doneEl = document.createElement('div');
                                doneEl.className = 'completion-indicator';
                                doneEl.textContent = '✓ complete';
                                contentEl.appendChild(doneEl);
                            }
                        }
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

// Poll fallback: fetch messages periodically to update a specific assistant message
function startMessagePollFallback(messageId, durationMs = 10000, intervalMs = 1000) {
    const startedAt = Date.now();
    const tick = async () => {
        if (Date.now() - startedAt > durationMs) return;
        try {
            const response = await fetch(`/api/v1/chat/sessions/${currentSessionId}/messages`);
            const messages = await response.json();
            const updated = messages.find(m => m.id === messageId);
            if (updated) {
                const st = streamState[messageId] = streamState[messageId] || { lastText: '', final: false };
                if (!st.final && updated.content && updated.content.length > (st.lastText || '').length) {
                    // Synthesize a delta event to reuse handler logic
                    handleAssistantDelta({ message_id: messageId, content: updated.content, final: false });
                }
                if (updated.audio_file_path) {
                    // Consider stream complete when audio is ready or on next delta.final
                    st.final = true;
                    return;
                }
            }
        } catch (e) {
            // swallow
        }
        setTimeout(tick, intervalMs);
    };
    setTimeout(tick, intervalMs);
}

function looksLikeBinary(text) {
    if (!text || typeof text !== 'string') return false;
    // Heuristics to avoid rendering raw binary dumps or PDF bytes
    const hexEscapes = (text.match(/\\x[0-9A-Fa-f]{2}/g) || []).length;
    if (hexEscapes > 8) return true;
    const lowered = text.toLowerCase();
    if (lowered.includes('%pdf') || lowered.includes('endstream') || lowered.includes('%%eof') || lowered.includes('startxref')) return true;
    // Only treat as binary if both: (a) substantial length and (b) high ratio of control/non-printable chars.
    // This avoids flagging short messages that include emoji or a few non-ASCII characters (like a paperclip).
    if (text.length > 200) {
        const nonPrintable = (text.match(/[^\x20-\x7E\r\n\t]/g) || []).length;
        if (nonPrintable / Math.max(1, text.length) > 0.3) return true;
    }
    return false;
}

// Filename helpers
function sanitizeFilename(name) {
    if (!name) return '';
    const m = name.match(/^[0-9a-fA-F]{32}_(.+)$/);
    if (m) name = m[1];
    return name.replace(/[\r\n]/g, '').trim();
}

function truncateFilename(name, maxLen = 60) {
    if (!name) return '';
    if (name.length <= maxLen) return name;
    const keep = Math.floor((maxLen - 3) / 2);
    return name.slice(0, keep) + '...' + name.slice(-keep);
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

    // Show file chip in input area
    if (fileChip && fileChipName) {
        fileChipName.textContent = sanitizeFilename(file.name);
        fileChip.style.display = 'flex';
    }
}

function clearUploadedFile() {
    uploadedFile = null;
    uploadedFiles.style.display = 'none';
    uploadedFiles.innerHTML = '';
    fileInput.value = '';
    if (fileChip) fileChip.style.display = 'none';
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

function renderReports(reports) {
    // Render into files panel (drawer) instead of inline area
    const panelContent = document.getElementById('filesPanelContent');
    if (!panelContent) return;
    panelContent.innerHTML = '';
    if (!reports || reports.length === 0) {
        panelContent.innerHTML = '<div class="muted">No uploaded files for this session.</div>';
        return;
    }

    const list = document.createElement('div');
    list.style.display = 'flex';
    list.style.flexDirection = 'column';
    list.style.gap = '0.5rem';

    reports.forEach(r => {
        const item = document.createElement('div');
        item.className = 'file-preview';
        item.style.display = 'flex';
        item.style.alignItems = 'center';
        item.style.justifyContent = 'space-between';

        const left = document.createElement('div');
        left.style.display = 'flex';
        left.style.alignItems = 'center';
        left.style.gap = '0.75rem';

    const icon = document.createElement('div');
    icon.className = 'file-icon';
    icon.textContent = r.report_type && r.report_type === 'image' ? '🖼️' : '📄';

        const info = document.createElement('div');
        info.style.display = 'flex';
        info.style.flexDirection = 'column';
        const name = document.createElement('div');
        let fname = r.original_filename || (r.original_file_path ? r.original_file_path.split(/\\/).pop().split('/').pop() : 'File');
        try {
            const m = fname && fname.match(/^[0-9a-fA-F]{32}_(.+)$/);
            if (m) fname = m[1];
        } catch (e) {}
        name.textContent = fname;
        name.style.fontWeight = '600';
        name.style.whiteSpace = 'nowrap';
        name.style.overflow = 'hidden';
        name.style.textOverflow = 'ellipsis';

        const meta = document.createElement('div');
        meta.style.fontSize = '0.85rem';
        meta.style.opacity = '0.8';
        meta.textContent = `${r.status || ''} • ${new Date(r.created_at).toLocaleString()}`;

        info.appendChild(name);
        info.appendChild(meta);

        left.appendChild(icon);
        left.appendChild(info);

        const right = document.createElement('div');
        right.style.display = 'flex';
        right.style.gap = '0.5rem';

        // Thumbnail preview for images
        if (r.report_type === 'image' && r.thumbnail_path) {
            const img = document.createElement('img');
            img.src = (r.thumbnail_path.startsWith('/') ? r.thumbnail_path : '/' + r.thumbnail_path);
            img.alt = fname;
            img.style.maxWidth = '48px';
            img.style.maxHeight = '48px';
            img.style.borderRadius = '6px';
            img.style.border = '1px solid var(--border-light)';
            img.style.marginRight = '8px';
            left.prepend(img);
        }

        if (r.original_file_path) {
            const link = document.createElement('a');
            const url = r.original_file_path.startsWith('/') ? r.original_file_path : '/' + r.original_file_path;
            link.href = encodeURI(url);
            link.target = '_blank';
            link.textContent = 'Download';
            link.className = 'btn-icon';
            link.style.padding = '0.4rem 0.6rem';
            right.appendChild(link);
        }

        item.appendChild(left);
        item.appendChild(right);
        list.appendChild(item);
    });

    panelContent.appendChild(list);
}

function toggleFilesPanel() {
    if (!filesPanel) return;
    const isOpen = filesPanel.getAttribute('aria-hidden') === 'false';
    if (isOpen) closeFilesPanel();
    else openFilesPanel();
}

function openFilesPanel() {
    if (!filesPanel) return;
    filesPanel.setAttribute('aria-hidden', 'false');
    filesPanel.style.transform = 'translateX(0)';

    // Create backdrop to capture clicks outside the panel
    let backdrop = document.getElementById('filesPanelBackdrop');
    if (!backdrop) {
        backdrop = document.createElement('div');
        backdrop.id = 'filesPanelBackdrop';
        Object.assign(backdrop.style, {
            position: 'fixed',
            inset: '64px 0 0 0',
            background: 'rgba(0,0,0,0.24)',
            zIndex: 1100,
            transition: 'opacity 180ms ease',
            opacity: '0'
        });
        document.body.appendChild(backdrop);
        // Tiny timeout to allow transition
        requestAnimationFrame(() => { backdrop.style.opacity = '1'; });
        backdrop.addEventListener('click', closeFilesPanel);
    }

    // Add Esc key handler
    document.addEventListener('keydown', filesPanelEscHandler);
    // Trap focus inside the panel
    previousActiveElement = document.activeElement;
    trapFocusToPanel();

    // If a session is active, fetch reports for it and render. Otherwise fetch all reports.
    (async () => {
        try {
            if (currentSessionId) {
                const resp = await fetch(`/api/v1/chat/sessions/${currentSessionId}`);
                if (resp.ok) {
                    const session = await resp.json();
                    if (typeof renderReports === 'function') renderReports(session.reports || []);
                    return;
                }
            }
            // fallback: load all reports
            const rresp = await fetch('/api/v1/reports/');
            const reports = await rresp.json();
            if (typeof renderReports === 'function') renderReports(reports || []);
        } catch (e) {
            console.warn('Failed to fetch reports for files panel', e);
        }
    })();
    // Announce to screen readers
    announceA11y('Files panel opened');
}

function closeFilesPanel() {
    if (!filesPanel) return;
    filesPanel.setAttribute('aria-hidden', 'true');
    filesPanel.style.transform = 'translateX(110%)';

    const backdrop = document.getElementById('filesPanelBackdrop');
    if (backdrop) {
        backdrop.style.opacity = '0';
        // remove after transition
        setTimeout(() => { backdrop.remove(); }, 200);
    }

    // cleanup Escape handler
    document.removeEventListener('keydown', filesPanelEscHandler);
    // cleanup focus trap
    releaseFocusTrap();
    try {
        if (previousActiveElement && typeof previousActiveElement.focus === 'function') previousActiveElement.focus();
    } catch (e) {}
    // Announce to screen readers
    announceA11y('Files panel closed');
}

function filesPanelEscHandler(e) {
    if (e.key === 'Escape') {
        closeFilesPanel();
    }
}

// Focus trap helpers
let previousActiveElement = null;
let filesPanelKeydownHandler = null;

function trapFocusToPanel() {
    if (!filesPanel) return;
    const focusable = getFocusableElements(filesPanel);
    if (focusable.length) focusable[0].focus();

    filesPanelKeydownHandler = function (e) {
        if (e.key !== 'Tab') return;
        const focusableEls = getFocusableElements(filesPanel);
        if (!focusableEls.length) return;
        const first = focusableEls[0];
        const last = focusableEls[focusableEls.length - 1];
        if (e.shiftKey) {
            if (document.activeElement === first) {
                e.preventDefault();
                last.focus();
            }
        } else {
            if (document.activeElement === last) {
                e.preventDefault();
                first.focus();
            }
        }
    };

    document.addEventListener('keydown', filesPanelKeydownHandler);
}

function releaseFocusTrap() {
    if (filesPanelKeydownHandler) {
        document.removeEventListener('keydown', filesPanelKeydownHandler);
        filesPanelKeydownHandler = null;
    }
}

function getFocusableElements(container) {
    if (!container) return [];
    const selectors = 'a[href], area[href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), button:not([disabled]), iframe, object, embed, [tabindex]:not([tabindex="-1"]), [contenteditable]';
    return Array.prototype.slice.call(container.querySelectorAll(selectors)).filter(el => el.offsetWidth > 0 || el.offsetHeight > 0 || el === document.activeElement);
}

function announceA11y(message) {
    try {
        const live = document.getElementById('a11yLive');
        if (live) {
            live.textContent = '';
            setTimeout(() => { live.textContent = message; }, 50);
        }
    } catch (e) {
        // ignore
    }
}
