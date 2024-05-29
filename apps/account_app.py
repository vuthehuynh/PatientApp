import streamlit as st 
from hydralit import HydraHeadApp
import pandas as pd
from db import DatabaseManager
from utils import sidebar_logo
class AccountApp(HydraHeadApp):
    def __init__(self, title = '', db: DatabaseManager=None, **kwargs):
        self.__dict__.update(kwargs)
        self.title = title
        self.db = db

        
    def run(self):
        logo_url = './resources/logo.png'
        sidebar_logo(logo_url)
        st.sidebar.markdown("***")
        st.sidebar.title("Account App")
        page = st.sidebar.radio("Account", options=["Patient Info", "Contact"])

        st.header('Accounts')
        accounts = self.db.fetch_all_records('signup_users')
        accounts = [
            account[1:] for account in accounts
        ]
        account_df = pd.DataFrame(accounts, columns=['Username', 'Password', 'Access Level'])
        st.dataframe(account_df)