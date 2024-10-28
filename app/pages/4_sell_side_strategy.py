import streamlit as st
import plotly.express as px
import requests
import pandas as pd
import io

# set the page config to wide mode
st.set_page_config(layout="wide")

# read the data from a REST api
BASE_URL = "https://backendservice-987-ea412ce0-q85m2kos.onporter.run/"

# Get the normalized data for INDEX
url = "{BASE_URL}stockmomentumdata"
url = url.format(BASE_URL=BASE_URL)
response = requests.get(url, headers={"Content-Type": "application/json"}, timeout=60)
momentum_data = pd.DataFrame()

# response is a media object of type "text/csv"
if response.status_code == 200:
    data = response.text
    momentum_data = pd.read_csv(io.StringIO(data), index_col=0)
    momentum_data = momentum_data.round(3)

else:
    st.write("Error fetching data from the API")


# -------------------------
# Title the page
# -------------------------

st.title("Sell Side Options Strategy")
st.write("The Sell Side Options Strategy is a strategy that involves selling options contracts to generate income. This strategy is used when the investor expects the price of the underlying asset to remain stable or increase slightly. The investor sells options contracts to earn the premium and keep the premium if the options expire worthless. This strategy is used to generate income in a low-volatility market environment.")

momentum_data.rename(columns={"Recent Momentum": "Peak Swing (%)", "Current Momentum": "Current Swing (%)", "Peak": "Peak ($)", "Recent Volume": "Current Vol.", "Median Volume": "Median Vol.", "Average Volume": "Avg Vol."}, inplace=True)

# -------------------------
# Show the Stocks that had strong momentum and recently slowed down
# -------------------------

st.write("#### Stocks that had strong Swing and recently slowed down")

with st.container(key="slowed_momentume_data"):
    # filter the data to show only stocks that had strong momentum and recently

    slowed_momentum_col1, slowed_momentum_col2 = st.columns([1, 1])

    slowed_momentum_stocks = momentum_data[momentum_data["Settled"]]
    slowed_momentum_stocks = slowed_momentum_stocks.drop(columns=["Settled", "Settled Duration", "Unsettled"])

    def highlight_current_volume(row):
        color = "background-color: lightgreen" if row["Current Vol."] > row["Avg Vol."] else ""
        return [None, None, None, color, None, None]
    slowed_momentum_stocks.style.apply(highlight_current_volume, axis=1)

    # order by better settled percentage
    slowed_momentum_stocks["Settled Percentage %"] = abs(slowed_momentum_stocks["Current Swing (%)"])
    slowed_momentum_stocks = slowed_momentum_stocks.sort_values(by="Settled Percentage %", ascending=True).drop(columns=["Settled Percentage %"])

    slowed_momentum_col1.dataframe(slowed_momentum_stocks)


# -------------------------
# Show the Stocks that had strong momentum and yet to slow down
# -------------------------

st.write("#### Stocks that had strong swing and yet to slow down")

with st.container(key="full_momentume_data"):
    # filter the data to show only stocks that had strong momentum and yet to slow down

    full_momentum_col1, full_momentum_col2 = st.columns([1, 1])

    full_momentum_stocks = momentum_data[momentum_data["Unsettled"]]
    full_momentum_stocks = full_momentum_stocks.drop(columns=["Settled", "Settled Duration", "Unsettled"])

    # order by better settled percentage
    full_momentum_stocks["Swing Percentage %"] = abs(full_momentum_stocks["Current Swing (%)"])
    full_momentum_stocks = full_momentum_stocks.sort_values(by="Swing Percentage %", ascending=False).drop(columns=["Swing Percentage %"])

    full_momentum_col1.dataframe(full_momentum_stocks)