from flask import Flask, jsonify, url_for, redirect, request
from services import data_analysis


app = Flask(__name__)

@app.route('/')
def home():
    hello_url = url_for("hello")
    return f'''
    <h1>Homepage</h1>
    <p>Click <a href="{hello_url}">here</a> to go to the Hello API.</p>
    '''


@app.route('/api/hello')
def hello():
    return jsonify({"message": "Hello from the backend!"})



if __name__ == '__main__':
    app.run(debug=True)
