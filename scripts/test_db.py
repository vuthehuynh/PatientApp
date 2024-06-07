import sys 
sys.path.append('/media/ben/data/02_prj/PatientApp')

from db import (
    Database,
    TableName, 
    tablename_to_class
)
from utils import Utils
import copy
import datetime
def gen_account_data(
        db_name="account.db",
        table_name=TableName.ACCOUNT.value,
        insert_data=False
    ):
    Database.create_default_db_account(db_name)
    table_name = TableName.ACCOUNT.value
    # Create tables
    if insert_data:
        Database.insert_record(db_name, table_name, values=("admin", "123", 1, 'PK1'))
        Database.insert_record(db_name, table_name, values=("huynh", "123", 1, 'PK2'))

    # View dataa 
    users = Database.fetch_all_records(db_name, table_name)

    print("Accounts:")
    for user in users:
        types = []
        for i in user:
            types.append(type(i))
        print(user)


def gen_patient_data(
        db_name="PK2_patient.db",
        table_name=TableName.PATIENTINFO.value,
        insert_data=False
    ):
    Database.create_default_db_patient(db_name)
    # Create tables
    table_name = TableName.PATIENTINFO.value
    values = [
        ["room1", "bed1", 0, 123456, 'present', datetime.date(2019, 7, 6)],
        ["room2", "bed1", 0, 123457, 'present', datetime.date(2019, 7, 8)],
        ["room3", "bed1", 0, 123458, 'present', datetime.date(2019, 7, 3)],
        ["room4", "bed1", 0, 123459, 'present', datetime.date(2019, 7, 1)]
    ]
    if insert_data:
        for entry in values:
            entry_copy = copy.copy(entry)
            cccd = entry_copy[3]
            bn_code = Utils.generate_unique_code(str(cccd))
            entry_copy[2] = bn_code

            entry_copy = [str(i) for i in entry_copy]            

            # values=(f"room{i}", f"bed{i}", f"city{i}", f"distric{i}")
            Database.insert_record(db_name, table_name, values=tuple(entry_copy))

    users = Database.fetch_all_records(db_name, table_name)
    print("Patients:")
    for user in users:
        types = []
        for i in user:
            types.append(type(i))
        print(user)

def gen_room_data(
        db_name="PK2_patient.db",
        table_name=TableName.ROOM.value,
        insert_data=False
    ):

    # Create tables
    table_name = TableName.ROOM.value
    if insert_data:
        for i in range(10):
            values=(f"room{i}")
            Database.insert_record(db_name, table_name, values=values)

    users = Database.fetch_all_records(db_name, table_name)
    print("Rooms:")
    for user in users:
        types = []
        for i in user:
            types.append(type(i))
        print(user)

def gen_db():
    gen_account_data(insert_data=True)
    gen_patient_data(insert_data=True)
    gen_room_data(insert_data=True)

if __name__ == '__main__':
    ##1. gen data for all database
    gen_db()
    # gen_room_data(insert_data=True)
    # gen_account_data(insert_data=True)
    # gen_patient_data(insert_data=True)
