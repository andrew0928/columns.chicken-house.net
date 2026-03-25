# Event Sourcing And Materialization Principles

This reference distills Andrew's article:

- Source article: `docs/_posts/2020/2020-01-01-microservice13-event-sourcing.md`

## Core Principles

- Store change history, not only final state, when replay, correction, audit, or alternate projections matter.
- Append-only source facts simplify history preservation but shift effort to projection and materialization.
- Event sourcing is rarely a standalone trick; it usually lives with message-driven processing, CQRS-style projections, and storage choices that favor pre-shaped reads.
- Distinguish event occurrence time from receive or processing time.
- Different decision contexts may need different projections over the same source facts.
- If delayed or corrected data is normal, the architecture must explain how prior results are revised.
- Define the maximum tolerable lateness and the exception path beyond that boundary.
- Prefer explicit projections for major read patterns instead of repeatedly reconstructing them on demand.

## Derived Workflow

### Modeling

- Decide whether the source of truth is current state, event history, or both.
- Define what must be reconstructable later.

### Read Design

- Identify each important view and why it exists.
- Materialize separate views when different consumers optimize for different notions of "correct now."

### Validation

- Test replay, correction, and late-arrival scenarios.
- Measure projection lag and correction lag, not only raw write success.

## Article-Specific Warnings

- Do not adopt event sourcing only because it sounds modern.
- Do not ignore the cost of rebuilding views or handling late corrections.
- Do not mix event time and processing time when business interpretation depends on the difference.
