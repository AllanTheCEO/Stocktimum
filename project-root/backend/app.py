from flask import Flask, jsonify, url_for, redirect, request, render_template, send_from_directory
from services import data_analysis
import os



app = Flask(__name__)

@app.route('/')
def home():
    api_data_url = url_for("api_data")
    api_chart_url = url_for("api_chart")
    api_test_chart = url_for("api_table")
    return f'''
    <h1>Homepage</h1>
    <p>Click <a href="{api_data_url}">here</a> to go to the API Data.</p>
    <p>Click <a href="{api_chart_url}">here</a> to go to the API Chart.</p>
    <p>Click <a href="{api_test_chart}">here</a> to go to the API Table.</p>
    '''

@app.route('/api/data')
def api_data():
    ticker = request.args.get('ticker', "AAPL")
    closing_price = request.args.get('closing_price', True)
    period = request.args.get('period', "10y")
    interval = request.args.get('interval', "1d")

    return jsonify(data_analysis.fetch_data_type(ticker, closing_price, period, interval))

@app.route('/api/chart') 
def api_chart():
    frontend_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'frontend/public')
    return send_from_directory(frontend_path, 'index.html')

@app.route('/api/style.css')
def serve_style_css():
    frontend_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'frontend/public')
    return send_from_directory(frontend_path, 'style.css')

@app.route('/api/src/index.js')
def serve_index_js():
    file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'frontend', 'src', 'index.js')
    return send_from_directory(os.path.dirname(file_path), os.path.basename(file_path))

@app.route('/api/table')
def api_table():
    frontend_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'frontend/public')
    return send_from_directory(frontend_path, 'test.html')

@app.route('/api/src/test.js')
def serve_test_js():
    file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'frontend', 'src', 'test.js')
    return send_from_directory(os.path.dirname(file_path), os.path.basename(file_path))  

@app.route('/api/src/stocks.js')
def serve_stocks_js():
    file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'frontend', 'src', 'stocks.js')
    return send_from_directory(os.path.dirname(file_path), os.path.basename(file_path))  
        
    
if __name__ == '__main__':
    app.run(debug=True)
