#refactored by Erika Skodova
#writer Sofya Grishkova (i6397764)

#Helper class for GUI
import streamlit as st

def _fragment_passthrough(func):
    return func

fragment = getattr(st, "fragment", _fragment_passthrough)

def _fragment_rerun() -> None:
    """Rerun only the active fragment when supported (fallback to full rerun)."""
    try:
        st.rerun(scope="fragment")
    except TypeError:
        st.rerun()