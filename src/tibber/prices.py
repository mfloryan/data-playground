"""Plotting Tibber hourly price statistics"""

import datetime
import os
from functools import partial
from dotenv import load_dotenv
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from tibber.api import get_price_history


def prices_boxplot(df):
    fig, ax = plt.subplots(figsize=(10, 4))
    df.boxplot(column="total", vert=False, ax=ax)
    fig.suptitle("Tibber hourly prices")
    ax.set_title(f"Date range: {df['date'].min()} - {df['date'].max()}")
    return fig


def prices_boxplot_per_date(df):
    fig, ax = plt.subplots(figsize=(10, 2 + (df["date"].unique().size / 5)))
    df.boxplot(column="total", by="date", vert=False, ax=ax)
    ax.set_title("Tibber hourly prices by date")
    ax.set_xlabel("Price")
    ax.invert_yaxis()
    fig.suptitle("")
    fig.subplots_adjust(left=0.15)
    return fig


def prices_boxplot_per_hour(df):
    fig, ax = plt.subplots(figsize=(10, 6))
    df.boxplot(column="total", by="hour", ax=ax)
    ax.set_title("Tibber hourly prices by hour of the day")
    ax.set_ylabel("price")
    ax.set_xlabel("hour")
    fig.suptitle("")
    return fig

def prices_boxplot_per_weekday(df):
    df["day_of_week"] = df["startsAt_local"].dt.weekday
    df["day_of_week_name"] = df["startsAt_local"].dt.strftime("%a")

    # Create ordered categories for days of the week
    day_order = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    df["day_of_week_name"] = pd.Categorical(
        df["day_of_week_name"], categories=day_order, ordered=True
    )

    fig, ax = plt.subplots(figsize=(10, 6))
    df.boxplot(column="total", by="day_of_week_name", ax=ax)
    ax.set_title("Tibber hourly prices by day of the week")
    ax.set_xlabel("Day of the Week")
    ax.set_ylabel("Price")
    fig.suptitle("")
    return fig

def prices_boxplot_grouped_by_weeks(df):
    df["week"] = df["startsAt_local"].dt.isocalendar().week
    df["day_of_week"] = df["startsAt_local"].dt.weekday
    df["day_of_week_name"] = df["startsAt_local"].dt.strftime("%a")

    # Create ordered categories for days of the week
    day_order = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    df["day_of_week_name"] = pd.Categorical(
        df["day_of_week_name"], categories=day_order, ordered=True
    )

    weeks = df["week"].unique()[::-1]  # Reverse the order of weeks
    n_weeks = len(weeks)
    n_cols = 3
    n_rows = (n_weeks + n_cols - 1) // n_cols

    fig, axes = plt.subplots(
        n_rows, n_cols, figsize=(15, 2 + n_rows * 2), sharex=True
    )
    axes = axes.flatten()

    for ax in axes[n_weeks:]:
        ax.axis("off")  # Turn off axes for empty subplots

    for ax, week in zip(axes, weeks):
        week_data = df[df["week"] == week]
        week_data.boxplot(column="total", by="day_of_week_name", ax=ax)
        ax.set_title(f"Week {week}")
        ax.set_xlabel("Day of the Week")
        ax.set_ylabel("Price")

    fig.suptitle("Tibber hourly prices by week and day of the week")
    fig.subplots_adjust(left=0.15, hspace=0.4, wspace=0.4)
    return fig


def title_page():
    fig = plt.figure(figsize=(10, 6))
    fig.text(
        0.5,
        0.5,
        "Tibber Hourly Electricity Prices",
        fontsize=28,
        ha="center",
        va="center",
    )
    return fig


def save_plot_to_pdf(pdf, *figure_generators):
    for generator in figure_generators:
        fig = generator()
        pdf.savefig(fig)
        plt.close(fig)


load_dotenv()

tibber_token = os.getenv("TIBBER_TOKEN")
house_id = os.getenv("HOUSE_ID")

price_history = get_price_history(tibber_token, house_id)
df = pd.DataFrame(price_history)
df["startsAt"] = pd.to_datetime(df["startsAt"], utc=True)
df["startsAt_local"] = df["startsAt"].dt.tz_convert("Europe/Stockholm")
df["date"] = df["startsAt_local"].dt.date
df["hour"] = df["startsAt_local"].dt.hour

metadata = {
    "Creator": "tibber_cost.py",
    "Author": "Marcin Floryan",
    "Title": "Visualisation of Tibber Hourly Prices",
    "CreationDate": datetime.datetime.today(),
}

with PdfPages("tibber-energy-prices.pdf", metadata=metadata) as pdf:

    save_plot_to_pdf(
        pdf,
        title_page,
        partial(prices_boxplot, df),
        partial(prices_boxplot_per_date, df),
        partial(prices_boxplot_grouped_by_weeks, df),
        partial(prices_boxplot_per_weekday, df),
        partial(prices_boxplot_per_hour, df),
    )
