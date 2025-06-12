// Guild Metrics Dashboard Enhancement
// This file handles the display of comprehensive guild metrics

class GuildMetricsManager {
    constructor() {
        this.updateInterval = 60000; // Update every minute
        this.lastUpdate = null;
        this.isLoading = false;
    }

    async init() {
        console.log('Initializing Guild Metrics Manager...');
        await this.loadGuildMetrics();
        this.startAutoUpdate();
    }

    async loadGuildMetrics() {
        if (this.isLoading) return;
        this.isLoading = true;

        try {
            const response = await fetch('/api/metrics/guilds');
            const data = await response.json();
            
            if (response.ok) {
                this.updateGuildDisplay(data);
                this.lastUpdate = new Date();
            } else {
                console.error('Error loading guild metrics:', data.error);
                this.showError('Failed to load guild metrics');
            }
        } catch (error) {
            console.error('Network error loading guild metrics:', error);
            this.showError('Network error loading guild metrics');
        } finally {
            this.isLoading = false;
        }
    }

    updateGuildDisplay(data) {
        // Update main guild count
        const guildCountElement = document.getElementById('server-count');
        if (guildCountElement) {
            guildCountElement.textContent = data.guild_count || 0;
            guildCountElement.setAttribute('data-count', data.guild_count || 0);
        }

        // Update total members across all guilds
        const totalMembersElement = document.getElementById('total-members');
        if (totalMembersElement) {
            totalMembersElement.textContent = (data.total_members || 0).toLocaleString();
        }

        // Update guild features statistics
        this.updateFeatureStats(data.feature_statistics || {});

        // Update recent guild activity
        this.updateGuildActivity(data.guild_history || []);

        // Add timestamp info
        this.updateLastRefresh(data.timestamp);

        console.log('Guild metrics updated successfully');
    }

    updateFeatureStats(features) {
        const featureContainer = document.getElementById('guild-features');
        if (!featureContainer) return;

        const sortedFeatures = Object.entries(features)
            .sort(([,a], [,b]) => b - a)
            .slice(0, 5); // Top 5 features

        featureContainer.innerHTML = sortedFeatures.map(([feature, count]) => `
            <div class="flex justify-between items-center py-2 border-b border-gray-200 dark:border-gray-600 last:border-b-0">
                <span class="text-sm text-gray-600 dark:text-gray-400">
                    ${feature.replace(/_/g, ' ').toLowerCase().replace(/\b\w/g, l => l.toUpperCase())}
                </span>
                <span class="text-sm font-medium text-gray-900 dark:text-white">${count}</span>
            </div>
        `).join('') || '<p class="text-gray-500 dark:text-gray-400 text-sm">No feature data available</p>';
    }

    updateGuildActivity(history) {
        const activityContainer = document.getElementById('guild-activity');
        if (!activityContainer) return;

        const recentActivity = history.slice(-5).reverse(); // Last 5 entries, most recent first

        activityContainer.innerHTML = recentActivity.map(entry => {
            const date = new Date(entry.timestamp || entry.date);
            const timeAgo = this.getTimeAgo(date);
            
            return `
                <div class="flex justify-between items-center py-2 border-b border-gray-200 dark:border-gray-600 last:border-b-0">
                    <div>
                        <span class="text-sm font-medium text-gray-900 dark:text-white">${entry.count || 0} servers</span>
                        <div class="text-xs text-gray-500 dark:text-gray-400">${timeAgo}</div>
                    </div>
                    <div class="text-xs text-gray-500 dark:text-gray-400">
                        ${date.toLocaleDateString()}
                    </div>
                </div>
            `;
        }).join('') || '<p class="text-gray-500 dark:text-gray-400 text-sm">No activity data available</p>';
    }

    updateLastRefresh(timestamp) {
        const refreshElement = document.getElementById('last-refresh');
        if (refreshElement && timestamp) {
            const date = new Date(timestamp);
            refreshElement.textContent = `Last updated: ${date.toLocaleTimeString()}`;
        }
    }

    getTimeAgo(date) {
        const now = new Date();
        const diff = now - date;
        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(diff / 3600000);
        const days = Math.floor(diff / 86400000);

        if (days > 0) return `${days}d ago`;
        if (hours > 0) return `${hours}h ago`;
        if (minutes > 0) return `${minutes}m ago`;
        return 'Just now';
    }

    showError(message) {
        // Create or update error display
        const errorContainer = document.getElementById('guild-metrics-error');
        if (errorContainer) {
            errorContainer.innerHTML = `
                <div class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-800 dark:text-red-200 px-4 py-3 rounded-lg">
                    <div class="flex items-center">
                        <svg class="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/>
                        </svg>
                        <span class="text-sm">${message}</span>
                    </div>
                </div>
            `;
        }
    }

    startAutoUpdate() {
        setInterval(() => {
            if (!this.isLoading) {
                this.loadGuildMetrics();
            }
        }, this.updateInterval);
    }

    // Manual refresh function
    async refresh() {
        await this.loadGuildMetrics();
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.guildMetrics = new GuildMetricsManager();
    window.guildMetrics.init();
});

// Make refresh function globally available
window.refreshGuildMetrics = () => {
    if (window.guildMetrics) {
        window.guildMetrics.refresh();
    }
};
