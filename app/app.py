import streamlit as st

indexSPY = st.Page(
    page="pages/2_index_spy.py",
    title="Index SPY",
    icon="📈"
    )

indexQQQ = st.Page(
    page="pages/3_index_qqq.py",
    title="Index QQQ",
    icon="📈"
    )

pg = st.navigation(
    {   
        "Index": [indexSPY, indexQQQ]
    }
    )
pg.run()