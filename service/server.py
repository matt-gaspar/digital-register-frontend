#!/usr/bin/env python
from service import app
import os
from flask import Flask, abort, render_template
import requests

register_title_api = app.config['REGISTER_TITLE_API']

def get_register_title(title_ref):
    response = requests.get(register_title_api+'titles/'+title_ref)
    return response

#This method gets all the infills of a particular entry that has been found.
def get_register_entry_infills(category, role_code, entry_groups):
    for entry_group in entry_groups:
        if entry_group['category'] == category:
            entries = (entry_group['entries'])
            for entry in entries:
                if entry['role_code'] == role_code:
                    infills = entry['infills']
                    return infills

#It is currently assumed that there will only be one proprieter register entry
#This method grabs the correct entry using the OWNERSHIP category and
#role code of RPRO
def get_proprietor_register_entry(entry_groups):
    proprietor_names = []
    category = 'OWNERSHIP'
    role_code = 'RPRO'
    infills = get_register_entry_infills(category, role_code, entry_groups)
    for infill in infills:
        proprietors = infill['proprietors']
        for proprietor in proprietors:
            name = proprietor['name']
            if 'forename' in name and 'surname' in name:
                proprietor_names += [{
                    "name": name['forename'] + ' ' + name['surname']
                }]
            if 'non_private_individual_name' in name:
                proprietor_names += [{
                    "name": name['non_private_individual_name']
                }]
    return proprietor_names

#It is currently assumed that there will only be one property address register
#entry this method grabs the correct entry using the PROPERTY category and
#role code of RDES
def get_property_address_register_entry(entry_groups):
    address_lines = []
    category = 'PROPERTY'
    role_code = 'RDES'
    infills = get_register_entry_infills(category, role_code, entry_groups)
    for infill in infills:
        address_part = infill['address']
        if address_part:
            first_line_address = ' '.join([address_part[k] for k in ['house_no', 'street_name'] if address_part.get(k, None)])
            all_address_lines = [
                first_line_address,
                address_part.get('town', ''),
                address_part.get('postcode', '')
            ]
            address_lines = [line for line in all_address_lines if line]
    return address_lines

@app.route('/titles/<title_ref>', methods=['GET'])
def display_title(title_ref):
    api_response = get_register_title(title_ref)
    if api_response:
        title_api = api_response.json()
        entry_groups = title_api['data']['groups']
        proprietor_names = get_proprietor_register_entry(entry_groups)
        address_lines = get_property_address_register_entry(entry_groups)

        title = {
            'number': title_api['title_number'],
            'last_changed': title_api['data']['last_app_timestamp'],
            'address_lines': address_lines,
            'lenders': [
                {'name': 'TODO lender name'},
            ],
            'proprietors': proprietor_names,
            'tenure': title_api['data']['tenure']
        }

        return render_template('display_title.html', asset_path = '../static/', title=title)
    else:
        abort(404)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8003))
    app.run(host='0.0.0.0', port=port, debug=True)
