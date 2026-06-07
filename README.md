# Account Recovery Security Project

Repository for our computer security project on account recovery mechanisms (password reset tokens, attack simulations, and defenses).

## Project content

- Minimal authentication + password recovery flow in Python
- Recovery token validation with configurable entropy / TTL / single-use behavior
- 3 attack simulations against recovery endpoints (1 parallelized, 2 sequential)
- Entropy, expiration, and rate-limiting experiments
- Experiment results and their summaries
- User adjustable experiments through GUI

## Repository layout

```text
configs/experiments/   experiment configs for RQ1 / RQ2 / RQ3 in .json format
data/                  results from experiments (raw / processed )
docs/                  additional documents
scripts/               small CLI entrypoints (gathering hardware specs)
src/recovery_project/  project code
tests/                 unit tests
```

## Code structure (`src/recovery_project`)

- `attacker_algorithms/` algorithms and helper used for breaking the tokens
- `domain/` models (`User`, `RecoveryToken`, `RecoveryAttempt`)
- `experiments/` experiment runners, metrics, helpers, and connector classes
- `repositories/` storage adapters (in memory)
- `services/` authentication, email validation, token generation, recovery flow, rate limiting
- `ui/` simple user-friendly GUI
- `utils/`  logging utility
- `config.py` loading and handling experiment configurations
- `main.py` GUI launcher

## Dependency and environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev,analysis]
```

## Tests

```bash
pytest
```

## Demo UI (Streamlit)

To run GUI through terminal:

```bash
streamlit run src/recovery_project/ui/streamlit_app.py
```

Otherwise, use `src/recovery_project/main.py`

## Architecture

Authentication and account-recovery architecture:
- `docs/authentication_architecture.md`
