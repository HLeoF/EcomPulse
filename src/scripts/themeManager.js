class ThemeManager {
    constructor() {
        this.themeSwitch = document.getElementById('theme-switch');
        this.themeStylesheet = document.getElementById('theme-stylesheet');
        this.initTheme();
    }

    initTheme() {
        // 检查本地存储的主题设置
        const isDark = localStorage.getItem('theme') === 'dark';
        this.themeSwitch.checked = isDark;
        this.applyTheme(isDark);

        this.themeSwitch.addEventListener('change', () => {
            this.applyTheme(this.themeSwitch.checked);
        });
    }

    applyTheme(isDark) {
        const body = document.body;
        if (isDark) {
            body.classList.replace('light-theme', 'dark-theme');
            this.themeStylesheet.href = 'styles/dark-theme.css';
        } else {
            body.classList.replace('dark-theme', 'light-theme');
            this.themeStylesheet.href = 'styles/light-theme.css';
        }
        // 保存主题设置到本地存储
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
    }
} 