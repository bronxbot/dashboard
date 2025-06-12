document.addEventListener('DOMContentLoaded', function() {
    // Update uptime counter
    const initialServerTime = Math.floor(Date.now() / 1000);
    let uptimeOffset = 0;
    
    function updateUptime() {
        const uptimeElement = document.getElementById('uptime');
        if (!uptimeElement) return;

        const baseUptime = parseInt(uptimeElement.dataset.uptime);
        // Add the time elapsed since page load
        const currentUptime = baseUptime + uptimeOffset;
        
        const days = Math.floor(currentUptime / 86400);
        const hours = Math.floor((currentUptime % 86400) / 3600);
        const minutes = Math.floor((currentUptime % 3600) / 60);
        const seconds = currentUptime % 60;
        
        uptimeElement.textContent = `${days}d ${hours}h ${minutes}m ${seconds}s`;
        uptimeOffset++;
    }

    // Auto-refresh stats functionality
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
                // Update command count
                const totalCommandsElement = document.getElementById('total-commands');
                if (totalCommandsElement && data.commands) {
                    const newCount = data.commands.total_executed || 0;
                    totalCommandsElement.textContent = formatNumber(newCount);
                    
                    // Add flash effect if count increased
                    const currentCount = parseInt(totalCommandsElement.dataset.count || '0');
                    if (newCount > currentCount) {
                        totalCommandsElement.classList.add('flash-update');
                        setTimeout(() => {
                            totalCommandsElement.classList.remove('flash-update');
                        }, 500);
                    }
                    totalCommandsElement.dataset.count = newCount;
                }
                
                // Update server count
                const serverCountElement = document.getElementById('server-count');
                if (serverCountElement && data.guilds) {
                    const newCount = data.guilds.count || 0;
                    serverCountElement.textContent = formatNumber(newCount);
                    
                    // Add flash effect if count changed
                    const currentCount = parseInt(serverCountElement.dataset.count || '0');
                    if (newCount !== currentCount) {
                        serverCountElement.classList.add('flash-update');
                        setTimeout(() => {
                            serverCountElement.classList.remove('flash-update');
                        }, 500);
                    }
                    serverCountElement.dataset.count = newCount;
                }
                
                // Update today's commands
                const todayCommandsElement = document.getElementById('today-commands');
                if (todayCommandsElement && data.commands && data.commands.daily_metrics) {
                    const today = new Date().toISOString().split('T')[0];
                    const todayMetric = data.commands.daily_metrics.find(m => m.date === today);
                    const todayCount = todayMetric ? todayMetric.count : 0;
                    
                    todayCommandsElement.textContent = formatNumber(todayCount);
                    
                    // Add flash effect if count increased
                    const currentCount = parseInt(todayCommandsElement.dataset.count || '0');
                    if (todayCount > currentCount) {
                        todayCommandsElement.classList.add('flash-update');
                        setTimeout(() => {
                            todayCommandsElement.classList.remove('flash-update');
                        }, 500);
                    }
                    todayCommandsElement.dataset.count = todayCount;
                }
                
                lastStatsUpdate = Date.now();
            })
            .catch(error => {
                console.warn('Failed to update stats:', error);
            });
    }
    
    // Start stats updates (every 5 seconds)
    setInterval(updateStats, 5000);
    
    // Initial stats update after 1 second
    setTimeout(updateStats, 1000);

    // Link hover effect
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('mouseover', () => {
            link.style.transform = 'translateY(-2px)';
        });
        
        link.addEventListener('mouseout', () => {
            link.style.transform = 'translateY(0)';
        });
    });

    // Mobile navigation toggle
    const navToggle = document.getElementById('nav-toggle');
    const navLinks = document.querySelector('.nav-links');
    
    if (navToggle) {
        navToggle.addEventListener('click', () => {
            navLinks.classList.toggle('active');
            navToggle.classList.toggle('active');
        });

        // Close navbar when clicking outside
        document.addEventListener('click', (e) => {
            if (!navLinks.contains(e.target) && 
                !navToggle.contains(e.target) && 
                navLinks.classList.contains('active')) {
                navLinks.classList.remove('active');
                navToggle.classList.remove('active');
            }
        });
    }

    // Collapsible sidebar toggle
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar = document.querySelector('.sidebar.collapsible');
    
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', () => {
            sidebar.classList.toggle('active');
        });

        // Close sidebar when clicking outside
        document.addEventListener('click', (e) => {
            if (!sidebar.contains(e.target) && 
                !sidebarToggle.contains(e.target) && 
                sidebar.classList.contains('active')) {
                sidebar.classList.remove('active');
            }
        });
    }
    
    // Initialize uptime
    setInterval(updateUptime, 1000);
    updateUptime();

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

    // Mobile hamburger menu functionality for home.html
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');
    
    if (mobileMenuButton && mobileMenu) {
        mobileMenuButton.addEventListener('click', () => {
            mobileMenu.classList.toggle('hidden');
            
            // Toggle hamburger icon
            const icon = mobileMenuButton.querySelector('svg path');
            if (mobileMenu.classList.contains('hidden')) {
                // Hamburger icon
                icon.setAttribute('d', 'M4 6h16M4 12h16M4 18h16');
            } else {
                // X icon
                icon.setAttribute('d', 'M6 18L18 6M6 6l12 12');
            }
        });

        // Close mobile menu when clicking outside
        document.addEventListener('click', (e) => {
            if (!mobileMenu.contains(e.target) && 
                !mobileMenuButton.contains(e.target) && 
                !mobileMenu.classList.contains('hidden')) {
                mobileMenu.classList.add('hidden');
                // Reset to hamburger icon
                const icon = mobileMenuButton.querySelector('svg path');
                icon.setAttribute('d', 'M4 6h16M4 12h16M4 18h16');
            }
        });

        // Close mobile menu when clicking on a link
        mobileMenu.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                mobileMenu.classList.add('hidden');
                // Reset to hamburger icon
                const icon = mobileMenuButton.querySelector('svg path');
                icon.setAttribute('d', 'M4 6h16M4 12h16M4 18h16');
            });
        });
    }

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

    // Dark/Light mode toggle functionality with improved deployment compatibility
    const themeToggle = document.getElementById('theme-toggle');
    const sunIcon = document.getElementById('sun-icon');
    const moonIcon = document.getElementById('moon-icon');
    
    // Function to get theme preference with fallback
    function getThemePreference() {
        try {
            return localStorage.getItem('theme') || 'light';
        } catch (e) {
            // Fallback for environments where localStorage might not be available
            console.warn('localStorage not available, using light theme');
            return 'light';
        }
    }
    
    // Function to save theme preference
    function saveThemePreference(theme) {
        try {
            localStorage.setItem('theme', theme);
        } catch (e) {
            console.warn('Unable to save theme preference to localStorage');
        }
    }
    
    // Function to update hero background theme
    function updateHeroTheme(isDark) {
        const heroBackground = document.getElementById('hero-background');
        if (heroBackground) {
            if (isDark) {
                heroBackground.classList.remove('light-theme');
                heroBackground.classList.add('dark-theme');
            } else {
                heroBackground.classList.remove('dark-theme');
                heroBackground.classList.add('light-theme');
            }
        }
    }
    
    // Function to apply theme
    function applyTheme(isDark) {
        if (isDark) {
            document.documentElement.classList.add('dark');
            if (sunIcon) sunIcon.classList.add('hidden');
            if (moonIcon) moonIcon.classList.remove('hidden');
        } else {
            document.documentElement.classList.remove('dark');
            if (sunIcon) sunIcon.classList.remove('hidden');
            if (moonIcon) moonIcon.classList.add('hidden');
        }
        updateHeroTheme(isDark);
    }
    
    // Initialize theme on page load
    function initializeTheme() {
        const currentTheme = getThemePreference();
        const isDark = currentTheme === 'dark';
        applyTheme(isDark);
    }
    
    // Initialize theme immediately to prevent flash
    initializeTheme();
    
    // Toggle theme when button is clicked
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const isDark = document.documentElement.classList.toggle('dark');
            
            // Toggle icons
            if (sunIcon && moonIcon) {
                if (isDark) {
                    sunIcon.classList.add('hidden');
                    moonIcon.classList.remove('hidden');
                } else {
                    sunIcon.classList.remove('hidden');
                    moonIcon.classList.add('hidden');
                }
            }
            
            // Update hero background theme
            updateHeroTheme(isDark);
            
            // Save theme preference
            saveThemePreference(isDark ? 'dark' : 'light');
        });
    }
});
