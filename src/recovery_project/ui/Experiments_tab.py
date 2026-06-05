#refactored by Erika Skodova
#writer Sofya Grishkova (i6397764)
import sys
import time

import streamlit as st

from recovery_project.config import TokenPolicy, RateLimitPolicy, ExperimentConfig
from recovery_project.experiments.Ui_experiment_runner import demo_run


def _experiments_tab() -> None:
    st.markdown('<div class="headline">Experiments</div>', unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        token_length = st.slider("Token length", 2, 12, 6)
        ttl = st.slider("Token TTL (seconds)", 10, 900, 300, step=30)
        attack_budget = st.number_input("Attack trails", 2, 1000, 500, step=10)
        alphabet = st.radio("Length of the alphabet used for token generation", [10,16], horizontal= True)
    with col_b:
        LABLES = {"parallel":"Parallelized bruteforce (most reliable but takes long, can't do rate limiting)",
                  "random":"Random guessing (fit for rate limit, guesses have chance to repeat)",
                  "exhaustive":"Exhaustive guessing (good for low rate limit, guesses don't repeat)"}

        algorithm = st.selectbox("Algorithm to use", LABLES.keys(), format_func=lambda x: LABLES[x],)
        rl_enabled = st.toggle("Enable rate limiting", value=True)
        rl_max = st.number_input("Rate limit max attempts", 1, 100000, 5, step=1, disabled=not rl_enabled)
        rl_window = st.number_input(
            "Rate limit window (sec)",
            10,
            600,
            60,
            step=10,
            disabled=not rl_enabled,
        )

    run_col, warning_col = st.columns([0.42, 0.58])
    run_clicked = run_col.button("Run demo experiment")

    ttl_too_short = rl_enabled and ttl < rl_window
    token_too_long = token_length > 7 and not rl_enabled
    ttl_bruteforce = algorithm == "parallel"
    algorithm_set = algorithm == "parallel" and rl_enabled
    trail_count = attack_budget < 50

    current_config = (token_length, ttl, attack_budget, alphabet, algorithm, rl_enabled, rl_max, rl_window)

    if st.session_state.get('last_config') != current_config:
        st.session_state['hide_warnings'] = False
        st.session_state['last_config'] = current_config

    if run_clicked:
        st.session_state['hide_warnings'] = True

    with warning_col:
        if not st.session_state.get('hide_warnings', False):
            if trail_count:
                warning_col.warning(f"Trail count set to {attack_budget}, results might be heavily skewed.")
            if token_too_long:
                warning_col.warning(f"Token is set to {token_length} and no restrictions are added, the test might take a while to finish")
            if ttl_too_short:
                warning_col.warning(f"Token is shorter than rate limit window {rl_window}s, the token will expire before window reset")
            if algorithm_set:
                warning_col.warning("Algorithm is set as parallelized bruteforce with rate limiting enabled, only token expire time is considered")
            elif ttl_bruteforce:
                warning_col.warning("Algorithm is set to be parallelized bruteforce, token expire time is only considered if rate limiting is enabled")


    if run_clicked:
        with st.spinner("Running demo experiments, please wait..."):
            time.sleep(0.1)
            configs = ExperimentConfig(
                name = "demo_ui_test",
                trials = attack_budget,
                strategy = algorithm,
                attack_rate_per_second = sys.maxsize,
                token_policy = TokenPolicy(length = token_length,
                                            alphabet= "1234567890" if alphabet == 10 else "1234567890ABCDEF",
                                            ttl_seconds = ttl,
                                            single_use= True),
                rate_limit_policy = RateLimitPolicy(enabled=rl_enabled,
                                                    max_attempts = rl_max,
                                                    window_seconds=rl_window))
            results = demo_run(configs)
        m1, m2, m3 = st.columns(3)
        m1.markdown(
            f'<div class="metric-chip"><strong>{results["success_rate"]*100:.6f}</strong><span>Estimated takeover probability in %</span></div>',
            unsafe_allow_html=True,
        )
        m2.markdown(
            f'<div class="metric-chip"><strong>{results["success_count"]:,}</strong><span>Total tokens found</span></div>',
            unsafe_allow_html=True,
        )
        m3.markdown(
            f'<div class="metric-chip"><strong>{results["mean_time_elapsed_ms"]/1000:.6f}/s</strong><span>Average time of security breach</span></div>',
            unsafe_allow_html=True,
        )
