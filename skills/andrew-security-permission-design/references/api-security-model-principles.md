# API Security Model Principles

This reference distills Andrew's article:

- Source article: `docs/_posts/2022/2022-07-15-microservices17-api-security-model.md`

## Core Principles

- API security must be designed from the integration surface, not inherited accidentally from UI-era assumptions.
- Choose the security model by the real scale and exposure shape:
  - single service
  - multi-service
  - public API
  - multi-tenant public API
- Model security dimensions explicitly:
  - domain method
  - scope
  - client environment
  - role
  - permission or token
  - delegated intention
- Different callers need different control models; first-party users, partner systems, and third-party contractors are not the same subject type.
- Abstract the security model enough that enforcement can later move from application code to gateway or proxy layers without redefining business meaning.
- Offloading checks to infrastructure is valid only after the security protocol and decision model are clear.

## Derived Workflow

### Surface Analysis

- List what APIs exist and how they cluster by risk and data sensitivity.
- Define who the callers are and what each caller category should never be allowed to access.

### Model Choice

- Choose the control model that matches the domain and exposure complexity.
- Distinguish design-time decisions from runtime authorization decisions.

### Enforcement Planning

- Decide what can live in middleware, gateway, or service code.
- Keep business meaning stable even if the enforcement layer changes later.

## Article-Specific Warnings

- Do not assume page-level security models transfer cleanly to API ecosystems.
- Do not pick a gateway product before you know the authorization semantics.
