import time
from typing import Dict
import streamlit as st
from hydralit import HydraHeadApp
from db import DatabaseManager, SingupUser, dataclass_to_tablename
from utils import hash_password, set_background


class LoginApp(HydraHeadApp):
    """
    This is an example login application to be used to secure access within a HydraApp streamlit application.
    This application implementation uses the allow_access session variable and uses the do_redirect method if the login check is successful.
    
    """

    def __init__(self, title = '', db: DatabaseManager=None, **kwargs):
        self.__dict__.update(kwargs)
        self.title = title
        self.db = db

    def run(self) -> None:
        """
        Application entry point.
        """
        set_background('./resources/background.png')

        st.markdown("<h1 style='text-align: center;'>App Login</h1>", unsafe_allow_html=True)


        c1,c2,c3, = st.columns([4,3,4])
        
        form_data = self._create_login_form(c2)
        
        pretty_btn = """
            <style>
            div[class="row-widget stButton"] > button {
                width: 100%;
            }
            </style>
            <br><br>
        """
        c2.markdown(pretty_btn,unsafe_allow_html=True)

        if form_data['submitted']:
            self._do_login(form_data, c2)


    def _create_login_form(self, parent_container) -> Dict:

        login_form = parent_container.form(key="login_form")

        form_state = {}
        form_state['username'] = login_form.text_input('Username')
        form_state['password'] = login_form.text_input('Password',type="password")
        form_state['access_level'] = login_form.selectbox('Example Access Level',(1,2))
        form_state['submitted'] = login_form.form_submit_button('Login')

        col1, col2 = parent_container.columns([1,1])
        if col1.button('Guest Login',key='guestbtn'):
            self.set_access(1, 'guest')
            self.do_redirect()
        if col2.button('Sign Up',key='signupbtn'):
            self.set_access(-1, 'guest')
            self.do_redirect()        

        return form_state


    def _do_login(self, form_data, msg_container) -> None:

        #access_level=0 Access denied!
        access_level = self._check_login(form_data)

        if access_level > 0:
            msg_container.success(f"✔️ Login success")
            with st.spinner("🤓 now redirecting to application...."):
                time.sleep(1)

                #access control uses an int value to allow for levels of permission that can be set for each user, this can then be checked within each app seperately.
                self.set_access(form_data['access_level'], form_data['username'])

                #Do the kick to the home page
                self.do_redirect()
        else:
            self.session_state.allow_access = 0
            self.session_state.current_user = None

            msg_container.error(f"❌ Login unsuccessful, 😕 please check your username and password and try again.")


    def _check_login(self, login_data) -> int:
        table_name = dataclass_to_tablename[SingupUser]
        data: list = self.db.fetch_all_records(table_name)
        for data_item in data:
            account: SingupUser = SingupUser(*data_item[1:])
            if account.username == login_data['username'] and account.password == hash_password(login_data['password']):
                return account.access_level
        return 0
