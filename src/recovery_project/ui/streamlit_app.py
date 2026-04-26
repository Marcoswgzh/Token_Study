from __future__ import annotations

import sys
import json
import secrets
from pathlib import Path

import streamlit as st
from streamlit_lottie import st_lottie

# These few lines are needed so that importing from other packages work
root_route = str(Path(__file__).resolve().parents[3])

if root_route not in sys.path:
    sys.path.append(root_route)


from src.recovery_project.services.recovery_service import issue_token, validate_token
from src.recovery_project.services.rate_limiter import is_locked, record_success, record_failure, get_remaining_lockout_time

# Sofya Grishkova (i6397764)
def _fragment_passthrough(func):
    return func


fragment = getattr(st, "fragment", _fragment_passthrough)


# Sofya Grishkova (i6397764)
def _fragment_rerun() -> None:
    """Rerun only the active fragment when supported (fallback to full rerun)."""
    try:
        st.rerun(scope="fragment")
    except TypeError:
        st.rerun()


# Sofya Grishkova (i6397764)
def _strip_lottie_background(animation: dict) -> dict:
    """Remove static pale background layers from the current robot Lottie."""
    layers = animation.get("layers")
    if not isinstance(layers, list) or len(layers) < 2:
        return animation

    filtered: list[dict] = []
    for idx, layer in enumerate(layers):
        if (
            idx >= len(layers) - 2
            and layer.get("ty") == 4
            and layer.get("nm") in {"Layer 1", "Layer 2"}
        ):
            continue
        filtered.append(layer)
    animation["layers"] = filtered
    return animation


# Sofya Grishkova (i6397764)
@st.cache_data(show_spinner=False)
def _load_lottie() -> dict | None:
    candidates = [
        Path("cute_robot.json"),
        Path("assets/animations/cute_robot.json"),
    ]
    for path in candidates:
        if path.exists():
            try:
                animation = json.loads(path.read_text(encoding="utf-8"))
                return _strip_lottie_background(animation)
            except json.JSONDecodeError:
                return None
    return None


