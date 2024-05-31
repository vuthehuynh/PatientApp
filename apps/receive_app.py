import streamlit as st 
from hydralit import HydraHeadApp
import pandas as pd
import datetime
from db import DatabaseManager, PatientInfo, dataclass_to_tablename
from utils import sidebar_logo
from collections import defaultdict
from st_aggrid import AgGrid
from typing import List, Dict

class ReceiveApp(HydraHeadApp):
    def __init__(self, title = '', db: DatabaseManager=None, **kwargs):
        self.__dict__.update(kwargs)
        self.title = title
        self.db = db
        self.edited_data = defaultdict(dict)
        self.patient_idx_selected = None
        self.patient: Dict = self._init_patient(is_remove_idx=False)

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
        tab_patient, tab_patient_view, tab_patient_edit = st.tabs(["Patients", "Patient List", "Patient Edit"])
        with tab_patient_view:
            self._tab_patient_view()

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

    def _load_receiving_paient_data(self):
        db = {}
        patient_info = self.db.fetch_all_records(dataclass_to_tablename[PatientInfo])
        patient_info = [
            account[1:] for account in patient_info
        ]
        keys = tuple(PatientInfo.__annotations__.keys())
        for data, key in zip(patient_info, keys):
            db[key] = ""
        return db    

    def _save_to_db(self, patient_info):
        print(f"Saving data {self.edited_data}")
        for row_id, data in self.edited_data.items():
            keys, values = data
            table_name = dataclass_to_tablename[PatientInfo]
            try:
                print(f"Saving data: {keys} {values} {row_id}")
                self.db.update_record_keys(table_name, keys, values, id=row_id)
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
                values = (patient_info.city, patient_info.district)
                self.db.insert_record(PatientInfo, values)

    def _tab_patient_view(self):
        ## Load data from database
        patients_db: List = self.db.fetch_all_records(dataclass_to_tablename[PatientInfo])        

        patients_df = pd.DataFrame(patients_db, columns=['id', 'city', 'district'])
        grid_return = AgGrid(
            patients_df, 
            update_on=["cellClicked"],
            fit_columns_on_grid_load=True,
            height=300,
            key="patient_table",
            reload_data=True
        )
        if grid_return.event_data is not None:
            _patient_selected = grid_return.event_data.get("data", None)  
            if _patient_selected is not None:
                self.patient_idx_selected = _patient_selected.get("id", None)
                for k,v in self.patient.items():
                    self.patient[k] = _patient_selected[k]

if __name__ == "__main__":
    # db = DatabaseManager("PK2_patient")
    db_manager = DatabaseManager("PK2_patient.db")
    db_manager.create_default_table_patient()
    patient = ReceiveApp(title="Account", db=db_manager)
    patient.run()
