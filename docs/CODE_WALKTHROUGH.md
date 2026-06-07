# Code Walkthrough

This document explains what the project currently does, how the main parts
connect, and which parts are still experimental or incomplete.

## 1. Project purpose

The project studies the security of password-recovery tokens. It has two main
uses:

1. A Streamlit demo where a user can register, sign in, request a reset token,
   verify it, and set a new password.
2. Research experiments that generate tokens, simulate brute-force attacks,
   and save measurements for RQ1, RQ2, and RQ3.

The research questions represented by the code are:

- **RQ1 - Token entropy:** How do token alphabet and length affect attack time?
- **RQ2 - Expiration window:** How does token TTL affect attacker success?
- **RQ3 - Rate limiting:** How much does limiting attempts reduce attacker
  success?

## 2. High-level architecture

```text
Streamlit UI
    |
    +--> auth_service.py ---------> services/users.txt
    |
    +--> recovery_service.py
            |
            +--> token_service.py
            +--> token_repository.py (in memory)
            +--> rate_limiter.py (in memory)

Experiment config
    |
    +--> experiment script/runner
            |
            +--> token_service.py
            +--> attack simulation
            +--> TrialResult / CSV output
```

There is an important separation:

- The **demo recovery flow** uses the functions in `services/` and the
  Streamlit UI.
- The **experiment flow** creates its own tokens and attacks them directly.
  It does not normally call the UI or the full recovery workflow.

## 3. Recommended reading order

To understand the project quickly, read these files in this order:

1. `src/recovery_project/domain/models.py`
2. `src/recovery_project/services/token_service.py`
3. `src/recovery_project/services/rate_limiter.py`
4. `src/recovery_project/services/recovery_service.py`
5. `src/recovery_project/services/auth_service.py`
6. `src/recovery_project/simulation/exp_window_attack.py`
7. `scripts/run_experiment.py`
8. `src/recovery_project/ui/streamlit_app.py`
9. `src/recovery_project/ui/Recovery_tab.py`
10. `tests/unit/`

## 4. Core data models

### `src/recovery_project/domain/models.py`

This file contains the dataclasses shared by the rest of the project.

- `User` stores a user ID, email, password hash, and MFA flag.
- `RecoveryToken` stores the account identifier, token value/hash, creation
  time, expiration time, and whether the token has been used.
- `RecoveryAttempt` describes one recovery-token guess.
- `TrialResult` is the standard output record for an experiment trial. It
  stores token settings, rate-limit settings, success, attempts, timing, and
  expiration information.

`TrialResult` is converted to CSV rows by
`src/recovery_project/experiments/metrics.py`.

## 5. Authentication and recovery flow

### 5.1 Password storage

`src/recovery_project/services/auth_service.py` handles demo users.

Passwords are not stored directly. `hash_password()`:

1. Creates a random 16-byte salt with `secrets.token_hex`.
2. Derives a hash with PBKDF2-HMAC-SHA256.
3. Stores the algorithm, iteration count, salt, and digest in one string.

`verify_password()` parses that string, derives a new digest from the submitted
password, and compares the two digests with `hmac.compare_digest()`.

The service stores users in:

```text
src/recovery_project/services/users.txt
```

Each line has this form:

```text
email:password_hash
```

Main functions:

- `register_user(email, password)` creates a user unless the email exists.
- `login_user(email, password)` checks the submitted password.
- `user_exists(email)` supports the recovery UI.
- `update_password(email, new_password)` replaces the stored password hash.
- `logout_user(email)` currently only prints a message; there is no backend
  session store.

`src/recovery_project/services/email_verifier.py` contains the small regular
expression check used by the Register, Sign in, and Recovery tabs. It checks
for a basic `name@domain.suffix` structure; it does not verify that the mailbox
exists.

`src/recovery_project/repositories/user_repository.py` is a separate in-memory
`User` repository with create, ID lookup, email lookup, and password-update
methods. The current Streamlit demo does not use it; `auth_service.py` reads
and writes `users.txt` instead.

### 5.2 Token generation

`src/recovery_project/services/token_service.py` contains `TokenService`.

Its constructor accepts:

- `alphabet`: characters allowed in a token.
- `token_length`: number of characters in a token.

`generate_token()` uses `secrets.choice()`, which is suitable for
security-sensitive randomness. It returns:

