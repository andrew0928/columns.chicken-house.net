---
name: andrew-architect-design
description: Design software architecture by extracting stable interfaces from messy or fast-changing requirements, then validating the design with explicit metrics, simulation, scenario mapping, and SLO-driven operational thinking. Use when Codex needs Andrew-style abstraction-first design, state-machine-driven API design, contract-first or API-first planning, extensibility analysis, theory-of-constraints reasoning, deliberate practice for architecture or design skill-building, systems with tradeoffs between correctness and latency or capacity, or when the user wants the output ordered as problem analysis, modeling, class, scenario, and poc.
---

# Andrew Architect Design

Current version: `0.1.0`

## Overview

Use this skill to turn unstable business examples into a stable design direction before committing to detailed implementation.

Treat concrete examples as evidence, not as the architecture. Hide calculation or rule details behind a stable contract that keeps the main flow readable and extendable.

When the user is trying to improve design ability, convert the target problem into a small practice loop with executable feedback instead of giving abstract advice only.

## Working Style

- Write in Traditional Chinese when the user or repo context is Chinese.
- Start from problem analysis before proposing classes or implementation.
- Treat API contracts as long-lived architecture surfaces. Validate them before writing substantial implementation code.
- Judge API quality by structural consistency before transport style or framework taste.
- Keep the main flow simple enough that a new rule usually means adding a new implementation, not rewriting orchestration.
- When the goal is skill-building, turn the problem into an isolated exercise with fast feedback instead of relying on vague discussion.
- Prefer explicit interfaces and contracts over pattern-name discussion.
- Define observability together with behavior. If the design has tradeoffs, make them measurable early.
- Use dimensional reduction in PoC work. Replace high-cost runtime dimensions with simpler local equivalents only when the mapping stays explicit and defensible.
- Treat service quality as a design problem, not only an ops problem. If the system has a service promise, the architecture should explain how that promise will be measured and defended.
- Separate business language from engineering mechanics. Do not expose workaround flags to business-facing configuration unless the tradeoff is explicit.
- Judge abstraction quality by stability: detail changes should not force main-flow redesign.
- Treat Dev and Ops as one design surface when runtime behavior, latency, loss, capacity, or reliability matters.
- Keep the core API surface minimal and stable. Prefer SDK, BFF, templates, or composition helpers over bloating the contract with UI-specific detail.

## Workflow

### 1. Problem Analysis

- Collect concrete examples, failure modes, and pain points first.
- State why the problem is difficult. Identify ambiguity, instability, or environmental uncertainty.
- Separate external factors from controllable parameters.
- Name the tradeoff explicitly. Examples: latency vs reliability, flexibility vs simplicity, throughput vs ordering.
- Decide whether the task needs only conceptual design, or also a runnable model or simulation.
- When the goal is practice, name the exact unknown, decision, or weakness the exercise should expose.
- For API design, ask what service, data, or capability the contract must expose and which callers or target systems need it.
- For API design, clarify whether the contract is exposing an internal domain service or only reflecting one current UI flow. Prefer the domain-service view.
- When the problem depends on schedule, expiry, timeout, delay, or event ordering, treat time as a first-class design variable.
- If the system serves users or downstream teams under time or quality expectations, name the SLO candidate early.
- Distinguish external agreement, internal objective, and measurable indicator when relevant: SLA, SLO, and SLI.

### 2. Modeling

- Ask what the main system truly cares about.
- Separate focus from detail.
- Write one contract sentence that captures the stable interaction between the main flow and the variable rules.
- Reject early taxonomies that only classify today's known examples.
- Align the abstraction boundary with the hardest design pain point, not with whichever implementation detail is currently loudest.
- Model the system as cooperating parts with clear responsibilities, not as one big algorithm.
- When runtime uncertainty matters, model both the mechanism and the surrounding environment.
- For API design, identify the primary subject, entity, or service whose lifecycle is actually being exposed.
- For service-quality problems, model the path the work travels through and mark where delay, queueing, or loss can accumulate.
- If workloads have different value or urgency, model them as separate classes instead of assuming one shared flow is always optimal.

### 3. API State Machine

- Model lifecycle-driven APIs with a state machine first.
- Keep only lifecycle-defining states at this layer. Do not promote every property, level, or flag into a state unless its transitions are core business logic.
- Mark all meaningful states, including conceptual start or end states when they help reasoning even if they are not persisted directly.
- Mark the operations that change state.
- Mark the operations that do not change state.
- Mark the actors that are allowed to trigger each operation.
- Mark the target systems that invoke, consume, or react to the contract.
- Mark follow-on events separately from direct state transitions.
- Treat the state machine as ground truth for legal combinations of current state, action, and identity.
- Treat composite API operations as wrappers around core transitions. Allow them only when they preserve the same state-machine semantics.

