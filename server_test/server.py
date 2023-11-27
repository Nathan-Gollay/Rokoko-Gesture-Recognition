"""
Server Test for communicating with Rokoko
Author: Nathan Gollay

CURRENTLY OBSOLETE
"""
#External Libraries
from flask import Flask, request

app = Flask(__name__)

@app.route('/data', methods=['POST'])
def receive_data():
    print(request.data)  # This will print the data received from ROKOKO
    return "Data received!"

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=14053)

