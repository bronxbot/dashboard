/**
 * Common Page Setup and Utilities
 * Includes shared functionality for all dashboard pages
 */

// Initialize common functionality when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize theme and UI components
    initializeCommonFeatures();
});

function initializeCommonFeatures() {
    // Add common event listeners and setup
    initializeSharedDropdowns();
    initializeCommonAnimations();
}

// Shared dropdown initialization for pages that don't use ui-components.js
function initializeSharedDropdowns() {
    const userDropdownToggle = document.getElementById('user-dropdown-toggle');
    const userDropdownMenu = document.getElementById('user-dropdown-menu');
    
    if (userDropdownToggle && userDropdownMenu && !window.uiComponents) {
        userDropdownToggle.addEventListener('click', (e) => {
            e.stopPropagation();
            userDropdownMenu.classList.toggle('show');
        });
        
        document.addEventListener('click', (e) => {
            if (!userDropdownToggle.contains(e.target) && !userDropdownMenu.contains(e.target)) {
                userDropdownMenu.classList.remove('show');
            }
        });
        
        userDropdownMenu.addEventListener('click', (e) => {
            e.stopPropagation();
        });
    }
}

// Common animations and effects
function initializeCommonAnimations() {
    // Link hover effects
    document.querySelectorAll('.nav-link, a[href]').forEach(link => {
        if (link.classList.contains('stat-card')) return; // Skip stat cards
        
        link.addEventListener('mouseover', () => {
            if (!link.style.transform) {
                link.style.transform = 'translateY(-1px)';
                link.style.transition = 'transform 0.2s ease';
            }
        });
        
        link.addEventListener('mouseout', () => {
            link.style.transform = 'translateY(0)';
        });
    });
}

// Utility function for number formatting
function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}

// Utility function for uptime formatting
function formatUptime(seconds) {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${days}d ${hours}h ${minutes}m`;
}

// Export utilities for global use
window.dashboardUtils = {
    formatNumber,
    formatUptime,
    initializeCommonFeatures
};
