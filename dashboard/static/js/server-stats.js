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
    fetch(`/api/guild/${guildId}/stats`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('stats-content').innerHTML = createStatsContentHTML(data);
        })
        .catch(error => {
            document.getElementById('stats-content').innerHTML = `
                <div class="text-center py-8">
                    <p class="text-red-600 dark:text-red-400">Failed to load stats</p>
                </div>
            `;
        });
}

function createStatsContentHTML(data) {
    return `
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
                <h4 class="font-semibold text-gray-900 dark:text-white mb-2">General Stats</h4>
                <div class="space-y-2">
                    <div class="flex justify-between">
                        <span class="text-gray-600 dark:text-gray-400">Total Members:</span>
                        <span class="font-medium text-gray-900 dark:text-white">${data.member_count || 'N/A'}</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-gray-600 dark:text-gray-400">Messages Today:</span>
                        <span class="font-medium text-gray-900 dark:text-white">${data.message_count || 'N/A'}</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-gray-600 dark:text-gray-400">Active Users:</span>
                        <span class="font-medium text-gray-900 dark:text-white">${data.active_users || 'N/A'}</span>
                    </div>
                </div>
            </div>
            <div class="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
                <h4 class="font-semibold text-gray-900 dark:text-white mb-2">Bot Activity</h4>
                <div class="space-y-2">
                    <div class="flex justify-between">
                        <span class="text-gray-600 dark:text-gray-400">Commands Used:</span>
                        <span class="font-medium text-gray-900 dark:text-white">${data.commands_used || '0'}</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-gray-600 dark:text-gray-400">Last Active:</span>
                        <span class="font-medium text-gray-900 dark:text-white">${data.last_active || 'Recently'}</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-gray-600 dark:text-gray-400">Status:</span>
                        <span class="font-medium text-green-600 dark:text-green-400">Online</span>
                    </div>
                </div>
            </div>
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
