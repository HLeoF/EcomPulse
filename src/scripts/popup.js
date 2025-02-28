document.addEventListener('DOMContentLoaded', async () => {
    const themeManager = new ThemeManager();
    const priceChart = new PriceChart();
    // 获取当前活动标签页的 URL
    try {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        if (tab?.url) {
            // 将 URL 传递给 PriceChart
            priceChart.submitUrl(tab.url);
        }
    } catch (error) {
        console.error('Error getting current tab:', error);
    }
}); 