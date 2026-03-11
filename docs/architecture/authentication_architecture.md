# Authentication and Recovery Architecture

## 1) What we are building

This is a university cybersecurity project.  
Our main goal is to test **how secure password recovery is** under different settings.

We are not trying to copy Instagram or any full production system 1:1.  
Instead, we keep the flow realistic, but simple enough to control in experiments.

## 2) Main decision (after team discussion)

We will use this recovery logic:
- user clicks **Forgot password**
- user enters email
- system sends a reset link with token in URL
- user opens link and sets a new password

So the backend behavior is close to real platforms, but the UI can stay simpler.

## 3) Architecture layers

1. `UI` (`src/recovery_project/ui/`)
- Sign in page
- Recovery request page (email input)
- Reset page (`/reset-password?token=...`)

2. `API` (`src/recovery_project/api/`)
- Login/logout routes
- Recovery routes (request, validate, reset)

3. `Services` (`src/recovery_project/services/`)
- `auth_service` for sessions/logout
- `token_service` for secure token generation/check
- `recovery_service` for full recovery workflow
- `rate_limiter` for brute-force protection

4. `Repositories` (`src/recovery_project/repositories/`)
- users, tokens, attempts, sessions
- start with in-memory storage, then optional DB adapter

5. `Experiments` (`src/recovery_project/experiments/`, `configs/experiments/`)
- run scenarios for entropy, TTL, and rate limiting
- export metrics for report/poster

## 4) Recovery flow we will implement

### Step 1: request token
`POST /auth/recovery/request`
- input: email
- response should be generic in all cases (avoid account enumeration)
- if email exists, create token and send reset link

Example link:
`https://app.local/reset-password?token=<token>`

### Step 2: validate token from URL
UI reads `token` from URL and calls:
`GET /auth/recovery/validate?token=...`

- if token is valid, show password reset form
- if token is invalid/expired/used, show error

### Step 3: reset password
`POST /auth/recovery/reset`
- input: token + new password
- backend checks:
  - token hash matches
  - token not expired
  - token not already used
  - optional rate-limit check
- on success:
  - update password hash
  - mark token as used
  - revoke active sessions (recommended)

## 5) Minimal API list

1. `POST /auth/login`
2. `POST /auth/logout`
3. `POST /auth/recovery/request`
4. `GET /auth/recovery/validate?token=...`
5. `POST /auth/recovery/reset`

## 6) Minimal data model

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

## 7) Security rules

1. Generate tokens with CSPRNG only.
2. Store only token hash in backend.
3. Compare token values in constant time.
4. Enforce single-use tokens.
5. Check TTL using server time.
6. Add rate limit on request/validate/reset endpoints.
7. Keep CSRF config compatible with frontend routes, especially for logout.

## 8) How this maps to RQ1-RQ3

1. **RQ1 (entropy)**  
Change token length/alphabet, keep others fixed.

2. **RQ2 (expiration)**  
Change token TTL, keep entropy and attack rate fixed.

3. **RQ3 (rate limiting)**  
Change limits/windows and measure:
- attacker success drop
- impact on legitimate users

## 9) Why this is good for our project

- It follows the real recovery idea used by big platforms.
- It stays small enough for fast implementation and testing.
- It directly supports our research questions and experiment configs.
