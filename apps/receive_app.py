import streamlit as st 
from hydralit import HydraHeadApp
import pandas as pd
import datetime
from db import (
    PatientInfo,
    DBName,
    TableName,
    tablename_to_class,
    update_record_keys,
    insert_record,
)
from utils import sidebar_logo
from collections import defaultdict
from st_aggrid import AgGrid, GridOptionsBuilder
from typing import List, Dict
from utils import Container
class ReceiveApp(HydraHeadApp):
    def __init__(self, title = '', db: Container = None, app_state = None, **kwargs):
        self.__dict__.update(kwargs)
        self.title = title
        self.edited_data = defaultdict(dict)
        self.patient_idx_selected = None
        self.patient: Dict = self._init_patient(is_remove_idx=False)
        if app_state is not None:
            self.user = app_state.username
            self.clinic = app_state.clinic
            self.login = True 
            self.db_name = f"{self.clinic}_patient.db"
            self.db: Container = db
            print(f"Loaded {len(self.db.patients)} patients")

    def run(self):
        ## Side bar
        logo_url = './resources/logo.png'
        sidebar_logo(logo_url)
        st.sidebar.markdown("***")
        st.sidebar.title("Legal Records")
        page = st.sidebar.radio("Receiving Patient", options=["Patient Info", "Contact"])
        
        ## Page select
        if page == "Patient Info":
            self.page_receiving_patients()
        elif page == "Contact":
            self.page_contact()


    def page_receiving_patients(self):
        tab_patient, tab_patient_edit = st.tabs(["Patients", "Patient Edit"])
        with tab_patient_edit:
            self._tab_patient_edit()

        with tab_patient:
            self._tab_patient()

    def page_contact(self):
        st.title("Contact Page")
        st.write("You can contact us here")    


    def _data_editor_changed(self):
        edited_rows = st.session_state.ed["edited_rows"]
        if edited_rows is not None:
            for row_id, data in edited_rows.items():
                keys = list(data.keys())
                values = list(data.values())
                st.write(f"edited row: {row_id} keys {keys} values {values}")   
                self.edited_data[row_id] = [keys, values]

    def _save_to_db(self, patient_info):
        print(f"Saving data {self.edited_data}")
        for row_id, data in self.edited_data.items():
            keys, values = data
            table_name = TableName.PATIENT_INFO.value
            
            try:
                print(f"Saving data: {keys} {values} {row_id}")
                update_record_keys(self.db_name, table_name, keys, values, id=row_id)
                st.success("Data saved")
            except Exception as e:
                st.error(f"Error saving db: {e}")
        st.session_state.patient_info = patient_info

    def _save_to_db1(self, patient_info):
        with st.popover("Save Changes"):
            pp_save = st.radio("Do you want to save?", ["No", "Yes"], index=0)
            if pp_save == 'Yes':
                self._save_to_db(patient_info)

    def _init_patient(self, is_remove_idx=True):
        patient: Dict = {}
        keys = tuple(PatientInfo.__annotations__.keys())
        for key in keys:
            patient[key] = ""
        return patient    
    
    def _tab_patient(self):
        with st.form(key="patient_edit"):
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
                                               value=self.patient.get("city", ""),key="txt_city_receive")
            with r41: txt_district = st.text_input("district", placeholder="Enter district",
                                               value=self.patient.get("district", ""), key="txt_district_receive")
                                
            r50, r51 = st.columns([1, 1])
            with r50: txt_ward = st.text_input("ward", placeholder="Enter ward")
            with r51: txt_religion = st.text_input("religion", placeholder="Enter religion")
            r60, r61 = st.columns([1, 1])
            with r60: txt_id_number = st.text_input("id_number", placeholder="Enter id_number")
            with r61: txt_job = st.text_input("job", placeholder="Enter job")
            submitted = st.form_submit_button("Add Patient")
            if submitted:
                # Write data here
                st.write("Form submitted")
                patient_info = PatientInfo(
                    city=txt_city,
                    district=txt_district,
                )
                values = ('', '', patient_info.city, patient_info.district)
                try:
                    table_name = TableName.PATIENTINFO.value
                    insert_record(self.db_name, table_name, values)
                    st.success("Data saved to DB")
                except Exception as e:
                    st.error(f"Error saving db: {e}")
                st.experimental_rerun()

    def _btn_delete_selected(self):
        if self.selected_ids is not None:
            table_name = TableName.PATIENTINFO.value
            self.db.delete_records(self.db_name, table_name, ids=self.selected_ids)
            st.success("Deleted successfully")
        else:
            st.warning("No row selected")

    def _tab_patient_edit(self):
        ## UI expander
        # with st.expander("Patient View Options"):
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
        patients_df = pd.DataFrame(self.db.patients, columns=['id'] + list( PatientInfo.__annotations__.keys()))

        gb = GridOptionsBuilder.from_dataframe(patients_df)
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
            patients_df, 
            gridOptions=gridOptions,
            update_on=["cellClicked"],
            fit_columns_on_grid_load=True,
            height=grid_height,
            key="patient_table",
            reload_data=True
        )
        st.button("Delete selected", on_click=self._btn_delete_selected)

        if grid_return.event_data is not None:
            _patient_selected = grid_return.event_data.get("data", None)  
            if _patient_selected is not None:
                self.patient_idx_selected = _patient_selected.get("id", None)
                for k,v in self.patient.items():
                    self.patient[k] = _patient_selected[k]

        selected_data = grid_return["selected_rows"]
        self.selected_ids = self._get_id(selected_data)

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
    from utils import read_db
    @dataclass 
    class AppState:
        username: str
        clinic: str
    app_state = AppState(username="huynh", clinic="PK2")
    db_patients = read_db(db_name=f"{app_state.clinic}_patient.db", db_table=TableName.SINGUPUSER.value)
    patient = ReceiveApp(title="Receive", db=db_patients, app_state=app_state)
    patient.run()
