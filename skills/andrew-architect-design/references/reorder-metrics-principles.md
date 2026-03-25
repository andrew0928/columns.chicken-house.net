# Reorder Metrics Principles

This reference distills the current skill draft from Andrew's article:

- Source article: `docs/_posts/2023/2023-10-01-reorder.md`
- Current scope: second draft input for the skill

## Core Principles

- Start by analyzing the problem, not by jumping into data structures or queues.
- Distinguish environmental uncertainty from design-controlled parameters.
- Define the communication interface and data shape early so the system can reason about order, gaps, and correctness.
- Treat metrics as part of the architecture, not as post-implementation monitoring garnish.
- Make tradeoffs explicit and measurable before optimizing the mechanism.
- Use tests and simulation to validate not only correctness but also runtime behavior under varying conditions.
- Prefer small, inspectable models that can be rerun quickly over heavyweight production-like implementations in the first pass.
- Use metrics to guide parameter choices. The right answer is usually a tradeoff boundary, not a clever algorithm.
- Consider Ops concerns part of the design: instrumentation, SLO thinking, and predictable runtime behavior belong in the architectural draft.

## Derived Workflow

### Problem Analysis

- Define the question in operational terms.
- Identify what is known, what is uncertain, and what must be guaranteed.
- List external variables such as noise, delay, loss, traffic shape, or unreliable ordering.
- List internal control knobs such as buffer size, timeout, retry policy, or concurrency.

### Interface

- Define the core interaction contract first.
- Define the event or message structure so ordering, missing items, timestamps, or sequence can be observed.
- Keep the handler boundary separate from the buffering or reordering mechanism.
- When useful, use events or callbacks to make decisions observable without coupling the whole system together.

### Metrics

- Define metrics before tuning. Good examples from the article:
  - push
  - send or pop
  - drop
  - skip
  - drop rate
  - max delay
  - average delay
  - buffer usage
- Separate business or system outcomes from uncontrollable transport effects.
- Prefer metrics that help compare two designs or two parameter settings quickly.

### Evaluation

- Run the same model across multiple parameter sets.
- Compare metric results side by side.
- Explain the tradeoff behind the numbers instead of only reporting raw output.
- Choose the design that satisfies the hard target first, then optimize secondary metrics.
- Feed conclusions back into the design. If one knob is too crude, add a new control mechanism instead of endlessly tuning the old one.

## Article-Specific Warnings

- Do not confuse correct ordering in one unit test with production readiness.
- Do not tune a parameter if you have not first decided what success metric it should improve.
- Do not let the algorithm become the goal. SLO and operability should drive the design.
- Do not wait until full implementation to think about monitoring or runtime diagnosis.
- Do not overbuild the first prototype. A compact simulation plus instrumentation is often the right first artifact.
