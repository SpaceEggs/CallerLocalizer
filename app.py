import csv
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

# 加载手机号码数据
def load_phone_data():
    phone_data = {}
    try:
        with open('PhoneNumber.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # 使用号段作为键
                phone_data[row['号段']] = {
                    '省区': row['省区'],
                    '城市': row['城市'],
                    '服务商': row['服务商'],
                    '区号': row['区号'],
                    '邮编': row['邮编'],
                    '区划代码': row['区划代码']
                }
        return phone_data
    except Exception as e:
        print(f"加载数据时出错: {e}")
        return {}

# 全局变量存储手机号码数据
phone_database = load_phone_data()

@app.route('/query', methods=['GET'])
def query_phone():
    phone_number = request.args.get('phone')
    
    # 验证手机号码格式
    if not phone_number or not phone_number.isdigit() or len(phone_number) != 11 or not phone_number.startswith('1'):
        return jsonify({
            'success': False,
            'message': '请提供有效的11位手机号码（以1开头）'
        }), 400
    
    # 获取前7位作为号段
    prefix = phone_number[:7]
    
    # 查询号码信息
    if prefix in phone_database:
        result = {
            'success': True,
            'phone': phone_number,
            'data': phone_database[prefix]
        }
        return jsonify(result)
    else:
        return jsonify({
            'success': False,
            'message': f'未找到号码 {phone_number} 的信息'
        }), 404

@app.route('/', methods=['GET'])
def index():
    return '''
    <html>
        <head>
            <title>手机号码查询服务</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; line-height: 1.6; }
                .container { max-width: 800px; margin: 0 auto; }
                h1 { color: #333; }
                .form-group { margin-bottom: 15px; }
                label { display: block; margin-bottom: 5px; }
                input[type="text"] { padding: 8px; width: 300px; }
                button { padding: 8px 15px; background: #4CAF50; color: white; border: none; cursor: pointer; }
                button:hover { background: #45a049; }
                pre { background: #f4f4f4; padding: 15px; border-radius: 5px; overflow: auto; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>手机号码查询服务</h1>
                <div class="form-group">
                    <label for="phone">输入11位手机号码（1开头）：</label>
                    <input type="text" id="phone" placeholder="例如：13812345678">
                    <button onclick="queryPhone()">查询</button>
                </div>
                <pre id="result">查询结果将显示在这里...</pre>
                
                <script>
                    function queryPhone() {
                        const phone = document.getElementById('phone').value;
                        const resultElement = document.getElementById('result');
                        
                        if (!phone || !/^1\\d{10}$/.test(phone)) {
                            resultElement.textContent = '请输入有效的11位手机号码（以1开头）';
                            return;
                        }
                        
                        resultElement.textContent = '正在查询...';
                        
                        fetch(`/query?phone=${phone}`)
                            .then(response => response.json())
                            .then(data => {
                                resultElement.textContent = JSON.stringify(data, null, 2);
                            })
                            .catch(error => {
                                resultElement.textContent = `查询出错: ${error.message}`;
                            });
                    }
                </script>
            </div>
        </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)