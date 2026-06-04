#refactored by Erika Skodova
#writer Sofya Grishkova (i6397764)

import streamlit as st

def user_details_panel(form_name: str, button_name: str) -> dict:
    with st.form(form_name, clear_on_submit=False, enter_to_submit=False):
        email = st.text_input("Email", placeholder="Enter your email")
        password = st.text_input("Password", type="password", placeholder="Enter password")
        submitted = st.form_submit_button(button_name)
        user_details = {"email": email, "password": password, "button": submitted}
    return user_details