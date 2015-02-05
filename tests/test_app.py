from service.server import app
import unittest
import json

import mock
import unittest
import requests
import responses

class ViewTitleTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_get_title_page(self):
        response = self.app.get('/titles/titleref')
        assert response.status_code == 200
