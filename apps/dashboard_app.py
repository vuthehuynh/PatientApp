import streamlit as st 
from hydralit import HydraHeadApp
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode
import pandas as pd
import datetime
from db import (
    PatientInfo,
    DBName,
    Room,
    TableName,
    tablename_to_class,
    update_record_keys,
    insert_record,
)
from collections import defaultdict
from utils import sidebar_logo
from typing import List, Dict 
from utils import Container
class DashboardApp(HydraHeadApp):
    def __init__(self, title = '', app_state = None , db:Container = None, **kwargs):
        self.__dict__.update(kwargs)
        self.room_data = {"name": ""}
        self.room_idx_selected = None
        if app_state is not None:
            self.user = app_state.username
            self.clinic = app_state.clinic
            self.login = True 
            self.db: Container = db

            self.rooms = [
                room[1] for room in self.db.rooms
            ]
            self.grid_return = defaultdict(list)
            self.patient_df = {}

            print(f"Dashboard login: {self.login}")
            print(f"Loaded {len(self.db.patients)} patients")
            print(f"Loaded {len(self.db.rooms)} rooms")            
        else:
            self.login = False
            print(f"Dashboard login: {False}")

        self.editor_visiable = False
    def run(self):
        ## Side bar
        logo_url = './resources/logo.png'
        sidebar_logo(logo_url)
        st.sidebar.markdown("***")
        st.sidebar.title(f"Welcome {self.user}")

        # ## UI main page
        self.UI_main()

    def _btn_update_rooms(self):
        ## TODO: write update room to db
        ## Update self.room_list
        st.experimental_rerun()

    def _argrid_update_data(self, data: Dict):
        '''
        Args: 
            event_data: {
                'type': 'cellClicked', # 'cellValueChanged',
                'rowIndex': int,
                'data': dict
                'oldValue': dict 
            }
        '''
        if data is not None:
            event_type: str = data.get("type", None)
            event_data: dict = data.get("data", None)
            rowIdx: int = data.get("rowIndex", None)
            if event_type == 'cellValueChanged':
                converted_data = {k: v for k, v in event_data.items() if k != '__pandas_index'}
                self.db.patients[rowIdx] = tuple(converted_data.values())
            ## TODO write to db

    def UI_patients_editor(self):
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
            enableUI_sidebar = st.checkbox("Enable grid sidebar", value=False)

        st.markdown("***")
        ## UI Patient List
        patients_df = pd.DataFrame(
            self.db.patients, 
            columns=['id'] + list( PatientInfo.__annotations__.keys())
        )
        gb = GridOptionsBuilder.from_dataframe(patients_df)
        gb.configure_column("id", hide=True)
        gb.configure_column(
            "room",
            cellEditor='agSelectCellEditor', 
            cellEditorParams={
                'values': self.rooms,
                'cellRenderer': 'ColourCellRenderer',
                'allowTyping': True,
                'filterList': True,
                'highlightMatch': True,
                'valueListMaxHeight': 100
            },
            editable=True
        )
        gb.configure_default_column(
            groupable=True, 
            value=True, 
            enableRowGroup=True, 
            aggFunc="sum", 
            editable=False
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
        if enableUI_sidebar:
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
        st.button("Update rooms", on_click=self._btn_update_rooms)

        self._argrid_update_data(grid_return.event_data)

    def _get_id(self, selected_data: pd.DataFrame):
        if selected_data is not None:
            data: List = selected_data.to_dict(orient="records")
            selected_id = [
                item.get("id", None) for item in data
            ]
            return selected_id
        return None
    
    def _btn_edit_room_func(self, txt_edit_room):
        table_name = TableName.ROOM.value
        db_name = DBName.PATIENT.value
        keys = tuple(Room.__annotations__.keys())
        values = (txt_edit_room)
        update_record_keys(db_name, table_name, keys, values, id=self.room_idx_selected)
        st.toast("Room edited successfully!")

    def _btn_add_room_func(self, txt_add_room):
        table_name = TableName.ROOM.value
        db_name = DBName.PATIENT.value
        insert_record(db_name, table_name, values=(txt_add_room))
        st.toast("Account added successfully!")
        st.toast("Room edited successfully!")

    def _get_patients_df(self):
        patients_db: List = self.db.patients
        patients_df = pd.DataFrame(patients_db, columns=['id'] + list( PatientInfo.__annotations__.keys()))
        return patients_df

    def _make_room_data(self, patients: List) -> Dict:
        '''
        Output: 
          {
            'room1': [],
            'room2': [],
          }
        '''
        room_data = {}
        for room in self.rooms:
            room_data[room] = []
        for patient in patients:
            room = patient.get('room', None)
            if room is not None:
                room_data[room].append(patient)
            else:
                room_data['None'].append(patient)
        return room_data

    def _room_dict_to_list(self, room_data: Dict) -> List:
        '''
        Input: 
            {
                'room1': [],
                'room2': [],
            }
        Output: 
            [
                {'room': 'room1', 'patients': []},
            ]
        '''
        room_list = []
        for room, patients in room_data.items():
                room_list.append({"room": room, "patients": patients})
        return room_list
        
    def UI_sidebar(self):
        with st.sidebar:
            rooms_df = pd.DataFrame(self.db.rooms, columns=['id'] + list(Room.__annotations__.keys()))
            gb = GridOptionsBuilder.from_dataframe(rooms_df)
            gb.configure_column("id", hide=True)
            gridOptions = gb.build()
            grid_return = AgGrid(
                rooms_df, 
                gridOptions=gridOptions,
                update_on=["cellClicked"],
                fit_columns_on_grid_load=True,
                height=180
            )
            if grid_return.event_data is not None:
                _room = grid_return.event_data.get("data", None)  
                if _room is not None:
                    self.room_idx_selected = _room.get("id", None)
                    for k,v in self.room_data.items():
                        self.room_data[k] = _room.get('name', '')
                        print(f"Room selected: {_room.get('name', '')}")

            with st.form("Edit Room", border=True):
                txt_edit_room = st.text_input(" ", value=self.room_data.get('name', ''), key='edit_room')
                btn_edit_room = st.form_submit_button("Edit Room", on_click=self._btn_edit_room_func,args=(txt_edit_room))
            with st.form("Add Room", border=True):
                txt_add_room = st.text_input(" ", key='add_room')
                btn_add_room = st.form_submit_button("Add Room", on_click=self._btn_add_room_func,args=(txt_add_room))        

    def UI_layout(self):
        patients_db: List = self.db.patients
        patients_df = pd.DataFrame(patients_db, columns=['id'] + list( PatientInfo.__annotations__.keys()))
        patients: List[Dict] = patients_df.to_dict(orient="records")
        room_data: Dict = self._make_room_data(patients)
        self.room_list: List = self._room_dict_to_list(room_data)

        st.markdown("***")

        ## UI Layout
        st.subheader("Room Layout")
        col_cols, _ = st.columns([1, 4])
        with col_cols:
            n_cols = st.number_input("n_cols", min_value=1, value=3)
        n_rows = len(self.rooms) // n_cols + 1

        idx = 0
        for i in range(n_rows):
            cols = st.columns(n_cols)
            for j in range(n_cols):
                with cols[j]:
                    idx = i*n_cols+j
                    if idx < len(self.rooms):                             
                        _room = self.room_list[idx].get('room', None)
                        _patients = self.room_list[idx].get('patients', [])
                        
                        self.patient_df[idx] = pd.DataFrame(
                            _patients, 
                            columns=['id'] + list( PatientInfo.__annotations__.keys())
                        )
                        gd = GridOptionsBuilder().from_dataframe(self.patient_df[idx])
                        gd.configure_column('id', hide=True)
                        go = gd.build()
                        self.grid_return[idx] = AgGrid(
                            self.patient_df[idx], 
                            gridOptions=go,
                            update_on=["cellClicked"],
                            fit_columns_on_grid_load=False,
                            key=f"patient_table_{idx}",
                            height=100
                        )
                        if self.grid_return[idx]:
                            if self.grid_return[idx].event_data is not None:
                                event_type: str = self.grid_return[idx].event_data.get("type", None)
                                event_data: dict = self.grid_return[idx].event_data.get("data", None)
                                rowIdx: int = self.grid_return[idx].event_data.get("rowIndex", None)
                                value: str = self.grid_return[idx].event_data.get("value", None)
                                if event_type == 'cellClicked':
                                    print(f"event_data: {self.grid_return[idx].event_data}")
                                    # # TODO, add global dictionary to store the event data
    def UI_main(self):
        ## UI Sidebar
        self.UI_sidebar()

        col_layout, col_editor = st.columns([4, 2])
        ## UI Patients Editor
        with col_editor:
            if not 'visible' in st.session_state:
                st.session_state.visible = False
            def toggle():
                st.session_state.visible = not st.session_state.visible
            btn_toggle = st.button("Toggle", on_click=toggle)
                
            with st.expander("Room Editor", expanded=st.session_state.visible):
                self.UI_patients_editor()


        with col_layout:
            self.UI_layout()

                            

if __name__ == "__main__":
    from dataclasses import dataclass
    from db import read_db, create_default_db_patient
    from utils import Container
    @dataclass 
    class AppState:
        username: str
        clinic: str
    app_state = AppState(username="huynh", clinic="PK2")
    db_name = f"PK2_patient.db"
    create_default_db_patient(db_name)
    db_patients = read_db(db_name=db_name, table_name=TableName.PATIENTINFO.value)
    db_rooms = read_db(db_name=db_name, table_name=TableName.ROOM.value)
    container = Container(
                    patients=db_patients,
                    rooms=db_rooms
                )    
    patient = DashboardApp(title="Dashboard", db=container, app_state=app_state)
    patient.run()