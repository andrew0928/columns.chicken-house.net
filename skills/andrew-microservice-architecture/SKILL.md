---
name: andrew-microservice-architecture
description: "Plan Andrew-style microservice architecture and migration by checking whether microservices truly fit, cutting service boundaries around real business responsibilities, evolving systems incrementally instead of rewriting, and engineering platform, runtime, and delivery capabilities as first-class architecture. Use when deciding whether to adopt microservices, decomposing a monolith, planning migration, choosing shared infrastructure, containerizing services, or defining the CI/CD and operability baseline needed to run many services safely."
---

# Andrew Microservice Architecture

## Overview

Use this skill when the question is not only how to build one service, but how to shape the whole application and platform so multiple services can evolve, deploy, and operate safely together.

Microservices are not the goal. They are one way to solve maintenance, deployment, scaling, and organizational-fit problems. Start from the pain that justifies service boundaries, move in small steps, and only add infrastructure that the team can actually run.

## Working Style

- Write in Traditional Chinese when the user or repo context is Chinese.
- Start from the business problem, maintenance pain, and team capability before proposing microservices.
- Treat microservice architecture as a socio-technical design, not only a code decomposition exercise.
- Align service boundaries with business flow and organizational responsibility, not only technical layers.
- Cut only as far as the system gains real independence or operability.
- Prefer refactoring and staged extraction over rewrite-from-scratch.
- Use mature external services when they solve the problem better than custom code.
- Treat API gateway, service discovery, messaging, logging, health, and deployment flow as part of the architecture, not afterthoughts.
- Prefer container and packaging models that make start, stop, deploy, and rollback predictable.
- Ask whether a capability needs runtime computation at all. If not, move it to build time or use simpler hosting.
- Validate risky changes with focused spikes and runnable POCs before institutionalizing them.

## Workflow

### 1. Problem Framing And Fit

- Define the actual pain the architecture must solve:
  - maintenance cost
  - deployment friction
  - fault isolation
  - scale-out need
  - mixed hosting environments
  - team ownership boundaries
- State why a monolith or modular system is not already sufficient.
- Check whether the team has enough baseline capability in:
  - source control
  - build and release
  - monitoring
  - deployment automation
  - production diagnosis
- Ask whether some parts of the system do not need runtime processes and should remain static or build-time generated instead.

### 2. Service Boundary And Responsibility

- Identify candidate boundaries from real business or organizational seams.
- Define each service by the one responsibility it should own end to end.
- Prefer boundaries that improve deployability, operability, and ownership together.
- Avoid over-splitting just because the code can be split.
- Decide where technical heterogeneity is worth the operational cost.
- Decide where a mature third-party service is better than a custom-built one.
- Ensure each service can be understood as a meaningful capability, not only a thin technical wrapper.

### 3. Migration And Transitional Architecture

- Do not rewrite everything from scratch unless there is a very strong reason.
- Stop making the monolith larger before trying to split it.
- Move upward through reuse levels deliberately:
  - source code
  - library
  - component
  - service
- Modularize first if direct service extraction is still too expensive.
- Use transitional glue code when it lowers migration risk, but treat it as disposable.
- Choose the first cut by impact and feasibility, not by fashion.
- Keep the system shippable while the migration is in progress.

### 4. Platform Capability Plan

- Decide which shared capabilities are required now and which can wait:
  - API gateway
  - service discovery
  - health check
  - communication and event system
  - centralized log or trace
  - configuration management
- For service discovery, define:
  - registration
  - query
  - health signal
  - metadata or tags
- Choose control style deliberately:
  - client-side discovery for maximum caller control
  - server-side discovery for centralized routing and lower client intrusion
- Plan how internal and external traffic will be routed without exposing unnecessary internal topology.
- Use service metadata when workload tier, region, or SLA class must affect routing.

### 5. Runtime And Hosting Model

- Design the runtime topology, not only the code topology.
- Decide which roles exist around one capability, such as:
  - public API
  - worker
  - scheduler
  - reverse proxy
  - SDK
- Choose hosting style based on lifecycle control, not habit.
- In containerized environments, prefer runtime models that let the service control its own startup, shutdown, health, and deregistration precisely.
- Treat one process per container as the default unless there is a clear reason not to.
- Let orchestration handle restart, placement, and scaling instead of duplicating those concerns inside each service host.
- Keep storage mounts, ports, health probes, and startup dependencies explicit.

