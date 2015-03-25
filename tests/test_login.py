from collections import namedtuple
import json
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
    def test_login_calls_api(self, mock_post):
        self.app.post
        (
            '/login',
            data={'username': 'username1', 'password': 'password1'},
            follow_redirects=False
        )

        expected_data = {
            'credentials':
                {'user_id': 'username1', 'password': 'password1'}
        }

        actual_calls = mock_post.mock_calls

        assert len(actual_calls) == 1
        args = actual_calls[0][1]
        kwargs = actual_calls[0][2]

        assert args == ('http://landregistry.local:8005/user/authenticate',)
        assert len(kwargs) == 2
        assert kwargs.get('headers') == {'content-type': 'application/json'}
        assert 'data' in kwargs
        body = json.loads(kwargs.get('data'))
        assert body == expected_data

    @mock.patch('requests.post', return_value=successful_response)
    def test_login_sends_escaped_credentials_to_api(self, mock_post):
        self.app.post(
            '/login',
            data={
                'username': 'user",
                "name": "some',
                'password': 'pass",
                "word": "some'
            },
            follow_redirects=False
        )

        expected_data = {
            'credentials': {
                'password': 'pass",
                "word": "some',
                'user_id': 'user",
                "name": "some'
            }
        }

        actual_calls = mock_post.mock_calls

        assert len(actual_calls) == 1
        kwargs = actual_calls[0][2]

        assert 'data' in kwargs
        body = json.loads(kwargs.get('data'))
        assert body == expected_data

    @mock.patch('requests.post', return_value=successful_response)
    def test_login_redirects_to_search_when_no_url_provided(self, mock_post):
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
        response = self.app.post
        (
            '/login',
            data={'username': '', 'password': 'password1'},
            follow_redirects=False
        )

        assert response.status_code == 200
        assert 'Username is required' in str(response.data)

    @mock.patch('requests.post', return_value=successful_response)
    def test_missing_password(self, mock_post):
        response = self.app.post
        (
            '/login',
            data={'username': 'username2', 'password': ''},
            follow_redirects=False
        )

        assert response.status_code == 200
        assert 'Password is required' in str(response.data)

    @mock.patch('requests.post', return_value=successful_response)
    def test_missing_password_and_username(self, mock_post):
        response = self.app.post
        (
            '/login',
            data={'username': '', 'password': ''},
            follow_redirects=False
        )

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
        username_password_error_message = '''There was an error with your
            Username/Password combination. Please try again
        '''
        assert username_password_error_message in str(response.data)

    def test_cant_login_after_too_many_bad_logins(self):
        m = mock.patch('requests.post', return_value=invalid_credentials)
        with m as mock_post:
            for i in range(15):
                response = self.app.post(
                    '/login',
                    data={'username': 'username1', 'password': 'wrongword'},
                    follow_redirects=False
                )

        m = mock.patch('requests.post', return_value=successful_response)
        with m as mock_post:
            response = self.app.post(
                '/login',
                data={'username': 'username1', 'password': 'password1'},
                follow_redirects=False
            )

            username_password_error_message = '''There was an error with your
                Username/Password combination. Please try again
            '''
            assert username_password_error_message in str(response.data)

    @mock.patch('requests.post', return_value=invalid_credentials)
    def test_overlong_username(self, mock_post):
        char_set = string.ascii_uppercase + string.digits
        long_user = ''.join(random.sample(char_set*100, 100))
        response = self.app.post(
            '/login',
            data={
                'username': long_user,
                'password': 'wrongword'
            },
            follow_redirects=False
        )

        assert 'Username is incorrect' in str(response.data)

    @mock.patch('requests.post', return_value=invalid_credentials)
    def test_too_short_username(self, mock_post):
        user_data = {'username': '123', 'password': 'wrongword'}
        response = self.app.post
        (
            '/login',
            data=user_data,
            follow_redirects=False
        )
        assert 'Username is incorrect' in str(response.data)


if __name__ == '__main__':
    pytest.main()
