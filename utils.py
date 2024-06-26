import hashlib
import base64
import streamlit as st
from db import PatientInfo
from typing import List
from db import Database, tablename_to_class, PatientInfo
from dataclasses import dataclass, fields

class Container:
    def __init__(self, patients, rooms):
        self.patients: List[PatientInfo] = patients
        self.rooms = rooms

class Utils:
    # @staticmethod
    # def types_converter(data: dict, data_class):
    #     # Get the fields and their types from the Account dataclass
    #     field_types = {f.name: f.type for f in fields(data_class)}
        
    #     # Convert the values in the data dictionary to the appropriate types
    #     converted_data = {}
    #     for key, value in data.items():
    #         if key in field_types:
    #             # Convert value to the type specified in the dataclass
    #             converted_data[key] = field_types[key](value)
        
    #     # Create and return an instance of Account
    #     return tuple(converted_data.values())
    
    @staticmethod
    def format_db_output(db: List, tablename: str, include_id=True)-> List:
        '''
        Format the output from the database to a list of dictionary
        '''
        table_class: dataclass =  tablename_to_class.get(tablename, None)
        if table_class is None:
            return []
        
        keys = Utils.get_class_fields(table_class) 
        
        data = []
        _class: dataclass = tablename_to_class.get(tablename, None)

        for record in db:
            record_dict = dict(zip(keys, record))
            data.append(record_dict)

        return [
            _class(**record) for record in data
        ]

    @staticmethod
    def get_class_fields(class_obj: dataclass) -> List:
        return tuple(class_obj.__annotations__.keys())

    @staticmethod
    def assign_dict_to_dict(dic1, dic2):
        for k,v in dic1.items():
            if dic2.get(k, None) is not None:
                dic1[k] = dic2.get(k, None)
        return dic1

    @staticmethod
    def assign_dict_to_class(data_class, dic):
        keys = list(data_class.__annotations__.keys())
        for key in keys:
            key_type = fields(data_class)[keys.index(key)].type
        # for k,v in dic1.items():
        #     if dic2.get(k, None) is not None:
        #         dic1[k] = dic2.get(k, None)
        # return dic1
        
    @staticmethod
    def generate_unique_code(s):
        return int(hashlib.md5(s.encode()).hexdigest(), 16) % 10**6
    
def hash_password(password):
    # Convert the password to bytes before hashing
    password_bytes = password.encode('utf-8')
    
    # Create a SHA-256 hash object
    hash_obj = hashlib.sha256()
    
    # Update the hash object with the password bytes
    hash_obj.update(password_bytes)
    
    # Get the hexadecimal representation of the hash
    hashed_password = hash_obj.hexdigest()
    
    return hashed_password

def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_background(png_file):
    bin_str = get_base64(png_file)
    page_bg_img = '''
    <style>
    .stApp {
    background-image: url("data:image/png;base64,%s");
    }
    </style>
    ''' % bin_str
    st.markdown(page_bg_img, unsafe_allow_html=True)

def sidebar_logo(side_bg):

   side_bg_ext = 'png'

   st.markdown(
      f"""
      <style>
      [data-testid="stSidebar"] > div:first-child {{
          background: url(data:image/{side_bg_ext};base64,{base64.b64encode(open(side_bg, "rb").read()).decode()});
          background-repeat: no-repeat;
          background-position: top;
          margin-top: 0%;
          background-size: 70% 17%;
      }}
      </style>
      """,
      unsafe_allow_html=True,
      )