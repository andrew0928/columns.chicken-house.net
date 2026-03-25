# Pipeline And Object Stream Principles

This reference distills Andrew's articles:

- Source article: `docs/_posts/2013/2013-04-15-large-data-processing-techniques-async-await.md`
- Source article: `docs/_posts/2019/2019-06-15-netcli-pipeline.md`
- Source article: `docs/_posts/2019/2019-06-20-netcli-tips.md`

## Core Principles

- Separate batch, stream, and pipeline thinking; they optimize different things.
- For staged processing, evaluate at least three metrics:
  - first-result latency
  - total completion time
  - max work-in-progress or intermediate items
- Pipeline processing is valuable when work can overlap by stage without violating order or resource constraints.
- Shape stage contracts so each stage can consume and emit incrementally rather than waiting for whole-batch completion.
- Preserve stage legality explicitly; data should carry enough state or type information to detect invalid transitions.
- Good CLI design is composition-friendly: stages can be chained, restarted selectively, or replaced independently.
- If both sides of a boundary are under your control, stdout and stdin can carry object streams, not only human-readable text.
- Favor transport formats that preserve streaming behavior item by item instead of forcing full-buffer parsing.
- Keep the programming model similar across in-process and cross-process boundaries when possible.

## Derived Workflow

### Analysis

- Decide whether the problem needs batch, stream, or pipeline behavior.
- Identify the slowest stage and the resource each stage consumes.

### Contract

- Define what each stage reads, writes, and guarantees.
- Make restart, replay, or partial rerun possible where it matters.

### Validation

- Measure first-result latency, full completion time, and max in-flight items.
- Compare alternate implementations with the same stage contract.

## Article-Specific Warnings

- Do not build CLI tools that are "usable once" but impossible to compose.
- Do not treat pipeline boundaries as text-only if the real need is structured data transfer.
- Do not optimize throughput without watching intermediate buffering cost and restart behavior.
