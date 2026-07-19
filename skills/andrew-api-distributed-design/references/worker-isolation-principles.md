# Worker Isolation Principles

This reference distills Andrew's article:

- Source article: `docs/_posts/2020/2020-02-09-process-pool.md`

## Core Principles

- Isolation level is an architecture choice with cost, blast radius, and startup-time consequences.
- Compare in-process, thread, app-domain-like, process, and infrastructure-level isolation by what they actually protect.
- Process-level isolation is often the practical upgrade when thread-level isolation is too weak and infrastructure orchestration is too coarse or mismatched.
- Benchmark activation cost and execution cost before choosing an isolation strategy.
- Rebuild only the narrow missing layer when mature infrastructure already solves the rest.
- Keep the scheduling unit and the infrastructure scaling unit distinct when they do not naturally align.

## Derived Workflow

### Isolation Choice

- Ask what must be isolated:
  - memory corruption
  - static state bleed
  - runtime version mismatch
  - bad code crash radius
  - resource exhaustion

### Pool Design

- Define queue, min and max pool size, idle timeout, and scaling behavior.
- Measure startup cost, task throughput, and shutdown behavior.

### Boundary With Infrastructure

- Let infrastructure handle the parts it is already good at.
- Keep custom orchestration focused on the application-specific gap.

## Article-Specific Warnings

- Do not choose infrastructure or framework patterns by fashion alone.
- Do not build a custom runtime if mature infrastructure already fits the real scheduling unit.
- Do not hand off job-level orchestration to service-level tools without checking the mismatch cost.
