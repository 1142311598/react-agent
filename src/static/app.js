// API URL - Update this to match your server
const API_URL = 'http://localhost:58011';

// DOM Elements
const researchForm = document.getElementById('research-form');
const researchTopic = document.getElementById('research-topic');
const plansList = document.getElementById('plans-list');
const reportsList = document.getElementById('reports-list');
const modal = document.getElementById('modal');
const modalTitle = document.getElementById('modal-title');
const modalBody = document.getElementById('modal-body');
const executePlanBtn = document.getElementById('execute-plan');
const closeModal = document.querySelector('.close');

// Current plan being viewed
let currentPlan = null;

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    loadPlans();
    loadReports();
});

researchForm.addEventListener('submit', (e) => {
    e.preventDefault();
    startResearch();
});

closeModal.addEventListener('click', () => {
    modal.style.display = 'none';
});

window.addEventListener('click', (e) => {
    if (e.target === modal) {
        modal.style.display = 'none';
    }
});

executePlanBtn.addEventListener('click', () => {
    if (currentPlan) {
        executePlan(currentPlan);
    }
});

// API Functions
async function startResearch() {
    const topic = researchTopic.value.trim();
    
    if (!topic) {
        alert('Please enter a research topic');
        return;
    }
    
    try {
        researchForm.querySelector('button').disabled = true;
        researchForm.querySelector('button').textContent = 'Starting...';
        
        const response = await fetch(`${API_URL}/research/start`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ topic })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert('Research started successfully!');
            researchTopic.value = '';
            loadPlans();
        } else {
            alert(`Error: ${data.detail || 'Failed to start research'}`);
        }
    } catch (error) {
        console.error('Error starting research:', error);
        alert('An error occurred while starting research');
    } finally {
        researchForm.querySelector('button').disabled = false;
        researchForm.querySelector('button').textContent = 'Start Research';
    }
}

async function loadPlans() {
    try {
        plansList.innerHTML = '<p class="loading">Loading research plans...</p>';
        
        const response = await fetch(`${API_URL}/plans`);
        const data = await response.json();
        
        if (response.ok) {
            displayPlans(data.plans);
        } else {
            plansList.innerHTML = `<p>Error: ${data.detail || 'Failed to load plans'}</p>`;
        }
    } catch (error) {
        console.error('Error loading plans:', error);
        plansList.innerHTML = '<p>An error occurred while loading plans</p>';
    }
}

async function loadReports() {
    try {
        reportsList.innerHTML = '<p class="loading">Loading research reports...</p>';
        
        const response = await fetch(`${API_URL}/reports`);
        const data = await response.json();
        
        if (response.ok) {
            displayReports(data.reports);
        } else {
            reportsList.innerHTML = `<p>Error: ${data.detail || 'Failed to load reports'}</p>`;
        }
    } catch (error) {
        console.error('Error loading reports:', error);
        reportsList.innerHTML = '<p>An error occurred while loading reports</p>';
    }
}

async function viewPlan(planName) {
    try {
        modalTitle.textContent = 'Loading Plan Details...';
        modalBody.innerHTML = '<p class="loading">Loading...</p>';
        modal.style.display = 'block';
        
        const response = await fetch(`${API_URL}/plans/${planName}`);
        const data = await response.json();
        
        if (response.ok) {
            currentPlan = planName;
            displayPlanDetails(data);
        } else {
            modalBody.innerHTML = `<p>Error: ${data.detail || 'Failed to load plan details'}</p>`;
        }
    } catch (error) {
        console.error('Error viewing plan:', error);
        modalBody.innerHTML = '<p>An error occurred while loading plan details</p>';
    }
}

async function executePlan(planName) {
    try {
        executePlanBtn.disabled = true;
        executePlanBtn.textContent = 'Executing...';
        
        const response = await fetch(`${API_URL}/research/execute`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ plan_name: planName })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert('Research plan execution started in the background!');
            modal.style.display = 'none';
            loadPlans();
        } else {
            alert(`Error: ${data.detail || 'Failed to execute plan'}`);
        }
    } catch (error) {
        console.error('Error executing plan:', error);
        alert('An error occurred while executing the plan');
    } finally {
        executePlanBtn.disabled = false;
        executePlanBtn.textContent = 'Execute Plan';
    }
}

