import streamlit as st
import time
import requests, socket
import logging
import os
import pandas as pd
import numpy as np
import altair as alt

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

st.set_page_config(page_title='ES Team LOG Monitoring! 👋', layout = 'wide', page_icon = 'logo2.png', initial_sidebar_state = 'auto')
p = st.empty()
p.title('ES Team Alert Log Monitoring! 👋')


def get_alert_api(db_http_host, _type):
    ''' interface es_config_api http://localhost:8004/config/get_mail_config '''
    try:
        es_config_host = str(db_http_host).split(":")[0]
        # logging.info(f"es_config_host : {es_config_host}")

        if _type == "alert":
            resp = requests.get(url="http://{}:8004/log/get_alert_log".format(es_config_host), timeout=5)
        elif _type == "monitoring":
            resp = requests.get(url="http://{}:8004/log/get_monitoring_log".format(es_config_host), timeout=5)
                
        if not (resp.status_code == 200):
            ''' save failure node with a reason into saved_failure_dict'''
            logging.error(f"get_alert_api do not reachable")
            return None

        # logging.info(f"get_mail_config - {resp}, {resp.json()}")
        return resp.json()
        

    except Exception as e:
        logging.error(e)
        pass


def work():
    ''' Main work func'''
    resp_alert = get_alert_api(os.getenv('API_HOST'), _type="alert")
    st.subheader('Alert logs.. (10 records based on the latest date)')
    
    if resp_alert:
        df_alert = pd.DataFrame(resp_alert)
        st.table(df_alert.head(10))

        df_alert['CREATE_DATE'] = pd.to_datetime(df_alert['CREATE_DATE'])
        df1 = df_alert['CREATE_DATE'].dt.date.value_counts().sort_index().reset_index()
        df1.columns = ['CREATE_DATE','Count']

        list_date = df1["CREATE_DATE"].tolist()
        new_list_date = []
        for element in list_date:
            new_list_date.append(element.strftime('%m/%d/%Y'))

        df_alert_grape = df1
        df1 = df1.sort_values(by='CREATE_DATE',ascending=False)
        st.write(df1.head(5))

        chart_data = pd.DataFrame(
            {
                # "x": ['2024-01-01','2024-01-02', '2024-01-03'],
                "date" : new_list_date,
                "Freq": df_alert_grape["Count"].astype(str).values.tolist()
                # "y": ['14', '11', '2']
            }
        )

        st.line_chart(
            chart_data,
            x="date",
            y="Freq",
        )
        # chart = alt.Chart(chart_data).mark_line().encode(
        #     x='date',
        #     y='Freq'
        # )
        # st.altair_chart(chart, theme="streamlit", use_container_width=True)
    

    resp_monitoring = get_alert_api(os.getenv('API_HOST'), _type="monitoring")
    st.subheader('Script logs.. (10 records based on the latest date)')
    
    if resp_monitoring:
        df_monitoring = pd.DataFrame(resp_monitoring)
        st.table(df_monitoring.head(10))

        df_monitoring['CREATE_DATE'] = pd.to_datetime(df_monitoring['CREATE_DATE'])
        df_groups = df_monitoring['CREATE_DATE'].dt.date.value_counts().sort_index().reset_index()
        df_groups.columns = ['CREATE_DATE','Count']

        list_date = df_groups["CREATE_DATE"].tolist()
        new_list_date = []
        for element in list_date:
            new_list_date.append(element.strftime('%m/%d/%Y'))

        df_monitoring_grape = df_groups
        df_groups = df_groups.sort_values(by='CREATE_DATE',ascending=False)
        st.write(df_groups.head(5))

        chart_data = pd.DataFrame(
            {
                # "x": ['2024-01-01','2024-01-02', '2024-01-03'],
                "date" : new_list_date,
                "Freq": df_monitoring_grape["Count"].astype(str).values.tolist()
                # "y": ['14', '11', '2']
            }
        )

        st.line_chart(
            chart_data,
            x="date",
            y="Freq",
        )
   

if __name__ == '__main__':
    # ''' streamlit run main.py '''
    work()