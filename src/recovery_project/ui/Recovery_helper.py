#refactored by Erika Skodova
#writer Sofya Grishkova (i6397764)

import streamlit as st
import secrets
from html import escape

def _go_to_recovery_step(step: int) -> None:
    st.session_state.recovery_step = max(1, min(step, 3))


def _reset_recovery_flow() -> None:
    st.session_state.issued_token = None
    st.session_state.token_verified = False
    st.session_state.recovery_step = 1

def _render_token_preview(token: str) -> None:
    st.markdown(
        f"""
        <div class="token-preview">
            <span>Reset token</span>
            <strong>{escape(token)}</strong>
        </div>
        """,
        unsafe_allow_html=True,
    )

#TODO use actual class for token generation
def _issue_demo_token(email: str, length: int = 6) -> str:
    alphabet = "0123456789ABCDEF"
    token = "".join(secrets.choice(alphabet) for _ in range(length))
    st.session_state.reset_email = email
    st.session_state.issued_token = token
    st.session_state.token_verified = False
    st.session_state.recovery_step = 2
    return token
