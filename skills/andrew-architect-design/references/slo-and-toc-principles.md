# SLO And TOC Principles

This reference distills the current skill draft from Andrew's article:

- Source article: `docs/_posts/2021/2021-06-04-slo.md`
- Current scope: SLO-driven design, monitoring, and theory-of-constraints reasoning

## Core Principles

- Treat service quality as a design target, not only as an operations concern after launch.
- Name the service objective early and make it measurable.
- Distinguish:
  - SLA: the external agreement or promise
  - SLO: the internal service objective
  - SLI: the measurable indicator used to judge the objective
- If you cannot measure the service objective, you cannot manage or improve it.
- Application teams must emit domain-specific metrics themselves. Infrastructure metrics alone are not enough.
- The best dashboard is not the one with the most graphs; it is the one that lets someone diagnose the problem quickly.
- Use theory of constraints to reason about pipelines: identify the bottleneck, protect it, and control intake when necessary.
- Optimize the whole system, not only the stage that is easiest to speed up.
- Consider cost alongside SLO when the real business decision depends on both.

## Derived Workflow

### Problem Analysis

- Define the service promise in concrete terms.
- Ask which user-visible or downstream-visible outcome must stay within bounds.
- Decide whether the main promise is completion time, success ratio, freshness, throughput, reliability, or another service characteristic.

### SLO Decomposition

- Break the top-level SLO into smaller stage-level SLIs that can actually be measured.
- Mark the exact observation points in the flow.
- For queued or asynchronous systems, measure not only execution time but also waiting time and queue buildup.

### Monitoring By Design

- Treat metric emission as part of the implementation contract.
- Put system metrics and application metrics together when they are both needed to diagnose the same outcome.
- Define alerts, thresholds, and dashboards as first-class design outputs.
- Prefer metrics that point to action, not vanity numbers.

### Theory Of Constraints

- Find the bottleneck by locating where work accumulates in front of the slowest stage.
- Protect the bottleneck with appropriate buffering.
- If the bottleneck is saturated, prioritize high-value work and reduce intake of lower-value work.
- Use upstream control such as feature toggles, throttling, alternate paths, or deferral when work would otherwise enter the system only to fail the objective.
- Re-check whether a local optimization shifts the bottleneck somewhere else.

### Cost And Tradeoff

- Include cost or resource-consumption proxies when they materially affect the decision.
- Compare SLO gain against cost, not only against technical elegance.
- Sometimes the correct answer is workload separation or prioritization, not scaling everything equally.

## Article-Specific Warnings

- Do not ask the observability platform to invent your domain metrics for you. Define and emit them yourself.
- Do not scale out blindly before understanding whether the queue, worker, downstream dependency, or shared resource is the real bottleneck.
- Do not let low-priority traffic consume capacity required by high-priority SLOs.
- Do not confuse local speedups with global improvement.
- Do not wait until production pain to define the metrics that should have guided the design from day one.
