"""Testing Tibber API code"""

import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from tibber import api


class TibberAPI(unittest.TestCase):

    def test_returning_data_from_a_single_page_response(self):
        with patch("tibber.api.CachedSession") as mocked_request:
            pretend_tibber_api.returns_single_item(mocked_request)
            response = api.get_price_history("test_token", "test_house_id")
            self.assertEqual(len(response), 1)

    def test_making_requests_until_there_is_no_previour_page(self):
        with patch("tibber.api.CachedSession") as mocked_request:
            pretend_tibber_api.returns_four_pages_of_data(mocked_request)
            api.get_price_history("test_token", "test_house_id")
            self.assertEqual(mocked_request.return_value.post.call_count, 4)

    def test_api_token_is_included_in_request(self):
        with patch("tibber.api.CachedSession") as mocked_request:
            pretend_tibber_api.returns_single_item(mocked_request)
            api.get_price_history("tibber_api_token", "house_id")
            post_call_arguments = mocked_request.return_value.post.call_args

            self.assertIn(
                "authorization", post_call_arguments.kwargs["headers"]
            )

            self.assertEqual(
                post_call_arguments.kwargs["headers"]["authorization"],
                "Bearer tibber_api_token",
            )


class pretend_tibber_api:

    @staticmethod
    def returns_single_item(mocked_request):
        mocked_request.return_value.post.return_value.json.return_value = (
            pretend_tibber_api.generate_responses(
                [[{"startsAt": "2023-09-15T12:00:00+00:00", "total": 0.1}]]
            )[0]
        )

    @staticmethod
    def returns_four_pages_of_data(mocked_request):
        now = datetime.now(timezone.utc)
        node_lists = [
            [
                {
                    "startsAt": (now - timedelta(days=i)).isoformat(),
                    "total": 0.1,
                }
                for i in range(1, 4)
            ],
            [
                {
                    "startsAt": (now - timedelta(days=i)).isoformat(),
                    "total": 0.2,
                }
                for i in range(4, 7)
            ],
            [
                {
                    "startsAt": (now - timedelta(days=i)).isoformat(),
                    "total": 0.3,
                }
                for i in range(7, 10)
            ],
            [
                {
                    "startsAt": (now - timedelta(days=10)).isoformat(),
                    "total": 0.4,
                }
            ],
        ]
        responses = pretend_tibber_api.generate_responses(node_lists)

        mocked_request.return_value.post.return_value.json.side_effect = (
            responses
        )

    @staticmethod
    def generate_responses(pages_of_nodes):
        responses = []
        for i, nodes in enumerate(pages_of_nodes):
            has_previous_page = i < len(pages_of_nodes) - 1
            response = {
                "data": {
                    "viewer": {
                        "home": {
                            "currentSubscription": {
                                "priceInfo": {
                                    "range": {
                                        "nodes": nodes,
                                        "pageInfo": {
                                            "hasPreviousPage": has_previous_page,
                                            "startCursor": (
                                                f"cursor{i}"
                                                if has_previous_page
                                                else None
                                            ),
                                        },
                                    }
                                }
                            }
                        }
                    }
                }
            }
            responses.append(response)
        return responses
