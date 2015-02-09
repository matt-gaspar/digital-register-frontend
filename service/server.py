#!/usr/bin/env python
from service import app
import os
from flask import Flask, abort, render_template
import requests

register_title_api = app.config['REGISTER_TITLE_API']

def get_register_title(title_ref):
    return requests.get(register_title_api+'titles/'+title_ref)

@app.route('/titles/<title_ref>', methods=['GET'])
def display_title(title_ref):
    api_response = get_register_title(title_ref)
    title = api_response.json()
    return render_template('display_title.html', asset_path = "../static/", title=title)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
