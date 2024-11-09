import streamlit as st
import plotly.express as px
import requests
import pandas as pd
import io

from streamlit_flow import streamlit_flow
from streamlit_flow.elements import StreamlitFlowNode, StreamlitFlowEdge
from streamlit_flow.state import StreamlitFlowState
from streamlit_flow.layouts import TreeLayout, LayeredLayout

#---------------------------------#
# Get the stock analysis data
#---------------------------------#

BASE_URL = "https://backendservice-987-ea412ce0-q85m2kos.onporter.run/"

# Get the normalized data for INDEX
url = "{BASE_URL}stockanalysis"
url = url.format(BASE_URL=BASE_URL)
response = requests.get(url, headers={"Content-Type": "application/json"}, timeout=60)
stockanalysis_df = pd.DataFrame()
# response is a media object of type "text/csv"
if response.status_code == 200:
    data = response.text
    stockanalysis_df = pd.read_csv(io.StringIO(data))

    # Remove the row index and make "Ticker" columns as index
    stockanalysis_df.set_index("Ticker", inplace=True)

else:
    st.write("Error fetching data from the API")


#---------------------------------#
# Get the spider data
#---------------------------------#

groups = {
    "Foundries": ["TSM", "INTC"],
    "Semi: CPU/GPU/Processor": ["NVDA", "AMD", "INTC", "QCOM"],
    "Semi: Comms": ["QCOM", "AVGO", "NXPI"],
    "Semi: Components": ["ADI", "TXN", "NXPI", "ON", "MRVL"],
    "Storage": ["WDC", "STX", "PSTG"],
    "Memory": ["MU"],
    "Servers/Computers": ["SMCI", "DELL"],
    "Data Center": ["MSFT", "GOOGL", "AMZN"],
    "Technology": ["AAPL", "MSFT", "GOOGL", "NFLX", "META", "PLTR"],
    "Networking": ["ANET", "CSCO", "NTAP"],
    "Heat Mgmt/Cooling": ["VRT", "NVT"],
    "Utilities/Power Solutions": ["VST", "NRG", "FSLR", "ENPH"],
    "Equipment/Tools": ["AMAT", "LRCX", "KLAC", "ASML"]
}

group_relation = {
    "Foundries": {
        "customers": ["Semi: CPU/GPU/Processor", "Semi: Comms", "Semi: Components"]
    },
    "Semi: CPU/GPU/Processor": {
        "customers": ["Data Center", "Technology", "Servers/Computers"]
    },
    "Semi: Comms": {
        "customers": ["Servers/Computers"]
    },
    "Semi: Components": {
        "customers": ["Servers/Computers", "Semi: CPU/GPU/Processor", "Semi: Comms"]
    },
    "Storage": {
        "customers": ["Data Center", "Servers/Computers"]
    },
    "Memory": {
        "customers": ["Data Center", "Servers/Computers"]
    },
    "Servers/Computers": {
        "customers": ["Data Center"]
    },
    "Data Center": {
        "customers": ["Technology"]
    },
    "Technology": {
        "customers": []
    },
    "Networking": {
        "customers": ["Data Center", "Servers/Computers"]
    },
    "Heat Mgmt/Cooling": {
        "customers": ["Servers/Computers", "Data Center"]
    },
    "Utilities/Power Solutions": {
        "customers": ["Data Center"]
    },
    "Equipment/Tools": {
        "customers": ["Foundries"]
    } 
}


#---------------------------------#
# Streamlit Flow
#---------------------------------#

#st.dataframe(stockanalysis_df)

st.write("## Semi and Tech Sector Web")
st.write("This is a spider web of the Semiconductor and Technology sector. The companies are grouped based on their business relationships.")

def convert_group_to_html(name="", data=[], stockanalysis_df=pd.DataFrame()):
    return f"""**{name}**
| Company | Today  |  YTD |
| - | :- | -: |
{
    "\n".join([f"| {company} | {stockanalysis_df.loc[company]["Today"]} | {stockanalysis_df.loc[company]["YTD"]} | " for company in data])
}
"""

def recommend_color(name, data, stockanalysis_df):
    percentage_sum = 0
    for company in data:
        try:
            percentage_sum += stockanalysis_df.loc[company]["Today %"]
        except:
            # Ignore if the data is not available
            pass
    if percentage_sum > 0:
        # retrun light green hex
        return "#90EE90"
    else:
        # return light red hex
        return "#FFB6C1"

nodes = []
for name, data in groups.items():
    nodes.append(
        StreamlitFlowNode(
            id=name,
            pos=(0, 0),
            data={'content':convert_group_to_html(name, data, stockanalysis_df)},
            node_type='default', 
            source_position='right',
            target_position='left', 
            draggable=True,
            style={'border': '2px solid ' + recommend_color(name, data, stockanalysis_df)}
        )
    )

edges = []
for stock, data in group_relation.items():
    for customer in data["customers"]:
        edges.append(StreamlitFlowEdge(
            id=f"{stock}-{customer}",
            source=stock,
            target=customer,
            animated=True,
            marker_end={"type": "arrow"}
        ))

state = StreamlitFlowState(nodes, edges)

streamlit_flow('tree_layout',
                state,
                layout=TreeLayout(direction="right"),
                show_controls=True,
                pan_on_drag=True,
                allow_zoom=True,
                hide_watermark=True,
                height=800)