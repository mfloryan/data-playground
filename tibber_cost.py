"""Plotting Tibber hourly price statistics"""

import datetime
import os
from functools import partial
from dotenv import load_dotenv
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from tibber_api import get_price_history


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


def title_page():
    fig = plt.figure(figsize=(10, 6))
    fig.text(0.5, 0.5, "Tibber Hourly Electricity Prices",
            fontsize=28, ha='center', va='center')
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

metadata = {
    'Creator': 'tibber_cost.py',
    'Author': 'Marcin Floryan',
    'Title': 'Visualisation of Tibber Hourly Prices',
    'CreationDate': datetime.datetime.today()
}

with PdfPages('tibber-energy-prices.pdf', metadata=metadata) as pdf:

    save_plot_to_pdf(pdf,
                     title_page,
                     partial(prices_boxplot, df),
                     partial(prices_boxplot_per_date, df),
                     partial(prices_boxplot_per_hour, df)
                     )
