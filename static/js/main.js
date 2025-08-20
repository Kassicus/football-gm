// Main JavaScript file for NFL GM Simulator

// Utility functions
function formatMoney(amount) {
    if (amount === null || amount === undefined) return 'N/A';
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);
}

function formatPercentage(value, total) {
    if (value === null || total === null || total === 0) return '0%';
    return `${Math.round((value / total) * 100)}%`;
}

// Loading and error indicators
function showLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = '<div class="loading">Loading...</div>';
    }
}

function showError(elementId, message) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `<div class="error">${message}</div>`;
    }
}

// Team selection handler for dashboard
function handleTeamSelection(teamId) {
    if (!teamId) return;
    
    console.log('Team selected:', teamId);
    
    // Load team overview
    loadTeamOverview(teamId);
    
    // Load roster summary
    loadRosterSummary(teamId);
    
    // Load salary cap
    loadSalaryCap(teamId);
}

// API helper functions
async function apiCall(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API call failed:', error);
        throw error;
    }
}

// Export functions for use in other scripts
window.NFLGM = {
    formatMoney,
    formatPercentage,
    showLoading,
    showError,
    handleTeamSelection,
    apiCall
};
