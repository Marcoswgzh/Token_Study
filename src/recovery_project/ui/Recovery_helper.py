#refactored by Erika Skodova
#writer Sofya Grishkova (i6397764)

import streamlit as st
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