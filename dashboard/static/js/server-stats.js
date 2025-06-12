// Server Statistics Modal functionality
function viewStats(guildId) {
    // Create modal overlay
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
    modal.innerHTML = createStatsModalHTML();
    document.body.appendChild(modal);
    
    // Fetch and display stats
    fetchServerStats(guildId);
}

function createStatsModalHTML() {
    return `
        <div class="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div class="flex justify-between items-center mb-4">
                <h3 class="text-xl font-semibold text-gray-900 dark:text-white">Server Statistics</h3>
                <button onclick="closeStatsModal()" class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" viewBox="0 0 256 256">
                        <path d="M205.66,194.34a8,8,0,0,1-11.32,11.32L128,139.31,61.66,205.66a8,8,0,0,1-11.32-11.32L116.69,128,50.34,61.66A8,8,0,0,1,61.66,50.34L128,116.69l66.34-66.35a8,8,0,0,1,11.32,11.32L139.31,128Z"></path>
                    </svg>
                </button>
            </div>
            <div id="stats-content">
                <div class="text-center py-8">
                    <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                    <p class="text-gray-600 dark:text-gray-400 mt-2">Loading stats...</p>
                </div>
            </div>
        </div>
    `;
}

function fetchServerStats(guildId) {
    // Fetch enhanced guild metrics from the new endpoint
    Promise.all([
        fetch(`/api/guild/${guildId}/stats`),
        fetch(`/api/metrics/guild/${guildId}`)
    ])
    .then(responses => Promise.all(responses.map(r => r.json())))
    .then(([basicStats, detailedMetrics]) => {
        // Combine both data sources for comprehensive stats
        const combinedData = {
            ...basicStats,
            ...detailedMetrics,
            // Ensure we have fallback values
            member_count: detailedMetrics.member_count || basicStats.member_count || 'N/A',
            name: detailedMetrics.name || basicStats.name || 'Unknown Server',
            features: detailedMetrics.features || [],
            created_at: detailedMetrics.created_at || null,
            permissions: detailedMetrics.permissions || null
        };
        document.getElementById('stats-content').innerHTML = createStatsContentHTML(combinedData);
    })
    .catch(error => {
        console.error('Error fetching guild stats:', error);
        // Fallback to basic stats only
        fetch(`/api/guild/${guildId}/stats`)
            .then(response => response.json())
            .then(data => {
                document.getElementById('stats-content').innerHTML = createStatsContentHTML(data);
            })
            .catch(err => {
                document.getElementById('stats-content').innerHTML = `
                    <div class="text-center py-8">
                        <p class="text-red-600 dark:text-red-400">Failed to load stats: ${err.message}</p>
                    </div>
                `;
            });
    });
}

function createStatsContentHTML(data) {
    // Helper function to format dates
    const formatDate = (dateString) => {
        if (!dateString) return 'N/A';
        try {
            return new Date(dateString).toLocaleDateString();
        } catch {
            return 'N/A';
        }
    };

    // Helper function to format numbers
    const formatNumber = (num) => {
        if (num === null || num === undefined) return 'N/A';
        return typeof num === 'number' ? num.toLocaleString() : num;
    };

    return `
        <div class="space-y-6">
            <!-- Server Overview -->
            <div class="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 p-4 rounded-lg border border-blue-200 dark:border-blue-800">
                <h4 class="font-semibold text-blue-900 dark:text-blue-100 mb-3 flex items-center">
                    <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                    </svg>
                    Server Overview
                </h4>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div class="text-center">
                        <div class="text-2xl font-bold text-blue-600 dark:text-blue-400">${formatNumber(data.member_count)}</div>
                        <div class="text-sm text-gray-600 dark:text-gray-400">Total Members</div>
                    </div>
                    <div class="text-center">
                        <div class="text-2xl font-bold text-green-600 dark:text-green-400">${data.name || 'Unknown'}</div>
                        <div class="text-sm text-gray-600 dark:text-gray-400">Server Name</div>
                    </div>
                    <div class="text-center">
                        <div class="text-2xl font-bold text-purple-600 dark:text-purple-400">${formatDate(data.created_at)}</div>
                        <div class="text-sm text-gray-600 dark:text-gray-400">Created</div>
                    </div>
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <!-- General Stats -->
                <div class="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
                    <h4 class="font-semibold text-gray-900 dark:text-white mb-3 flex items-center">
                        <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
                        </svg>
                        General Stats
                    </h4>
                    <div class="space-y-3">
                        <div class="flex justify-between items-center">
                            <span class="text-gray-600 dark:text-gray-400">Server ID:</span>
                            <span class="font-medium text-gray-900 dark:text-white font-mono text-sm">${data.id || data.guild_id || 'N/A'}</span>
                        </div>
                        <div class="flex justify-between items-center">
                            <span class="text-gray-600 dark:text-gray-400">Messages Today:</span>
                            <span class="font-medium text-gray-900 dark:text-white">${formatNumber(data.message_count)}</span>
                        </div>
                        <div class="flex justify-between items-center">
                            <span class="text-gray-600 dark:text-gray-400">Active Users:</span>
                            <span class="font-medium text-gray-900 dark:text-white">${formatNumber(data.active_users)}</span>
                        </div>
                        <div class="flex justify-between items-center">
                            <span class="text-gray-600 dark:text-gray-400">Bot Permissions:</span>
                            <span class="font-medium text-gray-900 dark:text-white">${data.permissions ? 'Admin' : 'Limited'}</span>
                        </div>
                    </div>
                </div>

                <!-- Bot Activity -->
                <div class="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
                    <h4 class="font-semibold text-gray-900 dark:text-white mb-3 flex items-center">
                        <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3z"/>
                        </svg>
                        Bot Activity
                    </h4>
                    <div class="space-y-3">
                        <div class="flex justify-between items-center">
                            <span class="text-gray-600 dark:text-gray-400">Commands Used:</span>
                            <span class="font-medium text-gray-900 dark:text-white">${formatNumber(data.commands_used || 0)}</span>
                        </div>
                        <div class="flex justify-between items-center">
                            <span class="text-gray-600 dark:text-gray-400">Last Active:</span>
                            <span class="font-medium text-gray-900 dark:text-white">${data.last_active || 'Recently'}</span>
                        </div>
                        <div class="flex justify-between items-center">
                            <span class="text-gray-600 dark:text-gray-400">Bot Status:</span>
                            <span class="font-medium text-green-600 dark:text-green-400 flex items-center">
                                <div class="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                                Online
                            </span>
                        </div>
                        <div class="flex justify-between items-center">
                            <span class="text-gray-600 dark:text-gray-400">Last Updated:</span>
                            <span class="font-medium text-gray-900 dark:text-white text-sm">${formatDate(data.timestamp || data.last_update)}</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Server Features (if available) -->
            ${data.features && data.features.length > 0 ? `
            <div class="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
                <h4 class="font-semibold text-gray-900 dark:text-white mb-3 flex items-center">
                    <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
                    </svg>
                    Server Features
                </h4>
                <div class="flex flex-wrap gap-2">
                    ${data.features.map(feature => `
                        <span class="px-3 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded-full text-sm font-medium">
                            ${feature.replace(/_/g, ' ').toLowerCase().replace(/\b\w/g, l => l.toUpperCase())}
                        </span>
                    `).join('')}
                </div>
            </div>
            ` : ''}
        </div>
    `;
}

function closeStatsModal() {
    const modal = document.querySelector('.fixed.inset-0');
    if (modal) {
        modal.remove();
    }
}

// Make functions globally available
window.viewStats = viewStats;
window.closeStatsModal = closeStatsModal;
