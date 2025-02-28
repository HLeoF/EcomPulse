class PriceComparison {
    constructor() {
        this.gallery = document.querySelector('.gallery-wrapper');
        this.dots = document.querySelectorAll('.dot');
        this.galleryContent = document.querySelector('.gallery');
        this.initScrollIndicator();
        this.initScrollButtons();
    }

    initScrollIndicator() {
        this.gallery.addEventListener('scroll', () => {
            const scrollPercentage = this.gallery.scrollLeft / (this.gallery.scrollWidth - this.gallery.clientWidth);
            const activeDotIndex = Math.round(scrollPercentage * (this.dots.length - 1));
            
            this.dots.forEach((dot, index) => {
                dot.classList.toggle('active', index === activeDotIndex);
            });
        });
    }

    initScrollButtons() {
        const leftButton = document.querySelector('.scroll-left');
        const rightButton = document.querySelector('.scroll-right');
        
        leftButton.addEventListener('click', () => {
            this.gallery.scrollBy({
                left: -200,
                behavior: 'smooth'
            });
        });
        
        rightButton.addEventListener('click', () => {
            this.gallery.scrollBy({
                left: 200,
                behavior: 'smooth'
            });
        });
    }

    updatePriceCards(itemsData) {
        try {
            console.log('Received itemsData in PriceComparison:', itemsData); // 调试日志

            // 检查数据结构
            if (!itemsData) {
                throw new Error('No data received');
            }

            // 清空现有内容
            this.galleryContent.innerHTML = '';

            // 将字符串转换为对象（如果需要）
            const items = typeof itemsData === 'string' ? JSON.parse(itemsData) : itemsData;

            // 确保 items 是数组
            const itemsArray = Array.isArray(items) ? items : [items];

            // 创建所有价格卡片
            itemsArray.forEach(item => {
                const card = document.createElement('div');
                card.className = 'price-card';
                card.innerHTML = `
                    <img src="${item.img_src || '../images/default.png'}" 
                         alt="${item.item_mall || '商城'}" 
                         class="platform-icon">
                    <div class="price-info">
                        <span class="platform-name">${item.item_mall || '未知商城'}</span>
                        <span class="item-name">${item.item_name || '未知商品'}</span>
                        <span class="price">${item.item_price || '暂无价格'}</span>
                    </div>
                `;

                // 添加点击事件跳转到商品链接
                if (item.item_link) {
                    card.style.cursor = 'pointer';
                    card.addEventListener('click', () => {
                        window.open(item.item_link, '_blank');
                    });
                }

                this.galleryContent.appendChild(card);
            });

            // 更新滚动指示器
            const dotCount = Math.ceil(this.galleryContent.scrollWidth / this.gallery.clientWidth);
            this.updateDots(dotCount);

            console.log('Price cards created successfully'); // 调试日志

        } catch (error) {
            console.error('Error updating price cards:', error);
            this.galleryContent.innerHTML = '<div class="error-message">暂无比价数据</div>';
        }
    }

    updateDots(count) {
        const dotsContainer = document.querySelector('.dots');
        dotsContainer.innerHTML = '';
        
        for (let i = 0; i < count; i++) {
            const dot = document.createElement('span');
            dot.className = 'dot' + (i === 0 ? ' active' : '');
            dotsContainer.appendChild(dot);
        }
        
        this.dots = document.querySelectorAll('.dot');
    }
}

// 挂载到全局
window.PriceComparison = PriceComparison;