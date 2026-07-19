---
name: andrew-architecture-core
description: "Build Andrew-style architecture foundations before domain-specific design: frame the real problem, extract stable abstractions, choose data and storage shapes from dominant constraints, validate ideas with measurable POCs, and turn architecture topics into deliberate-practice loops. Use when the task is cross-domain architecture thinking, abstraction-first modeling, storage tradeoff analysis, executable design validation, or architecture skill-building."
---

# Andrew Architecture Core

## Overview

Use this skill when the problem is still too raw, too cross-cutting, or too early to jump straight into API, security, reliability, or microservice patterns.

Start from the hardest constraint and the dominant operations. Treat examples as evidence, not as the architecture. Convert the problem into a stable model, choose where complexity should live, then prove the design with a small runnable slice and explicit metrics.

## Working Style

- Write in Traditional Chinese when the user or repo context is Chinese.
- Start from problem analysis before proposing classes, frameworks, or storage products.
- Judge design quality by stability under change, not by how quickly it fits today's examples.
- Let the hardest constraint decide the abstraction boundary.
- Prefer explicit contracts and measurable tradeoffs over pattern-name discussion.
- When data shape does not fit the storage model, reshape data deliberately instead of pretending the mismatch does not exist.
- Treat write-time work, read-time work, storage cost, and operational simplicity as one design surface.
- When time affects correctness, make time explicit in the model and controllable in the POC.
- Prefer small executable models over long conceptual discussion when feasibility is still uncertain.
- When the goal is growth, turn the topic into a repeatable practice loop with tests and metrics.

## Workflow

### 1. Problem Analysis

- Collect concrete scenarios, failure modes, and awkward edge cases first.
- State why the problem is difficult: scale, correctness, late data, storage mismatch, cross-step coordination, or unclear boundaries.
- Identify the dominant operations:
  - what is queried most often
  - what changes most often
  - what must stay correct under scale
- Separate external facts from controllable parameters.
- Distinguish occurrence time, receive time, and decision time when delayed data or replay matters.
- Decide whether the task needs only a model, or also a measurable POC.

### 2. Modeling

- Ask what the system must keep stable while examples continue to change.
- Write one contract sentence for the stable interaction.
- Separate focus from detail.
- Model the system as cooperating parts with explicit responsibilities.
- Do not classify only today's known cases. Choose boundaries that still make sense when tomorrow's case appears.
- When the design revolves around data, model identity, state, lifecycle, and ownership before choosing storage technology.

### 3. Data And Storage Design

- Choose schema and storage based on the hardest requirement, not on product preference.
- Decide whether the design should optimize read flexibility, write simplicity, replayability, tenant isolation, or scale-out behavior.
- Decide where to pay complexity:
  - write time vs read time
  - normalization vs materialization
  - dynamic query power vs fixed access paths
  - storage efficiency vs operational simplicity
- When the storage model does not naturally fit the domain shape, add explicit indexes, projections, or materialized forms.
- Make partition, tenant, or scope boundaries safe by default in the data access layer.
- Separate shared data from scoped data explicitly.
- Prefer combining complementary techniques over forcing one storage style to solve every problem.

### 4. Class And Boundary Design

- Define minimal contracts that expose stable input, output, and identity.
- Hide variant logic behind implementations, not behind orchestration conditionals.
- Introduce richer context objects only when the current signature is no longer enough.
- Keep the main flow readable in one short pass.
- Preserve composition boundaries so the same model can work in-process, across CLI boundaries, or against different storage backends.
- If streaming matters, define item-by-item transfer shape instead of batch-only contracts.
- Treat result objects as first-class outputs when the caller needs both final outcome and intermediate reasoning.

### 5. Scenario And Flow Mapping

- Start with the smallest end-to-end baseline that proves the core model.
- Add one structurally different case at a time and verify the main flow still does not change.
- Walk important flows step by step:
  - normal path
  - late or corrected data
  - high-volume path
  - restart or replay path
- If the system is staged, model what each stage consumes, produces, and guarantees.
- Track where work-in-progress accumulates, where data is reshaped, and where replay or correction must re-enter the flow.

### 6. Metrics And Theory Limits

- Define success metrics before tuning.
- Choose metrics that expose tradeoffs directly, such as:
  - first-result latency
  - full-run completion time
  - max work-in-progress or buffer size
  - replay cost
  - query cost
  - storage growth
  - correction lag
  - tenant isolation risk
- Mark hard constraints separately from optimization targets.
- Estimate a likely theory limit or practical ceiling so iteration has a stopping rule.
- When data arrives late, define tolerated lateness and the exception path beyond that limit.

### 7. POC And Dimensional Reduction

