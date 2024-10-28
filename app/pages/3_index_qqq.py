import streamlit as st
import plotly.express as px
import requests
import pandas as pd
import io

# set the page config to wide mode
st.set_page_config(layout="wide")

# read the data from a REST api

INDEX = "QQQ"
BASE_URL = "https://backendservice-987-ea412ce0-q85m2kos.onporter.run/"

# Get the normalized data for INDEX
url = "{BASE_URL}indexdata/{INDEX}/normalizedstockdata"
url = url.format(BASE_URL=BASE_URL, INDEX=INDEX)
response = requests.get(url, headers={"Content-Type": "application/json"}, timeout=60)
normalized_data = pd.DataFrame()
# response is a media object of type "text/csv"
if response.status_code == 200:
    data = response.text
    normalized_data = pd.read_csv(io.StringIO(data))

    date_value = normalized_data["Datetime"]
    date_value = pd.to_datetime(date_value)
    date_value = date_value.dt.strftime("%Y-%m-%d")
    normalized_data["Date"] = date_value

else:
    st.write("Error fetching data from the API")

# Get the companies that make up the index and its meta data
url = "{BASE_URL}indexdata/{INDEX}/metadata"
url = url.format(BASE_URL=BASE_URL, INDEX=INDEX)
response = requests.get(url, headers={"Content-Type": "application/json"}, timeout=60)
index_metadata = pd.DataFrame()
# response is of type application/json
if response.status_code == 200:
    index_metadata = response.json()
    index_metadata = pd.DataFrame(index_metadata)
else:
    st.write("Error fetching data from the API")

# Get the last value of the stocks for each day
unique_date_value = normalized_data["Date"].unique()
day_close_data = {}
for date in unique_date_value:
    temp_data = normalized_data[normalized_data["Date"] == date]
    day_close_data[date] = temp_data.iloc[-1]
day_close_data = pd.DataFrame(day_close_data)
day_close_data = day_close_data.T
day_close_data = day_close_data.drop(columns=["Datetime", "Date"])


# Get the last 60 points data showing the last 60 minutes of the stocks
lasthour_close_data = normalized_data.iloc[-60:].drop(columns=["Datetime", "Date"])


# -------------------------
# Title the page
# -------------------------

# Get the latest value of INDEX with 3 decimal points
latest_index = normalized_data.iloc[-1][INDEX]
latest_index = round(latest_index, 3)

# Find if INDEX has increased or decreased for the day
index_day_close_data = day_close_data[INDEX]
index_day_close_data = index_day_close_data.diff().iloc[-1]
index_day_close_data = round(index_day_close_data, 3)

st.markdown(f"# {INDEX} Index - {latest_index} {'🟢' if index_day_close_data > 0 else '🔻'} (Today: ${index_day_close_data})")
st.write(f"This page provides insights into the {INDEX} index and companies/sectors that make up the index. The data is from yahoo finance and is updated every 15 minutes.")
# -------------------------
# display a graph with only "INDEX", "Normalized INDEX" data and autofit the y scale
# -------------------------
fig = px.line(
    normalized_data,
    y=[INDEX, "Normalized "+INDEX],
    title=f"Actual {INDEX} Vs Normalized {INDEX}",
    labels={"value": "Price", "index": "Date"},
)
st.plotly_chart(fig)


# -------------------------
# Show the impact of a sector on the INDEX
# -------------------------

# Find the sector wise accumulated data

sector_data = pd.DataFrame()
for sector in index_metadata["Sector"].unique():
    sector_companies = index_metadata[index_metadata["Sector"] == sector][INDEX+" Company"].values
    temp_sector_data = normalized_data[sector_companies].sum(axis=1)
    sector_data[sector] = temp_sector_data


