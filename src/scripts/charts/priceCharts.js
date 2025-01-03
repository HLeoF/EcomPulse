class PriceChart {
    constructor() {
        this.chart = null;
        this.fullData = null;
        this.initChart();
        this.initTimeRangeSelector();
        this.fetchData();
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
                                return `¥${context.parsed.y}`;
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
                            maxRotation: 60,  // 设置为 60 度
                            minRotation: 60,  // 设置为 60 度
                            autoSkip: true,   // 自动跳过重叠的标签
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
                                return '¥' + value;
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

    async fetchData() {
        try {
            const response = await fetch('http://localhost:5000/get-list');
            this.fullData = await response.json();
            
            // 更新商品信息
            this.updateProductInfo(this.fullData);
            
            // 更新图表数据
            this.updateChartData();

        } catch (error) {
            console.error('Error fetching price data:', error);
        }
    }

    updateChartData() {
        if (!this.fullData) return;

        const days = parseInt(document.getElementById('timeRange').value);
        const currentDate = new Date();
        const cutoffDate = new Date(currentDate.setDate(currentDate.getDate() - days));

        // 过滤数据
        const filteredData = this.filterDataByDate(this.fullData, cutoffDate);

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