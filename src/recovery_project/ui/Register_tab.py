#Writer Erika Skodova

import streamlit as st
from User_details_helper import user_details_panel
from recovery_project.services.email_verifier import email_verifier
from recovery_project.services.auth_service import register_user

# Main module handling register tab
def _register_tab() -> None:
    st.markdown('<div class="headline">Register</div>', unsafe_allow_html=True)

    user_details = user_details_panel("register_form", "Sign up")
    email = user_details["email"]
    password = user_details["password"]
    submitted = user_details["button"]

    if submitted:
        if email and password:
            if email_verifier(email):
                if register_user(email, password):
                    st.info(f"User successfully registered")
                else:
                    st.info(f"User already registered with email: {email}")
            else:
                st.error("Invalid email format, required format: example@email.com")
        else:
            st.error("Fill in both email and password.")