#!/usr/bin/env python
from collections import Counter
import json
from flask import abort, render_template, request, redirect, url_for, session
from flask_login import login_user, login_required, current_user
from flask_wtf import Form
from flask_wtf.csrf import CsrfProtect
import logging
import logging.config
import os
import re
import requests
import time
from wtforms.fields import StringField, PasswordField
from wtforms.validators import Required, Length

from service import app, login_manager


REGISTER_TITLE_API = app.config['REGISTER_TITLE_API']
UNAUTHORISED_WORDING = '''There was an error with your Username/Password
                       combination. Please try again'''
VIEW_REGISTER_LOG = "VIEW REGISTER: Title number {0} was viewed by {1}"
SEARCH_REGISTER_LOG = "SEARCH REGISTER: {0} was searched by {1}"
GOOGLE_ANALYTICS_API_KEY = app.config['GOOGLE_ANALYTICS_API_KEY']
TITLE_NUMBER_REGEX = '^([A-Z]{0,3}[1-9][0-9]{0,5}|[0-9]{1,6}[ZT])$'
BASIC_POSTCODE_REGEX = '^[A-Z]{1,2}[0-9R][0-9A-Z]? [0-9][A-Z]{2}$'
BASIC_POSTCODE_WITH_SURROUNDING_GROUPS_REGEX = (
    r'(?P<leading_text>.*\b)\s?'
    r'(?P<postcode>[A-Z]{1,2}[0-9R][0-9A-Z]? [0-9][A-Z]{2}\b)\s?'
    r'(?P<trailing_text>.*)?'
)
LOGGER = logging.getLogger(__name__)


class User():
    def __init__(self, username):
        self.user_id = username

    def get_id(self):
        return self.user_id

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False


class LoginApiClient():
    def __init__(self, login_api_url):
        authentication_url = '{}user/authenticate'.format(login_api_url)
        self.authentication_endpoint_url = authentication_url

    def authenticate_user(self, username, password):
        user_dict = {"user_id": username, "password": password}
        request_dict = {"credentials": user_dict}
        request_json = json.dumps(request_dict)

        headers = {'content-type': 'application/json'}
        response = requests.post
        (
            self.authentication_endpoint_url,
            data=request_json,
            headers=headers
        )
        return response.status_code == 200


LOGIN_API_CLIENT = LoginApiClient(app.config['LOGIN_API'])


@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


@app.route('/', methods=['GET'])
def home():
    return render_template('home.html', asset_path='../static/')


@app.route('/login', methods=['GET'])
def signin_page():
    return render_template(
        'display_login.html',
        asset_path='../static/',
        form=SigninForm(csrf_enabled=_is_csrf_enabled())
    )


BAD_LOGIN_COUNTER = Counter()
MAX_LOGIN_ATTEMPTS = 10
NOF_SECS_BETWEEN_LOGINS = 1


@app.route('/login', methods=['POST'])
def signin():
    form = SigninForm(csrf_enabled=_is_csrf_enabled())
    if not form.validate():
        # entered details from login form incorrectly so send
        # back to same page with form error messages
        return render_template
        (
            'display_login.html',
            asset_path='../static/',
            form=form
        )

    next_url = request.args.get('next', 'title-search')

    # form was valid
    username = form.username.data
    too_many_bad_logins = BAD_LOGIN_COUNTER[username] > MAX_LOGIN_ATTEMPTS
    if not too_many_bad_logins:
        # form has correct details. Now need to check authorisation
        authorised = LOGIN_API_CLIENT.authenticate_user
        (
            username,
            form.password.data
        )

        if authorised:
            del BAD_LOGIN_COUNTER[username]
            login_user(User(username))
            LOGGER.info('User {} logged in'.format(username))
            return redirect(next_url)

    # too many bad log-ins or not authorised
    if app.config.get('SLEEP_BETWEEN_LOGINS', True):
        time.sleep(NOF_SECS_BETWEEN_LOGINS)
    BAD_LOGIN_COUNTER.update([username])
    if too_many_bad_logins:
        log_msg = 'Too many bad logins'
    else:
        log_msg = 'Invalid credentials used'
    nof_attempts = BAD_LOGIN_COUNTER[username]
    LOGGER.info('{}. username: {}, attempt: {}.'.format(log_msg, username,
                                                        nof_attempts))
    return render_template
    (
        'display_login.html',
        asset_path='../static/',
        form=form,
        unauthorised=UNAUTHORISED_WORDING,
        next=next_url
    )


@app.route('/titles/<title_ref>', methods=['GET'])
@login_required
def display_title(title_ref):
    # Check to see if the Title dict is in the session, else try to retrieve it
    title = session.pop('title', get_register_title(title_ref))
    if title:
        # If the title was found, display the page
        LOGGER.info(VIEW_REGISTER_LOG.format(title_ref, current_user.get_id()))
        return render_template
        (
            'display_title.html',
            asset_path='../static/',
            title=title,
            google_api_key=GOOGLE_ANALYTICS_API_KEY
        )
    else:
        abort(404)


