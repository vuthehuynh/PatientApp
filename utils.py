import hashlib
import base64
import streamlit as st
from db import PatientInfo
from typing import List
from db import fetch_all_records


def load_data(db_name, db_table):
    print("Hello")
    data = fetch_all_records(db_name, db_table)
    return data

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