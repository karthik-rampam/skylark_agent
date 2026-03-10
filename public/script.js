const chatMessages = document.getElementById('chat-messages');
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');

// Navigation
const navChat = document.getElementById('nav-chat');
const navDashboard = document.getElementById('nav-dashboard');
const chatView = document.getElementById('chat-view');
const dashboardView = document.getElementById('dashboard-view');

let pipelineChart, opsChart;

navChat.addEventListener('click', () => {
    switchView('chat');
});

navDashboard.addEventListener('click', () => {
    switchView('dashboard');
    loadDashboard();
});

function switchView(view) {
    if (view === 'chat') {
        chatView.style.display = 'flex';
        dashboardView.style.display = 'none';
        navChat.classList.add('active');
        navDashboard.classList.remove('active');
    } else {
        chatView.style.display = 'none';
        dashboardView.style.display = 'flex';
        navChat.classList.remove('active');
        navDashboard.classList.add('active');
    }
}

async function loadDashboard() {
    const grid = document.querySelector('.dashboard-grid');
    const originalContent = grid.innerHTML;
    grid.innerHTML = '<div class="loader-container"><div class="loader"></div></div>';

    try {
        const response = await fetch('/api/dashboard');
        const data = await response.json();

        grid.innerHTML = originalContent;
        renderPipelineChart(data.pipeline);
        renderOpsChart(data.ops);
    } catch (error) {
        grid.innerHTML = '<p style="padding: 20px; color: #ef4444;">Error loading dashboard data. Please try again.</p>';
        console.error('Error loading dashboard:', error);
    }
}

function renderPipelineChart(data) {
    const ctx = document.getElementById('pipelineChart').getContext('2d');
    if (pipelineChart) pipelineChart.destroy();

    pipelineChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(data),
            datasets: [{
                label: 'Pipeline Value (INR)',
                data: Object.values(data),
                backgroundColor: '#3b82f6',
                borderRadius: 8
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            plugins: { legend: { display: false } }
        }
    });
}

function renderOpsChart(data) {
    const ctx = document.getElementById('opsChart').getContext('2d');
    if (opsChart) opsChart.destroy();

    opsChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(data),
            datasets: [{
                data: Object.values(data),
                backgroundColor: ['#10b981', '#f59e0b', '#ef4444', '#3b82f6', '#8b5cf6']
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { position: 'bottom' } }
        }
    });
}

function appendMessage(role, text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;

    const avatar = document.createElement('div');
    avatar.className = 'avatar';
    avatar.innerText = role === 'ai' ? 'AI' : 'U';

    const textDiv = document.createElement('div');
    textDiv.className = 'text';
    textDiv.innerHTML = formatText(text);

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(textDiv);
    chatMessages.appendChild(messageDiv);

    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function formatText(text) {
    return text
        .replace(/### (.*)/g, '<h3>$1</h3>')
        .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
        .replace(/• (.*)/g, '<li>$1</li>')
        .replace(/\n/g, '<br>');
}

chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const message = userInput.value.trim();
    if (!message) return;

    appendMessage('user', message);
    userInput.value = '';

    // Add animated typing indicator
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message ai';
    typingDiv.innerHTML = `
        <div class="avatar">AI</div>
        <div class="text">
            <div class="typing-dots">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
            </div>
        </div>
    `;
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
        });

        const data = await response.json();
        chatMessages.removeChild(typingDiv);
        appendMessage('ai', data.response);
    } catch (error) {
        if (typingDiv.parentNode) chatMessages.removeChild(typingDiv);
        appendMessage('ai', "I'm having trouble connecting to the server. Please try again later.");
    }
});