- Build the thinnest runnable model that can prove the boundary and the tradeoff.
- Reduce dimensions deliberately:
  - distributed hosts to local threads
  - remote calls to local calls
  - database to in-memory collections
  - message bus to language-level events
  - realtime clock to controllable time
- Keep the mapping between reduced model and real system explicit.
- If time matters, use controllable time instead of sleeping in realtime or editing machine time.
- If data-shape tradeoffs matter, benchmark representative workloads instead of arguing from taste.
- Prefer POCs that show both correctness and cost.

### 8. Evaluation

- Compare options against the chosen metrics, not against preference.
- Explain what each metric pattern means operationally or development-wise.
- Decide what complexity belongs in application code, in storage, or in explicit projections.
- Prefer the design that keeps critical constraints predictable, even if it is not the most elegant on paper.
- Name the assumptions that would force a redesign later.

## Design Checks

- Revisit the abstraction if new cases require rewriting the main orchestration.
- Revisit the storage decision if you cannot explain it using dominant queries, updates, and scale constraints.
- Revisit the model if occurrence time and receive time are being mixed even though delayed data changes the answer.
- Revisit the data shape if every important query requires awkward reconstruction work.
- Revisit the write path if read performance depends on information that is never materialized or indexed.
- Revisit the boundary if scoped data access is safe only when every caller remembers to add the right filter.
- Revisit the POC if it proves only the happy path and hides the real tradeoff.
- Revisit the metrics if they cannot distinguish between a correct design and an expensive one.
- Revisit the flow design if pipeline stages cannot be restarted, replayed, or observed independently.
- Revisit the practice setup if the exercise is too entangled with production detail to rerun quickly.

## Default Output Shape

When the user asks for architecture design, respond in this order unless they request another structure:

1. Problem Analysis
2. Modeling
3. Data And Storage Design
4. Class And Boundary Design
5. Scenario And Flow Mapping
6. Metrics And Theory Limits
7. POC
8. Evaluation
9. Risks And Refactor Triggers

Use these expectations for each section:

- Problem Analysis: define the hard part, dominant operations, external constraints, and controllable variables.
- Modeling: define the stable concern, the hidden details, the main parts, and the contract sentence.
- Data And Storage Design: define identity, state, partitioning, access paths, and where complexity should live.
- Class And Boundary Design: define core entities, interfaces, result types, context objects, and composition boundaries.
- Scenario And Flow Mapping: walk at least one baseline path and one stress path step by step.
- Metrics And Theory Limits: define what to measure, what good or bad looks like, and what ceiling or cutoff matters.
- POC: propose the smallest runnable slice that proves the design and exposes the tradeoff.
- Evaluation: compare options or expected outcomes and state what decision follows.
- Risks And Refactor Triggers: name what would invalidate the current boundary later.

## Practice Mode

When the user asks how to build architecture skill, create exercises, or deliberately practice design thinking, respond in this order unless they request another structure:

1. Practice Goal
2. Simplified Problem
3. Correctness Harness
4. Baseline POC
5. Measurements
6. Iteration Plan
7. Theory Limit
8. Knowledge Gaps
9. Comparison Plan

Use these expectations for each section:

- Practice Goal: define the capability to strengthen and the weakness the exercise should expose.
- Simplified Problem: remove noise while keeping the real design tradeoff.
- Correctness Harness: define tests, scenarios, or executable checks first.
- Baseline POC: propose the simplest correct solution that can be run repeatedly.
- Measurements: define the metrics that compare versions fairly.
- Iteration Plan: change one thing at a time and state the hypothesis.
- Theory Limit: estimate the likely ceiling so the learner knows when to stop tuning.
- Knowledge Gaps: name the missing fundamentals the exercise exposed.
- Comparison Plan: make alternate solutions easy to compare with shared tests, metrics, and assumptions.

## References

- Read `references/interview-abstraction-principles.md` when the task is about abstraction boundaries, stable interfaces, extensibility, or refactoring toward richer context.
- Read `references/deliberate-practice-principles.md` when the task is about how to practice architecture or turn a vague topic into a repeatable exercise.
- Read `references/time-mock-poc-principles.md` when the design depends on time, delay, schedule, expiry, or deterministic replay.
- Read `references/data-shape-and-storage-principles.md` when the task involves persistence models, tenant isolation, schema tradeoffs, tree-like data on relational storage, or choosing where to pay indexing and materialization cost.
- Read `references/pipeline-and-object-stream-principles.md` when the task involves staged processing, streaming, CLI composition, object transfer across boundaries, or throughput-vs-latency tradeoffs.
- Read `references/event-sourcing-materialization-principles.md` when the task involves append-only history, late-arriving data, projection design, replay, or multiple reporting views over the same source facts.
- Keep article-specific notes in `references/`.
- Promote only stable, cross-article guidance back into this `SKILL.md`.
