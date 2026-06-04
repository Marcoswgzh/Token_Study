#refactored by Erika Skodova
#writer Sofya Grishkova (i6397764)

import streamlit as st

from Fragment_handler import _fragment_rerun

from Recovery_helper import _reset_recovery_flow, _render_token_preview,_go_to_recovery_step
from recovery_project.services.email_verifier import email_verifier
from recovery_project.services.auth_service import user_exists
from recovery_project.services.recovery_service import issue_token, reset_password, validate_token
from recovery_project.services.rate_limiter import is_locked, get_remaining_lockout_time

#TODO seem like a clutter look through if sth else is needed to split
def _recover_tab() -> None:
    step = int(st.session_state.recovery_step)
    if step > 1 and not st.session_state.issued_token:
        _go_to_recovery_step(1)
        step = 1
    if step > 2 and not st.session_state.token_verified:
        _go_to_recovery_step(2)
        step = 2

    st.markdown('<div class="headline">Recovery</div>', unsafe_allow_html=True)

    def _render_back_button(current_step: int) -> None:
        st.markdown('<div style="height:.35rem"></div>', unsafe_allow_html=True)
        if st.button("←", key=f"recover_back_{current_step}"):
            if current_step == 3:
                st.session_state.token_verified = False
            _go_to_recovery_step(current_step - 1)
            _fragment_rerun()

    if step == 1:
        with st.form("recover_request", enter_to_submit=False):
            email = st.text_input(
                "Account email",
                value=st.session_state.reset_email,
                placeholder="student@university.edu",
            )
            request_submitted = st.form_submit_button("Request reset token")
        if request_submitted:
            if email:
                if email_verifier(email):
                    if not user_exists(email):
                        st.error("No demo account exists for this email.")
                        return
                    # Changed the issue function to the one in services/recovery_service
                    token = issue_token(email)
                    # service returns None when this email requested too many tokens
                    if token is None:
                        st.error("Too many reset token requests. Try again later.")
                        return
                    # The new issue_token does not handle state updates, so do it here
                    st.session_state.reset_email = email
                    st.session_state.issued_token = token
                    st.session_state.token_verified = False
                    # after getting the token, user still needs to verify it
                    _go_to_recovery_step(2)
                    with st.expander("Debug (for demo/testing)", expanded=True):
                        _render_token_preview(token)
                    _fragment_rerun()
                else:
                    st.error("Invalid email format, required format: example@email.com")
            else:
                st.error("Enter email first.")
        return

    if step == 2:
        with st.form("recover_verify", enter_to_submit=False):
            guessed = st.text_input("Enter recovery token", placeholder="e.g. 1A2B3C")
            verify_submitted = st.form_submit_button("Verify token")
        st.success(f"Demo token issued for {st.session_state.reset_email}. Sent to terminal.")
        if verify_submitted:
            # Check if the workflow is locked for the desired email. If it is, display the error. Error should be displayed if the workflow is locked,
            # even if the correct token is submitted after lock
            if is_locked(st.session_state.reset_email):
                st.error(f"Too many attempts. Try again in {get_remaining_lockout_time(st.session_state.reset_email)}.")
            # Use the validate_token function in services/recovery_service
            elif validate_token(st.session_state.reset_email, guessed.strip()):
                st.session_state.token_verified = True
                _go_to_recovery_step(3)
                st.success("Token verified (demo).")
                _fragment_rerun()
            else:
                st.session_state.token_verified = False
                st.error("Invalid token.")

        _render_back_button(2)
        return

    with st.form("recover_reset", enter_to_submit=False):
        new_password = st.text_input("New password", type="password", placeholder="New password")
        confirm_password = st.text_input(
            "Confirm password",
            type="password",
            placeholder="Repeat new password",
        )
        reset_submitted = st.form_submit_button("Reset password")
    if reset_submitted:
        # prevent jumping straight to password reset without valid token
        if not st.session_state.token_verified:
            st.error("Verify the token before resetting the password.")
        elif not new_password or not confirm_password:
            st.error("Fill in both password fields.")
        elif new_password != confirm_password:
            st.error("Passwords do not match.")
        else:
            if reset_password(st.session_state.reset_email, new_password):
                st.session_state.logged_in = False
                st.session_state.current_user = None
                st.success("Password reset completed. You can now sign in with the new password.")
                _reset_recovery_flow()
            else:
                st.error("Password reset failed because the account was not found.")
    if st.session_state.recovery_step == 3:
        _render_back_button(3)
