import os
import __main__
from flask import jsonify, render_template, request, Flask
from model_core.model import ModelHandler
from crawl_core.yt_tw_crawl import Crawler  # 修改导入
from model_core.BertClassifier import BertClassifier
from datetime import datetime, timedelta

app = Flask(__name__)

# 解决载入模型时连结发生问题
setattr(__main__, "BertClassifier", BertClassifier)
# 设置模型路径
model_path = os.path.join(os.path.dirname(__file__), 'bert_lstm_model.pth')
# 实例化模型处理类
model_handler = ModelHandler(model_path=model_path)
# 实例化爬虫类
crawler = Crawler()

# 新建调用爬取函数并将结果保存到的upload目录
output_file = os.path.join('upload', 'test.txt')

# 用于存储预测结果的全局变量（模拟数据库）
predictions_history = []
user_url = None  # 全局变量，用于存储用户最初输入的URL
platform_type = None  # 用于存储用户选择的平台类型

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    global user_url, platform_type  # 使用全局变量来存储URL和平台类型
    platform = request.form['platform']
    url = request.form['url']
    
    # 检查平台是否为 'twitch' 或 'youtube'
    if platform == 'twitch' or platform == 'youtube':
        try:
            user_url = url  # 正确设置全局变量
            platform_type = platform  # 存储平台类型
            
            # 调用爬取函数并获取原始繁体数据
            original_traditional_data = crawler.crawl_chat(url, output_file)  # 使用类的方法
            
            # 使用模型进行预测
            predictions = model_handler.predict_from_file(output_file)
           
            # 为每个预测添加时间戳和原始繁体数据，并存储到全局变量中
            for i, pred in enumerate(predictions):
                predictions_history.append({
                    'prediction': pred,
                    'original_data': original_traditional_data[i],  # 添加原始繁体数据
                    'time': datetime.now()
                })

            # 清除超过30秒的数据
            cutoff_time = datetime.now() - timedelta(seconds=30)
            predictions_history[:] = [p for p in predictions_history if p['time'] > cutoff_time]

            # 返回预测结果和原始数据，仅返回最后10条数据
            return render_template('result.html', predictions=predictions_history[-10:])
        
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        
    else:
        return jsonify({"error": "Unsupported platform"}), 400

@app.route('/get_predictions', methods=['GET'])
def get_predictions():
    """提供最新的预测数据，供前端轮询获取"""
    # 返回最近30秒的数据
    cutoff_time = datetime.now() - timedelta(seconds=30)
    recent_predictions = [p for p in predictions_history if p['time'] > cutoff_time]
    return jsonify(recent_predictions)

@app.route('/auto_predict', methods=['POST'])
def auto_predict():
    """自动化预测，并更新全局预测历史"""
    global user_url, platform_type  # 使用全局变量来访问用户输入的URL和平台类型
    try:
        if user_url is None:
            return jsonify({"error": "No URL provided for predictions"}), 400

        # 使用用户最初输入的URL调用爬取函数并获取原始繁体数据
        original_traditional_data = crawler.crawl_chat(user_url, output_file)  # 使用类的方法

        # 使用模型进行预测
        predictions = model_handler.predict_from_file(output_file)

        # 为每个预测添加时间戳和原始繁体数据，并存储到全局变量中
        for i, pred in enumerate(predictions):
            
            predictions_history.append({
                'prediction': pred,
                'original_data': original_traditional_data[i],  # 添加原始繁体数据
                'time': datetime.now()
            })

        # 清除超过30秒的数据
        cutoff_time = datetime.now() - timedelta(seconds=30)
        predictions_history[:] = [p for p in predictions_history if p['time'] > cutoff_time]

        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

if __name__ == '__main__':
    app.run(debug=True, port=7000)
