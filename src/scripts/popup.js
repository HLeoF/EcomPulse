document.addEventListener('DOMContentLoaded', async () => {
    const themeManager = new ThemeManager();
    const priceChart = new PriceChart();
    
    try{
        const [tab] = await chrome.tabs.query({active:true, currentWindow:true});
        if (tab?.url) {
            priceChart.catchURL(tab.url);
        }
    } catch (error){
        console.error('Error Getting Current Tab: ', error);
    }
}); 