### 6. Delivery And System-As-Code Model

- Decide the minimum reliable delivery flow before buying more tooling.
- Keep these foundations in place:
  - version control
  - automated build and tests
  - artifact management
  - release management
- Use package feeds or image registries as the release backbone.
- Do not let developer laptops become the source of production deployment artifacts.
- Keep branch strategy only as complex as the release process needs.
- Treat deployment definitions, routing rules, templates, static site generation, and operational scripts as source-controlled code.
- If a capability can be rendered ahead of time, prefer static output plus simple hosting over a permanent runtime service.

### 7. POC And Incremental Validation

- Run spikes for the risks that could sink the migration, such as:
  - API compatibility
  - packaging and deployment
  - service discovery integration
  - container lifecycle behavior
  - external-service replacement
  - mixed cloud or on-prem hosting
- Prefer runnable slices over slideware.
- Validate both architecture fit and team operability.
- Fail early in the POC stage, not after the organization is already committed.

### 8. Evaluation

- Compare candidate architectures by:
  - reduced maintenance complexity
  - deployment independence
  - operational simplicity
  - platform fit
  - team skill fit
  - migration risk
  - long-term extensibility
- Prefer the design that solves the current pain without forcing premature infrastructure complexity.
- Name which later signals would justify more splitting, more platform investment, or rollback to a simpler approach.

## Design Checks

- Revisit the plan if microservices are proposed without a clearly named pain they solve.
- Revisit the boundary if the cut follows technical layers but not business or team ownership.
- Revisit the split if a service cannot operate independently enough to justify being a separate service.
- Revisit the migration if rewrite is being chosen only because the old code is unpleasant.
- Revisit the platform plan if the infrastructure list is larger than the team's operational ability.
- Revisit the runtime model if service registration, shutdown, and health cannot be aligned with process lifecycle.
- Revisit the build-vs-run decision if a service exists only to serve mostly static or precomputable content.
- Revisit the delivery model if production artifacts can still be created ad hoc from a developer machine.
- Revisit the architecture if every problem is being solved by custom code even when mature services already exist.

## Default Output Shape

When the user asks for microservice architecture or migration design, respond in this order unless they request another structure:

1. Problem Analysis
2. Microservice Fit
3. Service Boundaries
4. Migration Strategy
5. Platform Capabilities
6. Runtime And Hosting Model
7. Delivery And Operability Model
8. POC
9. Evaluation
10. Risks And Refactor Triggers

Use these expectations for each section:

- Problem Analysis: define the current pain, constraints, and organizational context.
- Microservice Fit: state why microservices are or are not justified now, and what entry conditions matter.
- Service Boundaries: define candidate services, responsibilities, autonomy, and build-vs-buy decisions.
- Migration Strategy: define extraction order, transitional glue, compatibility boundaries, and how to keep shipping.
- Platform Capabilities: define gateway, discovery, messaging, health, config, and observability needs.
- Runtime And Hosting Model: define roles, container or host model, lifecycle control, and health behavior.
- Delivery And Operability Model: define source control, CI/CD, artifacts, registry usage, and static-vs-runtime decisions.
- POC: propose the smallest validation slices that prove technical and operational feasibility.
- Evaluation: compare options and state the recommendation.
- Risks And Refactor Triggers: name what scale, org, or reliability changes would force the next architectural step.

## References

- Read `references/microservice-fit-and-boundary-principles.md` when the task is about whether microservices fit, where to cut boundaries, autonomy, technical heterogeneity, or why over-splitting is dangerous.
- Read `references/microservice-evolution-and-build-vs-buy-principles.md` when the task is about staged migration, modularize-then-serviceize strategy, transitional glue code, mature third-party service adoption, or avoiding hype-driven rewrites.
- Read `references/microservice-platform-and-discovery-principles.md` when the task is about API gateways, service discovery, registry patterns, service metadata, internal routing, health checks, or messaging infrastructure.
- Read `references/container-driven-runtime-principles.md` when the task is about container-driven design, runtime roles, self-host vs IIS-style hosting, service lifecycle control, or health and shutdown behavior.
- Read `references/delivery-and-system-as-code-principles.md` when the task is about CI/CD baseline, artifact and package management, infrastructure or site definitions as code, or replacing unnecessary runtime systems with static generation and simpler hosting.
- Keep article-specific notes in `references/`.
- Promote only stable cross-article guidance back into this `SKILL.md`.
