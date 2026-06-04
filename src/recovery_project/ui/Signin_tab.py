#refactored by Erika Skodova
#writer Timea Vojcikova - i6377033

import streamlit as st

from recovery_project.services.email_verifier import email_verifier
from recovery_project.services.auth_service import login_user
from User_details_helper import user_details_panel

def _sign_in_tab() -> None:
    st.markdown('<div class="headline">Sign in</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="recovery-hint">Forgot your password? Open <b>Recovery flow</b> to request a reset token and set a new password.</div>'
        '<div class="recovery-hint">No account yet? Open <b>Register</b> to add new user.</div>',
        unsafe_allow_html=True,
    )

    user_details = user_details_panel("sign_in_form","Sign in")
    email = user_details["email"]
    password = user_details["password"]
    submitted = user_details["button"]

    if submitted:
        if email and password:
            if email_verifier(email):
                if login_user(email, password):
                    st.session_state.logged_in = True
                    st.session_state.current_user = email
                    st.success(f"Signed in as {email}.")
                else:
                    st.session_state.logged_in = False
                    st.session_state.current_user = None
                    st.error("Invalid email or password.")
            else: st.error("Invalid email format, required format: example@email.com")
        else:
            st.error("Fill in both email and password.")

    if st.session_state.logged_in and st.session_state.current_user:
        st.info(f"Active session: {st.session_state.current_user}")
