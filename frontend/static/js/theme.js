/**
 * TalentLens Universal Theme Controller (Dark & Light Mode)
 * - Persists theme preference across sessions in localStorage
 * - Seamlessly syncs between User and Admin portals
 * - Automatically updates toggle buttons, icons, and labels
 */
(function () {
    const THEME_KEY = 'talentlens_theme';

    function getPreferredTheme() {
        const storedTheme = localStorage.getItem(THEME_KEY);
        if (storedTheme) {
            return storedTheme;
        }
        return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }

    function updateToggleButtons(theme) {
        const buttons = document.querySelectorAll('.theme-toggle-btn');
        buttons.forEach(btn => {
            const icon = btn.querySelector('.theme-toggle-icon');
            const label = btn.querySelector('.theme-toggle-label');
            if (theme === 'dark') {
                if (icon) {
                    icon.className = 'fa-solid fa-sun text-warning theme-toggle-icon';
                }
                if (label) {
                    label.textContent = 'Light';
                }
                btn.setAttribute('title', 'Switch to Light Mode');
                btn.setAttribute('aria-label', 'Switch to Light Mode');
            } else {
                if (icon) {
                    icon.className = 'fa-solid fa-moon text-dark theme-toggle-icon';
                }
                if (label) {
                    label.textContent = 'Dark';
                }
                btn.setAttribute('title', 'Switch to Dark Mode');
                btn.setAttribute('aria-label', 'Switch to Dark Mode');
            }
        });
    }

    function applyTheme(theme) {
        document.documentElement.setAttribute('data-bs-theme', theme);
        if (document.body) {
            document.body.setAttribute('data-bs-theme', theme);
        }
        updateToggleButtons(theme);
    }

    // Global toggle function triggered by UI buttons
    window.toggleTheme = function () {
        const currentTheme = document.documentElement.getAttribute('data-bs-theme') || 'light';
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        try {
            localStorage.setItem(THEME_KEY, newTheme);
        } catch (e) {
            console.warn('Could not save theme to localStorage:', e);
        }
        applyTheme(newTheme);
    };

    // Apply immediate attribute to prevent FOUC
    const initial = getPreferredTheme();
    document.documentElement.setAttribute('data-bs-theme', initial);

    // Sync buttons on DOM load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function () {
            applyTheme(getPreferredTheme());
        });
    } else {
        applyTheme(getPreferredTheme());
    }

    // Sync across open tabs
    window.addEventListener('storage', function (e) {
        if (e.key === THEME_KEY && e.newValue) {
            applyTheme(e.newValue);
        }
    });
})();
