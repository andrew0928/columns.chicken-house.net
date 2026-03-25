# Distributed Correctness Principles

This reference distills Andrew's articles:

- Source article: `docs/_posts/2018/2018-03-25-interview01-transaction.md`
- Source article: `docs/_posts/2018/2018-04-01-interview02-stream-statistic.md`
- Source article: `docs/_posts/2021/2021-03-15-idempotent-method.md`

## Core Principles

- Keep the invariant explicit. For transaction-like systems, define what must never be lost, doubled, or partially applied.
- The core problem is usually protecting a critical section at the right scope.
- Choose the smallest correct mechanism:
  - local lock
  - database transaction
  - storage-native atomic operation
  - distributed lock
- Prefer built-in atomic operations or trusted libraries over custom low-level coordination.
- Design APIs to be idempotent-safe when retry is unavoidable.
- Use idempotency keys when natural idempotency is unavailable or too weak.
- Reduce repeated computation by maintaining rolling summaries or materialized state when the read pattern is obvious.
- In distributed statistics or counters, move the same data-structure logic to shared storage only after checking the storage supports the needed atomic primitives.
- Distinguish event occurrence time from processing time when late-arriving data changes the interpretation.

## Tradeoff Patterns

### Transaction Correctness

- The same invariant can appear at different scales; only the implementation mechanism changes.
- If the operation spans one strong transactional boundary, use it.
- If the boundary is distributed, define how contention, retry, timeout, and lease expiry are handled.

### Idempotent Retry

- A timeout without a reply does not imply failure or success.
- Safe retry must be an explicit contract property, not just a caller habit.
- Correlation id and idempotency key serve different purposes; do not blur them.

### Continuous Statistics

- If exact raw recalculation is too expensive, pre-aggregate along the problem's natural precision boundary.
- Favor O(1)-style update and read paths when the same statistic is queried repeatedly.

## Article-Specific Warnings

- Do not assume distributed locks are the first answer.
- Do not retry money-like operations blindly.
- Do not move to distributed storage without rethinking atomicity and race conditions.
