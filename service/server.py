#!/usr/bin/env python
from service import app
import os
from flask import Flask, abort, render_template
import requests

register_title_api = app.config['REGISTER_TITLE_API']

def get_register_title(title_ref):
    response = requests.get(register_title_api+'titles/'+title_ref)
    return response

@app.route('/titles/<title_ref>', methods=['GET'])
def display_title(title_ref):
    #TODO Refactoring is needed, as well commenting on the code.
    api_response = get_register_title(title_ref)
    if api_response:
        title_api = api_response.json()
        entry_groups = title_api['data']['groups']
        #This is to get the proprietor entry that is in the ownership category
        proprietor_names = []
        property_description = {}
        address_lines = []
        for entry_group in entry_groups:
            if entry_group['category'] == 'OWNERSHIP':
                proprietor_entries = (entry_group['entries'])
                for entry in proprietor_entries:
                    if entry['role_code'] == 'RPRO':
                        infills = entry['infills']
                        for infill in infills:
                            proprietors = infill['proprietors']
                            for proprietor in proprietors:
                                proprietor_names += [
                                  {
                                    'name': proprietor['name']['forename'] + ' ' + proprietor['name']['surname']
                                  }
                                ]
            #This is to get the proprietor entry that is in the ownership category
            if entry_group['category'] == 'PROPERTY':
                property_entries = (entry_group['entries'])
                for entry in property_entries:
                    if entry['role_code'] == 'RDES':
                        infills = entry['infills']
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