```python
(raw_token, sha256_hash_of_token)
```

The raw token is shown or sent to the user. The hash is what should be stored
by the backend.

`verify_token(provided_token, stored_hash)` hashes a guess and compares it with
the stored hash.

### 5.3 Token repository

`src/recovery_project/repositories/token_repository.py` is an in-memory token
store.

- `store_token()` puts a `RecoveryToken` into a dictionary keyed by token hash.
- `find_token()` retrieves a token record by hash.
- `mark_token_used()` enforces single-use behavior by changing `used` to
  `True`.

Because this repository is in memory, all tokens disappear when the Python
process stops.

### 5.4 Rate limiting

`src/recovery_project/services/rate_limiter.py` implements an in-memory,
per-key lockout.

Each key, normally an email address, has an `AttemptBucket` containing:

- timestamps of recent failed attempts;
- an optional `locked_until` time.

`RateLimiter.record_failure()` removes old attempts, adds the new failure, and
locks the key when the configured maximum is reached.

`RateLimiter.is_locked()` returns `True` during lockout. Once the lockout time
has passed, it removes the old bucket.

`RateLimiter.record_success()` clears the bucket.

The module creates two global limiters:

- `validation_limiter`: 5 guesses per 60 seconds.
- `request_limiter`: 3 token requests per 60 seconds.

These are separate because repeatedly requesting reset emails and repeatedly
guessing tokens are different kinds of abuse.

### 5.5 Recovery orchestration

`src/recovery_project/services/recovery_service.py` connects token generation,
token storage, rate limiting, and password updates.

#### Issuing a token

`issue_token(email)`:

1. Checks `request_limiter`.
2. Generates a raw token and SHA-256 hash.
3. Creates a token record with a 300-second expiration.
4. Stores the record under its hash.
5. Records the request for rate-limiting purposes.
6. Prints the raw token for the demo and returns it.

The token record uses the email as `user_id`, so the token is bound to one
account.

#### Validating a token

`validate_token(email, provided_token)`:

1. Rejects the attempt if the email is locked.
2. Hashes the provided token.
3. Looks up the hash in the token repository.
4. Checks that the token belongs to the email.
5. Rejects tokens that were already used.
6. Rejects expired tokens.
7. Marks a valid token as used.
8. Clears previous validation failures.

Every invalid case records a failed attempt.

#### Resetting the password

`reset_password(email, new_password)` delegates to
`auth_service.update_password()`.

Token validation and password reset are separate calls. The UI is responsible
for calling reset only after successful validation.

## 6. Complete Streamlit demo flow

### Entry point

`src/recovery_project/ui/streamlit_app.py`:

1. Configures the Streamlit page.
2. Initializes values in `st.session_state`.
3. Loads `UI_design.css`.
4. Renders the left animation panel and right interaction panel.

Run it with:

```bash
streamlit run src/recovery_project/ui/streamlit_app.py
```

### UI files

- `Panels.py` creates the two-column layout and selects Sign in, Register,
  Recovery flow, or Experiments.
- `Register_tab.py` validates the email and calls `register_user()`.
- `Signin_tab.py` calls `login_user()` and records the current user in
  Streamlit session state.
- `Recovery_tab.py` implements the three-step recovery state machine.
- `Recovery_helper.py` changes recovery steps, clears state, and renders the
  demo token.
- `User_details_helper.py` provides the shared email/password form.
- `Experiments_tab.py` displays experiment controls, but currently calculates
  only a simple probability estimate.
- `Fragment_handler.py` provides compatibility helpers for Streamlit fragment
  reruns.
- `robot.py` loads and cleans the Lottie animation in `cute_robot.json`.
- `UI_design.css` contains the visual styling.

### Recovery state machine

```text
Step 1: enter registered email
    |
    +--> issue_token(email)
    |
Step 2: enter token
    |
    +--> validate_token(email, token)
    |
Step 3: enter and confirm new password
    |
    +--> reset_password(email, new_password)
```

The UI prevents moving to step 3 unless `token_verified` is true. After a
successful reset, it clears login and recovery state.

## 7. Attack simulations

### 7.1 Exhaustive brute force

`src/recovery_project/simulation/bruteforce.py` contains the worker functions:

