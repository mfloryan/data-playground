"""Tibber API"""

from datetime import datetime, timedelta, timezone
import importlib.resources
from requests_cache import CachedSession

TIBBER_API = "https://api.tibber.com/v1-beta/gql"


def load_query_from_file(filename):
    with importlib.resources.open_text(
         'tibber', filename, encoding='utf-8') as file:
        return file.read()


def get_price_history(tibber_token, house_id):
    query_template = load_query_from_file("tibber_price_info.graphql")

    session = CachedSession(
        "http_cache",
        backend="filesystem",
        serializer="json",
        allowable_methods=("GET", "POST"),
        expire_after=timedelta(minutes=90),
    )

    all_data = []
    cursor = ""
    cutoff_date = datetime.now(timezone.utc).astimezone() - timedelta(weeks=4)

    while True:

        query = query_template % (house_id, cursor)

        response = session.post(
            TIBBER_API,
            json={"query": query},
            headers={"Authorization": "Bearer " + tibber_token},
            timeout=0.5,
        )

        data = (response.json()["data"]["viewer"]["home"]
                ["currentSubscription"]["priceInfo"]["range"])

        all_data.extend(data["nodes"])

        date_of_earliest_price = datetime.fromisoformat(
            data["nodes"][0]["startsAt"])

        if date_of_earliest_price < cutoff_date:
            break

        if data["pageInfo"]["hasPreviousPage"]:
            cursor = data["pageInfo"]["startCursor"]
        else:
            break

    return all_data
