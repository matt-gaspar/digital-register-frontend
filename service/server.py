#!/usr/bin/env python
from collections import namedtuple
from flask_login import login_user, login_required, current_user
from flask.ext.wtf import Form
from service import app, login_manager
import os
from flask import Flask, abort, render_template, request, url_for, redirect
# from flask.ext.wtf import Form, validators
from wtforms.fields import TextField, BooleanField, PasswordField, SubmitField
from wtforms.validators import Required
import requests

register_title_api = app.config['REGISTER_TITLE_API']
login_api = app.config['LOGIN_API']

#This method attempts to retrieve the index polygon data for the entry
def get_property_address_index_polygon(geometry_data):
    indexPolygon = None
    if geometry_data and ('index' in geometry_data):
        indexPolygon = geometry_data['index']
    return indexPolygon

class User():
    def __init__(self, id):
        self.userid = id
    
    def get_id(self):
        return self.userid
    
    def is_authenticated(self):
        return True
    
    def is_active(self):
        return True
    
    def is_anonymous(self):
        return False

@login_manager.user_loader
def load_user(userid):
    return User(userid)

@app.route('/', methods=['GET'])
def home():
    return render_template('home.html', asset_path = '../static/')

@app.route('/login', methods=['GET'])
def signin_page():
    return render_template('display_login.html', asset_path = '../static/', form=SigninForm())

@app.route('/login', methods=['POST'])
def signin():
    # csrf_enabled = False for development environment only
    # form = SigninForm(csrf_enabled=False)
    form = SigninForm()
    if not form.validate():
        # entered details from login form incorrect so redirect back to same page with error messages
        return render_template('display_login.html',asset_path = '../static/', form=form)
    else:
        login_user(User(form.username.data))
        # form has correct details. Now need to check authorisation
        authorised = get_login_auth(form.username, form.password)
        if authorised:
            return redirect(url_for('search'))
        else:
            return render_template('display_login.html', asset_path = '../static/', form=form)
        
def get_login_auth(username, password):
    #response = requests.get(login_api+username+'/'+password)
    response = True
    return response

@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    return 'hello {}'.format(current_user.get_id())

@app.route('/titles/<title_ref>', methods=['GET'])
@login_required
def display_title(title_ref):
    api_response = get_register_title(title_ref)
    if api_response:
        title_api = api_response.json()
        proprietor_names = get_proprietor_names(title_api['data']['proprietors'])
        address_lines = get_address_lines(title_api['data']['address'])
        indexPolygon = get_property_address_index_polygon(title_api['geometry_data'])
        title = {
            #ASSUMPTION 1: All titles have a title number
            'number': title_api['title_number'],
            'last_changed': title_api['data'].get('last_application_timestamp', 'No data'),
            'address_lines': address_lines,
            'proprietors': proprietor_names,
            'tenure': title_api['data'].get('tenure', 'No data'),
            'indexPolygon': indexPolygon
        }
        return render_template('display_title.html', asset_path = '../static/', title=title)
    else:
        abort(404)

def get_register_title(title_ref):
    response = requests.get(register_title_api+'titles/'+title_ref)
    return response

def get_proprietor_names(proprietors_data):
    proprietor_names = []
    for proprietor in proprietors_data:
        name = proprietor['name']
        #ASSUMPTION 2: all proprietors have a name entry
        #ASSUMPTION 3: all proprietor names have either forename/surname or non_private_individual name
        if 'forename' in name and 'surname' in name:
            proprietor_names += [{
                "name": name['forename'] + ' ' + name['surname']
            }]
        if 'non_private_individual_name' in name:
            proprietor_names += [{
                "name": name['non_private_individual_name']
            }]
    return proprietor_names

def get_address_lines(address_data):
    address_lines = []
    #ASSUMPTION 4: all addresses are only in the house_no, street_name, town and postcode fields
    if address_data:
        first_line_address = ' '.join([address_data[k] for k in ['house_no', 'street_name'] if address_data.get(k, None)])
        all_address_lines = [
            first_line_address,
            address_data.get('town', ''),
            address_data.get('postcode', '')
        ]
        address_lines = [line for line in all_address_lines if line]
    return address_lines

class SigninForm(Form):
  # TODO: add validation
  username = TextField("username")
  password = PasswordField('password')

  def __init__(self, *args, **kwargs):
    Form.__init__(self, *args, **kwargs)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8003))
    app.run(host='0.0.0.0', port=port, debug=True)
