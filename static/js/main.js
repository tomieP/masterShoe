/**
 * MasterShoe - Main JavaScript
 * Sidebar toggle and navigation logic using Alpine.js
 */

document.addEventListener('DOMContentLoaded', function () {
    // Initialize Alpine.js component
    Alpine.data('layout', function () {
        return {
            sidebarOpen: window.innerWidth > 991.98,
            isMobile: window.innerWidth <= 991.98,

            init() {
                // Update on window resize
                window.addEventListener('resize', () => {
                    this.isMobile = window.innerWidth <= 991.98;
                    if (window.innerWidth > 991.98) {
                        this.sidebarOpen = true;
                    } else {
                        this.sidebarOpen = false;
                    }
                });

                // Set active nav item on load
                this.updateActiveNavItem();

                // Listen for navigation clicks
                document.querySelectorAll('.sidebar-nav-link').forEach(link => {
                    link.addEventListener('click', () => {
                        if (this.isMobile) {
                            this.sidebarOpen = false;
                        }
                    });
                });
            },

            toggleSidebar() {
                this.sidebarOpen = !this.sidebarOpen;
            },

            closeSidebar() {
                if (this.isMobile) {
                    this.sidebarOpen = false;
                }
            },

            updateActiveNavItem() {
                const currentPath = window.location.pathname;
                const navLinks = document.querySelectorAll('.sidebar-nav-link');

                navLinks.forEach(link => {
                    const href = link.getAttribute('href');
                    if (href && currentPath.startsWith(href)) {
                        link.classList.add('active');
                    } else {
                        link.classList.remove('active');
                    }
                });
            },

            // Helper to check user role
            isManager() {
                const roles = document.body.getAttribute('data-user-roles') || '';
                return roles.includes('Manager');
            },

            isStaff() {
                const roles = document.body.getAttribute('data-user-roles') || '';
                return roles.includes('Staff');
            }
        };
    });

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(link => {
        link.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href !== '#') {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });

    // Handle HTMX for dynamic content loading
    document.addEventListener('htmx:configRequest', function (event) {
        event.detail.headers['X-Requested-With'] = 'XMLHttpRequest';
    });

    // Show loading indicator on HTMX requests
    document.addEventListener('htmx:xhr:loadstart', function (event) {
        console.log('HTMX request started:', event.detail.xhr.url);
    });

    document.addEventListener('htmx:xhr:loadend', function (event) {
        console.log('HTMX request ended:', event.detail.xhr.url);
    });

    // Error handling for HTMX
    document.addEventListener('htmx:responseError', function (event) {
        console.error('HTMX error:', event.detail);
    });
});

// Utility function: Format currency
function formatCurrency(value) {
    return new Intl.NumberFormat('vi-VN', {
        style: 'currency',
        currency: 'VND',
        minimumFractionDigits: 0
    }).format(value);
}

// Utility function: Format date
function formatDate(date, locale = 'vi-VN') {
    if (typeof date === 'string') {
        date = new Date(date);
    }
    return new Intl.DateTimeFormat(locale, {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    }).format(date);
}

// Utility function: Show toast notification
function showToast(message, type = 'info', duration = 3000) {
    const alertClass = `alert-${type}`;
    const toastHTML = `
        <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;

    const toastContainer = document.querySelector('.toast-container') || createToastContainer();
    toastContainer.insertAdjacentHTML('beforeend', toastHTML);

    if (duration) {
        setTimeout(() => {
            const alert = toastContainer.querySelector('.alert:last-child');
            if (alert) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, duration);
    }
}

function createToastContainer() {
    const container = document.createElement('div');
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '9999';
    document.body.appendChild(container);
    return container;
}