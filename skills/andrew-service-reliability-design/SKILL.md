---
name: andrew-service-reliability-design
description: "Design Andrew-style service reliability mechanisms from explicit SLOs, bottleneck analysis, load shaping, queue fairness, and operable metrics. Use when Codex needs to design service-quality guarantees, SLI/SLO decomposition, admission control, throttling, queue or lineup mechanisms, workload separation, observability-by-design, or operational controls that protect user experience under load."
---

# Andrew Service Reliability Design

## Overview

Use this skill when the main problem is not only correctness, but whether the service can keep its promise under load, delay, spikes, and limited capacity.

Treat service quality as an architecture problem. Start from the promised outcome, turn it into measurable indicators, find the real bottleneck, then shape traffic and feedback so the whole system stays predictable instead of collapsing under pressure.

## Working Style

- Write in Traditional Chinese when the user or repo context is Chinese.
- Start from the service promise and user-visible outcome before discussing scaling tricks.
- Distinguish clearly:
  - SLA
  - SLO
  - SLI
- Treat application and domain metrics as design outputs, not as afterthoughts for Ops.
- Use bottleneck reasoning before adding capacity blindly.
- Prefer global optimization over local optimization.
- Separate high-value and low-value workloads when they compete for the same constrained resource.
- Decide explicitly how the system should reject, defer, queue, degrade, or reroute work.
- Treat queue fairness, feedback quality, and abandonment handling as part of reliability, not only UX polish.
- Validate control logic and monitoring logic with small executable models before production rollout.

## Workflow

### 1. Problem Analysis

- Define the exact service promise in user-visible terms:
  - completion time
  - success ratio
  - freshness
  - availability
  - queue wait
  - admission fairness
- Clarify the pressure shape:
  - steady load
  - short spikes
  - seasonal burst
  - shared downstream dependency
  - mixed-priority traffic
- State what failure looks like:
  - delayed too long
  - dropped too late
  - wrong users admitted first
  - overload spreading downstream
  - high-priority traffic blocked by low-priority traffic

### 2. Service Objective Model

- Define the SLO before proposing the mechanism.
- Decompose the top-level promise into measurable SLIs at real observation points.
- For staged or asynchronous flows, separate:
  - preparation time
  - queue wait time
  - execution time
  - downstream handoff time
- Distinguish internal operating goals from external agreements.
- Mark which indicators are:
  - hard service guarantees
  - early warning signals
  - optimization targets

### 3. Bottleneck And Workload Model

- Identify where work accumulates and why.
- Find the actual constrained resource:
  - worker throughput
  - queue capacity
  - storage IOPS
  - external provider quota
  - lock contention
  - human-facing checkout slots
- Model workload classes explicitly when they do not deserve the same service level.
- Estimate safe capacity and failure threshold with real units, not vague adjectives.
- Use queue buildup, wait-time drift, and backlog growth to infer whether the bottleneck is arrival rate, processing speed, or downstream slowness.

### 4. Capacity Control And Admission

- Decide how the system controls intake before overload becomes irreversible.
- Choose the admission strategy that matches the problem:
  - immediate reject
  - bounded queue
  - delayed execution
  - rate limit
  - token or budget allocation
  - feature toggle
  - workload separation
- Define what "service amount" means in measurable units.
- Define what happens after the limit is reached:
  - reject
  - retry later
  - join queue
  - degrade feature
  - switch to alternate path
- Reserve capacity deliberately for the workloads whose SLO matters most.
- Prefer simple, explainable control rules over opaque heuristics unless the added complexity is justified.

### 5. Queue And Lineup Design

- Use queueing when deferral is acceptable and fairness or ordering matters.
- Define queue semantics explicitly:
  - ordering rule
  - fairness rule
  - max queue length
  - admission window
  - abandonment timeout
  - duplicate join rule
- Make user-facing status cheap to query and easy to explain:
  - current state
  - queue position
  - estimated wait
  - may-enter signal
- Keep queue data structures aligned with the dominant operations.
- Support dynamic tuning and operational intervention when real load differs from prediction.
- Decide when users should be told not to enter the queue at all because the system already knows they will miss the objective.

### 6. Observability And Metrics

- Treat metric emission, dashboard design, and alert points as part of the design.
- Emit application and domain metrics directly from the service when infrastructure metrics cannot express the real promise.
- Prefer metrics that explain the situation, such as:
  - end-to-end completion time
  - stage latency
  - queue length
  - predicted delay
  - accepted vs rejected count
  - executed count
  - abandonment count
  - fairness violation count
  - workload split volume
  - capacity utilization
