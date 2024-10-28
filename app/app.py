import streamlit as st

mainPage = st.Page(
    page="pages/1_mainpage.py",
    title="Main page",
    icon="🚀",
    default=True
    )

indexSPY = st.Page(
    page="pages/2_index_spy.py",
    title="Index SPY",
    icon="📈"
    )

pg = st.navigation(
    {   
        "About": [mainPage],
        "Index": [indexSPY],
    }
    )
pg.run()