# API FSM Implementation Principles

This reference supplements the existing API-first and API workshop material with implementation-oriented viewpoints from Andrew's article:

- Source article: `docs/_posts/2022/2022-04-25-microservices16-api-implement.md`
- Current scope: translating FSM-driven API design into layered implementation and PoC validation

## Core Principles

- Validate the architecture with a runnable PoC or MVP. Prove the design can do the right thing before investing in doing things right.
- Design the service for the internal domain and collaborating systems, not as a direct mirror of one UI or screen flow.
- Keep the public API surface minimal. Not every caller convenience deserves a new endpoint in the core contract.
- Separate stable contracts from core implementation and from transport adapters. Contracts define the promise; core implements it; adapters expose it over HTTP, CLI, or other protocols.
- Keep controllers and protocol handlers thin. Domain behavior, lifecycle rules, and most authorization logic should live in reusable core services.
- Model security as three related but distinct concerns: authentication, authorization, and access control.
- Let tokens or equivalent request context carry identity data, and let the FSM or policy layer decide whether that identity may execute a given action.
- Centralize token parsing, action discovery, and cross-cutting authorization or FSM checks in middleware or similar interception layers when the framework allows it.
- Treat request tracking and correlation as part of adapter design too, not only as logic hidden inside the domain service.

## Derived Workflow

### Layering

- Use a contracts layer for shared interfaces and models that require compatibility discipline.
- Use a core layer for domain objects, lifecycle logic, policy checks, and reusable implementation.
- Use adapter layers such as WebAPI or CLI only to translate transport-specific concerns into the core contract.
- Use tests to validate the contracts and core behavior independently from transport concerns.

### PoC Strategy

- Validate the core behavior first with unit tests, CLI flows, or in-memory execution before adding the full HTTP surface.
- Simplify repository and persistence concerns aggressively in the PoC when they are not the design focus.
- Use in-memory repositories, import/export files, locks, or optimistic concurrency only as much as needed to validate the contract and lifecycle behavior.

### Security And Execution

- Decide what identity information must travel with each request and where it will be injected into execution scope.
- Extend FSM or policy entries with allowed identity types, roles, or scopes when that is the simplest accurate model.
- Accept that HTTP endpoints and core service methods are not always one-to-one. Allow adapters to compose or reshape calls while preserving core semantics.

## Article-Specific Warnings

- Do not let API growth become ad hoc feature-by-feature endpoint sprawl.
- Do not assume a microservice can skip layering, compatibility discipline, or security design just because it is smaller in scope.
- Do not bury all observability inside core code; request-level tracing often belongs in the transport layer too.
- Do not treat breaking contract changes as cheap once other teams have started to build on the API.