### 4. Class And Interface

- Define a base contract that carries only shared metadata and the core processing entry point.
- Return explicit result objects instead of hiding everything in side effects.
- Keep variant logic inside concrete implementations.
- Introduce a context object only when rule evaluation genuinely depends on accumulated state or previous results.
- Support rule ordering or priority when later evaluation depends on earlier outcomes.
- Use tags or markers only for cross-rule coordination such as exclusion or pairing, not as a substitute for the core business model.
- Keep framework responsibilities separate from rule or plugin responsibilities.
- Define message or entity structure so the system can actually reason about order, continuity, identity, or causality when those matter.
- Expose interaction boundaries in code-level contracts early. Prefer contract-first design when the implementation space is still open.
- For API-first work, translate the model into four surfaces: entity, action, authorize, and event.
- Separate authentication, authorization, and access control in the model even when an early PoC temporarily simplifies them into one identity scheme.
- Distinguish no-id create or static operations, id-based state-changing operations, id-based read-only operations, and multi-item query or export operations.
- Derive request and response shape from entity and action semantics, not from UI screens.
- Map actor, role, scope, and operation relationships explicitly.
- Prefer OpenAPI for request, response, and security contracts, and AsyncAPI for event contracts when relevant.
- Keep transport adapters thin. Let stable contracts and core services own lifecycle rules, authorization checks, and domain behavior wherever possible.
- Centralize cross-cutting checks such as token parsing, transition legality, and action authorization in middleware, filters, or AOP-style hooks when the framework supports it.

### 5. Scenario Mapping

- Start with the smallest end-to-end scenario that proves the main flow without special rules.
- Add the first concrete rule and verify the orchestration still reads as a generic pipeline.
- Add a second rule with a different shape and verify the orchestration still does not change.
- Add stress scenarios when relevant: exclusion, pairing, thresholds, ordering, and state-dependent behavior.
- Call out the exact moment the current contract becomes insufficient. Use that moment to justify refactoring toward a richer context or result model.
- Prefer executable scenarios or tests to pin down expected behavior before optimizing internals.
- For streaming or reliability problems, include both normal flow and degraded-environment scenarios.
- For API design, convert each business story into a scenario map with caller, action, start state, final state, target system, and expected event or returned data.
- Walk the scenario over the state machine like moving a token on a board.
- Validate three things at every step: the transition exists, the actor is allowed, and the output is sufficient for the next system.
- Validate consistency across naming, state, action, event, and authorization. If one view disagrees with the others, the API structure is not ready.
- Include masked-data, partner, and system-to-system scenarios when trust levels differ.

### 6. Metrics

- Define success metrics before tuning the design.
- Separate outcome metrics from environmental inputs and controllable configuration.
- Prefer metrics that reveal tradeoffs directly, such as drop rate, latency, delay, buffer usage, throughput, retry count, error rate, or recovery time.
- State which metrics are hard constraints and which are optimization targets.
- When relevant, align metrics with SLO thinking instead of algorithm elegance.
- Add instrumentation points to the model or POC early so evaluation is not an afterthought.
- For deliberate practice, use tests and metrics as the feedback loop so each iteration can be judged objectively.
- If the main design risk is contract correctness rather than runtime behavior, treat scenario coverage and scenario-mapping success as first-class validation signals.
- When SLO matters, decompose the objective into application-level SLIs that can actually be measured at concrete points in the workflow.
- Prefer a small set of diagnostic indicators over a noisy dashboard full of unrelated numbers.
- Combine infrastructure metrics and application metrics on the same operational view when diagnosis needs both.
- Define alert thresholds and response bands early enough that operators can tell safe, warning, and urgent states quickly.
- If cost is part of the real tradeoff, treat cost or resource-consumption proxies as metrics too, not as an afterthought.

### 7. POC

