# `apps.accounts` — User, OTP, KYC, 2FA, Auth

User identity, phone-OTP authentication, KYC, TOTP-based 2FA, and JWT
cookie sessions live here.

## Models

| Model | Purpose |
|-------|---------|
| `User` | Custom user. `phone` is `USERNAME_FIELD`. PII columns (`national_id`, `iban`) are stored encrypted-at-rest via `EncryptedCharField`; their SHA-256 hashes (`national_id_hash`, `iban_hash`) live alongside for lookups. Carries roadmap seams: `tier`, `referred_by`, `share_trades`, `tenant_id`. |
| `OTPCode` | Argon2-hashed 6-digit code with TTL, attempts and `purpose` (`login` / `withdraw` / `transfer` / `change_iban`). |
| `KYCSubmission` | Mandatory + optional documents; state machine `kyc` controls progression. |

## Services

* `services/otp.py` — `request_otp(phone, purpose)`, `verify_otp(phone, code, purpose)`. Plaintext code is never returned; delivery is via Kavenegar SMS.
* `services/kyc.py` — `submit_kyc(...)`, `start_review(...)`, `approve(...)`, `reject(...)`. All advance the `kyc` SM.
* `services/totp.py` — RFC 6238 TOTP (30 s, 6 digits, SHA-1, ±1 step) for 2FA. `provisioning_uri()` builds the `otpauth://` link.

## Auth

`apps.accounts.auth.CookieJWTAuthentication` reads the JWT from the
HttpOnly cookie `keyhan_access`; falls back to the `Authorization` header.
Refresh cookie is `keyhan_refresh`. Tokens are signed with **Ed25519**.

Permissions (`apps.accounts.permissions`):
* `IsKYCVerified` — must be `is_verified and not is_frozen`.
* `IsAdminRole` — `is_staff`.
* `IsVendor` — `is_vendor`.

## Key endpoints

```
POST /api/v1/auth/otp/request   ← send SMS
POST /api/v1/auth/otp/verify    ← exchange for JWT cookies
POST /api/v1/auth/logout
GET  /api/v1/me                  PATCH /api/v1/me
GET  /api/v1/kyc                 POST /api/v1/kyc (multipart)
POST /api/v1/me/2fa/{enroll,confirm,disable}
POST /api/v1/admin/kyc/<id>/{approve,reject}
```

## Events emitted

`accounts.otp.requested / delivered / verified / rejected`,
`accounts.user.registered`, `accounts.session.opened / refreshed / revoked`,
`accounts.user.frozen`, `kyc.submitted / approved / rejected / requires_more`,
`kyc.flag.aml`, `security.login.brute_force`.

## CI gates

* Catalogue ensures each event kind above is registered.
* `apps.audit.state_machine.kyc_sm` declares the only legal KYC paths;
  test in `tests/test_state_machines.py`.
