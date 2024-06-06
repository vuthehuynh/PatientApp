import sqlite3
from dataclasses import dataclass, fields
from typing import Tuple, Union
from enum import Enum
from datetime import datetime
# Define data classes for tables
@dataclass
class Account:
    id: int 
    username: str
    password: str
    access_level: int
    clinic: str

@dataclass
class Clinic:
    name: str

@dataclass
class Room:
    id: int
    name: str

@dataclass
class PatientInfo:
    id: int 
    room: str
    bed: str
    bncode: int
    cccd: int
    status : str
    dob: datetime
    

dataclass_to_tablename = {
    Account: "account",
    PatientInfo: "patient_info",
    Clinic: "clinic",
    Room: "room"
}
tablename_to_class = {
    "account": Account,
    "patient_info": PatientInfo,
    "clinic": Clinic,
    "room": Room
}

class TableName(str, Enum):
    ACCOUNT = "account"
    PATIENTINFO = "patient_info"
    CLINIC = "clinic"
    ROOM = "room"

class DBName(str, Enum):
    ACCOUNT = "account.db"
    PATIENT = "patient.db"

class PatientStatus(str, Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LEFT = "left"
    DEAD = "dead"

class Database:
    @staticmethod
    def create_table(db_name, table_name, columns):
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        columns_str = ", ".join(columns)
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_str})"
        cursor.execute(query)
        conn.close()

    @staticmethod
    def insert_record(db_name, table_name, values: Union[str, Tuple], remove_id: bool = True):
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        data_class = tablename_to_class[table_name]
        keys = tuple(data_class.__annotations__.keys())
        if remove_id:
            keys = keys[1:]
        if len(keys) == 1:
            keys = str(keys).replace(",", "")

        ## Remove the id fields 

        if isinstance(values, str):
            values = f"('{values}')"

        query = f"INSERT INTO {table_name} {keys} VALUES {values}"
        cursor.execute(query)
        inserted_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return inserted_id

    @staticmethod
    def get_table_names(db_name):
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        query = f"SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
        cursor.execute(query)
        t_names = cursor.fetchall()
        t_names = [
            i[0] for i in t_names
        ]
        conn.close()
        return t_names

    @staticmethod
    def get_table_numentry(db_name, table_name):
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()    

        query = f"SELECT COUNT(*) FROM {table_name};"
        cursor.execute(query)
        count = cursor.fetchone()[0]
        conn.close()
        return count

    @staticmethod
    def update_record(db_name, table_name, data_class: dataclass, values, id: int = None):
        '''
        e.g. update_record("account", Account, ("john_doe1", "password12345", 1), 1)
        '''
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()    
        keys = tuple(data_class.__annotations__.keys())
        ## generate query UPDATE table_name SET column1 = value1, column2 = value2...., columnN = valueN WHERE [condition]; from keys and values 
        pairs = []
        for key, value in zip(keys, values):
            if isinstance(value, str):
                pairs.append(f"{key} = '{value}'")
            else:
                pairs.append(f"{key} = {value}")
        pairs = ", ".join(pairs)
        query = f"UPDATE {table_name} SET {pairs} WHERE id = {id}"
        cursor.execute(query)
        conn.commit()
        conn.close()

    @staticmethod
    def delete_records(db_name, table_name, ids: list = []):
        '''
        e.g. update_record("account", Account, ("john_doe1", "password12345", 1), 1)
        '''
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()    
        # table_name = dataclass_to_tablename[data_class]
        if len(ids) == 1:
            ids_to_delete_str = str(ids[0])
        else:
            ids_to_delete_str = ', '.join(str(_) for _ in ids)
        query = f"DELETE from {table_name} WHERE id IN ({ids_to_delete_str})"
        cursor.execute(query)
        conn.commit()
        conn.close()

    @staticmethod
    def update_record_keys(db_name, table_name, keys, values, id: int = None):
        '''
        Update record with keys and values
        '''
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()    
        pairs = []
        for key, value in zip(keys, values):
            if isinstance(value, str):
                pairs.append(f"{key} = '{value}'")
            else:
                pairs.append(f"{key} = {value}")
        pairs = ", ".join(pairs)
        query = f"UPDATE {table_name} SET {pairs} WHERE id = {id}"
        cursor.execute(query)
        conn.commit()
        conn.close()

    @staticmethod
    def fetch_all_records(db_name, table_name) -> list:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()    
        query = f"SELECT * FROM {table_name}"
        cursor.execute(query)
        records = cursor.fetchall()
        conn.close()
        return records

    @staticmethod
    def types_converter(data: dict, data_class):
        # Get the fields and their types from the Account dataclass
        field_types = {f.name: f.type for f in fields(data_class)}
        
        # Convert the values in the data dictionary to the appropriate types
        converted_data = {}
        for key, value in data.items():
            if key in field_types:
                # Convert value to the type specified in the dataclass
                try:
                    if key in ["dob"]:
                        converted_data[key] = datetime.strptime(value, "%Y-%m-%d")
                    else:
                        converted_data[key] = field_types[key](value)
                except:
                    print(f"Error converting {key} with value {value}, field type {field_types[key]}")
        
        # Create and return an instance of Account
        return tuple(converted_data.values())
    
    @staticmethod
    def read_db(db_name, table_name, convert_type=True):
        if convert_type:
            data_class = tablename_to_class[table_name]
            org_db: list = Database.fetch_all_records(db_name, table_name)
            keys = tuple(data_class.__annotations__.keys())
            print(f"keys: {keys}")
            
            db = []
            for entry_values in org_db:
                print(f"values: {entry_values}")
                data = dict(zip(keys, entry_values))
                _db: tuple = Database.types_converter(data, data_class)
                db.append(_db)
        else:
            db: tuple = Database.fetch_all_records(db_name, table_name)
        return db 

    @staticmethod
    def create_default_db_account(db_name):
        # Table account
        conn = sqlite3.connect(db_name)
        table_fields = [
            "id INTEGER PRIMARY KEY", 
            "username VARCHAR(50)", 
            "password VARCHAR(255)",
            "access_level VARCHAR(50)",
            "clinic VARCHAR(100)"
        ]
        table_name = TableName.ACCOUNT.value
        Database.create_table(db_name, table_name, table_fields)
        conn.close()

    @staticmethod
    def create_default_db_patient(db_name):
        conn = sqlite3.connect(db_name)
        # Table patient_info
        table_fields = [
            "id INTEGER PRIMARY KEY", 
            "room VARCHAR(50)", 
            "bed VARCHAR(50)", 
            "bncode INTEGER", 
            "cccd INTEGER", 
            "status VARCHAR(50)", 
            "dob VARCHAR(50)", 
        ]
        table_name = TableName.PATIENTINFO.value    
        Database.create_table(db_name, table_name, table_fields)

        table_fields = [
            "id INTEGER PRIMARY KEY", 
            "name VARCHAR(50)", 
        ]
        table_name = TableName.ROOM.value
        Database.create_table(db_name, table_name, table_fields)
        conn.close()

# Usage example
if __name__ == "__main__":
    pass 
