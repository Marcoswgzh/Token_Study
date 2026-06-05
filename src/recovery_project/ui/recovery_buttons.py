#refactored by Erika Skodova
import sys
import time

import streamlit as st

from recovery_project.config import ExperimentConfig, TokenPolicy, RateLimitPolicy
from recovery_project.simulation.parallel_attacker import send_attack, get_token
from recovery_project.ui.Fragment_handler import _fragment_rerun
from recovery_project.ui.Recovery_helper import _go_to_recovery_step

#written by Sofya Grishkova (i6397764)
def _render_back_button(current_step: int) -> None:
    st.markdown('<div style="height:.35rem"></div>', unsafe_allow_html=True)
    if st.button("←", key=f"recover_back_{current_step}"):
        if current_step == 3:
            st.session_state.token_verified = False
        _go_to_recovery_step(current_step - 1)
        _fragment_rerun()

#written by Erika Skodova
def _add_break_button() -> None:
    st.markdown('<div style="height:.35rem"></div>', unsafe_allow_html=True)
    if st.button("Try to break into the account", key="break_button"):
        with st.spinner("Attempting to brute force token..."):
            configs = ExperimentConfig(
                name="demo_ui_test",
                trials=1,
                strategy="parallel",
                attack_rate_per_second=sys.maxsize,
                token_policy=TokenPolicy(length=5,
                                         alphabet="1234567890ABCDEF",
                                         ttl_seconds=2500,
                                         single_use=True),
                rate_limit_policy=RateLimitPolicy(enabled=False,
                                                  max_attempts=sys.maxsize,
                                                  window_seconds=sys.maxsize))
            result = send_attack(1, st.session_state.issued_token, configs)
        if result.success:
            st.session_state['token_input'] = get_token()
            st.warning("Token found.")
            time.sleep(1.5)
            st.rerun()
        else:
            st.warning("Could not find the token within the given constraints.")