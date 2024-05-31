import sqlite3
from dataclasses import dataclass
from typing import Tuple, Union

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
class PatientInfo:
    city: str
    district : str

dataclass_to_tablename = {
    SingupUser: "signup_users",
    PatientInfo: "patient_info",
    Clinic: "clinic"
}

# Database connection and utility functions
class DatabaseManager:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def create_table(self, table_name, columns):
        columns_str = ", ".join(columns)
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_str})"
        self.cursor.execute(query)

    def insert_record(self, data_class: dataclass, values: Union[str, Tuple]):
        table_name = dataclass_to_tablename[data_class]
        keys = tuple(data_class.__annotations__.keys())
        if len(keys) == 1:
            keys = str(keys).replace(",", "")
        if isinstance(values, str):
            values = f"('{values}')"
        query = f"INSERT INTO {table_name} {keys} VALUES {values}"
        print(query)
        self.cursor.execute(query)
        self.conn.commit()

    def get_table_names(self):
        query = f"SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
        self.cursor.execute(query)
        t_names = self.cursor.fetchall()
        t_names = [
            i[0] for i in t_names
        ]
        return t_names

    def get_table_numentry(self, table_name):
        query = f"SELECT COUNT(*) FROM {table_name};"
        self.cursor.execute(query)
        count = self.cursor.fetchone()[0]
        return count

    def update_record(self, table_name, data_class: dataclass, values, id: int = None):
        '''
        e.g. update_record("signup_users", SingupUser, ("john_doe1", "password12345", 1), 1)
        '''
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
        self.cursor.execute(query)
        self.conn.commit()

    def update_record_keys(self, table_name, keys, values, id: int = None):
        '''
        Update record with keys and values
        '''
        pairs = []
        for key, value in zip(keys, values):
            if isinstance(value, str):
                pairs.append(f"{key} = '{value}'")
            else:
                pairs.append(f"{key} = {value}")
        pairs = ", ".join(pairs)
        query = f"UPDATE {table_name} SET {pairs} WHERE id = {id}"
        self.cursor.execute(query)
        self.conn.commit()

    def fetch_all_records(self, table_name):
        query = f"SELECT * FROM {table_name}"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def close_connection(self):
        self.conn.close()

    def create_default_table(self):
        # Table signup_users
        table_name = dataclass_to_tablename[SingupUser]
        table_fields = [
            "id INTEGER PRIMARY KEY", 
            "username TEXT", 
            "password TEXT",
            "access_level INTEGER NOT NULL",
            "clinic TEXT"
        ]
        self.create_table(table_name, table_fields)

        # Table patient_info
        table_name = dataclass_to_tablename[PatientInfo]
        table_fields = [
            "id INTEGER PRIMARY KEY", 
            "city TEXT", 
            "district TEXT"
        ]
        self.create_table(table_name, table_fields)

        # Table clinic
        table_name = dataclass_to_tablename[Clinic]
        table_fields = [
            "id INTEGER PRIMARY KEY", 
            "name TEXT"
        ]
        self.create_table(table_name, table_fields)

# Usage example
if __name__ == "__main__":
    db_manager = DatabaseManager("test.db")
    db_manager.create_default_table()

    # Create tables
    table_name = "signup_users"
    table_fields = [
        "id INTEGER PRIMARY KEY", 
        "username TEXT", 
        "password TEXT",
        "access_level INTEGER NOT NULL"
    ]
    db_manager.create_table(table_name, table_fields)

    # Insert records without specifying the id column
    # values = ("john_doe", "password123", 1)
    # db_manager.insert_record(SingupUser, values)
    # values = ("huynh", "password13", 2)
    # db_manager.insert_record(SingupUser, values)

    # Update records
    db_manager.update_record(table_name, SingupUser, ("john_doe1", "password12345", 1), 1)

    # Fetch records
    users = db_manager.fetch_all_records(table_name)

    print("Signup Users:")
    for user in users:
        types = []
        for i in user:
            types.append(type(i))
        print(user, types)

    # Close connection
    db_manager.close_connection()
