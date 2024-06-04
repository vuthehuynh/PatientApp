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
from utils import sidebar_logo
from st_aggrid import AgGrid, GridOptionsBuilder

class AccountApp(HydraHeadApp):
    def __init__(self, title = '', db = None, **kwargs):
        self.__dict__.update(kwargs)
        self.title = title
        self.accounts = db
        self.ss = st.session_state        
        self.account_idx_selected = None 
        self.account_data = self._init_account_data()
        self.clinics = self._load_clinics()

    def run(self):
        ## UI Sidebar
        logo_url = './resources/logo.png'
        sidebar_logo(logo_url)
        st.sidebar.markdown("***")
        st.sidebar.title("Account App")
        page = st.sidebar.radio("Account", options=["Account Info", "DB statistics"])

        ## UI pages
        if page == "Account Info":
            self.page_account_info()
        elif page == "DB statistics":
            self.page_db_statistics()

    def page_account_info(self):
        ## UI for account table 
        
        # self.clinics = self._load_clinics()
        st.markdown("***")
        st.header('Accounts')
        UI_account = st.columns([1,1])


        with UI_account[0]:
            account_df = pd.DataFrame(self.accounts, columns=['id', 'username', 'password', 'access_level', 'clinic'])
            gd = GridOptionsBuilder().from_dataframe(account_df)
            gd.configure_column('id', hide=True)
            go = gd.build()
            grid_return = AgGrid(
                account_df, 
                gridOptions=go,
                update_on=["cellClicked"],
                fit_columns_on_grid_load=True
                )
            if grid_return.event_data is not None:
                _accounts = grid_return.event_data.get("data", None)  
                if _accounts is not None:
                    self.account_idx_selected = _accounts.get("id", None)
                    for k,v in self.account_data.items():
                        self.account_data[k] = _accounts[k]

        with UI_account[1]:
            tab_edit_account, tab_add_account = st.tabs(["Edit Account", "Add Account"])
            with tab_edit_account:
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
                        keys = tuple(Account.__annotations__.keys())
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

    def page_db_statistics(self):
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
        singup_db = {}
        keys = tuple(Account.__annotations__.keys())
        for key in keys:
            singup_db[key] = ""
        return singup_db    

    def _load_clinics(self):
        users = self.accounts
        users = [
            account[1:] for account in users
        ]
        keys = tuple(Account.__annotations__.keys())
        clinics = []
        for user in users:
            for key, value in zip(keys, user):
                if key == 'clinic':
                    clinics.append(value)

        return clinics
    
if __name__ == "__main__":
    from dataclasses import dataclass
    from db import read_db, create_default_db_account
    @dataclass 
    class AppState:
        username: str
        clinic: str
    app_state = AppState(username="huynh", clinic="PK2")
    db_name = 'account_db'
    create_default_db_account(db_name)
    db_account = read_db(db_name=db_name, table_name=TableName.ACCOUNT.value)  
    patient = AccountApp(title="Account", db=db_account, app_state=app_state)
    patient.run()