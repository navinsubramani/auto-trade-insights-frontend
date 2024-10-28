import streamlit as st

indexSPY = st.Page(
    page="pages/2_index_spy.py",
    title="SPY",
    icon="📈"
    )

indexQQQ = st.Page(
    page="pages/3_index_qqq.py",
    title="QQQ",
    icon="📈"
    )

sellSideStrategy = st.Page(
    page="pages/4_sell_side_strategy.py",
    title="Sell Side Strategy",
    icon="📉"
    )

pg = st.navigation(
    {   
        "Index": [indexSPY, indexQQQ],
        "Options": [sellSideStrategy]
    }
    )
pg.run()