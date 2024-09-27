"""Plotting Tibber hourly price statistics"""

import os
from dotenv import load_dotenv
from requests_cache import CachedSession
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

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
          range(resolution: HOURLY, last: 400) {
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


def prices_boxplot(df):
    fig, ax = plt.subplots(figsize=(10, 4))
    df.boxplot(column="total", vert=False, ax=ax)
    fig.suptitle('Tibber hourly prices')
    ax.set_title(f"Date range: {df['date'].min()} - {df['date'].max()}")
    return fig


def prices_boxplot_per_date(df):
    fig, ax = plt.subplots(figsize=(10, 6))
    df.boxplot(column='total', by='date', vert=False, ax=ax)
    ax.set_title('Tibber hourly prices by date')
    ax.set_xlabel('Price')
    fig.suptitle('')
    return fig


def prices_boxplot_per_hour(df):
    fig, ax = plt.subplots(figsize=(10, 6))
    df.boxplot(column='total', by='hour', vert=False, ax=ax)
    ax.set_title('Tibber hourly prices by hour of the day')
    ax.set_xlabel('Price')
    fig.suptitle('')
    return fig


def save_plot_to_pdf(pdf, *figure_generators):
    for generator in figure_generators:
        fig = generator()
        pdf.savefig(fig)
        plt.close(fig)


price_history = get_price_history()
df = pd.DataFrame(price_history)
df['startsAt'] = pd.to_datetime(df['startsAt'])
df['date'] = df['startsAt'].dt.date
df['hour'] = df['startsAt'].dt.hour

with PdfPages('tibber-energy-prices.pdf') as pdf:

    save_plot_to_pdf(pdf,
                     lambda: prices_boxplot(df),
                     lambda: prices_boxplot_per_date(df),
                     lambda: prices_boxplot_per_hour(df)
                     )
