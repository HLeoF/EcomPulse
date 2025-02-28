class PriceChart {
    constructor() {
        this.chart = null;
        this.fullData = null;
        this.priceComparison = new PriceComparison();
        this.initChart();
        this.initTimeRangeSelector();
    }
    
    async submitUrl(url) {
        try {
            const response = await fetch('http://localhost:5000/submit-url', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url: url })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            this.fullData = await response.json();
            this.updateProductInfo(this.fullData['history_price']);
            this.updateChartData();

            if(this.fullData['lowest_price']){
                this.priceComparison.updatePriceCards(this.fullData['lowest_price'])
            }

        } catch (error) {
            console.error('Error submitting URL:', error)
            if (this.fullData == null) {
                 // 使用 alert 显示错误信息
                alert('无法获取商品数据，请稍后重试');
            }
        }
    }

    initChart() {
        const ctx = document.getElementById('priceChart').getContext('2d');
        this.chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: '价格',
                    data: [],
                    borderColor: '#4CAF50',
                    backgroundColor: 'rgba(76, 175, 80, 0.1)',
                    tension: 0.1,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `¥${context.parsed.y.toFixed(2)}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        type: 'category',
                        grid: {
                            display: false
                        },
                        ticks: {
                            maxRotation: 60,
                            minRotation: 60,
                            autoSkip: true,
                            font: {
                                size: 11
                            }
                        }
                    },
                    y: {
                        beginAtZero: false,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        },
                        ticks: {
                            callback: function(value) {
                                return '¥' + value.toFixed(2);
                            }
                        }
                    }
                }
            }
        });
    }

    initTimeRangeSelector() {
        const selector = document.getElementById('timeRange');
        selector.addEventListener('change', () => {
            this.updateChartData();
        });
    }

    updateChartData() {
        if (!this.fullData['history_price']) return;

        const days = parseInt(document.getElementById('timeRange').value);
        const currentDate = new Date();
        const cutoffDate = new Date(currentDate.setDate(currentDate.getDate() - days));

        // 过滤数据
        const filteredData = this.filterDataByDate(this.fullData['history_price'], cutoffDate);

        // 格式化日期
        const formattedDates = filteredData.dates.map(date => {
            const d = new Date(date);
            return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
        });

        // 更新图表
        this.chart.data.labels = formattedDates;
        this.chart.data.datasets[0].data = filteredData.prices;
        this.chart.update();
    }

    filterDataByDate(data, cutoffDate) {
        const dates = data.date_list;
        const prices = data.price_list;
        const filteredDates = [];
        const filteredPrices = [];

        for (let i = 0; i < dates.length; i++) {
            const currentDate = new Date(dates[i]);
            if (currentDate >= cutoffDate) {
                filteredDates.push(dates[i]);
                filteredPrices.push(prices[i]);
            }
        }

        return {
            dates: filteredDates,
            prices: filteredPrices
        };
    }

    updateProductInfo(data) {
        // 更新商品名称
        const itemNameEl = document.querySelector('.item-name');
        itemNameEl.textContent = data.item_name;

        // 更新最低价格
        const lowestPriceEl = document.querySelector('.lowest-price .price');
        lowestPriceEl.textContent = `¥${data.lower_price}`;

        // 更新最低价格日期
        const lowestDateEl = document.querySelector('.lowest-date .date');
        const lowestDate = new Date(data.lower_price_data);
        lowestDateEl.textContent = `${lowestDate.getFullYear()}-${lowestDate.getMonth() + 1}-${lowestDate.getDate()}`;
    }
} 