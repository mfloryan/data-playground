"""Testing Tibber API code"""

import unittest
from unittest.mock import patch

from tibber import api
from tests.tibber_api_fixtures import single_item_scenario, four_pages_scenario


class TibberAPITest(unittest.TestCase):

    def setUp(self):
        self.patcher = patch("tibber.api.CachedSession")
        self.session_mock = self.patcher.start()
        self.addCleanup(self.patcher.stop)
        self.api_call_count = 0

    def simulate_api_response(self, scenario):
        if isinstance(scenario, list):
            self.session_mock.return_value.post.return_value.json.side_effect = scenario
        else:
            self.session_mock.return_value.post.return_value.json.return_value = scenario

        def count_calls(*args, **kwargs):
            self.api_call_count += 1
            return self.session_mock.return_value.post.return_value

        self.session_mock.return_value.post.side_effect = count_calls

    def get_last_request_headers(self):
        return self.session_mock.return_value.post.call_args.kwargs['headers']

    def test_returns_single_item_when_api_provides_one_item(self):
        self.simulate_api_response(single_item_scenario())
        response = api.get_price_history("test_token", "test_house_id")
        self.assertEqual(len(response), 1)

    def test_makes_multiple_requests_for_paginated_data(self):
        self.simulate_api_response(four_pages_scenario())
        api.get_price_history("test_token", "test_house_id")
        self.assertEqual(self.api_call_count, 4)

    def test_includes_api_token_in_request_headers(self):
        self.simulate_api_response(single_item_scenario())
        api.get_price_history("tibber_api_token", "house_id")
        headers = self.get_last_request_headers()

        self.assertIn("authorization", headers)
        self.assertEqual(headers["authorization"], "Bearer tibber_api_token")