with st.container(key="sector_container"):
    # Most impacted sector from last 60 data points

    sector_list_col, sector_graph_col = st.columns([1, 3])

    lasthour_close_sector_data_diff = (sector_data.iloc[-1] - sector_data.iloc[-60]).rename("60 min")    
    sector_list_col.dataframe(lasthour_close_sector_data_diff.to_frame().style.background_gradient(cmap='RdYlGn', vmin=-0.4, vmax=0.4), height=500)

    # User selection of the stock
    sectors_selected = sector_graph_col.multiselect("Select a Sector", options=sector_data.columns, default=["Semiconductors"])
    # Filter data based on selection
    selected_stock_data = sector_data[sectors_selected]
    # Plot the data
    fig = px.line(selected_stock_data)
    # Display the plot
    sector_graph_col.plotly_chart(fig)


# -------------------------
# order the stock with the highest movement for the last day
# -------------------------
day_close_data_diff = day_close_data.diff().drop(columns=[INDEX, "Normalized "+INDEX])
day_close_data_diff = day_close_data_diff.iloc[-1]
day_close_data_diff = day_close_data_diff.sort_values(ascending=False)

day_close_data_percentagediff = day_close_data.diff() / day_close_data.shift(1) * 100
day_close_data_percentagediff = day_close_data_percentagediff.drop(columns=[INDEX, "Normalized "+INDEX])
day_close_data_percentagediff = day_close_data_percentagediff.iloc[-1]
day_close_data_percentagediff = day_close_data_percentagediff.sort_values(ascending=False)


# -------------------------
# Find the difference between first and last value of lasthour_close_data (0th index and last index)
# -------------------------
lasthour_close_data_diff = (lasthour_close_data.iloc[-1] - lasthour_close_data.iloc[0]).rename("60 min")
lasthour_close_data_percentagediff = ((lasthour_close_data.iloc[-1] - lasthour_close_data.iloc[0]) / lasthour_close_data.iloc[0] * 100).rename("60 min")

lasthour_close_data_diff = lasthour_close_data_diff.drop(index=[INDEX, "Normalized "+INDEX])
lasthour_close_data_diff = lasthour_close_data_diff.sort_values(ascending=False)
lasthour_close_data_percentagediff = lasthour_close_data_percentagediff.drop(index=[INDEX, "Normalized "+INDEX])
lasthour_close_data_percentagediff = lasthour_close_data_percentagediff.sort_values(ascending=False)


# -------------------------
# Create a columns of information about the stocks
# -------------------------

with st.container(key="stock_container"):

    stock_day_impact_col, stock_hour_impact_col = st.columns(2, gap="small")

    stock_day_impact_col.markdown("#### Daily Impact")

    stock_col1, stock_col2, stock_col3, stock_col4 = stock_day_impact_col.columns(4, gap="small")
    stock_col1.markdown("**Most 🟢 Impact**")
    stock_col1.dataframe(day_close_data_diff, height=200)

    stock_col2.markdown("**Least 🔻 Impact**")
    stock_col2.dataframe(day_close_data_diff[::-1], height=200)

    stock_col3.markdown("**Most % 🟢 Impact**")
    stock_col3.dataframe(day_close_data_percentagediff, height=200)

    stock_col4.markdown("**Least % 🔻 Impact**")
    stock_col4.dataframe(day_close_data_percentagediff[::-1], height=200)

    stock_hour_impact_col.markdown("#### Hourly Impact")

    stock_col5, stock_col6, stock_col7, stock_col8 = stock_hour_impact_col.columns(4, gap="small")
    stock_col5.markdown("**Most 🟢 Impact**")
    stock_col5.dataframe(lasthour_close_data_diff, height=200)

    stock_col6.markdown("**Least 🔻 Impact**")
    stock_col6.dataframe(lasthour_close_data_diff[::-1], height=200)

    stock_col7.markdown("**Most % 🟢 Impact**")
    stock_col7.dataframe(lasthour_close_data_percentagediff, height=200)

    stock_col8.markdown("**Least % 🔻 Impact**")
    stock_col8.dataframe(lasthour_close_data_percentagediff[::-1], height=200)

# -------------------------
# display the data in a table
# -------------------------
