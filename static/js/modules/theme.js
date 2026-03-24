export function initTheme() {
    const toggleBtn = document.getElementById('theme-toggle');
    const icon = toggleBtn ? toggleBtn.querySelector('i') : null;
    
    function updateIcon(theme) {
        if (!icon) return;
        if (theme === 'dark') {
            icon.className = 'fas fa-sun';
            icon.style.color = '#ffc107'; // Sun color
        } else {
            icon.className = 'fas fa-moon';
            icon.style.color = 'inherit';
        }
    }

    // Initial icon setup
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
    updateIcon(currentTheme);

    if (toggleBtn) {
        toggleBtn.addEventListener('click', (e) => {
            e.preventDefault();
            let theme = document.documentElement.getAttribute('data-theme');
            if (theme === 'dark') {
                document.documentElement.removeAttribute('data-theme');
                localStorage.setItem('theme', 'light');
                updateIcon('light');
            } else {
                document.documentElement.setAttribute('data-theme', 'dark');
                localStorage.setItem('theme', 'dark');
                updateIcon('dark');
            }
        });
    }
}
