#!/usr/bin/env python
from service import app
import os
from flask import Flask, abort, render_template
import requests

@app.route('/titles/<title_ref>', methods=['GET'])
def display_title(title_ref):
    return render_template('display_title.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
