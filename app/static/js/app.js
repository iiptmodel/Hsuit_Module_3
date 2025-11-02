// Global token variable
let authToken = localStorage.getItem('token');

// Helper to handle API requests
async function apiRequest(endpoint, method = 'GET', body = null, headers = {}) {
    const defaultHeaders = {
        'Authorization': `Bearer ${authToken}`,
    };
    if (!(body instanceof FormData)) {
        defaultHeaders['Content-Type'] = 'application/json';
    }
    
    const config = {
        method,
        headers: { ...defaultHeaders, ...headers },
    };

    if (body) {
        config.body = (body instanceof FormData) ? body : JSON.stringify(body);
    }

    try {
        const response = await fetch(`/api/v1${endpoint}`, config);
        if (response.status === 401) {
            // Token is invalid or expired
            logout();
            return;
        }
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'An error occurred');
        }
        return await response.json();
    } catch (error) {
        console.error('API Request Error:', error);
        throw error;
    }
}

// Helper to set button loading state
function setButtonLoading(button, isLoading) {
    if (isLoading) {
        button.disabled = true;
        button.textContent = 'Processing...';
    } else {
        button.disabled = false;
        button.textContent = button.dataset.originalText || 'Submit';
    }
}

// --- Auth Functions ---
function handleLogin(event) {
    event.preventDefault();
    const form = event.target;
    const button = form.querySelector('#submit-button');
    const email = form.username.value;
    const password = form.password.value;
    const errorMessage = document.getElementById('error-message');

    setButtonLoading(button, true);

    // FastAPI's OAuth2 expects form-data, not JSON
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData,
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => { throw new Error(err.detail) });
        }
        return response.json();
    })
    .then(data => {
        authToken = data.access_token;
        localStorage.setItem('token', authToken);
        window.location.href = '/dashboard';
    })
    .catch(error => {
        errorMessage.textContent = error.message;
        setButtonLoading(button, false);
    });
}

function handleRegister(event) {
    event.preventDefault();
    const form = event.target;
    const button = form.querySelector('#submit-button');
    const email = form.email.value;
    const password = form.password.value;
    const errorMessage = document.getElementById('error-message');

    setButtonLoading(button, true);
    const body = { email, password };

    fetch('/api/v1/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => { throw new Error(err.detail) });
        }
        return response.json();
    })
    .then(data => {
        // Redirect to login after successful registration
        window.location.href = '/login';
    })
    .catch(error => {
        errorMessage.textContent = error.message;
        setButtonLoading(button, false);
    });
}

function logout() {
    localStorage.removeItem('token');
    authToken = null;
    window.location.href = '/login';
}

// --- Dashboard Functions ---

function createReportCard(report) {
    const template = document.getElementById('report-card-template');
    const card = template.content.cloneNode(true).firstElementChild;
    
    card.dataset.reportId = report.id;
    card.classList.add(report.status.toLowerCase()); // e.g., 'completed', 'processing'
    card.querySelector('.report-id').textContent = report.id;
    card.querySelector('.report-type').textContent = report.report_type;
    card.querySelector('.report-date').textContent = new Date(report.created_at).toLocaleString();
    
    const statusEl = card.querySelector('.status-value');
    statusEl.textContent = report.status;
    statusEl.className = 'status-value'; // reset classes
    statusEl.classList.add(report.status.toLowerCase());

    const summaryEl = card.querySelector('.report-summary');
    const audioEl = card.querySelector('.report-audio');

    if (report.status === 'completed') {
        summaryEl.style.display = 'block';
        card.querySelector('.summary-text').textContent = report.summary_text;
        
        if (report.audio_file_path) {
            audioEl.style.display = 'block';
            // The audio path is served from the root
            card.querySelector('audio').src = `/${report.audio_file_path}`; 
        }
    } else if (report.status === 'failed') {
        summaryEl.style.display = 'block';
        card.querySelector('.summary-text').textContent = report.summary_text || 'Analysis failed.';
    }
    
    return card;
}

function renderReportList(reports) {
    const listEl = document.getElementById('reports-list');
    listEl.innerHTML = '';
    
    if (reports.length === 0) {
        listEl.innerHTML = '<p>You have no reports yet.</p>';
        return;
    }
    
    reports.forEach(report => {
        const card = createReportCard(report);
        listEl.appendChild(card);
    });
}

async function loadReports() {
    const loadingMsg = document.getElementById('loading-message');
    try {
        const reports = await apiRequest('/reports');
        loadingMsg.style.display = 'none';
        renderReportList(reports);
    } catch (error) {
        loadingMsg.textContent = 'Failed to load reports.';
    }
}

async function handleTextUpload(event) {
    event.preventDefault();
    const form = event.target;
    const button = form.querySelector('#text-submit-button');
    button.dataset.originalText = 'Analyze Text';
    
    const textContent = form.querySelector('#text-content').value;
    const language = form.querySelector('#text-language').value;
    
    const formData = new FormData();
    formData.append('text_content', textContent);
    formData.append('language', language);

    setButtonLoading(button, true);

    try {
        // This will wait for the server to finish processing
        const newReport = await apiRequest('/reports/upload-text', 'POST', formData);
        
        // Add the *completed* report to the top of the list
        const listEl = document.getElementById('reports-list');
        const card = createReportCard(newReport);
        listEl.prepend(card);
        form.reset();
    } catch (error) {
        alert(`Text upload failed: ${error.message}`);
    } finally {
        setButtonLoading(button, false);
    }
}

async function handleFileUpload(event) {
    event.preventDefault();
    const form = event.target;
    const button = form.querySelector('#file-submit-button');
    button.dataset.originalText = 'Analyze File';

    const file = form.querySelector('#file-upload').files[0];
    const language = form.querySelector('#file-language').value;
    
    if (!file) {
        alert('Please select a file.');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('language', language);

    setButtonLoading(button, true);

    try {
        // This will wait for the server to finish processing
        const newReport = await apiRequest('/reports/upload-image', 'POST', formData);
        
        // Add the *completed* report to the top of the list
        const listEl = document.getElementById('reports-list');
        const card = createReportCard(newReport);
        listEl.prepend(card);
        form.reset();
    } catch (error)
    {
        alert(`File upload failed: ${error.message}`);
    } finally {
        setButtonLoading(button, false);
    }
}


// --- Page Initialization ---
document.addEventListener('DOMContentLoaded', () => {
    const path = window.location.pathname;

    if (path.includes('/login')) {
        document.getElementById('login-form')?.addEventListener('submit', handleLogin);
    } 
    else if (path.includes('/register')) {
        document.getElementById('register-form')?.addEventListener('submit', handleRegister);
    }
    else if (path.includes('/dashboard')) {
        if (!authToken) {
            window.location.href = '/login'; // Redirect if no token
            return;
        }
        // Dashboard page logic
        loadReports();
        document.getElementById('logout-button')?.addEventListener('click', logout);
        document.getElementById('text-upload-form')?.addEventListener('submit', handleTextUpload);
        document.getElementById('file-upload-form')?.addEventListener('submit', handleFileUpload);
    }
});