import streamlit as st 
from hydralit import HydraHeadApp
import pandas as pd
from db import DatabaseManager
from utils import sidebar_logo
class DashboardApp(HydraHeadApp):
    def __init__(self, title = '', db: DatabaseManager=None, **kwargs):
        self.__dict__.update(kwargs)
        self.title = title
        self.db = db

        
    def run(self):
        logo_url = './resources/logo.png'
        sidebar_logo(logo_url)
        st.sidebar.markdown("***")
        st.sidebar.title("Dashboard")
        page = st.sidebar.radio("Account", options=["Patient Info", "Contact"])

        st.header('Dashboard')
        l1 = [
        {"Name": "John", "Age": 30, "Room": "A1", "Bed": "B1"},
        {"Name": "John1", "Age": 31, "Room": "A1", "Bed": "B3"},
        {"Name": "John2", "Age": 32, "Room": "A1", "Bed": "B5"},

        {"Name": "huynh", "Age": 30, "Room": "A2", "Bed": "M1"},
        {"Name": "huynh1", "Age": 31, "Room": "A2", "Bed": "M2"},
        ]

        option = st.selectbox(
        "Options",
        ("Room", "Age"),
        index=1
        )

        st.write("You selected:", option)
        def get_data(option, data):
            data = pd.DataFrame(data)
            data = data.groupby(option).size().reset_index(name='count')
            return data
        data = get_data(option, l1)
        data = data.to_dict(orient='records')
        data2 = []
        for i in data:
            data2.append({i[option] : i['count']})

        xs = [list(i.keys())[0] for i in data2]
        ys = [list(i.values())[0] for i in data2]
        chart_data = pd.DataFrame(
            {
                option: xs,
                'count': ys
            }
        )
        # chart_data = pd.DataFrame(data2)
        st.bar_chart(chart_data, x = option, y = 'count', color=None, use_container_width=True)

        st.markdown("***")
        st.title("Patient Info")
        st.table(pd.DataFrame(l1))