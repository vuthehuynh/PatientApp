from hydralit import HydraApp
import streamlit as st
import apps
import apps.account_app
import apps.dashboard_app
from db import (
    Database,
    TableName, 
    Account,
    PatientInfo,
    Room,
)
from utils import Container, Utils
from typing import List 
## logging
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# file_handler = logging.FileHandler('log.txt')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# file_handler.setFormatter(formatter)
# logger.addHandler(file_handler)
logger.addHandler(logging.StreamHandler())

if __name__ == '__main__':
    ## database
    if not 'loaded_account_db' in st.session_state:
        logger.info(f"Start loading database account.db")
        db_name = 'account.db'
        Database.create_default_db_account(db_name)
        _db_account: List = Database.read_db(db_name=db_name, table_name=TableName.ACCOUNT.value)
        db_account: List[Account] = Utils.format_db_output(_db_account, TableName.ACCOUNT.value)
        logger.info(f"Successfully loading database account.db")
        st.session_state.loaded_account_db = db_account
    else:
        db_account = st.session_state.loaded_account_db
    over_theme = {'txc_inactive': '#FFFFFF'}

    #this is the host application, we add children to it and that's it!
    app = HydraApp(
        title='Secure Hydralit Data Explorer',
        favicon="🐙",
        hide_streamlit_markers=False,
        #add a nice banner, this banner has been defined as 5 sections with spacing defined by the banner_spacing array below.
        # use_banner_images=["./resources/hydra.png",None,{'header':"<h1 style='text-align:center;padding: 0px 0px;color:grey;font-size:200%;'>Secure Hydralit Explorer</h1><br>"},None,"./resources/lock.png"], 
        banner_spacing=[5,30,60,30,5],
        # use_navbar=True, 
        navbar_sticky=False,
        navbar_theme=over_theme,
    )

    #Home button will be in the middle of the nav list now
    # app.add_app("Home", icon="🏠", app=apps.HomeApp(title='Home'),is_home=True)
    app.add_app("Account", icon="📚", app=apps.AccountApp(title="Account", db=db_account))

    #we have added a sign-up app to demonstrate the ability to run an unsecure app
    #only 1 unsecure app is allowed
    app.add_app("Signup", icon="🛰️", app=apps.SignUpApp(title='Signup',db=db_account), is_unsecure=True)

    #we want to have secure access for this HydraApp, so we provide a login application
    #optional logout label, can be blank for something nicer!
    app.add_app("Logout", apps.LoginApp(title='Logout', db=db_account),is_login=True,icon="🔒") 

    #specify a custom loading app for a custom transition between apps, this includes a nice custom spinner
    app.add_loader_app(apps.MyLoadingApp(delay=0.01))
    # app.add_loader_app(apps.QuickLoaderApp())

    #we can inject a method to be called everytime a user logs out
    @app.logout_callback
    def mylogout_cb():
        logger.info('logout successfully!')
        st.session_state.login = False

    #we can inject a method to be called everytime a user logs in
    @app.login_callback
    def mylogin_cb():
        logger.info(f"Welcome back! {app.session_state.username} {app.session_state.clinic}")
        st.session_state.login = True
        st.rerun()
    #we can inject a method to be called everytime a user logs in

    if not 'login' in st.session_state:
        app.add_app("Receive", icon="📚", app=apps.ReceiveApp(title="Receive", db=None))
        app.add_app("Dashboard", icon="📚", app=apps.DashboardApp(db=None, app_state=None))            
    else:
        clinic = app.session_state.clinic
        if clinic is not None:
            if not 'loaded_db' in app.session_state:
                db_name = f"{clinic}_patient.db"
                
                logger.info(f"Start loading database {db_name}")
                Database.create_default_db_patient(db_name)
                _db_patients = Database.read_db(db_name=db_name, table_name=TableName.PATIENTINFO.value)
                db_patients: List[PatientInfo] = Utils.format_db_output(_db_patients, TableName.PATIENTINFO.value)
                _db_rooms = Database.read_db(db_name=db_name, table_name=TableName.ROOM.value)
                db_rooms: List[Room] = Utils.format_db_output(_db_rooms, TableName.ROOM.value)
                container = Container(
                    patients=db_patients,
                    rooms=db_rooms
                )
                logger.info(f"Successfully loading database {db_name}")
                app.session_state.loaded_db = container 

            else:
                container = app.session_state.loaded_db
            app.add_app("Receive", icon="📚", app=apps.ReceiveApp(title="Receive", db=container, app_state=app.session_state))
            app.add_app("Dashboard", icon="📚", app=apps.DashboardApp(db=container, app_state=app.session_state))            
        else:
            st.warning("No clinic selected")

    #if we want to auto login a guest but still have a secure app, we can assign a guest account and go straight in
    # app.enable_guest_access()

    #--------------------------------------------------------------------------------------------------------------------
    #if the menu is looking shit, use some sections
    #check user access level to determine what should be shown on the menu
    user_access_level, username = app.check_access()

    # If the menu is cluttered, just rearrange it into sections!
    # completely optional, but if you have too many entries, you can make it nicer by using accordian menus
    if user_access_level == 1:
        complex_nav = {
            'Dashboard': ['Dashboard'],
            'Receive': ['Receive'],
            'Account': ['Account'],
            
        }
    else:
        complex_nav = {
            'Dashboard': ['Dashboard'],
            'Receive': ['Receive'],
        }

  
    #and finally just the entire app and all the children.
    app.run(complex_nav)

    # db_manager.close_connection()
    # db_account.close_connection()
    # if 'login' in st.session_state:
    #     db_manager.close_connection()

    # #(DEBUG) print user movements and current login details used by Hydralit
    # #---------------------------------------------------------------------
    # user_access_level, username = app.check_access()
    # prev_app, curr_app = app.get_nav_transition()
    # print(prev_app,'- >', curr_app)
    # print(int(user_access_level),'- >', username)
    #---------------------------------------------------------------------