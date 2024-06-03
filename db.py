import sqlite3
from dataclasses import dataclass
from typing import Tuple, Union
from enum import Enum
# Define data classes for tables
@dataclass
class SingupUser:
    username: str
    password: str
    access_level: int
    clinic: str

@dataclass
class Clinic:
    name: str

@dataclass
class Room:
    name: str

@dataclass
class PatientInfo:
    room: str
    bed: str
    city: str
    district : str

dataclass_to_tablename = {
    SingupUser: "signup_users",
    PatientInfo: "patient_info",
    Clinic: "clinic",
    Room: "room"
}

class TableName(str, Enum):
    SINGUPUSER = "signup_users"
    PATIENTINFO = "patient_info"
    CLINIC = "clinic"
    ROOM = "room"

class DBName(str, Enum):
    ACCOUNT = "account.db"
    PATIENT = "patient.db"

tablename_to_class = {
    TableName.SINGUPUSER: SingupUser,
    TableName.PATIENTINFO: PatientInfo,
    TableName.CLINIC: Clinic,
    TableName.ROOM: Room
}

def create_table(db_name, table_name, columns):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    columns_str = ", ".join(columns)
    query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_str})"
    cursor.execute(query)
    conn.close()

def insert_record(db_name, data_class: dataclass, values: Union[str, Tuple]):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    table_name = dataclass_to_tablename[data_class]
    keys = tuple(data_class.__annotations__.keys())
    if len(keys) == 1:
        keys = str(keys).replace(",", "")
    if isinstance(values, str):
        values = f"('{values}')"
    query = f"INSERT INTO {table_name} {keys} VALUES {values}"
    cursor.execute(query)
    conn.commit()

    conn.close()

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

def get_table_numentry(db_name, table_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()    

    query = f"SELECT COUNT(*) FROM {table_name};"
    cursor.execute(query)
    count = cursor.fetchone()[0]
    conn.close()
    return count

def update_record(db_name, table_name, data_class: dataclass, values, id: int = None):
    '''
    e.g. update_record("signup_users", SingupUser, ("john_doe1", "password12345", 1), 1)
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

def delete_records(db_name, data_class: dataclass, ids: list = []):
    '''
    e.g. update_record("signup_users", SingupUser, ("john_doe1", "password12345", 1), 1)
    '''
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()    
    table_name = dataclass_to_tablename[data_class]
    if len(ids) == 1:
        ids_to_delete_str = str(ids[0])
    else:
        ids_to_delete_str = ', '.join(str(_) for _ in ids)
    query = f"DELETE from {table_name} WHERE id IN ({ids_to_delete_str})"
    cursor.execute(query)
    conn.commit()
    conn.close()

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

def fetch_all_records(db_name, table_name) -> list:
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()    
    query = f"SELECT * FROM {table_name}"
    cursor.execute(query)
    records = cursor.fetchall()
    conn.close()
    return records


def create_default_table_account(db_name, table_name):
    # Table signup_users
    conn = sqlite3.connect(db_name)
    table_fields = [
        "id INTEGER PRIMARY KEY", 
        "username TEXT", 
        "password TEXT",
        "access_level INTEGER NOT NULL",
        "clinic TEXT"
    ]
    create_table(db_name, table_name, table_fields)
    conn.close()

def create_default_table_patient(db_name, table_name):
    conn = sqlite3.connect(db_name)
    # Table patient_info
    table_fields = [
        "id INTEGER PRIMARY KEY", 
        "room TEXT", 
        "bed TEXT", 
        "city TEXT", 
        "district TEXT"
    ]
    create_table(db_name, table_name, table_fields)

    table_fields = [
        "id INTEGER PRIMARY KEY", 
        "name TEXT", 
    ]
    create_table(dataclass_to_tablename[Room], table_fields)
    conn.close()

# Usage example
if __name__ == "__main__":
    pass 
    # db_manager = DatabaseManager("test.db")
    # db_manager.create_default_table()

    # # Create tables
    # table_name = "signup_users"
    # table_fields = [
    #     "id INTEGER PRIMARY KEY", 
    #     "username TEXT", 
    #     "password TEXT",
    #     "access_level INTEGER NOT NULL"
    # ]
    # db_manager.create_table(table_name, table_fields)

    # # Insert records without specifying the id column
    # # values = ("john_doe", "password123", 1)
    # # db_manager.insert_record(SingupUser, values)
    # # values = ("huynh", "password13", 2)
    # # db_manager.insert_record(SingupUser, values)

    # # Update records
    # db_manager.update_record(table_name, SingupUser, ("john_doe1", "password12345", 1), 1)

    # # Fetch records
    # users = db_manager.fetch_all_records(table_name)

    # print("Signup Users:")
    # for user in users:
    #     types = []
    #     for i in user:
    #         types.append(type(i))
    #     print(user, types)

    # # Close connection
    # db_manager.close_connection()
