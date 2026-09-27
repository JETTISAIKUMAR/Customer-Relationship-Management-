// Main JavaScript for CRM System

document.addEventListener('DOMContentLoaded', () => {
    // Theme Toggle Functionality
    const themeBtn = document.getElementById('themeToggleBtn');
    if (themeBtn) {
        const savedTheme = localStorage.getItem('crm_theme') || 'light';
        document.documentElement.setAttribute('data-theme', savedTheme);
        updateThemeIcon(savedTheme);

        themeBtn.addEventListener('click', () => {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('crm_theme', newTheme);
            updateThemeIcon(newTheme);
        });
    }

    function updateThemeIcon(theme) {
        if (!themeBtn) return;
        themeBtn.innerHTML = theme === 'dark' ? '☀️' : '🌙';
    }

    // Navbar Activities Dropdown Toggle Functionality
    const activitiesBtn = document.getElementById('activitiesToggleBtn');
    const activitiesPopover = document.getElementById('activitiesPopover');

    if (activitiesBtn && activitiesPopover) {
        activitiesBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            activitiesPopover.classList.toggle('show');
            activitiesBtn.classList.toggle('active');
        });

        // Close activities dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!activitiesPopover.contains(e.target) && !activitiesBtn.contains(e.target)) {
                activitiesPopover.classList.remove('show');
                activitiesBtn.classList.remove('active');
            }
        });

        // Close on Escape key press
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                activitiesPopover.classList.remove('show');
                activitiesBtn.classList.remove('active');
            }
        });
    }

    // Auto-dismiss alert messages after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transition = 'opacity 0.5s ease';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });
});

