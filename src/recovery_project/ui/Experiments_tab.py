#refactored by Erika Skodova
#writer Sofya Grishkova (i6397764)

import streamlit as st

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

# TODO make experiments actually work -> adjust function to run experiments
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
