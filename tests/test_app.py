from service.server import app
import json
import mock
import unittest
import requests
import responses

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

class ViewTitleTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    @mock.patch('requests.get', return_value=fake_title)
    def test_get_title_page(self, mock_get):
        response = self.app.get('/titles/titleref')
        assert response.status_code == 200

    @mock.patch('requests.get', return_value=fake_title)
    def test_date_formatting_on_title_page(self, mock_get):
        response = self.app.get('/titles/titleref')
        self.assertIn('28 August 2014 at 12:37:13', str(response.data))

    @mock.patch('requests.get', return_value=fake_title)
    def test_address_on_title_page(self, mock_get):
        response = self.app.get('/titles/titleref')
        self.assertIn('17 Hazelbury Crescent', str(response.data))
        self.assertIn('Luton', str(response.data))
        self.assertIn('LU1 1DZ', str(response.data))

    @mock.patch('requests.get', return_value=fake_partial_address)
    def test_partial_address_on_title_page(self, mock_get):
        response = self.app.get('/titles/titleref')
        self.assertIn('Hazelbury Crescent', str(response.data))
        self.assertIn('Luton', str(response.data))
        self.assertIn('LU1 1DZ', str(response.data))

    @mock.patch('requests.get', return_value=fake_no_address_title)
    def test_not_available_when_no_address_on_title_page(self, mock_get):
        response = self.app.get('/titles/titleref')
        self.assertIn('Not Available', str(response.data))

    @mock.patch('requests.get', return_value=fake_title)
    def test_proprietor_on_title_page(self, mock_get):
        response = self.app.get('/titles/titleref')
        self.assertIn('Scott Oakes', str(response.data))

    @mock.patch('requests.get', return_value=fake_title)
    def test_index_geometry_on_title_page(self, mock_get):

        coordinate_data = "[[[508263.97, 221692.13], [508266.4, 221698.84], [508266.35, 221700.25], [508270.3, 221711.15], [508273.29, 221719.53], [508271.4, 221721.65], [508270.68, 221722.44], [508269.69, 221723.53], [508263.58, 221706.87], [508258.98, 221693.93], [508258.01, 221691.18], [508262, 221689.66], [508262.95, 221689.3], [508263.97, 221692.13]]]"
        response = self.app.get('/titles/titleref')
        self.assertIn('geometry', str(response.data))
        self.assertIn('coordinates', str(response.data))
        self.assertIn(coordinate_data, str(response.data))
