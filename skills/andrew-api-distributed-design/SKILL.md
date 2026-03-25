---
name: andrew-api-distributed-design
description: "Design Andrew-style API and distributed-system contracts from domain lifecycle, message flow, and correctness guarantees. Use when Codex needs state-machine-driven API design, contract-first or API-first planning, service-to-service messaging, retry and idempotency design, queue or scheduler workflows, worker isolation choices, or measurable validation of ordering, latency, and duplicate-execution tradeoffs."
---

# Andrew API Distributed Design

## Overview

Use this skill when the design surface crosses service boundaries, transport boundaries, or failure boundaries.

Start from the domain lifecycle and the exposed value, then derive both synchronous API contracts and asynchronous message contracts from the same model. Treat retry, duplication, delay, reordering, shutdown, and scale-out as part of the architecture, not as post-implementation surprises.

## Working Style

- Write in Traditional Chinese when the user or repo context is Chinese.
- Start from the domain object, lifecycle, and collaboration model before choosing endpoints, queues, or frameworks.
- Treat the API as the exposed form of a domain service, not as a mirror of one current UI flow.
- Keep one-way message, RPC message, HTTP API, and internal worker boundaries consistent with the same core model.
- Make actor, target system, identity, correlation, and delivery semantics explicit.
- Decide correctness boundaries up front: what must never happen twice, what may retry safely, and what may arrive late or out of order.
- Prefer the smallest coordination mechanism that is strong enough for the guarantee you need.
- Use storage-native atomic operations, transactions, or lock primitives before inventing your own coordination protocol.
- Keep transport adapters thin; let contracts, lifecycle rules, and policies live in reusable core code.
- Treat startup, shutdown, context propagation, observability, and autoscaling as first-class design concerns.

## Workflow

### 1. Problem Analysis

- Clarify why the contract exists and what value it exposes.
- Identify the consumers and collaborators:
  - human-facing clients
  - internal services
  - workers
  - schedulers
  - partner systems
- State the communication style required by the use case:
  - synchronous request/response
  - asynchronous one-way delivery
  - asynchronous RPC
  - scheduled execution
  - streaming or staged processing
- List the real failure model:
  - timeout
  - duplicate delivery
  - reordered delivery
  - lost reply
  - worker crash
  - shutdown during processing
  - delayed or corrected data
- Name the hard guarantee explicitly: exactly once, at least once, at most once, idempotent-safe retry, max delay, or bounded reordering.

### 2. Domain And Interaction Modeling

- Identify the primary subject, entity, or service whose lifecycle is being exposed.
- Model the domain using:
  - operation
  - state
  - actor
  - target system
  - event
- Distinguish occurrence time, receive time, and process time when interpretation depends on the difference.
- Separate core business state from ordinary properties or flags.
- Model major collaboration edges explicitly:
  - caller to service
  - service to queue
  - queue to worker
  - worker to storage
  - worker to result or reply channel

### 3. Contract Surfaces

- Translate the model into four surfaces:
  - entity
  - action
  - authorize
  - event
- Derive request and response shapes from domain semantics, not from screens.
- Keep the core API smaller than the full product surface when possible.
- Define message contracts separately from HTTP shape when the same domain action may travel over multiple transports.
- For message-driven RPC, define correlation, reply routing, and completion expectations explicitly.
- Propagate request or track context across boundaries so cross-service diagnosis remains possible.
- Keep message envelopes responsible for transport metadata and payloads responsible for domain meaning.

### 4. State Machine And Delivery Semantics

- Model lifecycle-driven APIs with a state machine first.
- Mark:
  - meaningful states
  - state-changing operations
  - read-only operations
  - allowed actors
  - follow-on events
- Use the state machine as the shared map for endpoint naming, action naming, event naming, and authorization.
- For every action or message, define delivery semantics explicitly:
  - may retry or not
  - idempotent by nature or requires a key
  - ordering scope
  - correlation id
  - dedupe key
  - ack point
- Treat undefined combinations of current state and action as invalid by design.

### 5. Correctness And Coordination

- Protect critical sections at the scope where contention actually exists.
- Choose coordination based on scope:
  - local lock for one process
  - database transaction for one durable transactional boundary
  - storage-native atomic operation for simple distributed counters or swaps
  - distributed lock only when shared critical sections truly cross instances
- Prefer atomic operations supplied by the platform or storage before composing them yourself.
- Design APIs to be naturally idempotent when possible.
- Use idempotency keys as an extra protection layer when natural idempotency is not enough.
- Ensure transition validation and state change are atomic enough for the failure model you accept.
- Distinguish:
  - safe retry
  - duplicate execution detection
  - duplicate execution tolerance
- When late or corrected data is normal, define how prior results are revised and where replay enters the system.

### 6. Worker And Runtime Topology

- Separate contracts, core implementation, and transport adapters.
- Abstract message senders and workers so business handlers do not own queue plumbing.
- Choose runtime isolation level deliberately:
  - in-process for lowest overhead
  - thread for concurrency without real isolation
  - process for stronger blast-radius control
  - container or infrastructure orchestration when the platform fit is good enough
- Compare isolation choices by startup cost, execution cost, blast radius, tech-stack freedom, and operational fit.
- Keep workers able to start, stop, drain, and shut down gracefully.
- Design scaling so Ops can change instance count without needing custom per-release manual fixes.

