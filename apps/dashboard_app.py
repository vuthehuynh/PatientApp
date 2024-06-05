import streamlit as st 
from hydralit import HydraHeadApp
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode
import pandas as pd
import datetime
from dataclasses import dataclass
from db import (
    Database,
    PatientInfo,
    Room,
    TableName,
)
from collections import defaultdict
from utils import sidebar_logo, Utils
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
            self.db_name = f"{self.clinic}_patient.db"
            self.rooms: List[Room] = db.rooms
            self.roomlist = [room.__dict__.get("name") for room in self.rooms]
            self.room_current: dict = {'name': ''}
            self.patients: List[PatientInfo] = db.patients

            self.grid_return = defaultdict(list)
            self.patient_df = {}
            print(f"Dashboard login: {self.login}")

        else:
            self.login = False
            print(f"Dashboard login: {False}")

        if not 'init' in st.session_state:
            # idx of account db when selected
            self.idx_patient_db = None
            self.idx_room_db = None
            st.session_state.init = True
            # selected idx of dataframe 
            self.idx_patient_df = None 
            self.idx_room_df = None 
            # The added idx of new item in db
            self.idx_room_added_record_db = None     
            # The ids of selected rows in dataframe
            self.ids_room_db = []
            

        self.editor_visiable = False

    def run(self):
        ## Side bar
        logo_url = './resources/logo.png'
        sidebar_logo(logo_url)
        st.sidebar.markdown("***")
        st.sidebar.title(f"Welcome {self.user}")

        # ## UI main page
        self.UI_main()

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
                self.patients[rowIdx] = tuple(converted_data.values())
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
            enable_selection = st.checkbox("Enable row patient selection1", value=False)
            if enable_selection:
                selection_mode = "multiple"
                use_checkbox = True
                groupSelectsChildren = True 
                groupSelectsFiltered = True                     
            enableUI_sidebar = st.checkbox("Enable grid sidebar1", value=False)

        st.markdown("***")
        ## UI Patient List

        _patients: List = [patient.__dict__ for patient in self.patients]
        self.patients_df = pd.DataFrame(_patients, columns=PatientInfo.__annotations__.keys())

        gb = GridOptionsBuilder.from_dataframe(self.patients_df)
        gb.configure_column("id", hide=True)
        # roomlist = [room.__dict__.get("name") for room in self.rooms]
        gb.configure_column(
            "room",
            cellEditor='agSelectCellEditor', 
            cellEditorParams={
                'values': self.roomlist,
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
            self.patients_df, 
            gridOptions=gridOptions,
            update_on=["cellValueChanged"],
            fit_columns_on_grid_load=True,
            height=grid_height,
            key="patient_table",
            reload_data=True
        )
        # st.button("Edit Patient", on_click=self._btn_edit_patient)
        if grid_return.event_data is not None:
            event_data = grid_return.event_data.get("data", None)  
            event_type = grid_return.event_data.get("type", None)  
            self.idx_patient_df: int = grid_return.event_data.get("rowIndex", None)
            if event_data is not None:
                self.idx_patient_db = event_data.get("id", None)
            if event_type == "cellValueChanged":
                converted_data = {k: v for k, v in event_data.items() if k != '__pandas_index' and k != 'id'}
                # print(converted_data, self.idx_patient_db)

                # patient_current = PatientInfo(**converted_data)
                self._btn_edit_patient(tuple(converted_data.values()))

    def _get_id(self, selected_data: pd.DataFrame):
        if selected_data is not None:
            data: List = selected_data.to_dict(orient="records")
            selected_id = [
                item.get("id", None) for item in data
            ]
            return selected_id
        return None
    
    def _btn_edit_room_func(self, txt_edit_room):
        ## Save to db
        keys = tuple(Room.__annotations__.keys())[1:]
        values = (txt_edit_room,)
        db_name = self.db_name
        table_name = TableName.ROOM.value
        Database.update_record_keys(db_name, table_name, keys, values, id=self.idx_room_db)
        st.toast("Room edited successfully!")

        ## Save to memory (self.accounts)
        self.rooms = self._update_to_memory(
            data=dict(zip(keys, values)),
            input_df=self.rooms_df,
            idx_df=self.idx_room_df,
            memory=self.rooms,
            classfootprint=Room
        )

    def _btn_edit_patient(self, values: tuple):
        ## Save to db
        keys = tuple(PatientInfo.__annotations__.keys())[1:]
        db_name = self.db_name
        table_name = TableName.PATIENTINFO.value
        Database.update_record_keys(db_name, table_name, keys, values, id=self.idx_patient_db)
        st.toast("Patient edited successfully!")

        ## Save to memory (self.accounts)
        self.patients = self._update_to_memory(
            data=dict(zip(keys, values)),
            input_df=self.rooms_df,
            idx_df=self.idx_patient_df,
            memory=self.patients,
            classfootprint=PatientInfo
        )

    def _btn_add_room_func(self, txt_add_room):
        ## Save to db
        values = (txt_add_room)
        db_name = self.db_name
        table_name = TableName.ROOM.value
        self.idx_added_record_db = Database.insert_record(db_name, table_name, values=values)
        st.toast("Room added successfully!")

        ## Update memory (self.accounts)
        keys = tuple(Room.__annotations__.keys())
        values = tuple([self.idx_added_record_db]) + tuple([txt_add_room])

        self.rooms = self._add_to_memory(
            data=dict(zip(keys, values)),
            memory=self.rooms,
            classfootprint=Room
        )

        # st.rerun()        

    def _update_to_memory(
            self, 
            data: dict,
            input_df: pd.DataFrame,
            idx_df: int,
            memory: List,
            classfootprint: dataclass = Room
        )-> List:
            
            mod_account_df: dict = input_df.iloc[idx_df].to_dict()
            mod_account_df = Utils.assign_dict_to_dict(mod_account_df, data)
            _id1 = mod_account_df.get('id', None)
            _id2 = [idx for idx, account in enumerate(memory) if account.id == _id1]
            if _id2:
                memory[_id2[0]] = classfootprint(**mod_account_df)
            return memory
    
    def _add_to_memory(
            self, 
            data: dict,
            memory: List,
            classfootprint: dataclass = Room
        )-> List:

            add_account = classfootprint(**data)
            memory.append(add_account)

            return memory
    
    def _get_patients_df(self):
        patients_db: List = self.patients
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
        # roomlist = [room.__dict__.get("name") for room in self.rooms]
        for room in self.roomlist:
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
            _rooms: List = [room.__dict__ for room in self.rooms]
            self.rooms_df = pd.DataFrame(_rooms, columns=Room.__annotations__.keys())
            gb = GridOptionsBuilder.from_dataframe(self.rooms_df)

            enable_selection = st.checkbox("Enable row selection", value=False)

            if enable_selection:
                selection_mode = "multiple"
                use_checkbox = True
                groupSelectsChildren = True 
                groupSelectsFiltered = True                     

                gb.configure_selection(selection_mode)
                if use_checkbox:
                    gb.configure_selection(
                        selection_mode,
                        use_checkbox=True,
                        groupSelectsChildren=groupSelectsChildren,
                        groupSelectsFiltered=groupSelectsFiltered,
                    )

            gridOptions = gb.build()
            
            grid_return = AgGrid(
                self.rooms_df, 
                gridOptions=gridOptions,
                update_on=["cellClicked"],
                fit_columns_on_grid_load=True,
                height=180
            )
            st.button("Delete selected", on_click=self._btn_delete_selected)

            if grid_return.event_data is not None:
                event_data = grid_return.event_data.get("data", None)  
                event_type = grid_return.event_data.get("type", None)  
                self.idx_room_df: int = grid_return.event_data.get("rowIndex", None)
                if event_data is not None:
                    self.idx_room_db = event_data.get("id", None)
                    self.room_current = Utils.assign_dict_to_dict(self.room_current, event_data)
                if event_type == "selectionChanged":
                    rows_data: pd.DataFrame = grid_return.selected_rows
                    rows: List = rows_data.to_dict(orient='records')
                    self.ids_room_db = [_row.get("id") for _row in rows]
            txt_edit_room = st.text_input(" ", value=self.room_current.get('name', ''), key='edit_room')
            values = (txt_edit_room)
            btn_edit_room = st.button("Edit Room", on_click=self._btn_edit_room_func,args=(txt_edit_room,))
            txt_add_room = st.text_input(" ", key='add_room')
            btn_add_room = st.button("Add Room", on_click=self._btn_add_room_func,args=(txt_add_room,))        

    def _btn_delete_selected(self):
        '''
        Deleted selected account
        '''
        ## Delete from db
        db_name = self.db_name
        table_name = TableName.ROOM.value
        Database.delete_records(db_name, table_name, ids=self.ids_room_db)

        ## Delete from memory 
        self.patients = self._delete_from_memory(
            ids_db=self.ids_room_db,
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
    
    def UI_layout(self):
        # patients_db: List = self.patients
        # patients_df = pd.DataFrame(patients_db, columns=['id'] + list( PatientInfo.__annotations__.keys()))

        _patients: List = [patient.__dict__ for patient in self.patients]
        patients_df = pd.DataFrame(_patients, columns=PatientInfo.__annotations__.keys())
        patients: List[Dict] = patients_df.to_dict(orient="records")
        room_data: Dict = self._make_room_data(patients)
        self.room_list: List = self._room_dict_to_list(room_data)
        st.markdown("***")

        ## UI Layout
        st.subheader("Room Layout")
        col_cols, _ = st.columns([1, 4])
        with col_cols:
            n_cols = st.number_input("n_cols", min_value=1, value=3)
        n_rows = len(self.roomlist) // n_cols + 1

        idx = 0
        for i in range(n_rows):
            cols = st.columns(n_cols)
            for j in range(n_cols):
                with cols[j]:
                    idx = i*n_cols+j
                    if idx < len(self.roomlist):   
                        # st.subheader(self.roomlist[idx])                          
                        st.markdown(f"**{self.roomlist[idx]}**")
                        _patients = self.room_list[idx].get('patients', [])
                        
                        self.patient_df[idx] = pd.DataFrame(
                            _patients
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
                                    pass 
                                    # # TODO, add global dictionary to store the event data
    def UI_main(self):
        ## UI Sidebar
        self.UI_sidebar()

        col_layout, col_editor = st.columns([4, 4])
        ## UI Patients Editor
        with col_editor:
            if not 'visible' in st.session_state:
                st.session_state.visible = False
            def toggle():
                st.session_state.visible = not st.session_state.visible
            st.button("Toggle", on_click=toggle)
                
            with st.expander("Room Editor", expanded=st.session_state.visible):
                self.UI_patients_editor()

        with col_layout:
            self.UI_layout()

                            

if __name__ == "__main__":
    from dataclasses import dataclass
    from db import Database
    from utils import Container, Utils
    @dataclass 
    class AppState:
        username: str
        clinic: str
    app_state = AppState(username="huynh", clinic="PK2")
    db_name = f"PK2_patient.db"
    Database.create_default_db_patient(db_name)
    _db_patients = Database.read_db(db_name=db_name, table_name=TableName.PATIENTINFO.value)
    db_patients: List[PatientInfo] = Utils.format_db_output(_db_patients, TableName.PATIENTINFO.value)

    _db_rooms = Database.read_db(db_name=db_name, table_name=TableName.ROOM.value)
    db_rooms: List[Room] = Utils.format_db_output(_db_rooms, TableName.ROOM.value)
    container = Container(
                    patients=db_patients,
                    rooms=db_rooms
                )    
    patient = DashboardApp(title="Dashboard", db=container, app_state=app_state)
    patient.run()