- `split_string()` divides an alphabet into chunks.
- `guess_parallel()` assigns each worker a group of possible first
  characters, generates every suffix with `itertools.product()`, and sets a
  shared event when it finds the token.

`src/recovery_project/simulation/attacker.py` wraps those functions in
`Attacker.send_attack()`. It starts one process per alphabet chunk, waits for
all processes, and returns elapsed milliseconds.

This path is used by the RQ1 entropy runner.

### 7.2 Expiration-window attack

`src/recovery_project/simulation/exp_window_attack.py` contains
`ExpirationWindowAttacker`.

The attacker generates random candidate tokens and compares their SHA-256
hashes with the target hash.

`attack()` selects one of two modes:

- If `attack_rate_per_second` is provided, `_rate_bounded_attack()` runs a
  single-process wall-clock loop until the TTL expires or the token is found.
- Otherwise, `_worker_loop()` runs random guessing in multiple processes,
  stopping on success, TTL expiration, or each worker's attempt budget.

The returned dictionary contains:

- `success`
- `found_token`
- `attempts`
- `time_elapsed`
- `attempts_per_second`

### 7.3 Rate-limited attack

`src/recovery_project/experiments/rq3_experiment.py` implements separate
sequential random and exhaustive attacks that call `RateLimiter` after each
failed guess.

For each trial it:

1. Generates a token.
2. Uses a new email/key so trials do not share lockout state.
3. Guesses until success or lockout.
4. converts the result into `TrialResult` data.
5. writes separate CSV files for exhaustive and random strategies.

`src/recovery_project/simulation/legitimate_user.py` is currently only a
placeholder. It is intended to measure false blocks or usability impact on
real users.

## 8. Experiment configuration and runners

### Configuration models

`src/recovery_project/config.py` defines:

- `TokenPolicy`: length, alphabet, TTL, and single-use flag.
- `RateLimitPolicy`: enabled flag, maximum attempts, and time window.
- `ExperimentConfig`: experiment name, trial count, attack budget/rate, and
  both policies.

`load_experiment_config()` currently reads one YAML configuration.

### Generic YAML experiment path

```text
YAML config
    |
    +--> load_experiment_config()
    |
    +--> ExperimentRunner.run()
            |
            +--> scripts/run_experiment.py:run_trial()
                    |
                    +--> TokenService.generate_token()
                    +--> ExpirationWindowAttacker.attack()
                    +--> TrialResult
    |
    +--> save_results()
    +--> compute_summary()
```

`src/recovery_project/experiments/runner.py` is intentionally generic. It
repeats a supplied `run_trial` function and collects its `TrialResult` values.

`src/recovery_project/experiments/__init__.py` is the package marker. It has no
runtime logic.

`src/recovery_project/experiments/metrics.py`:

- saves trial results to a timestamped CSV;
- calculates success rate, attempts, timing, blocked attempts, and expiration
  summary values;
- prints the summary to the terminal.

Example:

```bash
python scripts/run_experiment.py configs/experiments/rq2_expiration.yaml \
  --output-dir data/raw
```

### Other experiment entry points

- `src/recovery_project/experiments/etropy_runner.py` reads the RQ1 JSON file,
  generates tokens, and measures exhaustive brute-force time. The filename
  currently contains the typo `etropy`.
- `scripts/run_rq2_experiments.py` reads a JSON list of RQ2 experiments and
  writes one CSV per experiment.
- `src/recovery_project/experiments/rq3_experiment.py` reads RQ3 JSON and runs
  rate-limited attacks.

### Configuration files

- `rq1_entropy.yaml`: one RQ1 baseline for the generic runner.
- `rq1_entropy.json`: multiple RQ1 cases for `etropy_runner.py`.
- `rq2_expiration*.yaml`: individual RQ2 scenarios for the generic runner.
- `rq2_expiration_window_attack.json`: a large RQ2 experiment matrix for
  `run_rq2_experiments.py`.
- `rq3_rate_limit.yaml`: one RQ3 baseline in the generic format.
- `rq3_rate_limiting.json`: random and exhaustive RQ3 cases.

JSON and YAML are not interchangeable in the current entry points. Check which
loader a script uses before running it.

## 9. Data-processing and utility scripts

