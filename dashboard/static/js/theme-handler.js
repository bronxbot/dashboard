/**
 * Centralized Theme Management System
 * Handles dark/light mode toggle functionality with improved deployment compatibility
 */

class ThemeManager {
    constructor() {
        this.themeToggle = null;
        this.sunIcon = null;
        this.moonIcon = null;
        this.heroBackground = null;
        
        this.init();
    }
    
    init() {
        // Get DOM elements
        this.themeToggle = document.getElementById('theme-toggle');
        this.sunIcon = document.getElementById('sun-icon');
        this.moonIcon = document.getElementById('moon-icon');
        this.heroBackground = document.getElementById('hero-background');
        
        // Initialize theme immediately to prevent flash
        this.initializeTheme();
        
        // Add event listener for theme toggle
        if (this.themeToggle) {
            this.themeToggle.addEventListener('click', () => this.toggleTheme());
        }
    }
    
    // Function to get theme preference with fallback
    getThemePreference() {
        try {
            return localStorage.getItem('theme') || 'light';
        } catch (e) {
            // Fallback for environments where localStorage might not be available 
            console.warn('localStorage not available, using light theme');
            return 'light';
        }
    }
    
    // Function to save theme preference
    saveThemePreference(theme) {
        try {
            localStorage.setItem('theme', theme);
        } catch (e) {
            console.warn('Unable to save theme preference to localStorage');
        }
    }
    
    // Function to update hero background theme (if exists)
    updateHeroTheme(isDark) {
        if (this.heroBackground) {
            if (isDark) {
                this.heroBackground.classList.remove('light-theme');
                this.heroBackground.classList.add('dark-theme');
            } else {
                this.heroBackground.classList.remove('dark-theme');  
                this.heroBackground.classList.add('light-theme');
            }
        }
    }
    
    // Function to update theme icons
    updateThemeIcons(isDark) {
        if (this.sunIcon && this.moonIcon) {
            if (isDark) {
                this.sunIcon.classList.add('hidden');
                this.moonIcon.classList.remove('hidden');
            } else {
                this.sunIcon.classList.remove('hidden');
                this.moonIcon.classList.add('hidden');
            }
        }
    }
    
    // Function to apply theme
    applyTheme(isDark) {
        if (isDark) {
            document.documentElement.classList.add('dark');
        } else {
            document.documentElement.classList.remove('dark');
        }
        
        this.updateThemeIcons(isDark);
        this.updateHeroTheme(isDark);
        
        // Trigger custom event for components that need to react to theme changes
        window.dispatchEvent(new CustomEvent('themeChanged', { 
            detail: { isDark: isDark } 
        }));
    }
    
    // Initialize theme on page load
    initializeTheme() {
        const currentTheme = this.getThemePreference();
        const isDark = currentTheme === 'dark';
        this.applyTheme(isDark);
    }
    
    // Toggle theme when button is clicked
    toggleTheme() {
        const isDark = document.documentElement.classList.toggle('dark');
        
        this.updateThemeIcons(isDark);
        this.updateHeroTheme(isDark);
        this.saveThemePreference(isDark ? 'dark' : 'light');
        
        // Trigger custom event for components that need to react to theme changes
        window.dispatchEvent(new CustomEvent('themeChanged', { 
            detail: { isDark: isDark } 
        }));
    }
    
    // Get current theme state
    isDarkMode() {
        return document.documentElement.classList.contains('dark');
    }
}

// Initialize theme manager when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.themeManager = new ThemeManager();
});

// Also initialize immediately if DOM is already loaded
if (document.readyState === 'loading') {
    // DOM is still loading, wait for DOMContentLoaded
} else {
    // DOM is already loaded
    window.themeManager = new ThemeManager();
}
