import streamlit as st 

from hydralit import HydraHeadApp
import pandas as pd
from db import (
    Account,
    insert_record,
    update_record_keys,
    TableName,
    DBName
)
from utils import sidebar_logo, Utils
from st_aggrid import AgGrid, GridOptionsBuilder
from typing import List

class AccountApp(HydraHeadApp):
    def __init__(self, title = '', db = None, **kwargs):
        self.__dict__.update(kwargs)
        self.title = title
        self.accounts: List[Account] = db
        self.clinics = self._load_clinics()
        self.account_current = self._init_account_data()
        self.account_idx_selected = None 
        

    def run(self):
        ## UI Sidebar
        logo_url = './resources/logo.png'
        sidebar_logo(logo_url)
        st.sidebar.markdown("***")
        st.sidebar.title("Account App")
        page = st.sidebar.radio("Account", options=["Account Info", "DB statistics"])

        ## UI pages
        if page == "Account Info":
            self.UI_accounts()
        elif page == "DB statistics":
            self.UI_db_statistics()

    def UI_accounts(self):
        ## UI for account table 
        
        st.markdown("***")
        st.header('Accounts')
        UI_account = st.columns([1,1])


        with UI_account[0]:

            _accounts: List = [account.__dict__ for account in self.accounts]
            _account_df = pd.DataFrame(_accounts, columns=Account.__annotations__.keys())
            gd = GridOptionsBuilder().from_dataframe(_account_df)
            gd.configure_column('id', hide=True)
            go = gd.build()
            grid_return = AgGrid(
                _account_df, 
                gridOptions=go,
                update_on=["cellClicked"],
                fit_columns_on_grid_load=True
                )
            if grid_return.event_data is not None:
                event_data = grid_return.event_data.get("data", None)  
                event_rowIdx: int = grid_return.event_data.get("rowIndex", None)
                if event_data is not None:
                    self.account_idx_selected = event_data.get("id", None)
                    self.account_current = Utils.assign_dict_to_dict(self.account_current, event_data)

        with UI_account[1]:
            tab_edit_account, tab_add_account = st.tabs(["Edit Account", "Add Account"])
            with tab_edit_account:
                with st.form("Edit Account", border=True):
                    txt_user_name = st.text_input("Username", value=self.account_current.get('username', ''), key='edit_acc_username')
                    txt_password = st.text_input("Password", value=self.account_current.get('password', ''), key='edit_acc_password')
                    txt_access_level = st.text_input("Access Level", value=self.account_current.get('access_level', ''), key='edit_acc_access_level')
                    index_clinic = 0
                    if self.account_current.get("clinic", ""):
                        index_clinic = int(self.clinics.index(self.account_current.get("clinic", "")))
                    else:
                        index_clinic = 0
                    txt_clinic = st.selectbox(("Clinic"), options=self.clinics, index=index_clinic, key='edit_acc_clinic')

                    btn_submitted = st.form_submit_button("Edit Account")
                    if btn_submitted:
                        keys = tuple(Account.__annotations__.keys())[1:]
                        values = (txt_user_name, txt_password, txt_access_level, txt_clinic)
                        db_name = DBName.ACCOUNT.value
                        table_name = TableName.ACCOUNT.value
                        update_record_keys(db_name, table_name, keys, values, id=self.account_idx_selected)
                        st.toast("Account edited successfully!")

            with tab_add_account:
                with st.form("Add Account"):
                    txt_add_user_name = st.text_input("Username", key='add_acc_username')
                    txt_add_password = st.text_input("Password", key='add_acc_password')
                    txt_add_access_level = st.text_input("Access Level", key='add_acc_access_level')
                    txt_add_clinic = st.text_input("Clinic", key='add_acc_clinic')

                    btn_submitted = st.form_submit_button("Add Account")
                    if btn_submitted:
                        values = (txt_add_user_name, txt_add_password, txt_add_access_level, txt_add_clinic)
                        db_name = DBName.ACCOUNT.value
                        table_name = TableName.ACCOUNT.value
                        insert_record(db_name, table_name, values=values)
                        st.toast("Account added successfully!")

        st.markdown("***")

    def UI_db_statistics(self):
        ## Get list of clinics
        st.markdown("***")
        
        ## View list of DB
        st.header('DB Statistics')
        # db_func = {}
        # for clinic in self.clinics:
        #     if not hasattr(self, f'db_{clinic}'):
        #         db_func[clinic] = DatabaseManager(f"{clinic}_manager.db")

        # db_names = [f"{clinic}_manager.db" for clinic in self.clinics]
        # selected_db_name = st.selectbox("Clinic", options=db_names, index=0) 

        # btn_statistics = st.button("Show Statistics")
        # if btn_statistics:
        #     _db_name = selected_db_name.split("_")[0]
        #     _db_func = db_func.get(_db_name, None)
        #     if _db_func is not None:
        #         tables = _db_func.get_table_names()
        #         st.write(tables)
        #     else:
        #         st.error("DB not found!")
            
    def _init_account_data(self):
        account = {}
        keys = tuple(Account.__annotations__.keys())
        for key in keys:
            account[key] = ""
        return account    

    def _load_clinics(self):
        accounts: List[Account] = self.accounts
        clinics = [
            account.clinic for account in accounts
        ]
        return clinics
    
if __name__ == "__main__":
    from dataclasses import dataclass
    from db import read_db, create_default_db_account
    @dataclass 
    class AppState:
        username: str
        clinic: str
    app_state = AppState(username="huynh", clinic="PK2")
    db_name = 'account.db'
    create_default_db_account(db_name)
    _db_account = read_db(db_name=db_name, table_name=TableName.ACCOUNT.value)  
    db_account: List[Account] = Utils.format_db_output(_db_account, TableName.ACCOUNT.value)
    patient = AccountApp(title="Account", db=db_account, app_state=app_state)
    patient.run()