async function viewReport(reportName) {
    window.open(`${API_URL}/reports/${reportName}`, '_blank');
}

// Display Functions
function displayPlans(plans) {
    if (!plans || plans.length === 0) {
        plansList.innerHTML = '<p>No research plans found.</p>';
        return;
    }
    
    // Sort plans by created_at (newest first)
    plans.sort((a, b) => {
        return new Date(b.created_at) - new Date(a.created_at);
    });
    
    let html = '';
    
    plans.forEach(plan => {
        const statusClass = getStatusClass(plan.status);
        
        html += `
            <div class="list-item">
                <div>
                    <h3>${plan.topic}</h3>
                    <p>Status: <span class="status ${statusClass}">${plan.status}</span></p>
                    <p>Current Step: ${plan.current_step}</p>
                    <div class="progress">
                        <div class="progress-bar" style="width: ${plan.progress}%"></div>
                    </div>
                </div>
                <button class="btn primary" onclick="viewPlan('${plan.plan_name}')">View Details</button>
            </div>
        `;
    });
    
    plansList.innerHTML = html;
}

function displayReports(reports) {
    if (!reports || reports.length === 0) {
        reportsList.innerHTML = '<p>No research reports found.</p>';
        return;
    }
    
    // Sort reports by name (newest first, assuming timestamp in name)
    reports.sort((a, b) => b.localeCompare(a));
    
    let html = '';
    
    reports.forEach(report => {
        html += `
            <div class="list-item">
                <div>
                    <h3>${formatReportName(report)}</h3>
                </div>
                <button class="btn primary" onclick="viewReport('${report}')">View Report</button>
            </div>
        `;
    });
    
    reportsList.innerHTML = html;
}

function displayPlanDetails(plan) {
    modalTitle.textContent = `Plan: ${plan.topic}`;
    
    const statusClass = getStatusClass(plan.status);
    
    let html = `
        <div>
            <p>Status: <span class="status ${statusClass}">${plan.status}</span></p>
            <p>Progress: ${plan.progress}%</p>
            <p>Current Step: ${plan.current_step}</p>
            <div class="progress">
                <div class="progress-bar" style="width: ${plan.progress}%"></div>
            </div>
        </div>
        
        <h3>Main Questions:</h3>
        <ul>
    `;
    
    plan.main_questions.forEach(question => {
        html += `<li>${question}</li>`;
    });
    
    html += `
        </ul>
        
        <h3>Subtopics:</h3>
    `;
    
    plan.subtopics.forEach((subtopic, subtopicIdx) => {
        html += `
            <div class="card">
                <h4>${subtopic.name}</h4>
                <p>${subtopic.description}</p>
                
                <h5>Tasks:</h5>
                <ul>
        `;
        
        subtopic.tasks.forEach((task, taskIdx) => {
            const taskStatusClass = getStatusClass(task.status);
            
            html += `
                <li>
                    <p>${task.description}</p>
                    <p>Status: <span class="status ${taskStatusClass}">${task.status}</span></p>
                    <p>Estimated Time: ${task.estimated_time}</p>
                </li>
            `;
        });
        
        html += `
                </ul>
            </div>
        `;
    });
    
    modalBody.innerHTML = html;
    
    // Show/hide execute button based on plan status
    if (plan.status === 'planning' || plan.status === 'in_progress') {
        executePlanBtn.style.display = 'inline-block';
    } else {
        executePlanBtn.style.display = 'none';
    }
}

// Helper Functions
function getStatusClass(status) {
    switch (status) {
        case 'planning':
        case 'pending':
            return 'pending';
        case 'in_progress':
            return 'in-progress';
        case 'completed':
            return 'completed';
        default:
            return '';
    }
}

function formatReportName(reportName) {
    // Replace underscores with spaces and remove file extension
    return reportName
        .replace(/_/g, ' ')
        .replace(/\.md$/, '')
        .replace(/report \d{8}_\d{6}/, 'Report')
        .trim();
}

// Make functions available globally
window.viewPlan = viewPlan;
window.executePlan = executePlan;
window.viewReport = viewReport;