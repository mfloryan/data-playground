"""Plotting Tibber hourly price statistics"""

import os
from functools import partial
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from requests_cache import CachedSession
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


TIBBER_API = "https://api.tibber.com/v1-beta/gql"


def load_query_from_file(filename):
    with open(filename, 'r', encoding="utf-8") as file:
        return file.read()


def get_price_history(tibber_token, house_id):
    query_template = load_query_from_file('tibber_price_info.graphql')

    session = CachedSession('http_cache',
                            backend='filesystem',
                            serializer='json',
                            allowable_methods=('GET', 'POST'))

    all_data = []
    cursor = ""
    cutoff_date = datetime.now(timezone.utc).astimezone() - timedelta(weeks=4)

    while True:

        query = query_template % (house_id, cursor)

        response = session.post(
            TIBBER_API,
            json={'query': query},
            headers={
                'Authorization': 'Bearer ' + tibber_token
            },
            timeout=0.5)

        data = (response.json()['data']
                ['viewer']['home']['currentSubscription']
                ['priceInfo']['range'])

        all_data.extend(data['nodes'])

        date_of_earliest_price = datetime.fromisoformat(
            data['nodes'][0]['startsAt'])

        if date_of_earliest_price < cutoff_date:
            break

        if data['pageInfo']['hasPreviousPage']:
            cursor = data['pageInfo']['startCursor']
        else:
            break

    return all_data


def prices_boxplot(df):
    fig, ax = plt.subplots(figsize=(10, 4))
    df.boxplot(column="total", vert=False, ax=ax)
    fig.suptitle('Tibber hourly prices')
    ax.set_title(f"Date range: {df['date'].min()} - {df['date'].max()}")
    return fig


def prices_boxplot_per_date(df):
    fig, ax = plt.subplots(figsize=(10, 2 + (df['date'].unique().size / 5)))
    df.boxplot(column='total', by='date', vert=False, ax=ax)
    ax.set_title('Tibber hourly prices by date')
    ax.set_xlabel('Price')
    ax.invert_yaxis()
    fig.suptitle('')
    fig.subplots_adjust(left=0.15)
    return fig


def prices_boxplot_per_hour(df):
    fig, ax = plt.subplots(figsize=(10, 6))
    df.boxplot(column='total', by='hour', ax=ax)
    ax.set_title('Tibber hourly prices by hour of the day')
    ax.set_ylabel('price')
    ax.set_xlabel('hour')
    fig.suptitle('')
    return fig


def save_plot_to_pdf(pdf, *figure_generators):
    for generator in figure_generators:
        fig = generator()
        pdf.savefig(fig)
        plt.close(fig)


load_dotenv()

tibber_token = os.getenv('TIBBER_TOKEN')
house_id = os.getenv('HOUSE_ID')

price_history = get_price_history(tibber_token, house_id)
df = pd.DataFrame(price_history)
df['startsAt'] = pd.to_datetime(df['startsAt'])
df['date'] = df['startsAt'].dt.date
df['hour'] = df['startsAt'].dt.hour

with PdfPages('tibber-energy-prices.pdf') as pdf:

    save_plot_to_pdf(pdf,
                     partial(prices_boxplot, df),
                     partial(prices_boxplot_per_date, df),
                     partial(prices_boxplot_per_hour, df)
                     )
