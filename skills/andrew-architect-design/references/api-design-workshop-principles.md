# API Design Workshop Principles

This reference distills the current skill draft from Andrew's article:

- Source article: `docs/_posts/2023/2023-01-01-api-design-workshop.md`
- Current scope: state-machine-driven API design and scenario mapping

## Core Principles

- Start API design from the domain object's lifecycle, not from CRUD endpoints.
- Use a state machine to discover the allowed states and transitions of the primary subject.
- Infer the operations from the transitions, then separate state-changing and non-state-changing actions.
- Infer actors and target systems from who triggers or consumes each action.
- Infer authorization from actor, role, scope, and operation relationships.
- Infer events from state changes and action execution boundaries.
- Use scenario mapping to validate feasibility before writing detailed spec files.
- Translate the analyzed design into entity, action, authorize, and event contracts.

## Derived Workflow

### State Machine

- Pick the primary subject or entity.
- Draw the lifecycle states, including conceptual start or end states when useful.
- Mark transitions with the actions that cause them.
- Add self-loop actions for allowed reads or behaviors that do not change state.

### Actor And Target Mapping

- Mark which actor can trigger each action.
- Mark which external or internal systems call, observe, or consume the outputs.
- Identify where masked data, full data, or system-only operations are required.

### Contract Extraction

- Define entity shape from the subject's essential data.
- Define action surface from the allowed operations.
- Define authorization surface from roles and scopes.
- Define event types and payload shape from transitions and action execution.

### Scenario Mapping

- Convert each story into steps with caller, action, start state, final state, target system, and follow-on event or data need.
- Walk the steps over the state machine one by one.
- Fail the design immediately if the story needs an operation, actor, or transition that does not exist in the model.

## Article-Specific Warnings

- Do not let callers set state arbitrarily through CRUD-style updates when the lifecycle must be controlled.
- Do not design convenience endpoints that violate the underlying state-machine semantics.
- Do not leave authorization until after endpoints exist. Actor and scope mapping should follow directly from the model.
- Do not wait for final OpenAPI or AsyncAPI files before checking whether real stories can traverse the design.
