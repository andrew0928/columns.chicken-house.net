# API State Machine Principles

This reference distills Andrew's articles:

- Source article: `docs/_posts/2022/2022-03-25-microservices15-api-design.md`
- Source article: `docs/_posts/2022/2022-04-25-microservices16-api-implement.md`
- Source article: `docs/_posts/2023/2023-01-01-api-design-workshop.md`

## Core Principles

- Start API design from the primary subject's lifecycle, not from CRUD habit.
- Use one state machine as the shared map for state, action, naming, event, and authorization.
- Infer operations from transitions, then separate state-changing and non-state-changing actions.
- Infer actors and target systems from who triggers or consumes each action.
- Infer authorization from actor, role, scope, and operation relationships.
- Distinguish true lifecycle state from ordinary properties or flags.
- Keep the API surface minimal; convenience composition can live outside the core contract.
- Separate contracts, core implementation, and transport adapters.
- Keep controllers or protocol handlers thin; lifecycle rules and most authorization logic belong in reusable core code.
- Use scenario mapping to validate feasibility before writing final spec files.

## Derived Workflow

### State Machine

- Pick the primary subject.
- Draw the lifecycle states.
- Mark transitions, read-only actions, actors, and events.

### Contract Extraction

- Define entity, action, authorize, and event surfaces from the state machine.
- Keep the transport shape aligned with the lifecycle model.

### Enforcement

- Centralize transition and authorization checks when the framework allows it.
- Treat concurrency as part of the design if transition legality matters.

## Article-Specific Warnings

- Do not let callers set state arbitrarily through generic updates.
- Do not split state, event, and authorization design into drifting artifacts.
- Do not validate transitions conceptually but ignore atomicity in the execution path.
