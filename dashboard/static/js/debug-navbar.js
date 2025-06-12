// Debug script for navbar issues
console.log('BronxBot Dashboard - Debug Script Loaded');

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM Content Loaded');
    
    // Check if critical elements exist
    const themeToggle = document.getElementById('theme-toggle');
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const userDropdown = document.getElementById('user-dropdown-toggle');
    
    console.log('Theme Toggle:', themeToggle ? 'Found' : 'Missing');
    console.log('Mobile Menu Button:', mobileMenuButton ? 'Found' : 'Missing');
    console.log('User Dropdown:', userDropdown ? 'Found' : 'Missing');
    
    // Check if navbar structure is complete
    const navbar = document.querySelector('header');
    if (navbar) {
        console.log('Navbar found, checking structure...');
        const logo = navbar.querySelector('img[alt="BronxBot Logo"]');
        const navLinks = navbar.querySelectorAll('a');
        console.log('Logo:', logo ? 'Found' : 'Missing');
        console.log('Navigation links:', navLinks.length);
    } else {
        console.error('Navbar not found!');
    }
    
    // Force light theme if dark theme elements are missing
    if (!document.getElementById('sun-icon') || !document.getElementById('moon-icon')) {
        console.warn('Theme icons missing, forcing light theme');
        document.documentElement.classList.remove('dark');
    }
});

// Export debug info for manual checking
window.debugNavbar = function() {
    const info = {
        themeToggle: !!document.getElementById('theme-toggle'),
        mobileMenu: !!document.getElementById('mobile-menu-button'),
        userDropdown: !!document.getElementById('user-dropdown-toggle'),
        navbarExists: !!document.querySelector('header'),
        logoExists: !!document.querySelector('img[alt="BronxBot Logo"]'),
        linkCount: document.querySelectorAll('header a').length
    };
    console.table(info);
    return info;
};
