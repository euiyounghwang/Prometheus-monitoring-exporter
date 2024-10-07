import streamlit as st
import os

st.set_page_config(
    page_title="main",
    page_icon="👋",
)

st.write("# ES Team Alert Monitoring! 👋")

st.sidebar.success("Select a menu above.")

# https://docs.streamlit.io/get-started/tutorials/create-a-multipage-app
st.markdown(
    """
    Through ES Team Alert Monitoring, our team can check the history of Alert On/Off and Logs.
    **👈 Select a menu(log or alert) from the sidebar** to see!
    """
)

# st.markdown(
#     """
#     Through ES Team Alert Monitoring, our team can check the B&D Team's Alert On/Off request status and logs.
#     **👈 Select a menu(log or alert) from the sidebar** to see!
#     ### Want to see more?
#     - ES Team all Services Monitoring [ES Team Services Monitoring](%s)
#     - Elasticsearch Monitoring [ES Team Services Monitoring](%s)
#     """ % (os.getenv("GRAFANA"))
# )