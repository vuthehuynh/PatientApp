import streamlit as st 
from hydralit import HydraHeadApp
import pandas as pd
from db import DatabaseManager, Clinic, dataclass_to_tablename
from utils import sidebar_logo


class AccountApp(HydraHeadApp):
    def __init__(self, title = '', db: DatabaseManager=None, **kwargs):
        self.__dict__.update(kwargs)
        self.title = title
        self.db = db

    def add_clinic(self, txt_clinic):
        clinic_name = txt_clinic
        if clinic_name:
            self.db.insert_record(Clinic, values=(clinic_name))
            st.toast(f'Clinic {clinic_name} added successfully!')
        
    def run(self):
        logo_url = './resources/logo.png'
        sidebar_logo(logo_url)
        st.sidebar.markdown("***")
        st.sidebar.title("Account App")
        page = st.sidebar.radio("Account", options=["Patient Info", "Contact"])

        ## UI for add new clinic
        col1, col2 = st.columns([1, 4])
        with col1:
            txt_clinic = st.text_input("Clinic Name", key="clinic_name")
            btn_add_clinic = st.button("Add Clinic", key="add_new_clinic", on_click=self.add_clinic, args=(txt_clinic,))
        with col2:
            table_name = dataclass_to_tablename[Clinic]
            clinics = self.db.fetch_all_records(table_name)
            st.write(f"Number of clinics: {len(clinics)}")

        st.header('Accounts')
        accounts = self.db.fetch_all_records('signup_users')
        accounts = [
            account[1:] for account in accounts
        ]
        account_df = pd.DataFrame(accounts, columns=['Username', 'Password', 'Access Level'])
        st.dataframe(account_df)