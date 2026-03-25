# API FSM Consistency Principles

This reference supplements the existing API design workshop material with extra viewpoints from Andrew's article:

- Source article: `docs/_posts/2022/2022-03-25-microservices15-api-design.md`
- Current scope: API structural consistency and FSM-to-code alignment

## Core Principles

- Evaluate API quality in this order: structural clarity and consistency first, style and conventions second, runtime quality third.
- Use one state machine as the shared design map for naming, rules, states, actions, events, and authorization.
- Prefer action-oriented API surfaces over CRUD-style updates when the domain has a meaningful lifecycle.
- Distinguish true lifecycle state from ordinary properties or flags. Only keep the states that are essential to the business transition model.
- Treat undefined combinations of current state and action as invalid by design. Do not rely on scattered `if` statements to reconstruct the rules later.
- Keep the design accessible enough that PM, SA, and engineers can reason over the same FSM artifact when the domain is not too complex.

## Derived Workflow

### Structural Review

- Confirm the primary subject stays stable across endpoint naming, action naming, event naming, and permission rules.
- Use the FSM as the first place to look for structural contradictions between behavior and access rules.

### State Selection

- Start with the lifecycle states that decide what operations are legal.
- Push non-core dimensions such as levels, badges, or toggle-like properties out of the FSM unless their transitions are central to the domain.
- Add conceptual `START` or `END` states when they make lifecycle boundaries easier to reason about.

### FSM To Code

- Model the executable FSM either as a lookup table or as a transition list.
- Ensure the state-machine interface can answer at least two questions: can this action run from the current state, and what state should result if it does.
- Keep the design artifact and the executable mapping aligned closely enough that changing the FSM implies changing code and tests deliberately.

### Enforcement

- Use centralized enforcement when possible so transition legality is not reimplemented in every handler.
- Consider middleware, filters, or AOP-style interception when the framework can apply the same FSM checks consistently.
- Treat concurrency as part of the design. If the transition decision matters, define how racing requests will avoid double execution or invalid interleaving.

## Article-Specific Warnings

- Do not let CRUD semantics leak lifecycle control to callers when the service needs stronger business guarantees.
- Do not mix unrelated properties into the state model until the graph becomes unreadable and impossible to maintain.
- Do not split state, event, and authorization design into separate artifacts that can drift apart without detection.
- Do not validate transitions conceptually but ignore atomicity in the real execution path.