- Build the thinnest runnable example that can show raw inputs, applied rules, and final outcome.
- Prefer explicit item instances over compressed quantities when grouping, pairing, or exclusion matters.
- Keep the core workflow readable in one short function or class.
- Prove extensibility by adding at least one new concrete rule without rewriting the core flow.
- Use the POC to validate the abstraction boundary. Do not let admin UI, persistence, or production-scale configuration take over the first pass.
- For deliberate practice, isolate the exercise from production noise so the practice loop stays focused, repeatable, and easy to compare.
- Start with the simplest version that is clearly correct before chasing elegance, concurrency, or throughput.
- For systems with uncertain runtime behavior, build a simulation harness or deterministic test harness, not just a happy-path demo.
- Make the POC measurable: export logs, counters, or CSV-style outputs if needed to compare runs.
- For API-first work, use mocks, in-memory repositories, console traces, or minimal contracts to validate design before framework-heavy implementation.
- Prefer validating the core contract outside HTTP first, then add thin transport adapters to prove the design survives protocol translation.
- When time-dependent behavior matters, introduce a controllable time abstraction instead of waiting on real wall-clock time or changing machine time.
- Prefer fast-forwardable clocks or time contexts for PoC and tests so scheduled behavior can be replayed quickly.
- Keep time semantics explicit: usually allow forward-only progression within one run and require reset for replay.
- If time jumps can cross trigger boundaries, emit the events that should have occurred during the jump and distinguish expected occurrence time from actual handling time.
- Use tolerance-based assertions when realtime drift is unavoidable, but keep deterministic checks for fast-forwarded time.
- Apply dimensional reduction deliberately, such as host to thread, RPC to local call, database to in-memory collection, message bus to language event, or realtime clock to mock time.
- For service-quality designs, include instrumentation in the POC so the same experiment can reveal both correctness and bottleneck behavior.
- Prefer PoCs that can show queue buildup, processing delay, throughput, and over-SLO counts when those decide the design.

### 8. Evaluation

- Compare metric results across different environmental assumptions and configuration values.
- Use measurements to choose the design or parameters, not intuition alone.
- Interpret metrics, do not just print them. Explain what each pattern means operationally.
- Prefer designs that keep critical failure metrics within target while making delay or resource usage predictable.
- If results expose a missing control mechanism, feed that back into the design. Example: add timeout, active probing, or backpressure instead of just resizing buffers.
- When practicing, estimate the theory limit or practical ceiling so you know when to stop tuning and what gap is still conceptual rather than implementation-level.
- For API-first work, ensure the contract, scenario mapping, and authorization model all agree before translating them into concrete spec files.
- Diagnose with theory-of-constraints thinking when the system behaves like a pipeline or queueing network.
- Look for the bottleneck by finding where work accumulates ahead of the slowest stage.
- Protect the bottleneck first, then improve it.
- If the bottleneck cannot be improved quickly, route high-value work around lower-value contention or slow the intake at the source.
- When the system cannot satisfy SLO for incoming work, prefer explicit upstream control such as feature toggles, throttling, deferral, or alternate flows over silent degradation.
- Evaluate local optimizations against whole-system behavior. Faster non-bottlenecks can still make the overall system worse.
- Balance SLO against cost when the business problem actually requires both. The best design is often not the fastest one, but the one that achieves the required SLO at acceptable cost.

## Design Checks

- Revisit the abstraction if adding a new rule requires editing the main orchestration.
- Revisit the abstraction if many business-invisible flags are needed to emulate one special case.
- Revisit the abstraction if one advanced composite case forces every implementation to expose unnatural fields or mutate shared state.
- Revisit the model if you cannot name the environmental variables and controllable parameters separately.
- Revisit the design if you cannot define metrics that tell good outcomes from bad ones.
- Revisit the POC if it proves correctness but cannot expose runtime tradeoffs.
- Revisit the API design if the endpoints mirror screens instead of exposing the domain service or entity lifecycle.
- Revisit the state model if combinatorial growth suggests you encoded flags or properties as lifecycle states.
- Revisit the state machine if scenario mapping needs impossible jumps or hidden transitions.
- Revisit the authorization model if role or scope mapping cannot explain who is allowed to trigger each operation.
- Revisit the implementation boundary if controllers or handlers contain domain transition rules, repeated authorization branching, or other logic that should live in reusable core or middleware.
- Revisit the execution model if transition validation and the actual state change are not atomic under concurrent calls.
- Revisit the practice setup if the exercise is too entangled with unrelated code or environment details to give fast, repeatable feedback.
- Revisit the learning plan if the exercise improves output but still does not reveal what foundational knowledge is missing.
- Revisit the time model if validation depends on sleeping in real time, editing the machine clock, or manually waiting for scheduled actions.
- Revisit the PoC reduction strategy if the lower-dimensional model no longer maps cleanly to the real system behavior.
- Revisit the service design if the SLO exists only in prose and cannot be broken into measurable SLIs.
- Revisit the observability design if operators can see system health numbers but still cannot diagnose which application stage is failing the SLO.
- Revisit the workload design if one low-value workload can routinely consume capacity needed by a higher-value workload.
- Balance rigor and flexibility. Avoid both over-design and piles of workarounds.
- Prefer state-light designs when trial evaluation or comparison between alternatives is important.

