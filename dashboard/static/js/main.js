// Global functions for use across different templates
// Number counting animation function
function animateNumber(element, startValue, endValue, duration = 1000, useCommas = false) {
    const startTime = performance.now();
    const difference = endValue - startValue;
    
    function updateNumber(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Use easing function for smooth animation
        const easeProgress = 1 - Math.pow(1 - progress, 3);
        const currentValue = Math.round(startValue + (difference * easeProgress));
        
        // Format number based on useCommas parameter
        if (useCommas) {
            element.textContent = currentValue.toLocaleString();
        } else {
            element.textContent = formatNumber(currentValue);
        }
        
        if (progress < 1) {
            requestAnimationFrame(updateNumber);
        }
    }
    
    requestAnimationFrame(updateNumber);
}

// Format number function
function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}

document.addEventListener('DOMContentLoaded', function() {
    // Real-time uptime tracking
    let uptimeStartTime = null;
    let uptimeInterval = null;
    let lastCommandUpdate = 0;
    
    // Enhanced uptime update function with real-time calculation
    function updateUptime() {
        const uptimeElement = document.getElementById('uptime');
        if (!uptimeElement || !uptimeStartTime) return;

        // Calculate current uptime from start time
        const currentTime = Date.now() / 1000;
        const totalSeconds = Math.floor(currentTime - uptimeStartTime);
        
        const days = Math.floor(totalSeconds / 86400);
        const hours = Math.floor((totalSeconds % 86400) / 3600);
        const minutes = Math.floor((totalSeconds % 3600) / 60);
        const seconds = totalSeconds % 60;
        
        uptimeElement.textContent = `${days}d ${hours}h ${minutes}m ${seconds}s`;
    }

    // Auto-refresh stats functionality with enhanced animations
    let lastStatsUpdate = Date.now();
    
    function formatNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    }
    
    function updateStats() {
        fetch('/api/stats')
            .then(response => response.json())
            .then(data => {
                // Update uptime start time if available
                if (data.uptime && data.uptime.start_time) {
                    if (!uptimeStartTime) {
                        uptimeStartTime = data.uptime.start_time;
                        // Start real-time uptime updates every second
                        if (!uptimeInterval) {
                            uptimeInterval = setInterval(updateUptime, 1000);
                            updateUptime(); // Initial update
                        }
                    }
                }
                
                // Update command count with animation
                const totalCommandsElement = document.getElementById('total-commands');
                if (totalCommandsElement && data.commands) {
                    const newCount = data.commands.total_executed || 0;
                    const currentCount = parseInt(totalCommandsElement.dataset.count || '0');
                    
                    if (newCount !== currentCount) {
                        // Animate the number change
                        animateNumber(totalCommandsElement, currentCount, newCount, 800);
                        
                        // Add flash effect
                        totalCommandsElement.classList.add('flash-update');
                        setTimeout(() => {
                            totalCommandsElement.classList.remove('flash-update');
                        }, 800);
                    }
                    totalCommandsElement.dataset.count = newCount;
                }
                
                // Update server count with animation
                const serverCountElement = document.getElementById('server-count');
                if (serverCountElement && data.guilds) {
                    const newCount = data.guilds.count || 0;
                    const currentCount = parseInt(serverCountElement.dataset.count || '0');
                    
                    if (newCount !== currentCount) {
                        animateNumber(serverCountElement, currentCount, newCount, 600);
                        
                        // Add flash effect
                        serverCountElement.classList.add('flash-update');
                        setTimeout(() => {
                            serverCountElement.classList.remove('flash-update');
                        }, 600);
                    }
                    serverCountElement.dataset.count = newCount;
                }
                
                // Update user count with animation
                const userCountElement = document.getElementById('user-count');
                if (userCountElement && data.performance) {
                    const newCount = data.performance.user_count || 0;
                    const currentCount = parseInt(userCountElement.dataset.count || '0');
                    
                    if (newCount !== currentCount) {
                        animateNumber(userCountElement, currentCount, newCount, 700);
                        userCountElement.classList.add('flash-update');
                        setTimeout(() => {
                            userCountElement.classList.remove('flash-update');
                        }, 700);
                    }
                    userCountElement.dataset.count = newCount;
                }
                
                // Update today's commands with animation
                const todayCommandsElement = document.getElementById('today-commands');
                if (todayCommandsElement && data.commands && data.commands.daily_metrics) {
                    const today = new Date().toISOString().split('T')[0];
                    const todayMetric = data.commands.daily_metrics.find(m => m.date === today);
                    const todayCount = todayMetric ? todayMetric.count : 0;
                    const currentCount = parseInt(todayCommandsElement.dataset.count || '0');
                    
                    if (todayCount !== currentCount) {
                        animateNumber(todayCommandsElement, currentCount, todayCount, 500);
                        
                        // Add flash effect
                        todayCommandsElement.classList.add('flash-update');
                        setTimeout(() => {
                            todayCommandsElement.classList.remove('flash-update');
                        }, 500);
                    }
                    todayCommandsElement.dataset.count = todayCount;
                }
                
                // Update latency with animation
                const latencyElement = document.querySelector('[data-metric="latency"]');
                if (latencyElement && data.performance && data.performance.latency !== undefined) {
                    const newLatency = parseFloat(data.performance.latency);
                    const currentLatency = parseFloat(latencyElement.dataset.latency || '0');
                    
                    if (Math.abs(newLatency - currentLatency) > 0.1) {
                        // Animate latency change
                        const startTime = performance.now();
                        const difference = newLatency - currentLatency;
                        
                        function updateLatency(currentTime) {
                            const elapsed = currentTime - startTime;
                            const progress = Math.min(elapsed / 500, 1);
                            const easeProgress = 1 - Math.pow(1 - progress, 3);
                            const currentValue = currentLatency + (difference * easeProgress);
                            
                            latencyElement.textContent = `${currentValue.toFixed(1)}ms`;
                            
                            if (progress < 1) {
                                requestAnimationFrame(updateLatency);
                            }
                        }
                        
                        requestAnimationFrame(updateLatency);
                        latencyElement.dataset.latency = newLatency;
                    }
                }
                
                // Update memory usage with animation
                const memoryElement = document.querySelector('[data-metric="memory"]');
                if (memoryElement && data.performance && data.performance.memory_usage !== undefined) {
                    const newMemory = parseFloat(data.performance.memory_usage);
                    const currentMemory = parseFloat(memoryElement.dataset.memory || '0');
                    
                    if (Math.abs(newMemory - currentMemory) > 0.1) {
                        // Animate memory change
                        const startTime = performance.now();
                        const difference = newMemory - currentMemory;
                        
                        function updateMemory(currentTime) {
                            const elapsed = currentTime - startTime;
                            const progress = Math.min(elapsed / 600, 1);
                            const easeProgress = 1 - Math.pow(1 - progress, 3);
                            const currentValue = currentMemory + (difference * easeProgress);
                            
                            memoryElement.textContent = `${currentValue.toFixed(1)} MB`;
                            
                            if (progress < 1) {
                                requestAnimationFrame(updateMemory);
                            }
                        }
                        
                        requestAnimationFrame(updateMemory);
                        memoryElement.dataset.memory = newMemory;
                    }
                }
                
                // Update CPU usage with animation
                const cpuElement = document.querySelector('[data-metric="cpu"]');
                if (cpuElement && data.performance && data.performance.cpu_usage !== undefined) {
                    const newCpu = parseFloat(data.performance.cpu_usage);
                    const currentCpu = parseFloat(cpuElement.dataset.cpu || '0');
                    
                    if (Math.abs(newCpu - currentCpu) > 0.1) {
                        // Animate CPU change
                        const startTime = performance.now();
                        const difference = newCpu - currentCpu;
                        
                        function updateCpu(currentTime) {
                            const elapsed = currentTime - startTime;
                            const progress = Math.min(elapsed / 700, 1);
                            const easeProgress = 1 - Math.pow(1 - progress, 3);
                            const currentValue = currentCpu + (difference * easeProgress);
                            
                            cpuElement.textContent = `${currentValue.toFixed(1)}%`;
                            
                            if (progress < 1) {
                                requestAnimationFrame(updateCpu);
                            }
                        }
                        
                        requestAnimationFrame(updateCpu);
                        cpuElement.dataset.cpu = newCpu;
                    }
                }
                
                lastStatsUpdate = Date.now();
                
                // Also update charts and metrics if we're on the dev dashboard
                if (typeof updateMetricsAndChart === 'function') {
                    updateMetricsAndChart();
                }
            })
            .catch(error => {
                console.warn('Failed to update stats:', error);
            });
    }
    
    // Start stats updates (every 5 seconds)
    setInterval(updateStats, 5000);
    
    // Initial stats update after 1 second
    setTimeout(updateStats, 1000);

    // Prefix Management
    const prefixInput = document.getElementById('newPrefix');
    const prefixContainer = document.getElementById('prefixContainer');
    const prefixesHiddenInput = document.getElementById('prefixesInput');
    
    if (prefixInput && prefixContainer) {
        // Add new prefix
        prefixInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                const prefix = prefixInput.value.trim();
                if (prefix && !getPrefixes().includes(prefix)) {
                    addPrefix(prefix);
                    prefixInput.value = '';
                    updatePrefixCounter();
                }
            }
        });

        // Remove prefix
        prefixContainer.addEventListener('click', (e) => {
            if (e.target.classList.contains('prefix-tag') || e.target.classList.contains('remove-prefix')) {
                const button = e.target.closest('.prefix-tag');
                if (button && getPrefixes().length > 1) {  // Prevent removing last prefix
                    button.style.animation = 'slideIn 0.3s ease reverse';
                    setTimeout(() => {
                        button.remove();
                        updatePrefixCounter();
                        updateHiddenInput();
                    }, 300);
                }
            }
        });

        function addPrefix(prefix) {
            const button = document.createElement('button');
            button.type = 'button';
            button.className = 'prefix-tag';
            button.dataset.prefix = prefix;
            button.innerHTML = `${prefix}<span class="remove-prefix">×</span>`;
            prefixContainer.appendChild(button);
            updateHiddenInput();
        }

        function getPrefixes() {
            return Array.from(prefixContainer.children).map(btn => btn.dataset.prefix);
        }

        function updateHiddenInput() {
            prefixesHiddenInput.value = getPrefixes().join(',');
        }

        function updatePrefixCounter() {
            const counter = document.querySelector('.prefix-counter');
            if (counter) {
                const count = getPrefixes().length;
                counter.textContent = `${count} total ${count === 1 ? 'prefix' : 'prefixes'}`;
            }
        }
    }

    // Mobile menu functionality is now handled by ui-components.js

    // Hero background scroll animation
    const heroBackground = document.getElementById('hero-background');
    
    if (heroBackground) {
        let ticking = false;
        
        function updateHeroBackground() {
            const scrollY = window.scrollY;
            const speed = 0.5; // Control the parallax speed
            const rotation = scrollY * 0.1; // Rotation effect
            
            // Create parallax and rotation effect
            const transform = `translate(-55px, ${-15 - scrollY * speed}px) rotate(${rotation}deg)`;
            
            // Update the SVG pattern transform
            const currentStyle = heroBackground.style.background;
            const updatedStyle = currentStyle.replace(
                /transform="translate\([^"]*\)"/,
                `transform="${transform}"`
            );
            
            heroBackground.style.background = updatedStyle;
            ticking = false;
        }
        
        function requestTicker() {
            if (!ticking) {
                requestAnimationFrame(updateHeroBackground);
                ticking = true;
            }
        }
        
        // Add scroll event listener with throttling
        window.addEventListener('scroll', requestTicker, { passive: true });
        
        // Add floating animation with CSS
        heroBackground.style.animation = 'heroFloat 6s ease-in-out infinite';
    }

    // Cursor interaction for hero background
    const heroSection = document.querySelector('.hero-background');
    const cursorOverlay = document.getElementById('cursor-overlay');
    
    if (heroSection && cursorOverlay) {
        let mouseX = 0;
        let mouseY = 0;
        let isMouseInHero = false;
        
        // Update cursor position
        function updateCursorPosition(e) {
            const rect = heroSection.getBoundingClientRect();
            mouseX = e.clientX - rect.left;
            mouseY = e.clientY - rect.top;
            
            // Update CSS custom properties for cursor effect
            cursorOverlay.style.setProperty('--mouse-x', `${mouseX}px`);
            cursorOverlay.style.setProperty('--mouse-y', `${mouseY}px`);
        }
        
        // Mouse enter hero section
        heroSection.addEventListener('mouseenter', (e) => {
            isMouseInHero = true;
            cursorOverlay.style.opacity = '1';
            updateCursorPosition(e);
        });
        
        // Mouse move in hero section
        heroSection.addEventListener('mousemove', (e) => {
            if (isMouseInHero) {
                updateCursorPosition(e);
            }
        });
        
        // Mouse leave hero section
        heroSection.addEventListener('mouseleave', () => {
            isMouseInHero = false;
            cursorOverlay.style.opacity = '0';
        });
        
        // Add ripple effect on click
        heroSection.addEventListener('click', (e) => {
            if (isMouseInHero) {
                const rect = heroSection.getBoundingClientRect();
                const clickX = e.clientX - rect.left;
                const clickY = e.clientY - rect.top;
                
                // Create ripple element
                const ripple = document.createElement('div');
                ripple.className = 'cursor-ripple';
                ripple.style.left = `${clickX}px`;
                ripple.style.top = `${clickY}px`;
                
                heroSection.appendChild(ripple);
                
                // Remove ripple after animation
                setTimeout(() => {
                    if (ripple.parentNode) {
                        ripple.parentNode.removeChild(ripple);
                    }
                }, 600);
            }
        });
    }

    // Dark/Light mode toggle functionality is now handled by theme-handler.js
});
