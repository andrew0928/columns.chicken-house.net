# Time Mock And PoC Principles

This reference distills the current skill draft from Andrew's article:

- Source article: `docs/_posts/2022/2022-05-29-datetime-mock.md`
- Current scope: controllable time and dimensional-reduction PoC techniques

## Core Principles

- When time affects correctness, time should be modeled as a controllable dependency in PoC and tests.
- A frozen clock is not always enough. For many architecture problems, the mocked time must continue to move and also support fast-forward.
- Prefer a low-friction time context that is easy to use across the whole prototype when the goal is fast design validation.
- Keep time travel semantics strict. Forward-only progression is usually safe; backward time travel should require reset and replay.
- If scheduled or time-based events matter, the time abstraction should emit the events that should have happened during fast-forward.
- Separate expected occurrence time from actual handling time when delayed triggering is acceptable.
- Use tolerance windows only for realtime-linked checks; keep fast-forward checks deterministic.
- Build PoC tools that help reasoning, not only unit testing.

## Dimensional Reduction

- Use PoC to validate concepts, not to reproduce the full production stack.
- Lower the problem dimension while preserving the design meaning.
- Typical reductions from the article:
  - distributed hosts to local threads
  - remote calls to local calls
  - database to in-memory collections
  - message bus to language-level events
  - realtime clock to controllable mock time
- Only use these reductions when the mapping between real and reduced models is clear enough to reason about.

## Derived Workflow

### Problem Analysis

- Identify whether time, delay, schedule, timeout, expiry, or event ordering is part of the real design risk.
- Decide whether the PoC needs frozen time, flowing time, or fast-forwarded time.

### Interface

- Define a minimal time control surface, typically:
  - current time
  - initialize or reset
  - fast-forward
  - optional event hooks for time-based triggers
- Keep the interface usage obvious enough that prototypes and demos can adopt it quickly.

### Validation

- Test direct time reads.
- Test time jumps across trigger boundaries.
- Test realtime-linked behavior with explicit tolerance.
- Use the same controllable time tool in demos when that helps stakeholders understand the design.

## Article-Specific Warnings

- Do not wait in real time for a PoC if the goal is to validate design logic rather than wall-clock integration.
- Do not edit the machine clock just to prove a design concept.
- Do not overbuild the clock abstraction before the concept is proven.
- Do not allow backward time travel without reset unless you are prepared to define full rollback semantics.
