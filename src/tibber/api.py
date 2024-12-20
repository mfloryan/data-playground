"""Tibber API"""

from datetime import datetime, timedelta, timezone
from importlib.resources import files
from requests_cache import CachedSession

TIBBER_API = "https://api.tibber.com/v1-beta/gql"


def load_query_from_file(filename):
    with files("tibber").joinpath(filename).open("r", encoding="utf-8") as file:
        return file.read()


def get_price_history(tibber_token, house_id, weeks_to_get=4):
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
    cutoff_date = datetime.now(timezone.utc).astimezone() - timedelta(weeks=weeks_to_get)

    while True:

        query = query_template % (house_id, cursor)

        response = session.post(
            TIBBER_API,
            json={"query": query},
            headers={"authorization": "Bearer " + tibber_token},
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
