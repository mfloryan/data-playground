"""Plotting Tibber hourly price statistics"""

import os
from dotenv import load_dotenv
from requests_cache import CachedSession
import pandas as pd
import matplotlib.pyplot as plt

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


price_history = get_price_history()
df = pd.DataFrame(price_history)
df['startsAt'] = pd.to_datetime(df['startsAt'])

plt.figure(figsize=(8, 6))
plt.boxplot(df['total'], vert=False)
plt.title('Tibber hourly prices')
plt.xlabel('Price')
plt.show()
