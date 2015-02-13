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
    title_api = api_response.json()
    title = {
        'number': title_api['title_number'],
        'last_changed': title_api['data']['last_app_timestamp'],
        'address': 'TODO Address',
        'lenders': [
            {'name': 'TODO lender name'},
        ],
    }
    entries = title_api['data']['entries']
    proprietor_names = []
    first_line_address = []
    for entry in entries:
        if entry['role_code'] == 'RPRO':
            infills = entry['infills']
            for infill in infills:
                proprietors = infill['proprietors']
                for proprietor in proprietors:
                    proprietor_names += [proprietor['name']['forename'] + ' ' + proprietor['name']['surname']]
        if entry['role_code'] == 'RDES':
            infills = entry['infills']
            for infill in infills:
                address_part = infill['address']
                first_line_address.append(address_part['house_no'] + ' ' + address_part['street_name'])
                property_description = {'first_line_address': first_line_address, 'town': address_part['town'], 'postcode': address_part['postcode'] }

    return render_template('display_title.html', asset_path = '../static/',
                           title=title, proprietors=proprietor_names, property_description=property_description)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
