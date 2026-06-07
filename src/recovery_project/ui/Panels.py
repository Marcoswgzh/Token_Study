#refactored by Erika Skodova
#writer Sofya Grishkova (i6397764)

import streamlit as st
from streamlit_lottie import st_lottie

from Fragment_handler import fragment
from Experiments_tab import _experiments_tab
from Signin_tab import _sign_in_tab
from Recovery_tab import _recover_tab
from Register_tab import _register_tab
from robot import _load_lottie

# Main panel settings for all tabs in GUI

@fragment
def _render_left_panel() -> None:
    lottie = _load_lottie()
    if lottie:
        try:
            st_lottie(lottie, height=520, speed=1, loop=True, quality="high", key="robot_lottie")
        except TypeError:
            st_lottie(lottie, height=520, speed=1, loop=True, quality="high")
    else:
        st.warning("Lottie file not found. Expected `cute_robot.json` in project root.")
        st.markdown(
            """
            <div style="padding:1rem 0;color:#5f6673;">
              Add a local Lottie JSON file to the project root or working directory.
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('<div style="height:.3rem"></div>', unsafe_allow_html=True)

@fragment
def _render_right_panel() -> None:
    section = st.radio(
        "Section",
        ["Sign in","Register", "Recovery flow", "Experiments"],
        horizontal=True,
        label_visibility="collapsed",
        key="main_section",
    )

    if section == "Sign in":
        _sign_in_tab()
    elif section == "Recovery flow":
        _recover_tab()
    elif section == "Register":
        _register_tab()
    else:
        _experiments_tab()
