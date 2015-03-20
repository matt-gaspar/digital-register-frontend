from collections import namedtuple
import mock
import pytest
from service.server import app


login_json = '{{"credentials":{{"user_id":"{}","password":"{}"}}}}'
mock_response = namedtuple('Response', ['status_code'])
successful_response = mock_response(200)
invalid_credentials = mock_response(401)


class TestLogin:
    def setup_method(self, method):
        self.app = app.test_client()

    def test_get_login_page(self):
        response = self.app.get('/login')
        assert response.status_code == 200
        assert 'Digital Register Login' in str(response.data)

    def test_get_home_page(self):
        response = self.app.get('/')
        assert response.status_code == 200
        assert 'Home' in str(response.data)

    @mock.patch('requests.post', return_value=successful_response)
    def test_calls_api(self, mock_post):
        self.app.post('/login', data={'username': 'username1', 'password': 'password1'}, follow_redirects=False)

        mock_post.assert_called_with(
            'http://landregistry.local:8005/user/authenticate',
            data='{"credentials":{"user_id":"username1","password":"password1"}}',
            headers={'content-type': 'application/json'}
        )

    @mock.patch('requests.post', return_value=successful_response)
    def test_login_redirects_to_title_search_when_no_url_provided(self, mock_post):
        response = self.app.post(
            '/login?next=titles',
            data={'username': 'username1', 'password': 'password1'},
            follow_redirects=False
        )

        assert response.status_code == 302

        assert 'Location' in response.headers
        assert response.headers['Location'].endswith('/titles')
        assert 'Set-Cookie' in response.headers
        assert response.headers['Set-Cookie'].startswith('session=')

    @mock.patch('requests.post', return_value=successful_response)
    def test_login_redirects_to_url_provided(self, mock_post):
        next_url = 'titles/AGL1234'

        response = self.app.post(
            '/login?next={}'.format(next_url),
            data={'username': 'username1', 'password': 'password1'},
            follow_redirects=False
        )

        assert response.status_code == 302

        assert 'Location' in response.headers
        assert response.headers['Location'].endswith(next_url)
        assert 'Set-Cookie' in response.headers
        assert response.headers['Set-Cookie'].startswith('session=')

    @mock.patch('requests.post', return_value=successful_response)
    def test_missing_username(self, mock_post):
        response = self.app.post('/login', data={'username': '', 'password': 'password1'}, follow_redirects=False)

        assert response.status_code == 200
        assert 'Username is required' in str(response.data)

    @mock.patch('requests.post', return_value=successful_response)
    def test_missing_password(self, mock_post):
        response = self.app.post('/login', data={'username': 'username2', 'password': ''}, follow_redirects=False)

        assert response.status_code == 200
        assert 'Password is required' in str(response.data)

    @mock.patch('requests.post', return_value=successful_response)
    def test_missing_password_and_username(self, mock_post):
        response = self.app.post('/login', data={'username': '', 'password': ''}, follow_redirects=False)

        assert response.status_code == 200
        assert 'Password is required' in str(response.data)
        assert 'Username is required' in str(response.data)

    @mock.patch('requests.post', return_value=invalid_credentials)
    def test_invalid_credentials(self, mock_post):
        response = self.app.post(
            '/login',
            data={'username': 'wrongname', 'password': 'wrongword'},
            follow_redirects=False
        )

        assert 'There was an error with your Username/Password combination. Please try again' in str(response.data)

    @mock.patch('requests.post', return_value=invalid_credentials)
    def test_overlong_username(self, mock_post):
        response = self.app.post(
            '/login',
            data={
                'username': '12345678901234567890123456789012345678901234567890123456789012345678901',
                'password': 'wrongword'
            },
            follow_redirects=False
        )

        assert 'Username is incorrect' in str(response.data)

    @mock.patch('requests.post', return_value=invalid_credentials)
    def test_too_short_username(self, mock_post):
        response = self.app.post('/login', data={'username': '123', 'password': 'wrongword'}, follow_redirects=False)
        assert 'Username is incorrect' in str(response.data)


if __name__ == '__main__':
    pytest.main()
