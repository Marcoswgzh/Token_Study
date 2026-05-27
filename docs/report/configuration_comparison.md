# Configuration Comparison: Recovery Security Experiments

Generated on 2026-05-27 after connecting the Streamlit recovery flow to the
backend services.

This report compares the existing recovery-flow security configurations and the
experiment results produced by the current runner.

## Source configurations

| Research question | Config file | Experiment name | Main variable |
| --- | --- | --- | --- |
| RQ1 | `configs/experiments/rq1_entropy.yaml` | `rq1_entropy_baseline` | Token entropy |
| RQ2 | `configs/experiments/rq2_expiration.yaml` | `rq2_expiration_baseline` | Token expiration time |
| RQ3 | `configs/experiments/rq3_rate_limit.yaml` | `rq3_rate_limit_defense` | Rate limiting |

## Configuration values

| Experiment | Token length | Alphabet size | Token space | TTL | Configured attack budget | Rate limit enabled | Rate limit |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| `rq1_entropy_baseline` | 4 | 16 | 65,536 | 300s | 500 | No | 999,999 attempts / 60s |
| `rq2_expiration_baseline` | 6 | 16 | 16,777,216 | 60s | 500 | No | 999,999 attempts / 60s |
| `rq3_rate_limit_defense` | 6 | 16 | 16,777,216 | 300s | 500 | Yes | 5 attempts / 60s |

Token space is:

```text
alphabet_size ^ token_length
```

## Experiment runs

The experiments were run with:

```bash
PYTHONPATH=src python scripts/run_experiment.py configs/experiments/rq1_entropy.yaml --output-dir data/raw
PYTHONPATH=src python scripts/run_experiment.py configs/experiments/rq2_expiration.yaml --output-dir data/raw
PYTHONPATH=src python scripts/run_experiment.py configs/experiments/rq3_rate_limit.yaml --output-dir data/raw
```

Output files:

| Experiment | CSV result file |
| --- | --- |
| `rq1_entropy_baseline` | `data/raw/baseline/rq1_entropy_baseline_20260527T114751.csv` |
| `rq2_expiration_baseline` | `data/raw/baseline/rq2_expiration_baseline_20260527T115142.csv` |
| `rq3_rate_limit_defense` | `data/raw/defense/rq3_rate_limit_defense_20260527T115142.csv` |

## Measured results

| Experiment | Trials | Success count | Success rate | Mean attempts | Median attempts | Mean time elapsed | Total blocked | Token expired count |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `rq1_entropy_baseline` | 1000 | 4 | 0.4% | 491.08 | 492.0 | 118.87 ms | 0 | 0 |
| `rq2_expiration_baseline` | 1000 | 0 | 0.0% | 492.00 | 492.0 | 219.72 ms | 0 | 0 |
| `rq3_rate_limit_defense` | 1000 | 0 | 0.0% | 492.00 | 492.0 | 219.87 ms | 0 | 0 |

The measured number of attempts is about 492 rather than exactly 500 because
the current attacker splits the configured attack budget across CPU workers
using integer division.

## Expected probability from configuration

The current attacker uses random sampling. For small attack budgets compared
with the token space, expected success probability is approximately:

```text
effective_attempts / token_space
```

The more exact probability for random sampling with replacement is:

```text
1 - (1 - 1 / token_space) ^ effective_attempts
```

| Experiment | Token space | Effective attempts used for estimate | Approx. expected success | Exact random-sampling estimate |
| --- | ---: | ---: | ---: | ---: |
| `rq1_entropy_baseline` | 65,536 | 500 | 0.7629% | 0.7600% |
| `rq2_expiration_baseline` | 16,777,216 | 500 | 0.00298% | 0.00298% |
| `rq3_rate_limit_defense`, if rate limit is enforced | 16,777,216 | 5 | 0.0000298% | 0.0000298% |

## Interpretation

### RQ1: entropy

`rq1_entropy_baseline` uses a 4-character hexadecimal token. This gives only
65,536 possible tokens. In the measured run, the attacker succeeded in 4 out of
1000 trials, giving a measured success rate of 0.4%.

This is the weakest configuration in the current set because the token space is
small enough that 500 guesses can cover a visible part of it.

### RQ2: expiration

`rq2_expiration_baseline` increases token length from 4 to 6 while keeping the
same hexadecimal alphabet. This increases the token space from 65,536 to
16,777,216 possible tokens.

In the measured run, the attacker succeeded in 0 out of 1000 trials. This is
consistent with the expected probability of about 0.003% per trial: with only
1000 trials, seeing zero successes is plausible.

The shorter TTL of 60 seconds also reduces the period during which a recovery
token can be exploited.

### RQ3: rate limiting

`rq3_rate_limit_defense` enables rate limiting in the configuration:

```text
5 attempts / 60 seconds
```

In the measured CSV, however, `total_blocked` is still 0 and the mean attempts
remain about 492. This shows that the current experiment runner records the
rate-limit configuration fields, but does not yet enforce the rate limiter
inside the attack simulation.

Therefore, the measured RQ3 result should not be interpreted as a complete
rate-limiting experiment yet. The expected security effect, if the validation
rate limit is enforced, is much stronger: effective guesses drop from about 500
to 5 per window.

## Security ranking

| Rank | Experiment | Reason |
| ---: | --- | --- |
| 1 | `rq1_entropy_baseline` | Weakest: short 4-character token and measurable attack success |
| 2 | `rq2_expiration_baseline` | Stronger: 256x larger token space and shorter TTL |
| 3 | `rq3_rate_limit_defense` | Strongest by design, but current runner does not yet enforce blocking |

## Effect of the frontend/backend fix

The recent fix connected the Streamlit UI to the backend services:

- sign-in now uses `auth_service.login_user`
- recovery token issuing now uses `recovery_service.issue_token`
- token validation now uses `recovery_service.validate_token`
- password reset now updates the backend password through `reset_password`
- recovery tokens are bound to account email

This makes the demo recovery flow work end-to-end. It does not automatically
change the experiment runner behavior. The runner still needs an additional
change before RQ3 can measure actual blocked attempts.

## Conclusion

The measured experiment data shows that short recovery tokens are the main
weakness: `rq1_entropy_baseline` produced successful attacks, while the
6-character token configurations produced zero successes in these 1000-trial
runs.

The configuration comparison also shows that rate limiting should be the
strongest defense when enforced. At the moment, the application recovery flow
uses the rate limiter, but the experiment runner does not yet apply it during
the simulated attack.