## Default Output Shape

When the user asks for a design, respond in this order unless they request another structure:

1. Problem Analysis
2. Modeling
3. API State Machine
4. Class And Interface
5. Scenario Mapping
6. Metrics
7. POC
8. Evaluation
9. Risks and Refactor Triggers

Use these expectations for each section:

- Problem Analysis: define the hard part, external factors, controllable parameters, and core tradeoff.
- Modeling: define the stable concern, the hidden details, the system parts, the primary subject, and the contract sentence.
- API State Machine: define states, operations, actors, target systems, and events.
- Class And Interface: define core entities, abstract contracts, concrete extension points, authorization shape, and any ordering or context needs.
- Scenario Mapping: walk through at least one happy path and one stress path step by step.
- Metrics: define what to measure, why it matters, and what good or bad looks like.
- POC: propose the smallest runnable slice that proves the architecture and exposes the metrics.
- Evaluation: compare likely outcomes or simulated results and state what decision follows.
- Risks and Refactor Triggers: name the assumptions that would force a boundary change later.

## Practice Mode

When the user asks how to build design ability, create exercises, or practice architecture thinking, respond in this order unless they request another structure:

1. Practice Goal
2. Simplified Problem
3. Correctness Harness
4. Metrics
5. Baseline POC
6. Iteration Plan
7. Theory Limit
8. Knowledge Gaps and Next Practice
9. Peer Review Or Comparison Plan

Use these expectations for each section:

- Practice Goal: define the target capability, the specific weakness to expose, and why this exercise matters.
- Simplified Problem: strip the problem down until it is small enough to run repeatedly without losing the core design challenge.
- Correctness Harness: define tests, scenarios, or executable checks that tell whether the solution is right.
- Metrics: define what signals show better or worse design quality, not only pass or fail.
- Baseline POC: propose the simplest correct implementation that can be measured.
- Iteration Plan: list the next one or two design changes to try and what hypothesis each change is testing.
- Theory Limit: estimate the likely ceiling so the learner knows whether they are fighting implementation waste or a real design constraint.
- Knowledge Gaps and Next Practice: name the missing foundations, related topics, or adjacent domains the exercise surfaced.
- Peer Review Or Comparison Plan: make the practice easy to compare across alternate solutions, for example by sharing code, tests, metrics, or PRs.

## References

- Read `references/interview-abstraction-principles.md` before extending this skill or when the request is explicitly grounded in Andrew's 2020 abstraction article.
- Read `references/reorder-metrics-principles.md` before extending this skill or when the request involves buffering, ordering, streaming, reliability, latency, or metrics-driven architecture validation.
- Read `references/api-first-strategy-principles.md` before extending this skill or when the request is about API-first or contract-first planning, API boundary decisions, or minimizing API surface while preserving long-term reuse.
- Read `references/api-design-workshop-principles.md` before extending this skill or when the request needs state-machine-driven API design, actor and scope mapping, event design, or scenario mapping validation.
- Read `references/api-fsm-consistency-principles.md` before extending this skill or when the request needs extra API design guidance on structural consistency, state-versus-property decisions, or FSM-driven enforcement choices.
- Read `references/api-fsm-implementation-principles.md` before extending this skill or when the request needs implementation guidance for API-first design, layered contracts/core/web adapters, centralized security enforcement, or PoC validation of the API design.
- Read `references/time-mock-poc-principles.md` before extending this skill or when the request depends on time-based behavior, timers, expiry, schedule simulation, or PoC techniques that benefit from controllable time and dimensional reduction.
- Read `references/slo-and-toc-principles.md` before extending this skill or when the request involves service quality, SLO or SLI design, observability-by-design, queueing bottlenecks, or theory-of-constraints reasoning.
- Read `references/deliberate-practice-principles.md` before extending this skill or when the request is about cultivating design ability, creating architecture practice exercises, exposing unknown unknowns, or building a deliberate-practice loop with code, metrics, and theory limits.
- Keep future article-specific notes in separate files under `references/`.
- Promote only stable cross-article guidance back into this `SKILL.md`.
