# SLO And TOC Principles

This reference distills the stable design ideas from:

- `docs/_posts/2021/2021-06-04-slo.md`

## Core Principles

- Treat service quality as a design target, not only as an after-launch operations concern.
- Distinguish clearly:
  - SLA: external agreement or promise
  - SLO: internal service objective
  - SLI: measurable indicator used to judge the objective
- If the service objective cannot be measured, it cannot be managed.
- Decompose the top-level SLO into stage-level indicators at points the system can actually observe.
- For asynchronous systems, queue wait is often as important as execution time.
- Application teams must define and emit domain metrics themselves. Infrastructure metrics alone are not enough.
- A useful dashboard is one that helps operators decide what to do next.
- Use Theory of Constraints to find the real bottleneck, protect it, and control intake when needed.
- Optimize the whole system, not only the stage that is easiest to scale.
- Consider cost together with SLO when the business decision depends on both.

## Derived Workflow

### Define The Promise

- State the user-visible service goal in explicit numbers.
- Clarify what event starts the clock and what event stops the clock.
- Decide whether the objective is latency, freshness, success ratio, throughput, or another service property.

### Decompose Into Measurable Signals

- Split the promise into real observation points such as:
  - preparation
  - queue wait
  - execution
  - downstream acceptance
- Add backlog size when queue buildup changes the meaning of latency.
- Distinguish direct objective metrics from diagnostic helper metrics.

### Diagnose With Bottleneck Reasoning

- Look for where work accumulates in front of a slower stage.
- Use wait-time growth plus backlog growth to infer whether the bottleneck is arrival rate, worker speed, or downstream capacity.
- Re-check whether scaling one stage simply moves the bottleneck somewhere else.

### Protect The Bottleneck

- Use buffering, workload separation, throttling, or source-side control to protect constrained capacity.
- When work is already guaranteed to miss the objective, stop admitting it as early as possible.
- Preserve capacity for higher-value or stricter-SLO work.

### Design The Response Loop

- Define alerts and SOPs from the metric decomposition.
- Expose enough signal for both humans and upstream systems to react.
- Use domain metrics to drive feature toggles, alternate flows, or intake reduction when necessary.

## Article-Specific Warnings

- Do not assume the observability platform can invent domain metrics for you.
- Do not scale out blindly before understanding whether the queue, worker, or downstream provider is the real bottleneck.
- Do not let low-priority traffic consume the capacity required by high-priority objectives.
- Do not confuse local speedups with overall system improvement.
