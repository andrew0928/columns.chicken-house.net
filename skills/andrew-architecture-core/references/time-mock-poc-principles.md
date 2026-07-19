# Time Mock And PoC Principles

This reference distills Andrew's article:

- Source article: `docs/_posts/2022/2022-05-29-datetime-mock.md`

## Core Principles

- When time affects correctness, time should be a controllable dependency in PoC and tests.
- A frozen clock is not always enough; many design problems need flowing time plus fast-forward.
- Prefer low-friction time control that the whole prototype can adopt quickly.
- Keep time-travel semantics strict: usually forward-only within one run, reset for replay.
- If time jumps cross trigger boundaries, emit the events that should have occurred.
- Separate expected occurrence time from actual handling time when delayed triggering is acceptable.
- Use tolerance windows only for realtime-linked checks; keep fast-forward checks deterministic.

## Dimensional Reduction

- Use PoC to validate concepts, not to reproduce the full production stack.
- Lower the problem dimension while preserving design meaning.
- Typical reductions:
  - distributed hosts to local threads
  - remote calls to local calls
  - database to in-memory collections
  - message bus to language-level events
  - realtime clock to controllable time

## Article-Specific Warnings

- Do not wait in realtime just to prove design logic.
- Do not edit machine time for PoC work.
- Do not overbuild the clock abstraction before the concept is proven.