- Use dashboards to support diagnosis, not decoration.
- Define alert rules that map to real operator actions.

### 7. Operational Controls And Response

- Protect the bottleneck instead of feeding it blindly.
- Decide what operators or automated controls can change safely:
  - worker count
  - queue limit
  - admission threshold
  - per-class capacity
  - feature toggle
  - manual removal
- Define the emergency path when the SLO is already impossible to meet.
- Push the signal upstream when admitting more work only increases failure and cost.
- Consider cost together with SLO when long-term operation matters.
- If a local optimization shifts the bottleneck elsewhere, update the control plan accordingly.

### 8. POC And Simulation

- Build the thinnest executable model that proves the service-control logic and the metrics model.
- Use controllable traffic patterns:
  - normal load
  - burst load
  - idle gaps
  - mixed-priority traffic
  - slow downstream
- Prefer CSV, charts, or simple dashboards for early comparison if that is enough to expose the behavior.
- Validate both the control mechanism and the observability plan in the same POC.
- Use cheap local models before production-scale infrastructure when the goal is to validate the design.

### 9. Evaluation

- Compare designs by whether they preserve the intended service objective under realistic pressure.
- Prefer the design whose overload behavior is explicit, diagnosable, and operationally controllable.
- If queueing is chosen, evaluate both system protection and user fairness.
- If throttling is chosen, evaluate both protection strength and lost business value.
- If workload separation is chosen, confirm it protects the high-priority SLO rather than only moving metrics around.
- Name the assumptions that would invalidate the design later.

## Design Checks

- Revisit the design if the SLO cannot be stated as something measurable.
- Revisit the decomposition if the top-level promise cannot be traced to stage-level indicators.
- Revisit the bottleneck analysis if scale-out is proposed before backlog and delay patterns are understood.
- Revisit the control model if overload is detected only after downstream damage is already visible.
- Revisit the queue design if status queries are expensive, unfairness is unexplained, or abandonment is ignored.
- Revisit the workload model if low-value traffic can still consume capacity needed by high-value traffic.
- Revisit the metrics if they cannot distinguish wait, execution, rejection, and backlog growth.
- Revisit the dashboard if operators can see charts but still cannot decide what to do.
- Revisit the POC if it proves only average load and hides the spike behavior that actually matters.

## Default Output Shape

When the user asks for service reliability design, respond in this order unless they request another structure:

1. Problem Analysis
2. Service Objective Model
3. Bottleneck And Workload Model
4. Capacity Control And Admission
5. Queue And Lineup Design
6. Observability And Metrics
7. Operational Controls And Response
8. POC
9. Evaluation
10. Risks And Refactor Triggers

Use these expectations for each section:

- Problem Analysis: define the promised outcome, load shape, failure mode, and the real pressure source.
- Service Objective Model: define SLA, SLO, SLI, observation points, and hard-vs-soft indicators.
- Bottleneck And Workload Model: define constrained resources, workload classes, backlog signals, and safe capacity assumptions.
- Capacity Control And Admission: define how work is accepted, deferred, rejected, or degraded.
- Queue And Lineup Design: define fairness, position/status feedback, abandonment policy, and queue-boundary rules.
- Observability And Metrics: define application metrics, dashboards, alerts, and diagnosis signals.
- Operational Controls And Response: define knobs, escalation path, upstream protection, and cost-aware actions.
- POC: propose the smallest simulation or runnable slice that exposes overload behavior and metrics usefulness.
- Evaluation: compare alternatives and state the decision.
- Risks And Refactor Triggers: name what traffic, dependency, or business changes would force redesign.

## References

- Read `references/slo-and-toc-principles.md` when the task is about decomposing a service promise into SLIs, finding bottlenecks, or designing dashboards and controls around SLOs.
- Read `references/throttle-and-qos-principles.md` when the task is about rate limiting, admission control, service-amount modeling, or choosing how to reject, defer, or reserve capacity.
- Read `references/lineup-and-queue-fairness-principles.md` when the task is about waiting-room design, fairness, polling status, queue-state modeling, or operator controls for large waiting populations.
- Keep article-specific notes in `references/`.
- Promote only stable cross-article guidance back into this `SKILL.md`.
