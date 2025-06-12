/**
 * Common UI Components and Interactions
 * Handles dropdowns, mobile menus, and other shared UI functionality
 */

class UIComponents {
    constructor() {
        this.dropdowns = new Map();
        this.mobileMenus = new Map();
        
        this.init();
    }
    
    init() {
        // Initialize all UI components when DOM is ready
        this.initDropdowns();
        this.initMobileMenus();
        this.initClickOutsideHandlers();
    }
    
    // Initialize dropdown functionality
    initDropdowns() {
        // User dropdown
        const userDropdownToggle = document.getElementById('user-dropdown-toggle');
        const userDropdownMenu = document.getElementById('user-dropdown-menu');
        
        if (userDropdownToggle && userDropdownMenu) {
            this.dropdowns.set('user', {
                toggle: userDropdownToggle,
                menu: userDropdownMenu
            });
            
            userDropdownToggle.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleDropdown('user');
            });
            
            // Prevent dropdown from closing when clicking inside menu
            userDropdownMenu.addEventListener('click', (e) => {
                e.stopPropagation();
            });
        }
        
        // Generic dropdown handler for any dropdown with data-dropdown attribute
        document.querySelectorAll('[data-dropdown]').forEach(toggle => {
            const dropdownId = toggle.getAttribute('data-dropdown');
            const menu = document.getElementById(dropdownId);
            
            if (menu) {
                this.dropdowns.set(dropdownId, {
                    toggle: toggle,
                    menu: menu
                });
                
                toggle.addEventListener('click', (e) => {
                    e.stopPropagation();
                    this.toggleDropdown(dropdownId);
                });
                
                menu.addEventListener('click', (e) => {
                    e.stopPropagation();
                });
            }
        });
    }
    
    // Initialize mobile menu functionality
    initMobileMenus() {
        // Standard mobile menu
        const mobileMenuButton = document.getElementById('mobile-menu-button');
        const mobileMenu = document.getElementById('mobile-menu');
        
        if (mobileMenuButton && mobileMenu) {
            this.mobileMenus.set('main', {
                button: mobileMenuButton,
                menu: mobileMenu
            });
            
            mobileMenuButton.addEventListener('click', () => {
                this.toggleMobileMenu('main');
            });
            
            // Close mobile menu when clicking on a link
            mobileMenu.querySelectorAll('a').forEach(link => {
                link.addEventListener('click', () => {
                    this.closeMobileMenu('main');
                });
            });
        }
        
        // Mobile menu toggle (alternative naming)
        const mobileMenuToggle = document.getElementById('mobile-menu-toggle');
        const mobileMenuAlt = document.getElementById('mobile-menu');
        
        if (mobileMenuToggle && mobileMenuAlt && !mobileMenuButton) {
            this.mobileMenus.set('main', {
                button: mobileMenuToggle,
                menu: mobileMenuAlt
            });
            
            mobileMenuToggle.addEventListener('click', () => {
                this.toggleMobileMenu('main');
            });
        }
        
        // Navigation toggle for older style menus
        const navToggle = document.getElementById('nav-toggle');
        const navLinks = document.querySelector('.nav-links');
        
        if (navToggle && navLinks) {
            this.mobileMenus.set('nav', {
                button: navToggle,
                menu: navLinks
            });
            
            navToggle.addEventListener('click', () => {
                navLinks.classList.toggle('active');
                navToggle.classList.toggle('active');
            });
        }
        
        // Sidebar toggle
        const sidebarToggle = document.getElementById('sidebar-toggle');
        const sidebar = document.querySelector('.sidebar.collapsible');
        
        if (sidebarToggle && sidebar) {
            this.mobileMenus.set('sidebar', {
                button: sidebarToggle,
                menu: sidebar
            });
            
            sidebarToggle.addEventListener('click', () => {
                sidebar.classList.toggle('active');
            });
        }
    }
    
    // Initialize click outside handlers
    initClickOutsideHandlers() {
        document.addEventListener('click', (e) => {
            // Close all dropdowns when clicking outside
            this.dropdowns.forEach((dropdown, id) => {
                if (!dropdown.toggle.contains(e.target) && 
                    !dropdown.menu.contains(e.target)) {
                    this.closeDropdown(id);
                }
            });
            
            // Close mobile menus when clicking outside
            this.mobileMenus.forEach((menu, id) => {
                if (menu.menu && menu.button && 
                    !menu.menu.contains(e.target) && 
                    !menu.button.contains(e.target)) {
                    
                    if (id === 'main') {
                        this.closeMobileMenu(id);
                    } else if (id === 'nav' && menu.menu.classList.contains('active')) {
                        menu.menu.classList.remove('active');
                        menu.button.classList.remove('active');
                    } else if (id === 'sidebar' && menu.menu.classList.contains('active')) {
                        menu.menu.classList.remove('active');
                    }
                }
            });
        });
    }
    
    // Toggle dropdown by ID
    toggleDropdown(dropdownId) {
        const dropdown = this.dropdowns.get(dropdownId);
        if (!dropdown) return;
        
        // Close other dropdowns first
        this.dropdowns.forEach((otherDropdown, otherId) => {
            if (otherId !== dropdownId) {
                this.closeDropdown(otherId);
            }
        });
        
        // Toggle current dropdown
        dropdown.menu.classList.toggle('show');
    }
    
    // Close dropdown by ID
    closeDropdown(dropdownId) {
        const dropdown = this.dropdowns.get(dropdownId);
        if (dropdown) {
            dropdown.menu.classList.remove('show');
        }
    }
    
    // Close all dropdowns
    closeAllDropdowns() {
        this.dropdowns.forEach((dropdown, id) => {
            this.closeDropdown(id);
        });
    }
    
    // Toggle mobile menu by ID
    toggleMobileMenu(menuId) {
        const menu = this.mobileMenus.get(menuId);
        if (!menu) return;
        
        if (menuId === 'main') {
            menu.menu.classList.toggle('hidden');
            this.updateMobileMenuIcon(menu.button, !menu.menu.classList.contains('hidden'));
        }
    }
    
    // Close mobile menu by ID
    closeMobileMenu(menuId) {
        const menu = this.mobileMenus.get(menuId);
        if (!menu) return;
        
        if (menuId === 'main') {
            menu.menu.classList.add('hidden');
            this.updateMobileMenuIcon(menu.button, false);
        }
    }
    
    // Update mobile menu icon (hamburger/X)
    updateMobileMenuIcon(button, isOpen) {
        const icon = button.querySelector('svg path');
        if (icon) {
            if (isOpen) {
                // X icon  
                icon.setAttribute('d', 'M6 18L18 6M6 6l12 12');
            } else {
                // Hamburger icon
                icon.setAttribute('d', 'M4 6h16M4 12h16M4 18h16');
            }
        }
    }
}

// Initialize UI components when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.uiComponents = new UIComponents();
});

// Also initialize immediately if DOM is already loaded
if (document.readyState === 'loading') {
    // DOM is still loading, wait for DOMContentLoaded
} else {
    // DOM is already loaded
    window.uiComponents = new UIComponents();
}
