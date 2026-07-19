---
name: andrew-security-permission-design
description: "Design Andrew-style authentication, authorization, permission, and trust-boundary mechanisms for applications and APIs. Use when Codex needs security-by-design thinking, token or key-based trust models, permission-system architecture, RBAC or policy design, anti-replay and signature choices, multi-tenant authorization boundaries, or operational enforcement and audit considerations."
---

# Andrew Security Permission Design

## Overview

Use this skill when the problem is about who can be trusted, who can do what, what evidence proves it, and where that decision must be enforced.

Treat security as a design-quality problem, not as a bolt-on feature. Start from business risk and trust boundaries, then separate authentication, authorization, access control, and audit clearly. Prefer standard cryptographic and authorization models over clever custom mechanisms.

## Working Style

- Write in Traditional Chinese when the user or repo context is Chinese.
- Treat security requirements as product quality requirements, not optional implementation detail.
- Start from threat model and trust boundary before selecting libraries or protocols.
- Separate clearly:
  - authentication
  - authorization
  - access control
  - audit
- Prefer standard, proven cryptographic mechanisms and frameworks over custom crypto.
- Protect secrets and keys; assume code and algorithms may be visible.
- Design security control points so developers can use them consistently with low friction.
- Prefer centralized or reusable enforcement over one-off checks scattered through pages or handlers.
- Treat multi-tenant and third-party integration scenarios as first-class security cases.
- Make enforcement explicit at API, service, and data boundaries.

## Workflow

### 1. Problem Analysis

- State what must be protected:
  - identity
  - money-like value
  - personal data
  - business data
  - service capability
  - licensed feature
- Define the threat boundary:
  - trusted server
  - untrusted client
  - partner system
  - third-party integrator
  - tenant boundary
  - offline or closed-network environment
- Identify what can realistically be stolen, replayed, tampered with, or overused.
- Distinguish feature requirement from quality requirement. Security usually belongs to quality and must survive hostile conditions, not only happy-path tests.
- Clarify whether the main problem is:
  - proving identity
  - proving source integrity
  - limiting capability
  - scoping data access
  - preventing replay
  - simplifying permission management

### 2. Trust Boundary And Threat Model

- Map who trusts whom and on what evidence.
- Decide which parties can be fully trusted, partially trusted, or not trusted at all.
- Model offline verification separately from online verification.
- Distinguish integrity, confidentiality, authenticity, and authorization; do not solve one and assume the others are solved too.
- Assume anything delivered to client side or partner-controlled infrastructure is inspectable and potentially replayable.
- If code can be copied or modified, account for that instead of assuming license or token logic alone is enough.

### 3. Identity And Authentication

- Define what identifies the subject:
  - user
  - service
  - device
  - tenant
  - partner application
- Define how that identity is authenticated.
- Keep authentication output explicit as a principal or equivalent identity object.
- Record authentication strength and source when they matter to later decisions.
- Reuse framework identity abstractions when they fit, instead of inventing new ones without need.
- For service-to-service trust, decide whether signed tokens, mutual trust anchors, or online verification is the primary mechanism.

### 4. Authorization Model

- Define the minimal authorization question clearly:
  - who is requesting
  - what action is requested
  - on what scope or resource
  - under what policy or environment
- Choose the management model that matches the problem:
  - role-based
  - permission-based
  - policy-based
  - attribute-based
  - access-control-list
  - contract or entitlement based
- Treat permissions as business-facing capability boundaries, not only code-level toggles.
- Group permissions deliberately to balance management cost and precision.
- Distinguish action permission from data-scope permission.
- Separate subject, role, permission, session, and operation in the model even if some layers collapse in implementation.
- For third-party delegation, model intention and delegation scope explicitly instead of pretending every caller is the same first-party actor.

### 5. Token, Key, And Credential Design

- Decide whether the token or credential is proving:
  - identity
  - integrity
  - entitlement
  - expiry
  - execution scope
- Prefer signed tokens when the core need is authenticity and integrity rather than secrecy.
- Use hashes for password verification; do not store raw passwords.
- Distinguish signature use from encryption use.
- Include only the claims needed for downstream decisions.
- Add replay defenses when a stolen valid token would still be dangerous:
  - short expiry
  - client binding
  - device binding
  - nonce
  - server-side revocation or usage tracking
- Protect private keys aggressively.
- Decide how public keys or trust roots are distributed and updated.
- If offline verification is required, design for local verification of integrity and expiry.
- If key substitution is possible, account for trust-anchor protection, not only token format correctness.

### 6. Enforcement Boundaries

- Place enforcement where the resource is actually exposed:
  - page or UI
  - API endpoint
  - service method
  - message handler
  - query boundary
  - data filter
