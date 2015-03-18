#!/usr/bin/env python
from service import app
import os
from flask import Flask, abort, render_template, request, redirect, url_for, session
import requests
import re
import logging
import logging.config

logger = logging.getLogger(__name__)
register_title_api = app.config['REGISTER_TITLE_API']
google_analytics_api_key = app.config['GOOGLE_ANALYTICS_API_KEY']

# TODO Create a proper secret key and store it securely
app.secret_key = 'a_secret_key'

@app.route('/', methods=['GET'])
def home():
    return render_template('home.html', asset_path = '../static/')

@app.route('/titles/<title_ref>', methods=['GET'])
def display_title(title_ref):
    # Check to see if the Title dict is in the session, else try to retrieve it
    title = session.pop('title', get_register_title(title_ref))
    if title:
        # If the title was found, display the page
        logger.info("VIEW REGISTER: Title number {0} was viewed by {1}".format(title_ref, "todo-user"))
        return render_template('display_title.html', asset_path = '../static/', title=title, google_api_key=google_analytics_api_key)
    else:
        abort(404)

@app.route('/title-search/', methods=['GET', 'POST'])
def find_titles():
    if request.method == "POST":
        search_term = request.form['search_term']
        logger.info("SEARCH REGISTER: {0} was searched by {1}".format(search_term, "todo-user"))
        # Determine search term type and preform search
        title_number_regex = re.compile("^([A-Z]{0,3}[1-9][0-9]{0,5}|[0-9]{1,6}[ZT])$")
        if title_number_regex.match(search_term.upper()):
            title = get_register_title(search_term.upper())
            if title:
                # If the title exists store it in the session
                session['title'] = title
                # Redirect to the display_title method to display the digital register
                return redirect(url_for('display_title', title_ref=search_term.upper()))
            else:
                # If title not found display 'no title found' screen
                return render_template('no_title_number_results.html', asset_path = '../static/', search_term=search_term, google_api_key=google_analytics_api_key)
        else:
            # If search value doesn't match, return no results found screen
            return render_template('no_title_number_results.html', asset_path = '../static/', search_term=search_term, google_api_key=google_analytics_api_key)
    else:
        # If not search value enter or a GET request, display the search page
        return render_template('search.html', asset_path = '../static/', google_api_key=google_analytics_api_key)

def get_register_title(title_ref):
    response = requests.get(register_title_api+'titles/'+title_ref)
    title = format_display_json(response)
    return title

def format_display_json(api_response):
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
        return title
    else:
        return None

def get_proprietor_names(proprietors_data):
    proprietor_names = []
    for proprietor in proprietors_data:
        name = proprietor['name']
        #TODO: decide which of the following fields we want to display
        # company_reg_num
        # country_incorporation
        # company_location
        # local_authority_area
        # name_supplimentary
        # charity_name
        # trust_format
        # name_information
        if 'forename' in name and 'surname' in name:
            proprietor_names += [{
                "name": name['forename'] + ' ' + name['surname']
            }]
        if 'non_private_individual_name' in name:
            proprietor_names += [{
                "name": name['non_private_individual_name']
            }]
    return proprietor_names

def get_building_description_lines(address_data):
    lines = []
    if 'sub_building_description' in address_data and 'sub_building_no' in address_data:
        lines.append("{0} {1}".format(address_data['sub_building_description'], address_data['sub_building_no']))
    elif 'sub_building_description' in address_data:
        lines.append(address_data['sub_building_description'])
    elif 'sub_building_no' in address_data:
        lines.append(address_data['sub_building_no'])
    return lines

def get_street_name_lines(address_data):
    lines = []
    street_name_string = ""
    if 'house_no' in address_data or 'house_alpha' in address_data:
        street_name_string+="{0}{1}".format(address_data.get('house_no', ''), address_data.get('house_alpha', ''))
    if 'secondary_house_no' in address_data or 'secondary_house_alpha' in address_data:
        secondary_string = "{0}{1}".format(address_data.get('secondary_house_no', ''), address_data.get('secondary_house_alpha', ''))
        if street_name_string:
            street_name_string+="-{0}".format(secondary_string)
        else:
            street_name_string+=secondary_string
    if 'street_name' in address_data:
        street_name = address_data['street_name']
        if street_name_string:
            street_name_string+=" {0}".format(street_name)
        else:
            street_name_string+=street_name
    if street_name_string:
        lines.append(street_name_string)
    return lines

def get_address_lines(address_data):
    lines = []
    if address_data:
        lines.append(address_data.get('leading_info', None))
        lines = get_building_description_lines(address_data)
        lines.append(address_data.get('house_description', None))
        lines += get_street_name_lines(address_data)
        lines.append(address_data.get('street_name_2', None))
        lines.append(address_data.get('local_name', None))
        lines.append(address_data.get('local_name_2', None))
        lines.append(address_data.get('town', None))
        lines.append(address_data.get('postcode', None))
        lines.append(address_data.get('trail_info', None))
    non_empty_lines = [x for x in lines if x is not None]
    return non_empty_lines

#This method attempts to retrieve the index polygon data for the entry
def get_property_address_index_polygon(geometry_data):
    indexPolygon = None
    if geometry_data and ('index' in geometry_data):
        indexPolygon = geometry_data['index']
    return indexPolygon

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8003))
    app.run(host='0.0.0.0', port=port, debug=True)
