# Pipeline And Scheduling Principles

This reference distills Andrew's articles:

- Source article: `docs/_posts/2013/2013-04-15-large-data-processing-techniques-async-await.md`
- Source article: `docs/_posts/2019/2019-07-06-pipeline-practices.md`
- Source article: `docs/_posts/2019/2019-08-30-scheduling-practices.md`
- Source article: `docs/_posts/2023/2023-10-01-reorder.md`

## Core Principles

- Overlap work only when the dependency graph allows it.
- Measure staged systems with explicit metrics, not intuition.
- Good metrics often include:
  - time to first result
  - time to last completion
  - average lead time
  - max work in progress
  - buffer usage
  - delay average and standard deviation
  - drop, skip, or retry counts
  - cost score for polling or lock attempts
- Identify the bottleneck stage and estimate the theory limit before heavy optimization.
- For scheduler-like systems, balance precision against polling cost explicitly.
- For multi-instance schedulers, prevent duplicate execution even under race, restart, or shutdown.
- Early lock can improve latency but raises shutdown and collision risk; treat lead time as a tunable design parameter.
- Add controlled randomness when many instances would otherwise collide on the same precise timing.
- Use compact simulations and repeated benchmark runs to compare parameter sets.

## Derived Workflow

### Analysis

- Define the hard guarantee and the time window.
- List external uncertainty and internal control knobs separately.

### Design

- Separate scanning, lock acquisition, execution, and completion responsibilities.
- Keep stage contracts explicit enough to observe ordering, waiting, and backlog.

### Evaluation

- Compare measured results against the theory limit or target window.
- Optimize the real bottleneck first.

## Article-Specific Warnings

- Do not tune worker counts or poll intervals before deciding what metric should improve.
- Do not optimize throughput while ignoring duplicate execution or delay variance.
- Do not mistake one passing happy-path test for scheduler correctness.
