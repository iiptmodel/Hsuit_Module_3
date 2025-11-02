// No authentication in development mode — clear any stored token
let authToken = null;
let currentFilter = 'all';
let allReports = [];

// Helper to handle API requests
async function apiRequest(endpoint, method = 'GET', body = null, headers = {}) {
    const defaultHeaders = {};
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
            const err = await response.json().catch(()=>({detail:'Unauthorized'}));
            throw new Error(err.detail || 'Unauthorized');
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
        button.classList.add('loading');
        const span = button.querySelector('span');
        if (span) {
            button.dataset.originalText = span.textContent;
        }
    } else {
        button.disabled = false;
        button.classList.remove('loading');
        const span = button.querySelector('span');
        if (span && button.dataset.originalText) {
            span.textContent = button.dataset.originalText;
        }
    }
}

// Show notification (simple alert for now, can be enhanced)
function showNotification(message, type = 'info') {
    // You can implement a custom notification system here
    if (type === 'error') {
        alert('Error: ' + message);
    } else if (type === 'success') {
        // Success notification
        console.log('Success:', message);
    }
}

// --- Tab Management ---
function initTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const forms = document.querySelectorAll('.upload-form');
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetTab = btn.dataset.tab;
            
            // Update active tab button
            tabBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // Show corresponding form
            forms.forEach(form => {
                form.classList.remove('active');
                if (form.id === `${targetTab}-upload-form`) {
                    form.classList.add('active');
                }
            });
        });
    });
}

// --- File Upload Display ---
function initFileUpload() {
    const fileInput = document.getElementById('file-upload');
    const fileNameDisplay = document.querySelector('.file-name-display');
    
    if (fileInput) {
        fileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                fileNameDisplay.textContent = `📄 ${file.name}`;
                fileNameDisplay.classList.add('active');
            } else {
                fileNameDisplay.classList.remove('active');
            }
        });
    }
}

// --- Dashboard Functions ---

function createReportCard(report) {
    const template = document.getElementById('report-card-template');
    const card = template.content.cloneNode(true).firstElementChild;
    
    card.dataset.reportId = report.id;
    card.dataset.status = report.status.toLowerCase();
    card.classList.add(report.status.toLowerCase());
    
    card.querySelector('.report-id').textContent = report.id;
    card.querySelector('.report-type-badge').textContent = report.report_type;
    card.querySelector('.report-date').textContent = new Date(report.created_at).toLocaleString();
    
    const statusEl = card.querySelector('.status-value');
    statusEl.textContent = report.status;
    statusEl.className = 'status-value';
    statusEl.classList.add(report.status.toLowerCase());

    const summaryEl = card.querySelector('.report-summary');
    const audioEl = card.querySelector('.report-audio');

    if (report.status === 'completed') {
        summaryEl.style.display = 'block';
        card.querySelector('.summary-text').textContent = report.summary_text;
        
        if (report.audio_file_path) {
            audioEl.style.display = 'block';
            card.querySelector('audio').src = `/${report.audio_file_path}`; 
        }
    } else if (report.status === 'failed') {
        summaryEl.style.display = 'block';
        card.querySelector('.summary-text').textContent = report.summary_text || 'Analysis failed.';
    }
    
    // Add event listeners for action buttons
    const downloadBtn = card.querySelector('.download-btn');
    const shareBtn = card.querySelector('.share-btn');
    
    downloadBtn.addEventListener('click', () => downloadReport(report));
    shareBtn.addEventListener('click', () => shareReport(report));
    
    return card;
}

function downloadReport(report) {
    if (report.audio_file_path) {
        const a = document.createElement('a');
        a.href = `/${report.audio_file_path}`;
        a.download = `medical_report_${report.id}.mp3`;
        a.click();
    } else {
        showNotification('No audio file available for this report', 'error');
    }
}

function shareReport(report) {
    const shareText = `Medical Report Analysis #${report.id}\n\n${report.summary_text?.substring(0, 200)}...`;
    
    if (navigator.share) {
        navigator.share({
            title: `Medical Report #${report.id}`,
            text: shareText,
        }).catch(err => console.log('Error sharing:', err));
    } else {
        // Fallback: copy to clipboard
        navigator.clipboard.writeText(shareText).then(() => {
            showNotification('Report summary copied to clipboard!', 'success');
        });
    }
}

