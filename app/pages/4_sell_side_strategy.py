import streamlit as st
import plotly.express as px
import requests
import pandas as pd
import io

# set the page config to wide mode
st.set_page_config(layout="wide")

# read the data from a REST api
# BASE_URL = "https://backendservice-987-ea412ce0-q85m2kos.onporter.run/"
BASE_URL = "http://127.0.0.1:8000/"

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


# Get the options data
url = "{BASE_URL}selloptionsdata"
url = url.format(BASE_URL=BASE_URL)
response = requests.get(url, headers={"Content-Type": "application/json"}, timeout=60)
sell_options_data = pd.DataFrame()

# response is a media object of type "text/csv"
if response.status_code == 200:
    data = response.text
    sell_options_data = pd.read_csv(io.StringIO(data), index_col=0)

else:
    st.write("Error fetching data from the API")


stock_url = "{BASE_URL}stockoptionsdata/{company}"

def on_option_selection(*args, **kwargs):
    selection = st.session_state["sell_options_data_dataframe"]["selection"]["rows"]
    if selection:
        company = sell_options_data.iloc[selection[0]].name
        stock_url = "{BASE_URL}stockoptionsdata/{company}".format(BASE_URL=BASE_URL, company=company)

        response = requests.get(stock_url, headers={"Content-Type": "application/json"}, timeout=60)
        call_options_chain_data = pd.DataFrame()
        put_options_chain_data = pd.DataFrame()

        if response.status_code == 200:
            # response is a dictionary
            options_chain_data = response.json()
            call_options_chain_data = pd.DataFrame(options_chain_data["Call Options"])
            put_options_chain_data = pd.DataFrame(options_chain_data["Put Options"])
            information = options_chain_data["Information"]

            # reverse the rows
            call_options_chain_data = call_options_chain_data.iloc[::-1]
            put_options_chain_data = put_options_chain_data.iloc[::-1]

        else:
            sell_side_options_col2.error("Error fetching data from the API")
        
        try:
            tab_call_chain.dataframe(call_options_chain_data)
            tab_put_chain.dataframe(put_options_chain_data)
            tab_info_info.write("**Ticker:** {data}".format(data=information["Company"]))
            tab_info_info.write("**Sector:** {data}".format(data=information["sector"]))
            tab_info_info.write("**Earnings Date:** {data}".format(data=information["Earnings Date"]))
            tab_info_info.write("**Average Volume:** {data}".format(data=information["averageVolume"]))
            tab_info_info.write("**Current Price:** {data}".format(data=information["Last Value"].__round__(2)))
            tab_info_info.write("**Last Week Open:** {data}".format(data=information["7_day_open_price"].__round__(2)))
            tab_info_info.write("**52 Week High:** {data}".format(data=information["fiftyTwoWeekHigh"].__round__(2)))
            tab_info_info.write("**52 Week Low:** {data}".format(data=information["fiftyTwoWeekLow"].__round__(2)))
            tab_info_info.write("**Forward PE:** {data}".format(data=information["forwardPE"]))
            tab_info_info.write("**Dividend Yield:** {data}".format(data=information["dividendYield"]))

        except Exception as e:
            tab_info_info.warning("Some information is not available")

        try:
            if information["news"]:
                for news in information["news"]:
                    tab_info_news.page_link(news["link"], label=news["title"])
            else:
                tab_info_news.warning("No news available")
        
        except Exception as e:
            tab_info_news.warning("No news available")

        try:
            # plot the column "strike", "extrinsic_gain_ratio"
            # plot 2 would be a vertical line at current price
            tab_info_stats.line_chart(call_options_chain_data, x="strike", y="extrinsic_gain_ratio", height=450)
        
        except Exception as e:
            tab_info_stats.warning("No Plot data available")
       


# -------------------------
# Title the page
# -------------------------

st.title("Sell Side Options Strategy")
st.write("The Sell Side Options Strategy is a strategy that involves selling options contracts to generate income. This strategy is used when the investor expects the price of the underlying asset to remain stable or increase slightly. The investor sells options contracts to earn the premium and keep the premium if the options expire worthless. This strategy is used to generate income in a low-volatility market environment.")

# -------------------------
# Show the Sell Side Options Data
# -------------------------

with st.container(key="sell_options_data_container"):
    st.write("#### Sell Side Options Data")
    st.write("The below table shows the information on which stock has the maximum percentage profit (option value / stock value) when selling option of the stock at **90%** of the stock price. The expectation is that stock will not go down by 10% in a week time, and the option will expire worthless. The table also shows the percentage profit when selling call and put options.")

    sell_side_options_col1, sell_side_options_col2 = st.columns([1.4, 2.6])

    #drop the rows with value 0
    sell_options_data = sell_options_data[sell_options_data["Extrinsic sell call gain at 90%"] != 0]
    sell_options_data = sell_options_data[sell_options_data["Extrinsic sell put gain at 90%"] != 0]
    # remove the Earnings Date column
    sell_options_data = sell_options_data.drop(columns=["Earnings Date"])
    # rename the columns for better readability
    sell_options_data.rename(columns={"Extrinsic sell call gain at 90%": "Call Opt. Gain (%)", "Extrinsic sell put gain at 90%": "Put Opt. Gain (%)"}, inplace=True)
    
    sell_side_options_col1.dataframe(sell_options_data, height=500, key="sell_options_data_dataframe", on_select=on_option_selection, selection_mode="single-row")

    # -------------------------
    # Show a single stock information in a tab
    # -------------------------

    tab_info, tab_info_news, tab_call_chain, tab_put_chain = sell_side_options_col2.tabs(["Info", "News", "Call Options Chain", "Put Options Chain"])

    with tab_info.container():
        tab_info_info, tab_info_stats = st.columns([1, 3])



# -------------------------
# Show the Momentum Data
# -------------------------

momentum_data.rename(columns={"Recent Momentum": "Peak Swing (%)", "Current Momentum": "Current Swing (%)", "Peak": "Peak ($)", "Recent Volume": "Current Vol.", "Median Volume": "Median Vol.", "Average Volume": "Avg Vol."}, inplace=True)

with st.container(key="momentume_data"):

    try:
        slowed_momentum_col1, full_momentum_col1 = st.columns([1, 1])

        # -------------------------
        # Show the Stocks that had slowed and continued strong momentum recently
        # -------------------------

        # filter the data to show only stocks that had strong momentum and recently
        slowed_momentum_col1.write("#### Momentum Stocks that had recently slowed down")
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

        full_momentum_col1.write("#### Momentum Stocks that continues strong momentum")

        full_momentum_stocks = momentum_data[momentum_data["Unsettled"]]
        full_momentum_stocks = full_momentum_stocks.drop(columns=["Settled", "Settled Duration", "Unsettled"])

        # order by better settled percentage
        full_momentum_stocks["Swing Percentage %"] = abs(full_momentum_stocks["Current Swing (%)"])
        full_momentum_stocks = full_momentum_stocks.sort_values(by="Swing Percentage %", ascending=False).drop(columns=["Swing Percentage %"])

        full_momentum_col1.dataframe(full_momentum_stocks)

    except Exception as e:
        st.write("Error displaying the momentum data")
        st.write(e)
