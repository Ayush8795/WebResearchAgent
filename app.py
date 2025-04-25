from flask import Flask, render_template, request, jsonify, url_for
from flask_cors import CORS
import os
import agents


app= Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}})

@app.before_request
def before_request():
    if request.method == 'OPTIONS':
        # Handle preflight request
        response = app.make_default_options_response()
    
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization,access-control-allow-origin')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        response.headers.add('Access-Control-Allow-Origin', '*')

        return response


@app.route('/',methods=['GET'])
def welcome():
     return render_template('home.html')

@app.route('/queryResponse/', methods = ['POST'])
def query_response():
    data = request.json
    query = data['query']
    response = agents.run_agents(query)

    if not response:
        return jsonify({
            "success": False,
            "message": "Unable to fetch the results",
            "data": []
        }), 500
    

    return jsonify({
        "success": True,
        "message": "success",
        "data": response
    }), 200


if __name__=='__main__':
    app.run(debug = True, host = '0.0.0.0', port = 8000)