# Sofya Grishkova (i6397764)
def _inject_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --bg: rgb(15, 17, 22);
            --panel: #101625;
            --panel-2: rgb(15, 17, 22);
            --panel-3: #131b2d;
            --border: #232c44;
            --text: #edf1fb;
            --muted: #98a3bd;
            --accent: #2f6df6;
            --accent-2: #5fa8ff;
            --input: #151d31;
        }
        #MainMenu, footer,
        header[data-testid="stHeader"],
        [data-testid="stToolbar"],
        [data-testid="stDecoration"],
        [data-testid="stStatusWidget"],
        [data-testid="stElementToolbar"],
        [data-testid="stElementToolbarButton"],
        [data-testid="stElementToolbarToggleButton"] {
            display: none !important;
            visibility: hidden !important;
            height: 0 !important;
        }
        .element-container:has(iframe[title^="streamlit_lottie"]) [data-testid="stElementToolbar"],
        .element-container:has(iframe[title^="streamlit_lottie"]) [data-testid="stElementToolbarButton"] {
            display: none !important;
        }
        iframe[title^="streamlit_lottie"] {
            border: 0 !important;
            background: transparent !important;
            border-radius: 18px !important;
        }
        .element-container:has(iframe[title^="streamlit_lottie"]) {
            background: rgb(15, 17, 22) !important;
            border-radius: 22px;
            padding: 0.5rem;
        }
        .stApp {
            background:
                radial-gradient(circle at 94% 82%, rgba(72, 151, 255, 0.07), transparent 48%),
                radial-gradient(circle at 86% 20%, rgba(47, 109, 246, 0.05), transparent 44%),
                radial-gradient(circle at 102% 10%, rgba(120, 170, 255, 0.025), transparent 36%),
                linear-gradient(
                    90deg,
                    rgb(15, 17, 22) 0%,
                    rgb(15, 17, 22) 52%,
                    rgb(17, 20, 27) 74%,
                    rgb(19, 24, 35) 100%
                ),
                var(--bg);
            color: var(--text);
        }
        [data-testid="stAppViewContainer"] {
            background: transparent;
        }
        .block-container {
            max-width: 1400px;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
            padding-top: 5.75rem;
            padding-bottom: 0.75rem;
        }
        .ui-shell-marker {
            display: none;
        }
        div[data-testid="stVerticalBlock"]:has(.ui-shell-marker) > div[data-testid="stHorizontalBlock"] {
            align-items: stretch;
            gap: 1rem;
            background: linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.02));
            border: 1px solid rgba(255,255,255,0.06);
            box-shadow:
                0 24px 80px rgba(0, 0, 0, 0.42),
                inset 0 1px 0 rgba(255,255,255,0.04);
            border-radius: 28px;
            padding: 14px;
            min-height: 760px;
            transform: translateY(0);
        }
        div[data-testid="stVerticalBlock"]:has(.ui-shell-marker)
            > div[data-testid="stHorizontalBlock"]
            > div[data-testid="column"] {
            align-self: stretch;
        }
        div[data-testid="stVerticalBlock"]:has(.ui-shell-marker)
            > div[data-testid="stHorizontalBlock"]
            > div[data-testid="column"]:first-child
            > div[data-testid="stVerticalBlock"] {
            background: rgb(15, 17, 22);
            border: none;
            border-radius: 22px;
            padding: 0.85rem 0.85rem 0.35rem 0.85rem;
            min-height: 730px;
        }
        div[data-testid="stVerticalBlock"]:has(.ui-shell-marker)
            > div[data-testid="stHorizontalBlock"]
            > div[data-testid="column"]:last-child
            > div[data-testid="stVerticalBlock"] {
            background:
                linear-gradient(180deg, rgba(18,24,40,0.97) 0%, rgba(13,18,31,0.98) 100%);
            border: 1px solid rgba(255,255,255,0.05);
            border-radius: 22px;
            padding: 1.15rem 1.15rem 1rem 1.15rem;
            min-height: 730px;
        }
        .top-line {
            display: flex;
            justify-content: flex-end;
            align-items: center;
            color: var(--muted);
            font-size: .95rem;
            margin: 0 0 1.25rem 0;
            padding: 0.35rem 0.1rem;
        }
        .top-line b {
            color: var(--text);
            font-weight: 600;
        }
        .headline {
            font-size: clamp(2rem, 5vw, 3.4rem);
            line-height: 1;
            letter-spacing: -0.03em;
            font-weight: 700;
            color: var(--text);
            margin: 0 0 .9rem 0;
        }
        .subtext {
            color: var(--muted);
            font-size: 1rem;
            margin-bottom: 1.05rem;
        }
        .security-note {
            background: rgba(47, 109, 246, 0.10);
            border: 1px solid rgba(95, 168, 255, 0.22);
            color: #bfd7ff;
            border-radius: 14px;
            padding: .75rem .9rem;
            font-size: .9rem;
            margin-bottom: 1rem;
        }
        .security-note code {
            color: #d8e7ff;
            background: rgba(0,0,0,0.25);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 7px;
            padding: 0.1rem 0.35rem;
        }
        .metric-chip {
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 12px;
            padding: .65rem .8rem;
            margin-bottom: .6rem;
        }
        .metric-chip strong {
            display: block;
            color: var(--text);
            font-size: .95rem;
        }
        .metric-chip span {
            color: var(--muted);
            font-size: .85rem;
        }
        [data-testid="stRadio"] {
            margin-bottom: 1.15rem;
        }
        [data-testid="stRadio"] > div {
            background: transparent !important;
        }
        [data-testid="stRadio"] div[role="radiogroup"] {
            display: flex !important;
            flex-wrap: wrap;
            gap: .45rem;
            align-items: center;
        }
        [data-testid="stRadio"] label[data-baseweb="radio"] {
            margin: 0 !important;
            min-height: 40px;
            padding: 0.55rem 0.95rem;
            gap: 0 !important;
            border-radius: 999px;
            border: 1px solid rgba(255,255,255,0.07);
            background: rgba(255,255,255,0.03);
            display: inline-flex !important;
            align-items: center;
            justify-content: center;
            width: auto !important;
            cursor: pointer;
            transition: border-color .18s ease, background-color .18s ease, box-shadow .18s ease;
            text-align: center;
        }
        [data-testid="stRadio"] label[data-baseweb="radio"] > div:first-child {
            display: none !important;
        }
        [data-testid="stRadio"] label[data-baseweb="radio"] > div:last-child {
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            width: 100%;
            margin: 0 !important;
            padding: 0 !important;
        }
        [data-testid="stRadio"] label[data-baseweb="radio"] p,
        [data-testid="stRadio"] label[data-baseweb="radio"] span {
            display: block !important;
            width: 100% !important;
            margin: 0 !important;
            color: var(--muted) !important;
            font-weight: 500;
            font-size: 0.95rem;
            text-align: center !important;
        }
        [data-testid="stRadio"] label[data-baseweb="radio"]:hover {
            border-color: rgba(95, 168, 255, 0.18);
        }
        [data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) {
            background: rgba(47, 109, 246, 0.20) !important;
            border-color: rgba(95, 168, 255, 0.35) !important;
            box-shadow: inset 0 0 0 1px rgba(47,109,246,0.25);
        }
        [data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) p {
            color: #eaf1ff !important;
        }
        .stTextInput label p,
        .stNumberInput label p,
        .stSelectbox label p,
        .stSlider label p {
            color: #c9d3e8 !important;
            font-weight: 500;
        }
        .stSelectbox [data-baseweb="select"] {
            background: var(--input) !important;
            border: 1px solid var(--border) !important;
            border-radius: 14px !important;
            min-height: 48px !important;
            box-shadow: none !important;
        }
        .stSelectbox [data-baseweb="select"]:hover {
            border-color: rgba(95, 168, 255, 0.22) !important;
        }
        .stSelectbox [data-baseweb="select"] > div {
            color: var(--text) !important;
        }
        .stSelectbox [data-baseweb="select"] svg {
            color: #a4b3d6 !important;
        }
        .stTextInput [data-baseweb="input"],
        .stNumberInput [data-baseweb="input"] {
            background: var(--input) !important;
            border-radius: 14px !important;
            border: 1px solid var(--border) !important;
            box-shadow: none !important;
            overflow: hidden !important;
        }
        .stTextInput [data-baseweb="input"]:focus-within,
        .stNumberInput [data-baseweb="input"]:focus-within {
            border-color: rgba(95, 168, 255, 0.42) !important;
            box-shadow: 0 0 0 3px rgba(47, 109, 246, 0.10) !important;
        }
        .stTextInput input,
        .stNumberInput input {
            color: var(--text) !important;
            background: transparent !important;
        }
        .stNumberInput [data-baseweb="input"] > div:last-child {
            gap: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
            background: transparent !important;
            border-left: 1px solid rgba(255,255,255,0.06) !important;
        }
        .stNumberInput [data-baseweb="input"] > div:last-child > button {
            background: rgba(255,255,255,0.02) !important;
            border: none !important;
            color: var(--text) !important;
            min-width: 54px !important;
            box-shadow: none !important;
        }
        .stNumberInput [data-baseweb="input"] > div:last-child > button:hover {
            background: rgba(255,255,255,0.06) !important;
        }
        .stNumberInput [data-baseweb="input"] > div:last-child > button:focus {
            outline: none !important;
            box-shadow: inset 0 0 0 1px rgba(95, 168, 255, 0.28) !important;
        }
        .stTextInput input::placeholder,
        .stNumberInput input::placeholder {
            color: #7f8aa5 !important;
        }
        .stTextInput [data-baseweb="input"] button {
            background: transparent !important;
            color: #a4b3d6 !important;
            border: none !important;
         }
        [data-testid="InputInstructions"] {
            display: none !important;
            visibility: hidden !important;
            height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        [data-testid="stForm"] {
            background: rgba(255,255,255,0.02);
            border: 1px solid rgba(255,255,255,0.05);
            border-radius: 16px;
            padding: 0.85rem 0.95rem 0.95rem 0.95rem;
            margin-bottom: 0.9rem;
        }
        [data-testid="stForm"] .stFormSubmitButton > button {
            margin-top: 0.35rem;
        }
        .stButton > button {
            width: auto;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            text-align: center !important;
            border-radius: 999px;
            border: 1px solid rgba(95, 168, 255, 0.26);
            background: linear-gradient(180deg, rgba(95,168,255,0.16) 0%, rgba(47,109,246,0.10) 100%);
            color: white;
            font-weight: 600;
            min-height: 40px;
            padding: 0.35rem 0.95rem;
            box-shadow: 0 8px 20px rgba(47, 109, 246, 0.10);
        }
        .stButton > button:hover {
            border-color: rgba(95, 168, 255, 0.38);
            background: linear-gradient(180deg, rgba(95,168,255,0.20) 0%, rgba(47,109,246,0.14) 100%);
            box-shadow: 0 10px 24px rgba(47, 109, 246, 0.16);
        }
        .stButton > button:focus {
            box-shadow: 0 0 0 3px rgba(95, 168, 255, 0.14) !important;
        }
        .secondary-btn .stButton > button {
            background: rgba(255,255,255,0.03) !important;
            color: var(--text) !important;
            border-color: rgba(255,255,255,0.08) !important;
            box-shadow: none !important;
        }
        .stSuccess, .stInfo, .stWarning, .stError {
            border-radius: 14px;
        }
        .stCaption, .stMarkdown p {
            color: var(--muted);
        }
        .left-note {
            color: var(--muted);
            font-size: .92rem;
            line-height: 1.45;
            padding: .5rem .2rem .2rem .2rem;
        }
        .recovery-hint {
            color: var(--muted);
            font-size: .9rem;
            margin: 0.15rem 0 0.75rem 0;
        }
        .recovery-hint b {
            color: #cfe0ff;
            font-weight: 600;
        }
        @media (max-width: 900px) {
            div[data-testid="stVerticalBlock"]:has(.ui-shell-marker) > div[data-testid="stHorizontalBlock"] {
                min-height: auto;
                padding: 10px;
                transform: translateY(0);
            }
            div[data-testid="stVerticalBlock"]:has(.ui-shell-marker)
                > div[data-testid="stHorizontalBlock"]
                > div[data-testid="column"]:first-child
                > div[data-testid="stVerticalBlock"],
            div[data-testid="stVerticalBlock"]:has(.ui-shell-marker)
                > div[data-testid="stHorizontalBlock"]
                > div[data-testid="column"]:last-child
                > div[data-testid="stVerticalBlock"] {
                min-height: auto;
                padding: 0.9rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# Sofya Grishkova (i6397764)
def _init_state() -> None:
    defaults = {
        "reset_email": "",
        "issued_token": None,
        "token_verified": False,
        "last_status": None,
        "recovery_step": 1,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# Sofya Grishkova (i6397764)
def _issue_demo_token(email: str, length: int = 6) -> str:
    alphabet = "0123456789ABCDEF"
    token = "".join(secrets.choice(alphabet) for _ in range(length))
    st.session_state.reset_email = email
    st.session_state.issued_token = token
    st.session_state.token_verified = False
    st.session_state.recovery_step = 2
    return token


# Sofya Grishkova (i6397764)
def _go_to_recovery_step(step: int) -> None:
    st.session_state.recovery_step = max(1, min(step, 3))


# Sofya Grishkova (i6397764)
def _reset_recovery_flow() -> None:
    st.session_state.issued_token = None
    st.session_state.token_verified = False
    st.session_state.recovery_step = 1


# Sofya Grishkova (i6397764)
def _sign_in_tab() -> None:
    st.markdown('<div class="headline">Sign in</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="recovery-hint">Forgot your password? Open <b>Recovery flow</b> to request a reset token and set a new password.</div>',
        unsafe_allow_html=True,
    )

    with st.form("sign_in_form", clear_on_submit=False, enter_to_submit=False):
        email = st.text_input("Email", placeholder="student@university.edu")
        password = st.text_input("Password", type="password", placeholder="Enter password")
        submitted = st.form_submit_button("Sign in")

    if submitted:
        if email and password:
            st.success("Demo login submitted. Next step: connect `auth_service`.")
        else:
            st.error("Fill in both email and password.")


# Sofya Grishkova (i6397764)
def _recover_tab() -> None:
    step = int(st.session_state.recovery_step)
    if step > 1 and not st.session_state.issued_token:
        _go_to_recovery_step(1)
        step = 1
    if step > 2 and not st.session_state.token_verified:
        _go_to_recovery_step(2)
        step = 2

    st.markdown('<div class="headline">Recovery</div>', unsafe_allow_html=True)

    # Sofya Grishkova (i6397764)
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
                # Changed the issue function to the one in services/recovery_service
                token = issue_token(email)
                # The new issue_token does not handle state updates, so do it here
                st.session_state.reset_email = email
                st.session_state.issued_token = token
                st.session_state.token_verified = False
                _go_to_recovery_step(3)
                st.success(f"Demo token issued for {email}")
                with st.expander("Debug (for demo/testing)", expanded=True):
                    st.code(f"Reset token: {token}", language="text")
                _fragment_rerun()
            else:
                st.error("Enter email first.")
        return

    if step == 2:
        with st.form("recover_verify", enter_to_submit=False):
            guessed = st.text_input("Enter recovery token", placeholder="e.g. 1A2B3C")
            verify_submitted = st.form_submit_button("Verify token")
        if verify_submitted:
            if is_locked(st.session_state.reset_email):
                st.error(f"Too many attempts. Try again in {get_remaining_lockout_time(st.session_state.reset_email)} minute(s).")
            # Use the validate_token function in services/recovery_service
            elif validate_token(st.session_state.reset_email, guessed.strip()):
                st.session_state.token_verified = True
                _go_to_recovery_step(3)
                record_success(st.session_state.reset_email)
                st.success("Token verified (demo).")
                _fragment_rerun()
            else:
                st.session_state.token_verified = False
                st.error("Invalid token.")
                record_failure(st.session_state.reset_email) 

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
        if not new_password or not confirm_password:
            st.error("Fill in both password fields.")
        elif new_password != confirm_password:
            st.error("Passwords do not match.")
        else:
            st.success("Password reset completed (demo state).")
            _reset_recovery_flow()
    if st.session_state.recovery_step == 3:
        _render_back_button(3)


# Sofya Grishkova (i6397764)
def _experiments_tab() -> None:
    st.markdown('<div class="headline">Experiments</div>', unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        token_length = st.slider("Token length", 4, 12, 6)
        ttl = st.slider("Token TTL (seconds)", 30, 900, 300, step=30)
        attack_budget = st.number_input("Attack attempt budget", 10, 100000, 500, step=10)
    with col_b:
        attack_rate = st.slider("Attack rate (attempts/sec)", 1, 100, 10)
        rl_enabled = st.toggle("Enable rate limiting", value=True)
        rl_max = st.number_input("Rate limit max attempts", 1, 100, 5, step=1, disabled=not rl_enabled)
        rl_window = st.number_input(
            "Rate limit window (sec)",
            10,
            600,
            60,
            step=10,
            disabled=not rl_enabled,
        )

    run_col, _ = st.columns([0.42, 0.58])
    run_clicked = run_col.button("Run demo experiment")
    if run_clicked:
        search_space = 16 ** token_length
        naive_prob = min(attack_budget / search_space, 1.0)
        penalty = 0.25 if rl_enabled else 1.0
        ttl_penalty = min(ttl / 300, 1.0)
        estimated_prob = naive_prob * penalty * ttl_penalty
        st.info("Demo-only estimate. Replace with actual simulation output.")
        m1, m2, m3 = st.columns(3)
        m1.markdown(
            f'<div class="metric-chip"><strong>{estimated_prob:.6f}</strong><span>Estimated takeover probability</span></div>',
            unsafe_allow_html=True,
        )
        m2.markdown(
            f'<div class="metric-chip"><strong>{search_space:,}</strong><span>Token search space</span></div>',
            unsafe_allow_html=True,
        )
        m3.markdown(
            f'<div class="metric-chip"><strong>{attack_rate}/s</strong><span>Configured attack rate</span></div>',
            unsafe_allow_html=True,
        )

        st.caption(
            "Next step: connect this button to `scripts/run_experiment.py` and write CSV results into `results/`."
        )


# Sofya Grishkova (i6397764)
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
              Add a local Lottie JSON file to the project root or `assets/animations/`.
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('<div style="height:.3rem"></div>', unsafe_allow_html=True)


# Sofya Grishkova (i6397764)
@fragment
def _render_right_panel() -> None:
    section = st.radio(
        "Section",
        ["Sign in", "Recovery flow", "Experiments"],
        horizontal=True,
        label_visibility="collapsed",
        key="main_section",
    )

    if section == "Sign in":
        _sign_in_tab()
    elif section == "Recovery flow":
        _recover_tab()
    else:
        _experiments_tab()


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
        _render_left_panel()
    with right:
        _render_right_panel()


if __name__ == "__main__":
    main()
