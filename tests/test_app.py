from collections import namedtuple
import json
import mock
import pytest
import requests
import responses


from service.server import app


from .fake_response import FakeResponse

with open('tests/fake_title.json', 'r') as fake_title_json_file:
    fake_title_json_string = fake_title_json_file.read()
    fake_title_bytes = str.encode(fake_title_json_string)
    fake_title = FakeResponse(fake_title_bytes)

with open('tests/fake_no_address_title.json', 'r') as fake_no_address_title_file:
    fake_no_address_title_json_string = fake_no_address_title_file.read()
    fake_no_address_title_bytes = str.encode(fake_no_address_title_json_string)
    fake_no_address_title = FakeResponse(fake_no_address_title_bytes)

with open('tests/fake_partial_address.json', 'r') as fake_partial_address_file:
    fake_partial_address_json_string = fake_partial_address_file.read()
    fake_partial_address_bytes = str.encode(fake_partial_address_json_string)
    fake_partial_address = FakeResponse(fake_partial_address_bytes)

class TestViewTitle:

    def setup_method(self, method):
        self.app = app.test_client()

    @mock.patch('requests.get', return_value=fake_title)
    def test_get_title_page(self, mock_get):
        response = self.app.get('/titles/titleref')
        assert response.status_code == 200

    @mock.patch('requests.get', return_value=fake_title)
    def test_date_formatting_on_title_page(self, mock_get):
        response = self.app.get('/titles/titleref')
        assert '28 August 2014 at 12:37:13' in str(response.data)

    @mock.patch('requests.get', return_value=fake_title)
    def test_address_on_title_page(self, mock_get):
        response = self.app.get('/titles/titleref')
        assert '17 Hazelbury Crescent' in str(response.data)
        assert 'Luton' in str(response.data)
        assert 'LU1 1DZ' in str(response.data)

    @mock.patch('requests.get', return_value=fake_partial_address)
    def test_partial_address_on_title_page(self, mock_get):
        response = self.app.get('/titles/titleref')
        assert 'Hazelbury Crescent' in str(response.data)
        assert 'Luton' in str(response.data)
        assert 'LU1 1DZ' in str(response.data)

    @mock.patch('requests.get', return_value=fake_no_address_title)
    def test_not_available_when_no_address_on_title_page(self, mock_get):
        response = self.app.get('/titles/titleref')
        assert 'Not Available' in str(response.data)

    @mock.patch('requests.get', return_value=fake_title)
    def test_proprietor_on_title_page(self, mock_get):
        response = self.app.get('/titles/titleref')
        assert 'Scott Oakes' in str(response.data)

    @mock.patch('requests.get', return_value=fake_title)
    def test_index_geometry_on_title_page(self, mock_get):

        coordinate_data = "[[[508263.97, 221692.13], [508266.4, 221698.84], [508266.35, 221700.25], [508270.3, 221711.15], [508273.29, 221719.53], [508271.4, 221721.65], [508270.68, 221722.44], [508269.69, 221723.53], [508263.58, 221706.87], [508258.98, 221693.93], [508258.01, 221691.18], [508262, 221689.66], [508262.95, 221689.3], [508263.97, 221692.13]]]"
        response = self.app.get('/titles/titleref')
        assert 'geometry' in str(response.data)
        assert 'coordinates' in str(response.data)
        assert coordinate_data in str(response.data)


login_json = '{{"credentials":{{"user_id":"{}","password":"{}"}}}}'
mock_response = namedtuple('Response', ['status_code'])
successful_response = mock_response(200)
invalid_credentials = mock_response(401)


class TestLogin:

    def setup_method(self, method):
        self.app = app.test_client()

    @mock.patch('requests.post', return_value=successful_response)
    def test_calls_api(self, mock_post):
        self.app.post('/login', data={'username': 'username1',
                                                 'password': 'password1'},
                                 follow_redirects=True)

        mock_post.assert_called_with('http://landregistry.local:8005/user/authenticate',
                                     data='{"credentials":{"user_id":"username1","password":"password1"}}',
                                     headers={'content-type': 'application/json'})

    @mock.patch('requests.post', return_value=successful_response)
    def test_correct_login(self, mock_post):
        response = self.app.post('/login', data={'username': 'username1',
                                                 'password': 'password1'},
                                 follow_redirects=True)
        
        assert True

    @mock.patch('requests.post', return_value=successful_response)
    def test_missing_username(self, mock_post):
        response = self.app.post('/login', data={'username': '',
                                                 'password': 'password1'},
                                 follow_redirects=True)

        assert response.status_code == 200
        assert 'Username is required' in str(response.data)

    @mock.patch('requests.post', return_value=successful_response)
    def test_missing_password(self, mock_post):
        response = self.app.post('/login', data={'username': 'username2',
                                                 'password': ''},
                                 follow_redirects=True)

        assert response.status_code == 200
        assert 'Password is required' in str(response.data)

    @mock.patch('requests.post', return_value=successful_response)
    def test_missing_password_and_username(self, mock_post):
        response = self.app.post('/login', data={'username': '',
                                                 'password': ''},
                                 follow_redirects=True)

        assert response.status_code == 200
        assert 'Password is required' in str(response.data)
        assert 'Username is required' in str(response.data)

    @mock.patch('requests.post', return_value=invalid_credentials)
    def test_invalid_credentials(self, mock_post):
        response = self.app.post('/login', data={'username': 'wrongname',
                                                 'password': 'wrongword'},
                                 follow_redirects=True)
        assert 'There was an error with your Username/Password combination. Please try again' in str(response.data)

if __name__ == '__main__':
    pytest.main()
