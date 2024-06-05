import streamlit as st 
from hydralit import HydraHeadApp
import pandas as pd
import datetime
from dataclasses import dataclass
from db import (
    PatientInfo,
    DBName,
    TableName,
    tablename_to_class,
    delete_records,
    update_record_keys,
    insert_record,
)
from utils import sidebar_logo, Utils
from collections import defaultdict
from st_aggrid import AgGrid, GridOptionsBuilder
from typing import List, Dict
from utils import Container
class ReceiveApp(HydraHeadApp):
    def __init__(self, title = '', db: Container = None, app_state = None, **kwargs):
        self.__dict__.update(kwargs)
        self.title = title
        self.patient_current: Dict = self._init_patient(is_remove_idx=False)
        if app_state is not None:
            self.user = app_state.username
            self.clinic = app_state.clinic
            self.login = True 
            self.db_name = f"{self.clinic}_patient.db"
            self.patients: List[PatientInfo] = db.patients
            print(f"Loaded {len(self.patients)} patients")

        if not 'init' in st.session_state:
            # idx of account db when selected
            self.idx_patient_db = None
            st.session_state.init = True
            # selected idx of dataframe 
            self.idx_df = None 
            # The added idx of new item in db
            self.idx_added_record_db = None     
            # The ids of selected rows in dataframe
            self.ids_df = []
            self.ids_db = []
            

    def run(self):
        ## Side bar
        logo_url = './resources/logo.png'
        sidebar_logo(logo_url)
        st.sidebar.markdown("***")
        st.sidebar.title("Legal Records")
        page = st.sidebar.radio("Receiving Patient", options=["Patient Info"])
        
        ## Page select
        if page == "Patient Info":
            self.page_receiving_patients()


    def page_receiving_patients(self):
        tab_patient, tab_patient_edit = st.tabs(["Patients", "Patient Edit"])
        with tab_patient_edit:
            self._tab_patient_edit()

        with tab_patient:
            self._tab_patient_add()  

    def _init_patient(self, is_remove_idx=True):
        patient: Dict = {}
        keys = tuple(PatientInfo.__annotations__.keys())
        for key in keys:
            patient[key] = ""
        return patient    
    
    def _tab_patient_add(self):
        with st.form(key="patient_add"):
            r10, r11, r12, r14 = st.columns([1, 1, 1, 1])
            with r10: txt_BN_code = st.text_input("BN Code", placeholder="Enter BN Code")
            with r11: 
                txt_dob = st.date_input("Date of Birth", datetime.date(2019, 7, 6))
            with r12: 
                rb_sex = st.radio("Sex", ["Male ", "Female"])
            cb_Nameless = st.checkbox("Nameless")
            txt_fullname = st.text_input("Full Name", placeholder="Enter Full Name")
            r20, r21 = st.columns([1, 1])
            with r20: txt_phone = st.text_input("Phone", placeholder="Enter Phone")
            with r21: txt_email = st.text_input("Email", placeholder="Enter Email")
            r30, r31 = st.columns([1, 1])
            with r30: txt_address = st.text_input("Adress", placeholder="Enter the address")
            with r31: txt_shortcut_address = st.text_input("Shortcut address", placeholder="Enter the type off address")
            r40, r41 = st.columns([1, 1])
            with r40: txt_city = st.text_input("city", placeholder="Enter city",
                                               value=self.patient_current.get("city", ""),key="txt_city_receive")
            with r41: txt_district = st.text_input("district", placeholder="Enter district",
                                               value=self.patient_current.get("district", ""), key="txt_district_receive")
                                
            r50, r51 = st.columns([1, 1])
            with r50: txt_ward = st.text_input("ward", placeholder="Enter ward")
            with r51: txt_religion = st.text_input("religion", placeholder="Enter religion")
            r60, r61 = st.columns([1, 1])
            with r60: txt_id_number = st.text_input("id_number", placeholder="Enter id_number")
            with r61: txt_job = st.text_input("job", placeholder="Enter job")
            btn_add_patient = st.form_submit_button("Add Patient")
            btn_edit_patient = st.form_submit_button("Edit Patient")
            if btn_add_patient:
                ## Save to db
                values = ("", "", txt_city, txt_district)
                db_name = self.db_name
                table_name = TableName.PATIENTINFO.value
                self.idx_added_record_db = insert_record(db_name, table_name, values=values)
                st.toast("Patient added successfully!")

                ## Update memory (self.accounts)
                keys = tuple(PatientInfo.__annotations__.keys())
                values = tuple([self.idx_added_record_db]) + values

                self.patients = self._add_to_memory(
                    data=dict(zip(keys, values)),
                    memory=self.patients,
                    classfootprint=PatientInfo
                )
                st.rerun()

            if btn_edit_patient:
                keys = tuple(PatientInfo.__annotations__.keys())[1:]
                values = ("", "", txt_city, txt_district)
                db_name = self.db_name
                table_name = TableName.PATIENTINFO.value
                update_record_keys(db_name, table_name, keys, values, id=self.idx_patient_db)
                st.toast("Patient edited successfully!")

                ## Save to memory (self.accounts)
                self.patients = self._update_patient_to_memory(
                    data=dict(zip(keys, values)),
                    input_df=self.patients_df,
                    idx_df=self.idx_df,
                    memory=self.patients,
                    classfootprint=PatientInfo
                )
                st.rerun()

    def _btn_delete_selected(self):
        '''
        Deleted selected account
        '''
        ## Delete from db
        db_name = DBName.ACCOUNT.value
        table_name = TableName.ACCOUNT.value
        delete_records(db_name, table_name, ids=self.ids_db)

        ## Delete from memory 
        self.patients = self._delete_from_memory(
            ids_db=self.ids_db,
            memory=self.patients
        )
    def _delete_from_memory(
            self, 
            ids_db: dict,
            memory: list,
        )-> list:
            '''
            ids_db: idx of rows in db
            '''
            new_memory = [
                account for account in memory if str(account.id) not in ids_db
            ]
                
            return new_memory
        
    def _add_to_memory(
            self, 
            data: dict,
            memory: List,
            classfootprint: dataclass = PatientInfo
        )-> List:

            add_account = classfootprint(**data)
            memory.append(add_account)

            return memory
    
    def _update_patient_to_memory(
            self, 
            data: dict,
            input_df: pd.DataFrame,
            idx_df: int,
            memory: List,
            classfootprint: dataclass = PatientInfo
        )-> List:
            
            mod_account_df: dict = input_df.iloc[idx_df].to_dict()
            mod_account_df = Utils.assign_dict_to_dict(mod_account_df, data)
            _id1 = mod_account_df.get('id', None)
            _id2 = [idx for idx, account in enumerate(memory) if account.id == _id1]
            if _id2:
                memory[_id2[0]] = classfootprint(**mod_account_df)
            return memory
    
    def _tab_patient_edit(self):
        ## UI expander
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:    
            n_rows = st.number_input("rows", min_value=10, value=30)
        with col2: 
            grid_height = st.number_input(
                "Grid height", min_value=200, max_value=800, value=300
            )
        with col3:
            enable_selection = st.checkbox("Enable row selection", value=False)
            if enable_selection:
                selection_mode = "multiple"
                use_checkbox = True
                groupSelectsChildren = True 
                groupSelectsFiltered = True                     
            enable_sidebar = st.checkbox("Enable grid sidebar", value=False)

        st.markdown("***")
        ## UI Patient List
        _patients: List = [account.__dict__ for account in self.patients]
        self.patients_df = pd.DataFrame(_patients, columns=PatientInfo.__annotations__.keys())

        gb = GridOptionsBuilder.from_dataframe(self.patients_df)
        # gb.configure_column("id", hide=True)
        gb.configure_default_column(
            groupable=True, value=True, enableRowGroup=True, aggFunc="sum", editable=False
        )

        if enable_selection:
            gb.configure_selection(selection_mode)
            if use_checkbox:
                gb.configure_selection(
                    selection_mode,
                    use_checkbox=True,
                    groupSelectsChildren=groupSelectsChildren,
                    groupSelectsFiltered=groupSelectsFiltered,
                )
        if enable_sidebar:
            gb.configure_side_bar()
        gb.configure_grid_options(domLayout="normal")
        gridOptions = gb.build()
        grid_return = AgGrid(
            self.patients_df, 
            gridOptions=gridOptions,
            update_on=["cellClicked"],
            fit_columns_on_grid_load=True,
            height=grid_height,
            key="patient_table",
            reload_data=True
        )
        st.button("Delete selected", on_click=self._btn_delete_selected)

        if grid_return.event_data is not None:
            event_data = grid_return.event_data.get("data", None)  
            event_type = grid_return.event_data.get("type", None)  
            self.idx_df: int = grid_return.event_data.get("rowIndex", None)
            if event_data is not None:
                self.idx_patient_db = event_data.get("id", None)
                self.patient_current = Utils.assign_dict_to_dict(self.patient_current, event_data)
            if event_type == "selectionChanged":
                rows_data: pd.DataFrame = grid_return.selected_rows
                rows: List = rows_data.to_dict(orient='records')
                self.ids_df = rows_data.index.tolist()
                self.ids_db = [_row.get("id") for _row in rows]

    def _get_id(self, selected_data: pd.DataFrame):
        if selected_data is not None:
            data: List = selected_data.to_dict(orient="records")
            selected_id = [
                item.get("id", None) for item in data
            ]
            return selected_id
        return None

if __name__ == "__main__":
    from dataclasses import dataclass
    from db import read_db
    @dataclass 
    class AppState:
        username: str
        clinic: str
    app_state = AppState(username="huynh", clinic="PK2")
    db_name = f"PK2_patient.db"
    _db_patients = read_db(db_name=db_name, table_name=TableName.PATIENTINFO.value)
    db_patients: List[PatientInfo] = Utils.format_db_output(_db_patients, TableName.PATIENTINFO.value)
    
    db_rooms = read_db(db_name=db_name, table_name=TableName.ROOM.value)
    container = Container(
        patients=db_patients,
        rooms=db_rooms
    )
    patient = ReceiveApp(title="Receive", db=container, app_state=app_state)
    patient.run()