function filterReports(filter) {
    currentFilter = filter;
    
    if (filter === 'all') {
        renderReportList(allReports);
    } else {
        const filtered = allReports.filter(report => 
            report.status.toLowerCase() === filter
        );
        renderReportList(filtered);
    }
}

function renderReportList(reports) {
    const listEl = document.getElementById('reports-list');
    const emptyState = document.getElementById('empty-state');
    
    listEl.innerHTML = '';
    
    if (reports.length === 0) {
        emptyState.style.display = 'block';
        return;
    }
    
    emptyState.style.display = 'none';
    
    reports.forEach(report => {
        const card = createReportCard(report);
        listEl.appendChild(card);
    });
}

function updateStats() {
    const totalReports = allReports.length;
    const completedReports = allReports.filter(r => r.status === 'completed').length;
    
    document.getElementById('total-reports').textContent = totalReports;
    document.getElementById('completed-reports').textContent = completedReports;
}

async function loadReports() {
    const loadingMsg = document.getElementById('loading-message');
    const emptyState = document.getElementById('empty-state');
    
    try {
        allReports = await apiRequest('/reports');
        loadingMsg.style.display = 'none';
        renderReportList(allReports);
        updateStats();
    } catch (error) {
        loadingMsg.innerHTML = '<p>Failed to load reports.</p>';
        emptyState.style.display = 'none';
    }
}

async function handleTextUpload(event) {
    event.preventDefault();
    const form = event.target;
    const button = form.querySelector('#text-submit-button');
    
    const textContent = form.querySelector('#text-content').value;
    const language = form.querySelector('#text-language').value;
    
    const formData = new FormData();
    formData.append('text_content', textContent);
    formData.append('language', language);

    setButtonLoading(button, true);

    try {
        const newReport = await apiRequest('/reports/upload-text', 'POST', formData);
        
        // Add the report to the list
        allReports.unshift(newReport);
        const listEl = document.getElementById('reports-list');
        const card = createReportCard(newReport);
        listEl.prepend(card);
        
        updateStats();
        form.reset();
        
        // Scroll to the new report
        setTimeout(() => {
            card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }, 100);
        
    } catch (error) {
        showNotification(`Text upload failed: ${error.message}`, 'error');
    } finally {
        setButtonLoading(button, false);
    }
}

async function handleFileUpload(event) {
    event.preventDefault();
    const form = event.target;
    const button = form.querySelector('#file-submit-button');

    const file = form.querySelector('#file-upload').files[0];
    const language = form.querySelector('#file-language').value;
    
    if (!file) {
        showNotification('Please select a file.', 'error');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('language', language);

    setButtonLoading(button, true);

    try {
        const newReport = await apiRequest('/reports/upload-image', 'POST', formData);
        
        // Add the report to the list
        allReports.unshift(newReport);
        const listEl = document.getElementById('reports-list');
        const card = createReportCard(newReport);
        listEl.prepend(card);
        
        updateStats();
        form.reset();
        document.querySelector('.file-name-display').classList.remove('active');
        
        // Scroll to the new report
        setTimeout(() => {
            card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }, 100);
        
    } catch (error) {
        showNotification(`File upload failed: ${error.message}`, 'error');
    } finally {
        setButtonLoading(button, false);
    }
}

// --- Filter Management ---
function initFilters() {
    const filterBtns = document.querySelectorAll('.filter-btn');
    
    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const filter = btn.dataset.filter;
            
            // Update active filter button
            filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // Apply filter
            filterReports(filter);
        });
    });
}

// --- Page Initialization ---
document.addEventListener('DOMContentLoaded', () => {
    const path = window.location.pathname;

    if (path.includes('/dashboard')) {
        // Initialize dashboard features
        initTabs();
        initFileUpload();
        initFilters();
        loadReports();
        
        // Setup form handlers
        document.getElementById('text-upload-form')?.addEventListener('submit', handleTextUpload);
        document.getElementById('file-upload-form')?.addEventListener('submit', handleFileUpload);
    }
});