@app.route('/title-search/', methods=['GET', 'POST'])
@login_required
def find_titles():
    # TODO: make this method use a WTF form, just like signin()
    if request.method == "POST":
        search_term = request.form['search_term']
        user_id = current_user.get_id()
        LOGGER.info(SEARCH_REGISTER_LOG.format(search_term, user_id))
        # Determine search term type and preform search
        title_number_regex = re.compile(TITLE_NUMBER_REGEX)
        if title_number_regex.match(search_term.upper()):
            title = get_register_title(search_term.upper())
            if title:
                # If the title exists store it in the session
                session['title'] = title
                # Redirect to the display_title method to display
                # the digital register
                return redirect
                (
                    url_for('display_title', title_ref=search_term.upper())
                )
        # If search value doesn't match, return no results found screen
        return render_template
        (
            'no_title_number_results.html',
            asset_path='../static/',
            search_term=search_term,
            google_api_key=GOOGLE_ANALYTICS_API_KEY,
            form=TitleSearchForm()
        )
    else:
        # If not search value enter or a GET request, display the search page
        return render_template
        (
            'search.html',
            asset_path='../static/',
            google_api_key=GOOGLE_ANALYTICS_API_KEY,
            form=TitleSearchForm()
        )


def _is_csrf_enabled():
    return app.config.get('DISABLE_CSRF_PREVENTION') != True


def get_register_title(title_ref):
    response = requests.get(
        '{}titles/{}'.format(REGISTER_TITLE_API, title_ref)
    )
    title = format_display_json(response)
    return title


def format_display_json(api_response):
    if api_response:
        title_api = api_response.json()
        proprietor_names = get_proprietor_names
        (
            title_api['data']['proprietors']
        )
        address_lines = get_address_lines(title_api['data']['address'])
        indexPolygon = get_property_address_index_polygon
        (
            title_api['geometry_data']
        )
        last_changed = title_api['data'].get
        (
            'last_application_timestamp',
            'No data'
        )
        title = {
            'number': title_api['title_number'],
            'last_changed': last_changed,
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
        # TODO: decide which of the following fields we want to display
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
    if (
        'sub_building_description' in address_data and
        'sub_building_no' in address_data
    ):
        sub_building_string = "{0} {1}".format
        (
            address_data['sub_building_description'],
            address_data['sub_building_no']
        )
        lines.append(sub_building_string)
    elif 'sub_building_description' in address_data:
        lines.append(address_data['sub_building_description'])
    elif 'sub_building_no' in address_data:
        lines.append(address_data['sub_building_no'])
    return lines


def get_street_name_lines(address_data):
    lines = []
    street_name_string = ""
    if 'house_no' in address_data or 'house_alpha' in address_data:
        street_name_string += "{0}{1}".format
        (
            address_data.get('house_no', ''),
            address_data.get('house_alpha', '')
        )
    if (
        'secondary_house_no' in address_data or
        'secondary_house_alpha' in address_data
    ):
        secondary_string = "{0}{1}".format
        (
            address_data.get('secondary_house_no', ''),
            address_data.get('secondary_house_alpha', '')
        )
        if street_name_string:
            street_name_string += "-{0}".format(secondary_string)
        else:
            street_name_string += secondary_string
    if 'street_name' in address_data:
        street_name = address_data['street_name']
        if street_name_string:
            street_name_string += " {0}".format(street_name)
        else:
            street_name_string += street_name
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
    # If the JSON doesn't contain the individual fields non_empty_lines
    # will be empty
    # Check if this is the case and if their is an address_string
    if (
        not non_empty_lines and
        address_data and
        address_data.get('address_string')
    ):
        non_empty_lines = format_address_string
        (
            address_data.get('address_string')
        )
    return non_empty_lines


def format_address_string(address_string):
    # remove brackets and split the address string on commas
    address_lines = re.sub('[\(\)]', '', address_string).split(', ')
    # Strip leading and trailing whitespace and see
    # if the last line is a just a postcode
    last_line = address_lines[-1].strip()
    if not re.search(BASIC_POSTCODE_REGEX, last_line):
        # If not, remove the line from address_lines, splt out the postcode and
        # any preceeding text and trailing text and add them to address_lines
        # as separate lines (if they exist)
        del(address_lines[-1])
        matches = re.match
        (
            BASIC_POSTCODE_WITH_SURROUNDING_GROUPS_REGEX,
            last_line
        )
        if (
            matches.group('leading_text') and
            len(matches.group('leading_text').strip()) > 0
        ):
            address_lines.append(matches.group('leading_text').strip())
        address_lines.append(matches.group('postcode').strip())
        if (
            matches.group('trailing_text') and
            len(matches.group('trailing_text').strip()) > 0
        ):
            address_lines.append(matches.group('trailing_text').strip())
    return address_lines


# This method attempts to retrieve the index polygon data for the entry
def get_property_address_index_polygon(geometry_data):
    indexPolygon = None
    if geometry_data and ('index' in geometry_data):
        indexPolygon = geometry_data['index']
    return indexPolygon


class SigninForm(Form):
    user_name_constraints =
    [
        Required(message='Username is required'),
        Length(min=4,
               max=70,
               message='Username is incorrect')
    ]
    username = StringField('username', user_name_constraints)
    password_constraints =
    [
        Required(message='Password is required')
    ]
    password = PasswordField('password', password_constraints)

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)


class TitleSearchForm(Form):
    # Form used for providing CSRF tokens for title search HTTP form
    pass


def run_app():
    CsrfProtect(app)
    port = int(os.environ.get('PORT', 8003))
    app.run(host='0.0.0.0', port=port, debug=True)


if __name__ == '__main__':
    run_app()
