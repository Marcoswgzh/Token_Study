# Authentication and Recovery Architecture

## 1) What we are building

Simple architecture to demonstrate weaknesses in recovery systems for password resetting.
The project consists of 2 parts:
- demo application -> GUI that the user can interact with and see the results in real time
- runnable experiments -> series of trials (configurations written in .json files) to get accurate results for analysis

## 2) Main decision

We will follow this recovery pipline logic:
- user clicks **Forgot password**
- user enters email
- system sends a reset link with token in URL
- user opens link and sets a new password

With this, the backend will behave very similar to real-world applications,
while keeping the frontend simple and user-friendly for experiment demonstration purposes.

## 3) Architecture layers

1. `UI` (`src/recovery_project/ui/`)
- Register page
- Sign in page
- Recovery request page (email input)
- Reset page (`/reset-password?token=...`)
- Experiment page

2. `Services` (`src/recovery_project/services/`)
- `auth_service` for sessions/logout
- `password_service` for password handling
- `email-verifier` for simple verifying of the email validity
- `token_service` for secure token generation/check
- `recovery_service` for full recovery workflow
- `rate_limiter` for brute-force protection

3. `Repositories` (`src/recovery_project/repositories/`)
- users, tokens
- in-memory storage -> simple txt file 

4. `Experiments` (`src/recovery_project/experiments/`, `configs/experiments`)
- run scenarios for complexity, TTL, rate limiting, and connecting class for experiments from gui
- export metrics for report/poster

5. `Attack Algorithms` (`src/recovery_project/attacker_algorithms/`)
- 2 classes for attack algorithms -> 1 parallelized, 2 sequential algorithms
- for comparison as well as different experiments require different approach

## 4) Recovery flow we will implement

### Step 1: request token
`POST /auth/recovery/request`
- input: email
- response should be generic in all cases (avoid account enumeration)
- if email exists, create token and send reset link

### Step 2: validate token from URL
UI reads `token` from URL and calls:
`GET /auth/recovery/validate?token=...`

- if token is valid, show password reset form
- if token is invalid/expired/used, show error
- backend checks:
  - token hash matches
  - token not expired
  - token not already used
  - optional rate-limit check

### Step 3: reset password
`POST /auth/recovery/reset`
- input: old + new password
- on success:
  - update password hash
  - revoke active sessions

## 5) Minimal data model

`users`
- `id`, `email`, `password_hash`, `created_at`

`recovery_tokens`
- `id`, `user_id`
- `token_hash` (only hash, never raw token)
- `issued_at`, `expires_at`, `used_at`
- `request_ip`, `request_user_agent`

`recovery_attempts`
- `id`, `user_id` (nullable)
- `attempted_at`
- `result` (`success`, `invalid`, `expired`, `blocked_rate_limit`)
- `source_ip`

`sessions` (recommended)
- `id`, `user_id`, `created_at`, `revoked_at`

## 6) RQs experiments set up

1. **RQ1 (complexity)**  
Testing different lengths of token on 2 different alphabets.
Comparing all 3 algorithms.

2. **RQ2 (expiration)**  
Testing different lengths of token and token TTL on 2 different alphabets.
Comparing all 3 algorithms.

3. **RQ3 (rate limiting)**  
Testing different realistic limits/windows for legitimate users with different token lengths on 2 different alphabets.
Comparing 2 sequential algorithms only.
