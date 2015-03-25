import mock
import pytest

from service.server import app
from .fake_response import FakeResponse


with open('tests/fake_title.json', 'r') as fake_title_json_file:
    fake_title_json_string = fake_title_json_file.read()
    fake_title_bytes = str.encode(fake_title_json_string)
    fake_title = FakeResponse(fake_title_bytes)


with open('tests/fake_no_address_title.json', 'r') as fake_no_address_file:
    fake_no_address_title_json_string = fake_no_address_file.read()
    fake_no_address_title_bytes = str.encode(fake_no_address_title_json_string)
    fake_no_address_title = FakeResponse(fake_no_address_title_bytes)


with open('tests/fake_partial_address.json', 'r') as fake_partial_address_file:
    fake_partial_address_json_string = fake_partial_address_file.read()
    fake_partial_address_bytes = str.encode(fake_partial_address_json_string)
    fake_partial_address = FakeResponse(fake_partial_address_bytes)


unavailable_title = FakeResponse('', 404)


class TestViewTitleUnauthorised:
    def setup_method(self, method):
        self.app = app.test_client()

    def test_get_title_page_redirects_when_user_not_logged_in(self):
        response = self.app.get('/titles/titleref')
        assert response.status_code == 302

        assert 'Location' in response.headers
        login_location = '/login?next=%2Ftitles%2Ftitleref'
        assert response.headers['Location'].endswith(login_location)


class TestViewTitle:

    def setup_method(self, method):
        self.app = app.test_client()

        auth_method = 'service.server.LoginApiClient.authenticate_user'
        with mock.patch(auth_method, return_value=True) as mock_authorize:
            self._log_in_user()

    @mock.patch('requests.get', return_value=unavailable_title)
    def test_get_title_page_no_title(self, mock_get):
        response = self.app.get('/titles/titleref')
        assert response.status_code == 404

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
    def test_address_string_only_on_title_page(self, mock_get):
        response = self.app.get('/titles/titleref')
        address = '17 Hazelbury Crescent<br>Luton<br>LU1 1DZ'
        assert address in str(response.data)

    @mock.patch('requests.get', return_value=fake_title)
    def test_proprietor_on_title_page(self, mock_get):
        response = self.app.get('/titles/titleref')
        assert 'Scott Oakes' in str(response.data)

    @mock.patch('requests.get', return_value=fake_title)
    def test_index_geometry_on_title_page(self, mock_get):
        coordinate_data = '''
            [[[508263.97, 221692.13],
            [508266.4, 221698.84],
            [508266.35, 221700.25],
            [508270.3, 221711.15],
            [508273.29, 221719.53],
            [508271.4, 221721.65],
            [508270.68, 221722.44],
            [508269.69, 221723.53],
            [508263.58, 221706.87],
            [508258.98, 221693.93],
            [508258.01, 221691.18],
            [508262, 221689.66],
            [508262.95, 221689.3],
            [508263.97, 221692.13]]]
        '''
        response = self.app.get('/titles/titleref')
        assert 'geometry' in str(response.data)
        assert 'coordinates' in str(response.data)
        assert coordinate_data in str(response.data)

    def test_get_title_search_page(self):
        response = self.app.get('/title-search/')
        assert response.status_code == 200
        assert 'Find a title' in str(response.data)

    @mock.patch('requests.get', return_value=fake_title)
    def test_title_search_success(self, mock_get):
        response = self.app.post
        (
            '/title-search/',
            data=dict(search_term='DN1000'),
            follow_redirects=True
        )
        assert response.status_code == 200
        assert 'DN1000' in str(response.data)
        assert '28 August 2014 at 12:37:13' in str(response.data)
        assert '17 Hazelbury Crescent' in str(response.data)
        assert 'Luton' in str(response.data)
        assert 'LU1 1DZ' in str(response.data)

    def test_title_search_invalid_search_value_format(self):
        response = self.app.post
        (
            '/title-search/',
            data=dict(search_term='invalid value')
        )
        assert 'No result(s) found' in str(response.data)

    @mock.patch('requests.get', return_value=unavailable_title)
    def test_title_search_title_not_found(self, mock_get):
        response = self.app.post
        (
            '/title-search/',
            data=dict(search_term='DT1000')
        )
        assert 'No result(s) found' in str(response.data)

    def _log_in_user(self):
        self.app.post(
            '/login',
            data={'username': 'username1', 'password': 'password1'},
            follow_redirects=False
        )


if __name__ == '__main__':
    pytest.main()
