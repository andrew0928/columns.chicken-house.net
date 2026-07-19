# Messaging And Operation Principles

This reference distills Andrew's article:

- Source article: `docs/_posts/2019/2019-01-01-microservice12-mqrpc.md`

## Core Principles

- Message Queue is not only for fire-and-forget events; it can support one-way delivery and RPC if the contract is explicit.
- Abstract queue plumbing into team-facing client and worker interfaces before broad adoption.
- Distinguish payload shape from message envelope metadata.
- Use correlation id and reply routing explicitly for RPC-style messaging.
- Prefer dedicated or well-scoped reply channels so returned results are not blocked by unrelated traffic.
- Propagate tracking context across service boundaries so logs and traces can be stitched back together.
- Integrate transport abstractions with dependency injection or scoped execution so contextual data is hard to forget.
- Design workers for operation: graceful shutdown, startup behavior, scale-out, and queue draining are architectural concerns.
- Let Ops scale instance count with normal infrastructure controls; application design should cooperate with that model.

## Derived Workflow

### Abstraction

- Define a message client contract.
- Define a worker contract with a delegated handler.
- Keep shared transport details out of business handlers.

### RPC Over Messaging

- Define reply routing, correlation, and completion behavior.
- Keep reply handling efficient and client-scoped where appropriate.

### Operational Design

- Support graceful shutdown.
- Keep configuration centralized.
- Make startup and shutdown behavior automation-friendly.

## Article-Specific Warnings

- Do not leak raw broker complexity into every service team.
- Do not treat context propagation as optional if cross-service diagnosis matters.
- Do not call a service "DevOps-ready" if it cannot scale or shut down cleanly.
