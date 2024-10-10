"""Mock data and response generation for Tibber API tests"""

from datetime import datetime, timedelta, timezone


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
                                        "startCursor": f"cursor{i}" if has_previous_page else None,
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


def single_item_scenario():
    return generate_responses(
        [[{"startsAt": "2023-09-15T12:00:00+00:00", "total": 0.1}]]
    )[0]


def four_pages_scenario():
    now = datetime.now(timezone.utc)
    node_lists = [
        [{"startsAt": (now - timedelta(days=i)).isoformat(), "total": 0.1} for i in range(1, 4)],
        [{"startsAt": (now - timedelta(days=i)).isoformat(), "total": 0.2} for i in range(4, 7)],
        [{"startsAt": (now - timedelta(days=i)).isoformat(), "total": 0.3} for i in range(7, 10)],
        [{"startsAt": (now - timedelta(days=10)).isoformat(), "total": 0.4}],
    ]
    return generate_responses(node_lists)
