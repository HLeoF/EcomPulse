class ReviewChart {
    constructor() {
        this.chart = null;
        this.initChart();
    }

    initChart() {
        const ctx = document.getElementById('reviewChart').getContext('2d');
        this.chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['1★', '2★', '3★', '4★', '5★'],
                datasets: [{
                    label: 'Review Distribution',
                    data: [],
                    backgroundColor: [
                        '#FF6B6B',
                        '#FFA06B',
                        '#FFD93D',
                        '#6BCB77',
                        '#4CAF50'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }

    updateData(data) {
        this.chart.data.datasets[0].data = data;
        this.chart.update();
    }
} 