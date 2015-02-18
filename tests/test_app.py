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
        self.assertIn('28 Aug 2014 at 12:37:13', str(response.data))

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
    def test_property_tenure_on_title_page(self, mock_get):
        response = self.app.get('/titles/titleref')
        self.assertIn('Freehold', str(response.data))
