import os
from dotenv import load_dotenv
from requests_cache import CachedSession

load_dotenv()

tibber_token = os.getenv('TIBBER_TOKEN')
house_id = os.getenv('HOUSE_ID')

TIBBER_API = "https://api.tibber.com/v1-beta/gql"

def get_price_history():
    query = """
{
  viewer {
    home(id: "%s") {
      currentSubscription {
        priceInfo {
          range(resolution: HOURLY, last: 200) {
            nodes {
              startsAt
              total
            }
          }
        }
      }
    }
  }
}
""" % house_id

    session = CachedSession('http_cache',
                            backend='filesystem',
                            serializer='json',
                            allowable_methods=('GET', 'POST'))

    response = session.post(
        TIBBER_API,
        json={'query': query},
        headers={
            'Authorization': 'Bearer ' + tibber_token
        },
        timeout=0.5)

    return (response.json()['data']
            ['viewer']['home']['currentSubscription']
            ['priceInfo']['range']['nodes'])



print(get_price_history())
