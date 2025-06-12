/**
 * Flash of Unstyled Content (FOUC) Prevention
 * This script runs immediately to prevent theme flashing
 * Must be included inline in the <head> before any other styles
 */

(function() {
    'use strict';
    
    // Prevent FOUC by setting theme class immediately
    function preventFOUC() {
        try {
            const theme = localStorage.getItem('theme') || 'light';
            if (theme === 'dark') {
                document.documentElement.classList.add('dark');
            }
        } catch (e) {
            // Fallback for environments without localStorage
            // Check system preference
            if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
                document.documentElement.classList.add('dark');
            }
        }
    }
    
    // Run immediately
    preventFOUC();
    
    // Also export for manual use if needed
    window.preventFOUC = preventFOUC;
})();
