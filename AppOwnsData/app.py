# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

from services.pbiembedservice import PbiEmbedService
from utils import Utils
from flask import Flask, render_template, send_from_directory, request
import json
import os

# Initialize the Flask app
app = Flask(__name__)

# Load configuration
app.config.from_object('config.BaseConfig')

@app.route('/')
def index():
    '''Returns a static HTML page'''

    return render_template('index.html')

@app.route('/getembedinfo', methods=['GET'])
def get_embed_info():
    '''Returns report embed configuration'''

    config_result = Utils.check_config(app)
    if config_result is not None:
        return json.dumps({'errorMsg': config_result}), 500

    try:
        embed_info = PbiEmbedService().get_embed_params_for_single_report(app.config['WORKSPACE_ID'], app.config['REPORT_ID'])
        return embed_info
    except Exception as ex:
        return json.dumps({'errorMsg': str(ex)}), 500

@app.route('/getembedinfo_rls', methods=['POST'])
def get_embed_info_rls():
    '''Returns report embed configuration with Row-Level Security (RLS)'''

    config_result = Utils.check_config(app)
    if config_result is not None:
        return json.dumps({'errorMsg': config_result}), 500

    try:
        # Get customer info from request
        customer_id = request.json.get('customerId')
        
        if not customer_id:
            return json.dumps({'errorMsg': 'Customer ID is required'}), 400
        
        # Get customer info from config
        customer_mapping = app.config.get('CUSTOMER_MAPPING', {})
        customer_info = customer_mapping.get(customer_id)
        
        if not customer_info:
            return json.dumps({'errorMsg': f'Customer {customer_id} not found'}), 404
        
        # Generate embed token with RLS
        embed_info = PbiEmbedService().get_embed_params_for_single_report_with_rls(
            app.config['WORKSPACE_ID'], 
            app.config['REPORT_ID'],
            customer_info['username'],
            customer_info['roles']
        )
        
        # Add customer info to response for display
        embed_info_dict = json.loads(embed_info)
        embed_info_dict['customerInfo'] = {
            'customerId': customer_id,
            'customerName': customer_info['name'],
            'username': customer_info['username'],
            'roles': customer_info['roles']
        }
        
        return json.dumps(embed_info_dict)
    except Exception as ex:
        return json.dumps({'errorMsg': str(ex)}), 500

@app.route('/getcustomers', methods=['GET'])
def get_customers():
    '''Returns list of available customers for demo'''

    try:
        customer_mapping = app.config.get('CUSTOMER_MAPPING', {})
        customers = [
            {
                'id': customer_id,
                'name': info['name']
            }
            for customer_id, info in customer_mapping.items()
        ]
        return json.dumps({'customers': customers})
    except Exception as ex:
        return json.dumps({'errorMsg': str(ex)}), 500

@app.route('/favicon.ico', methods=['GET'])
def getfavicon():
    '''Returns path of the favicon to be rendered'''

    return send_from_directory(os.path.join(app.root_path, 'static'), 'img/favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    app.run()