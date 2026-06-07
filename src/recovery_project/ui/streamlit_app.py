#refactored by Erika Skodova

from __future__ import annotations

import sys
from pathlib import Path
import streamlit as st

import Panels

root_route = str(Path(__file__).resolve().parents[3])

if root_route not in sys.path:
    sys.path.append(root_route)

# Main module handling connecting the whole GUI together

# Sofya Grishkova (i6397764)
def _inject_styles() -> None:
    css_path = Path(__file__).parent / "UI_design.css"
    with open(css_path) as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Timea Vojcikova - i6377033
def _init_state() -> None:
    defaults = {
        "reset_email": "",
        "issued_token": None,
        "token_verified": False,
        "last_status": None,
        "recovery_step": 1,
        "logged_in": False,
        "current_user": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# Sofya Grishkova (i6397764)
def main() -> None:
    st.set_page_config(
        page_title="Account Recovery Project UI",
        page_icon="🔐",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    _init_state()
    _inject_styles()

    st.markdown('<div class="ui-shell-marker"></div>', unsafe_allow_html=True)
    left, right = st.columns([1.05, 1.0], gap="large")
    with left:
        Panels._render_left_panel()
    with right:
        Panels._render_right_panel()


if __name__ == "__main__":
    main()
