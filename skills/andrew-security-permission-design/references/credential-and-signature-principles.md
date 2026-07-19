# Credential And Signature Principles

This reference distills Andrew's articles:

- Source article: `docs/_posts/2016/2016-02-17-casestudy_license_01_requirement.md`
- Source article: `docs/_posts/2016/2016-02-24-casestudy_license_02_serialization.md`
- Source article: `docs/_posts/2016/2016-02-24-casestudy_license_03_digital_signature.md`
- Source article: `docs/_posts/2016/2016-03-19-casestudy_license_03_appendix_key_management.md`
- Source article: `docs/_posts/2016/2016-12-01-microservice7-apitoken.md`

## Core Principles

- Separate readable payload from proof of authenticity. A token can be non-secret yet still require strong origin verification.
- Use digital signatures to prove source integrity; do not invent custom crypto to hide or scramble content.
- Prefer standard serialization and a stable token abstraction so new token types can reuse the same infrastructure.
- Put token-specific validation logic inside the token or equivalent domain object, but keep encoding, signing, and decoding centralized.
- Protect private keys aggressively; if private keys leak, signature-based trust collapses immediately.
- Public-key distribution is part of the design. If attackers can swap the trusted public key, token correctness alone is useless.
- Offline verification requires local trust anchors and local expiry or rule checks.
- Replay protection often needs extra binding beyond signature validity, such as client binding, device binding, or short expiry.
- Signed tokens are useful for both human-installed licensing and service-to-service trust.

## Derived Workflow

### Token Design

- Define the payload fields.
- Define validation rules such as expiry and subject binding.
- Keep token generation and verification APIs small and developer-friendly.

### Key Design

- Decide where private keys live.
- Decide how public keys or trust roots are delivered.
- Plan for trust-anchor tampering, not only token tampering.

### Replay Defense

- Identify whether stolen but valid tokens are still dangerous.
- Bind tokens to short-lived or caller-specific context when needed.

## Article-Specific Warnings

- Do not rely on secret algorithms.
- Do not leave key management as an afterthought.
- Do not assume signature validity alone prevents replay.
