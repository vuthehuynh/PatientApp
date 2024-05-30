import streamlit as st 

from hydralit import HydraHeadApp
import pandas as pd
from db import DatabaseManager, Clinic, dataclass_to_tablename, SingupUser
from utils import sidebar_logo
from st_aggrid import AgGrid

class AccountApp(HydraHeadApp):
    def __init__(self, title = '', db: DatabaseManager=None, **kwargs):
        self.__dict__.update(kwargs)
        self.title = title
        self.db = db

    def _load_account_data(self):
        singup_db = {}
        users = self.db.fetch_all_records(dataclass_to_tablename[SingupUser])
        users = [
            account[1:] for account in users
        ]
        keys = tuple(SingupUser.__annotations__.keys())
        for key in keys:
            singup_db[key] = ""
        return singup_db    

    def _load_clinics(self):
        users = self.db.fetch_all_records(dataclass_to_tablename[SingupUser])
        users = [
            account[1:] for account in users
        ]
        keys = tuple(SingupUser.__annotations__.keys())
        clinics = []
        for user in users:
            for key, value in zip(keys, user):
                if key == 'clinic':
                    clinics.append(value)

        return clinics



    def _add_clinic(self, txt_clinic):
        clinic_name = txt_clinic
        if clinic_name:
            self.db.insert_record(Clinic, values=(clinic_name))
            st.toast(f'Clinic {clinic_name} added successfully!')

    def _account_edit(self):
        edited_rows = st.session_state.ed["edited_rows"]
        if edited_rows is not None:
            for row_id, data in edited_rows.items():
                keys = list(data.keys())
                values = list(data.values())
                st.write(f"edited row: {row_id} keys {keys} values {values}")   
                self.edited_data[row_id] = [keys, values]


    def run(self):
        ## Sidebar
        logo_url = './resources/logo.png'
        sidebar_logo(logo_url)
        st.sidebar.markdown("***")
        st.sidebar.title("Account App")
        page = st.sidebar.radio("Account", options=["Patient Info", "Contact"])

        ## UI for account table 
        if not hasattr(self, 'account_data'):
            self.account_data = self._load_account_data()
        self.clinics = self._load_clinics()
        st.markdown("***")
        st.header('Accounts')
        UI_account = st.columns([1,1])


        # cb_editable = st.checkbox("Edit", value=False, key='account_editable')
        accounts = self.db.fetch_all_records('signup_users')
        accounts = [
            account[1:] for account in accounts
        ]

        # account_info = st.data_editor(accounts, on_change = self._account_edit, key='ed', disabled=not(cb_editable))
        with UI_account[0]:
            account_df = pd.DataFrame(accounts, columns=['username', 'password', 'access_level', 'clinic'])
            grid_return = AgGrid(account_df, update_on=["cellClicked"])
            if grid_return.event_data is not None:
                _accounts = grid_return.event_data.get("data", None)   
                if _accounts is not None:
                    for k,v in self.account_data.items():
                        self.account_data[k] = _accounts[k]

        with UI_account[1]:

            tab_edit_account, tab_add_account = st.tabs(["Edit Account", "Add Account"])

            with tab_edit_account:
                # clinics = [v for k,v in self.account_data.items() if k == 'clinic']
                with st.form("Edit Account", border=True):
                    txt_user_name = st.text_input("Username", value=self.account_data.get('username', ''), key='edit_acc_username')
                    txt_password = st.text_input("Password", value=self.account_data.get('password', ''), key='edit_acc_password')
                    txt_access_level = st.text_input("Access Level", value=self.account_data.get('access_level', ''), key='edit_acc_access_level')
                    index_clinic = 0
                    if self.account_data.get("clinic", ""):
                        index_clinic = int(self.clinics.index(self.account_data.get("clinic", "")))
                    else:
                        index_clinic = 0
                    txt_clinic = st.selectbox(("Clinic"), options=self.clinics, index=index_clinic, key='edit_acc_clinic')

                    btn_submitted = st.form_submit_button("Edit Account")
                    if btn_submitted:
                        self.db.insert_record(SingupUser, values=(txt_user_name, txt_password, txt_access_level, txt_clinic))
                        st.toast("Account added successfully!")

            with tab_add_account:
                with st.form("Add Account"):
                    txt_add_user_name = st.text_input("Username", key='add_acc_username')
                    txt_add_password = st.text_input("Password", key='add_acc_password')
                    txt_add_access_level = st.text_input("Access Level", key='add_acc_access_level')
                    txt_add_clinic = st.text_input("Clinic", key='add_acc_clinic')

                    btn_submitted = st.form_submit_button("Add Account")
                    if btn_submitted:
                        values = (txt_add_user_name, txt_add_password, txt_add_access_level, txt_add_clinic)
                        self.db.insert_record(SingupUser, values=values)
                        st.toast("Account added successfully!")

        st.markdown("***")

if __name__ == "__main__":
    db_manager = DatabaseManager("my_database.db")
    db_manager.create_default_table()
    account = AccountApp(title="Account", db=db_manager)
    account.run()