"""Testing Tibber API code"""

import unittest
from unittest.mock import patch, MagicMock

from tibber import api


class TibberAPI(unittest.TestCase):

    def test_returning_data_from_a_single_page_response(self):
        with patch("tibber.api.CachedSession") as mocked_request:
            pretend_tibber_api.returns_single_item(mocked_request)
            response = api.get_price_history("test_token", "test_house_id")
            self.assertEqual(len(response), 1)

    def test_api_token_is_included_in_request(self):
        with patch("tibber.api.CachedSession") as mocked_request:
            pretend_tibber_api.returns_single_item(mocked_request)
            api.get_price_history("tibber_api_token", "house_id")
            post_call_arguments = mocked_request.return_value.post.call_args

            self.assertIn(
                "authorization",
                post_call_arguments.kwargs['headers'])

            self.assertEqual(
                post_call_arguments.kwargs['headers']['authorization'],
                "Bearer tibber_api_token")


class pretend_tibber_api:

    @staticmethod
    def returns_single_item(mocked_request):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "viewer": {
                    "home": {
                        "currentSubscription": {
                            "priceInfo": {
                                "range": {
                                    "nodes": [
                                        {"startsAt": "2023-09-15T12:00:00+00:00", "total": 0.1},
                                    ],
                                    "pageInfo": {
                                        "hasPreviousPage": False,
                                        "startCursor": ""
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        mock_session_instance = mocked_request.return_value
        mock_session_instance.post.return_value = mock_response
