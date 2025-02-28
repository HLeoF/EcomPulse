from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
from DataScript import get_history_price, get_lowest_price

app = Flask(__name__)
CORS(app)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/submit-url', methods=['POST'])
def submit_url():
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'error': 'URL is required'}), 400
            
        url = data['url']
        logger.info(f"Received URL: {url}")
        
        # 验证 URL 格式
        if not url.startswith(('http://', 'https://')):
            return jsonify({'error': 'Invalid URL format'}), 400
        
        # 获取数据
        try:
            result = get_history_price(url)
            logger.info(f"Item Name: {result['item_name']}")
            item_lowest_price = get_lowest_price(result['item_name'])
            return jsonify({
                "history_price": result,
                "lowest_price": item_lowest_price
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        
    except Exception as e:
        logger.error(f"Error in submit_url: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000)