- Do not rely on menus or UI visibility alone.
- Prefer enforcing once at a shared boundary instead of repeating ad hoc checks.
- Keep identity extraction, permission lookup, and decision logic reusable.
- Ensure the same permission rule cannot be bypassed through an alternate entry path.
- For APIs, define method-level, scope-level, and environment-level control points separately when needed.
- For multi-tenant systems, ensure tenant scoping is safe by default.

### 7. Permission Management And Scaling

- Evaluate permission design on two axes:
  - management complexity
  - decision precision
- Avoid designs that are perfectly precise but operationally impossible to maintain.
- Avoid designs that are easy to manage but cannot express critical business boundaries.
- Cache or precompute permission sets when repeated high-frequency checks would otherwise explode combinatorially.
- Prefer session-context plus module-context or equivalent coarse-grained decision surfaces when per-action checks are too expensive.
- Use groups, roles, or policy composition to reduce management load deliberately.
- Keep the permission-definition model stable enough that new features do not require redesigning the whole matrix.

### 8. Operational Controls And Audit

- Design for key rotation, token expiry, revocation, and incident response.
- Log enough evidence to answer:
  - who acted
  - what was attempted
  - what was allowed or denied
  - what scope was involved
  - what credential or policy version was used
- Define how administrators manage permissions without accidentally granting excessive power.
- Consider rate limit, source restriction, and environment checks when they materially reduce risk.
- Treat secret storage, trust-root distribution, and deployment updates as part of the architecture.
- If the system must work offline, define what validation still works and what must fail closed.

### 9. POC And Evaluation

- Build the smallest validation slice that proves the security model, not just the happy path.
- Test hostile or misuse scenarios:
  - tampered token
  - expired token
  - replayed token
  - wrong tenant
  - alternate entry path
  - delegated third party exceeding scope
  - replaced or untrusted public key
- Validate both correctness and operational usability.
- Compare candidate models by:
  - expressiveness
  - management cost
  - developer friction
  - runtime cost
  - blast radius of mistakes
- Prefer the model that removes whole classes of mistakes rather than one that depends on every developer remembering every check.

## Design Checks

- Revisit the design if authentication and authorization are being treated as the same thing.
- Revisit the design if security depends on hiding a custom algorithm.
- Revisit the design if private-key protection is vague or hand-waved.
- Revisit the design if a valid token can be replayed freely and that still causes damage.
- Revisit the design if permission checks exist only in UI or menu code.
- Revisit the design if the same data can be reached through two paths with inconsistent permission behavior.
- Revisit the design if tenant isolation depends on every caller remembering the right filter.
- Revisit the permission model if management complexity is exploding faster than feature count.
- Revisit the caching strategy if permission checks are too frequent and too granular to scale.
- Revisit the ops model if you cannot rotate keys, audit decisions, or revoke compromised credentials cleanly.

## Default Output Shape

When the user asks for security or permission design, respond in this order unless they request another structure:

1. Problem Analysis
2. Trust Boundary And Threat Model
3. Identity And Authentication
4. Authorization Model
5. Token, Key, And Credential Design
6. Enforcement Boundaries
7. Permission Management And Scaling
8. Operational Controls And Audit
9. POC
10. Evaluation
11. Risks And Refactor Triggers

Use these expectations for each section:

- Problem Analysis: define what is protected, the hostile scenarios, and the key quality requirement.
- Trust Boundary And Threat Model: define who is trusted, what is untrusted, and what attacks or misuse matter.
- Identity And Authentication: define subject types and how identity is established.
- Authorization Model: define subject, role, permission, policy, scope, and delegation shape.
- Token, Key, And Credential Design: define token contents, signing or hashing approach, expiry, replay defense, and key distribution.
- Enforcement Boundaries: define where decisions are enforced and how alternate paths are covered.
- Permission Management And Scaling: define management structure, caching or grouping strategy, and precision-vs-cost tradeoff.
- Operational Controls And Audit: define rotation, revocation, logging, and admin operations.
- POC: propose hostile-path validation, not only normal-path checks.
- Evaluation: compare options and state why one model should be adopted.
- Risks And Refactor Triggers: name assumptions that would invalidate the current model later.

## References

- Read `references/credential-and-signature-principles.md` when the task involves license tokens, API tokens, signatures, key management, replay defense, or offline trust verification.
- Read `references/security-by-design-principles.md` when the task is about security as a quality requirement, framework choice, or why standard mechanisms beat custom shortcuts.
- Read `references/api-security-model-principles.md` when the task is about public APIs, multi-tenant authorization, partner access, or choosing control dimensions for API security.
- Read `references/permission-model-principles.md` when the task is about RBAC, permission systems, policy design, management complexity, caching, or application-level authorization interfaces.
- Keep article-specific notes in `references/`.
- Promote only stable cross-article guidance back into this `SKILL.md`.
