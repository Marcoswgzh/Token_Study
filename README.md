# Account Recovery Security Project

Repository for our computer security project on account recovery mechanisms (password reset tokens, attack simulations, and defenses).

## What will be built here

- Minimal authentication + password recovery flow in Python
- Recovery token validation with configurable entropy / TTL / single-use behavior
- Brute-force attack simulation against recovery endpoints
- Rate-limiting defense experiments
- Result export for plots/tables used in the report and poster

## Repository layout

```text
configs/experiments/   experiment configs for RQ1 / RQ2 / RQ3
data/                  generated data (raw / processed / seeds)
docs/                  proposal, report, poster, diagrams
results/               experiment outputs, figures, tables
scripts/               small CLI entrypoints (run experiments, generate plots)
src/recovery_project/  project code
tests/                 unit / integration / simulation tests
```

## Code structure (`src/recovery_project`)

- `domain/` models (`User`, `RecoveryToken`, `RecoveryAttempt`)
- `services/` token generation, recovery flow, rate limiting
- `repositories/` storage adapters (start with in-memory)
- `simulation/` attacker and legitimate-user behavior
- `experiments/` runners and metrics aggregation
- `api/` optional HTTP layer if we decide to expose endpoints

## Suggested build order

1. Implement `token_service` + `recovery_service`
2. Add in-memory repositories
3. Build attacker simulation for brute-force token guessing
4. Add experiment runner for RQ1/RQ2/RQ3 configs
5. Add result export and plotting
6. (Optional) wrap it with an API for demo purposes

## Local setup (when you start coding)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev,analysis]
pytest
```

## Demo UI (Streamlit)

If you want a quick UI for the authentication/recovery flow:

```bash
pip install -e .[dev,ui]
streamlit run src/recovery_project/ui/streamlit_app.py
```

The app looks for `cute_robot.json` in the project root (or `assets/animations/cute_robot.json`).