- `scripts/summarize_data.py` reads RQ2 CSV files from
  `data/raw/expiration/`, extracts token length and TTL from filenames, and
  combines them into `data/processed/rq2_summarized_data.csv`.
- `scripts/capture_hardware.py` records CPU, core count, RAM, and operating
  system so results from different machines can be compared.
- `scripts/run_ui.py` prints the Streamlit launch command.
- `scripts/generate_plots.py` is currently a placeholder.
- `src/recovery_project/utils/logging.py` creates consistently formatted,
  idempotent console loggers.
- `src/recovery_project/main.py` is a placeholder package entry point.

Generated outputs are organized under:

- `data/raw/`: individual experiment CSV files.
- `data/processed/`: combined or cleaned datasets.
- `results/`: figures, tables, and report-ready outputs.

## 10. Tests

### `tests/unit/test_smoke.py`

Checks that default token and rate-limit configuration values are positive.

### `tests/unit/test_bruteforce_attack.py`

Checks alphabet chunking and whether `guess_parallel()` correctly signals
success or failure.

### `tests/unit/test_expiration_window_attack.py`

Describes the expected contract for a rate-bounded attack:

- attempts should be limited by `TTL * attack rate`;
- a smaller explicit attempt budget should stop the attack earlier;
- reported elapsed time and attempts per second should match those limits.

The current wall-clock implementation does not yet satisfy that contract; see
the known gaps below.

### `tests/unit/test_rate_limiter.py`

Resets global recovery state before every test, then checks:

- repeated bad guesses lock an account;
- a locked account rejects even the correct token;
- success clears previous failures;
- a token works only for its own email;
- old failures leave the active time window;
- repeated reset-token requests are limited.

Run the test suite with:

```bash
pytest
```

## 11. Security properties currently implemented

- Passwords use salted PBKDF2 hashes.
- Tokens use `secrets.choice()` for generation.
- Only the token hash is stored in the token repository.
- Tokens are bound to an account email.
- Tokens expire after a TTL.
- Tokens become unusable after successful validation.
- Validation failures and token requests are rate-limited.
- Password-hash verification uses constant-time comparison.

## 12. Current gaps and important limitations

These points describe the code as it exists now:

1. `recovery_service.issue_token()` hardcodes the token TTL to 300 seconds.
   UI controls and experiment configuration do not change this demo TTL.
2. The demo `TokenService` uses its default 10-character alphanumeric policy,
   while several configs use hexadecimal tokens of other lengths.
3. `TokenService.verify_token()` uses normal string equality for hashes rather
   than `hmac.compare_digest()`.
4. The rate-bounded expiration attacker currently ignores
   `max_attempts_budget` and does not pace guesses to
   `attack_rate_per_second`. It runs as fast as possible until real TTL time
   passes.
5. The multiprocessing expiration attacker assumes
   `max_attempts_budget` is not `None` and drops any remainder when dividing
   the budget among workers.
6. The Experiment UI is a demo estimate and is not connected to the real
   experiment runners.
7. `RateLimitPolicy.enabled` is recorded by the generic experiment runner, but
   `scripts/run_experiment.py` does not apply a rate limiter to its attacker.
8. User data is file-based, while token and rate-limit data are in memory.
   Restarting the app keeps users but removes active tokens and lockouts.
9. The UI identifies a login through Streamlit session state only. There is no
   server-side session repository or session revocation.
10. The recovery request UI reveals whether an email exists. A production
    system should return the same generic response for existing and unknown
    accounts.
11. The raw recovery token is printed and shown in the demo. This is useful
    for testing but should be replaced by email delivery in a real system.
12. `single_use` exists in configuration, but the demo always enforces
    single-use and experiment attackers do not use that setting.
13. `RecoveryAttempt` and `legitimate_user.py` are not integrated into current
    experiment execution.
14. Plot generation and the package `main.py` entry point are placeholders.

## 13. Short mental model

When explaining the project to someone else, use this summary:

1. A token policy defines the possible token space and expiration time.
2. `TokenService` creates a random token and its hash.
3. The demo stores the hash, not the raw token.
4. The recovery service checks ownership, expiration, single use, and rate
   limits.
5. Attack simulations repeatedly generate guesses and measure whether they
   find the token before their stopping condition.
6. Experiment runners repeat attacks under different policies.
7. `TrialResult` and CSV files preserve measurements for analysis.
