# Throttle And QoS Principles

This reference distills stable ideas from:

- `docs/_posts/2018/2018-06-10-microservice10-throttle.md`

## Core Principles

- Before controlling load, define what load means in measurable business or service units.
- Throttling has two separate design questions:
  - how load is measured
  - what happens after the limit is reached
- Admission control is part of service design, not only infrastructure tuning.
- Good load control protects the system before overload turns into a larger cascade.
- QoS often requires reserving capacity or protecting higher-value work from lower-value work.
- Early POC value comes from making the throttle behavior observable and comparable, not from building production infrastructure first.

## Derived Workflow

### Define Service Amount

- Choose the unit that matters:
  - requests
  - items
  - messages
  - transactions
  - business volume
- Decide whether the limit is instantaneous, averaged over time, burst-tolerant, or budget-based.

### Define Admission Outcome

- For over-limit traffic, decide whether to:
  - reject immediately
  - delay
  - queue
  - downgrade
  - route elsewhere
- Keep the decision explicit and measurable.

### Measure Behavior

- Capture counts such as:
  - total request
  - accepted request
  - rejected request
  - executed request
  - average wait before execution
- Compare control strategies by the shape of the outcome under the same traffic pattern.

### Validate With Cheap Instrumentation

- Use simple chartable output when it is enough to compare strategies quickly.
- Validate burst handling separately from steady-state handling.
- Prefer a POC that makes the tradeoff visible over one that hides it behind framework complexity.

## Article-Specific Warnings

- Do not assume "requests per second" is always the right unit.
- Do not define control rules without defining the post-limit behavior.
- Do not wait until the backend is already failing before deciding how admission should work.