### 7. Scenario Mapping

- Start with one minimal happy path over the state machine.
- Then walk at least these stress scenarios:
  - retry after timeout with unknown result
  - duplicate message arrival
  - out-of-order arrival
  - worker restart during processing
  - scheduler race between instances
  - scale-out plus shutdown
- For each scenario, verify:
  - the transition exists
  - the actor is allowed
  - the delivery semantics are consistent
  - the result is sufficient for the next system
- If the same story needs one model for API docs and another model for workers, the design is not yet coherent.

### 8. Metrics

- Define metrics before tuning knobs such as worker count, polling frequency, lock lead time, or buffer size.
- Pick metrics that match the architecture shape:
  - request latency
  - queue delay
  - throughput
  - retry count
  - duplicate-execution count
  - lock acquisition failure
  - early-lock count
  - delay exceed count
  - reorder buffer usage
  - drop or skip count
  - work in progress
  - time to first result
  - time to last completion
  - average lead time
  - delay standard deviation
  - DB cost score or polling cost
- Mark which metrics are correctness gates and which are optimization targets.
- Use theory limits when the architecture behaves like a pipeline or staged worker system.

### 9. POC And Simulation

- Validate the architecture with the thinnest runnable model that can expose the guarantee and the tradeoff.
- Prefer validating core behavior outside HTTP first.
- Use mocks, in-memory repositories, or local queues when they preserve the design meaning.
- Simulate failure modes deliberately:
  - retry
  - duplicate delivery
  - delayed reply
  - out-of-order events
  - shutdown during work
  - multiple instances racing for the same job
- Use controllable time when delay windows, polling cadence, or scheduling precision matter.
- Run the same model across different parameter sets instead of arguing from intuition.

### 10. Evaluation

- Compare candidate designs against the chosen guarantee first, then secondary efficiency metrics.
- Prefer designs whose failure behavior is explicit and explainable.
- If one coordination mechanism is expensive, check whether the contract can be redesigned to need less coordination.
- If the bottleneck is a stage, optimize the bottleneck or change the topology, not just the surrounding code.
- If a custom mechanism only solves a narrow gap, keep the rest delegated to mature infrastructure.
- Name the assumptions that would force a redesign later.

## Design Checks

- Revisit the API if endpoints mirror screens instead of the domain lifecycle.
- Revisit the message design if correlation, ordering scope, or ack semantics are implicit.
- Revisit the state model if flags or properties are inflating the FSM.
- Revisit the correctness design if duplicate handling is described only as "the caller should avoid retry."
- Revisit the coordination design if you introduced distributed locks before checking storage-native atomic options.
- Revisit the worker model if graceful shutdown is impossible without manual cleanup.
- Revisit the topology if isolation requirements and runtime choice do not match.
- Revisit the scheduler or queue design if multiple instances can still execute the same job without a clear defense.
- Revisit the metrics if they cannot distinguish correctness failure from efficiency loss.
- Revisit the POC if it proves only the happy path and hides the real failure model.

## Default Output Shape

When the user asks for design, respond in this order unless they request another structure:

1. Problem Analysis
2. Domain And Interaction Modeling
3. Contract Surfaces
4. State Machine And Delivery Semantics
5. Correctness And Coordination
6. Worker And Runtime Topology
7. Scenario Mapping
8. Metrics
9. POC
10. Evaluation
11. Risks And Refactor Triggers

Use these expectations for each section:

- Problem Analysis: define the business value, consumers, failure model, and hard guarantee.
- Domain And Interaction Modeling: define the primary subject, states, actors, target systems, and time semantics.
- Contract Surfaces: define entities, actions, authorization shape, events, and transport metadata boundaries.
- State Machine And Delivery Semantics: define legal transitions plus retry, ordering, dedupe, correlation, and ack behavior.
- Correctness And Coordination: define critical sections, atomicity mechanisms, idempotency strategy, and replay behavior.
- Worker And Runtime Topology: define layers, worker roles, scaling, isolation, and shutdown model.
- Scenario Mapping: walk one happy path and at least one failure-heavy path.
- Metrics: define correctness gates and optimization signals.
- POC: propose the smallest runnable validation and the failure injections to run.
- Evaluation: compare alternatives and state the architectural decision.
- Risks And Refactor Triggers: name what would invalidate the current choice later.

## References

- Read `references/api-first-strategy-principles.md` when the task is about API-first or contract-first planning.
- Read `references/api-state-machine-principles.md` when the task is about lifecycle-driven API design, actors, authorization, or scenario mapping.
- Read `references/distributed-correctness-principles.md` when the task is about transactions, distributed locks, idempotency, retries, late data, or atomic operations.
- Read `references/messaging-and-operation-principles.md` when the task is about message queues, RPC over messaging, context propagation, worker lifecycle, or design for operation.
- Read `references/pipeline-scheduling-principles.md` when the task is about staged workers, scheduling, reordering, buffering, queue metrics, or theory-limit reasoning.
- Read `references/worker-isolation-principles.md` when the task is about process pools, runtime isolation, or choosing between process and infrastructure orchestration.
- Keep article-specific notes in `references/`.
- Promote only stable cross-article guidance back into this `SKILL.md`.
