from service.server import app
import json
import mock
import unittest
import requests
import responses

from .fake_response import FakeResponse

fake_title = FakeResponse(b'''{
    "address": "5 Granary Avenue Poundbury Dorchester DT1 4YY",
    "coordinates": {
        "latitude": 45,
        "longitude": 45
    },
    "last_changed": "2014-05-22 15:39:52",
    "lenders": [
        {
        "name": "Santander"
        }
    ],
    "number": "DT122047",
    "proprietors": [
        {
        "address": "5 Granary Avenue Poundbury Dorchester DT1 4YY",
        "name": "Raymond Frank Easton"
        },
        {
        "address": "5 Granary Avenue Poundbury Dorchester DT1 4YY",
        "name": "Carol Easton"
        }
    ],
    "tenure_type": "Leasehold"
    }'''
)


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
        self.assertTrue(str('22 May 2014 at 15:39:52') in str(response.data))
