# Data Shape And Storage Principles

This reference distills Andrew's articles:

- Source article: `docs/_posts/2013/2013-03-12-azure-multi-tenancy-application-1-design-concepts.md`
- Source article: `docs/_posts/2013/2013-03-17-azure-multi-tenancy-application-2-data-layer-choices.md`
- Source article: `docs/_posts/2013/2013-03-21-azure-multi-tenancy-application-3-data-layer-implementation.md`
- Source article: `docs/_posts/2019/2019-06-01-nested-query.md`
- Source article: `docs/_posts/2020/2020-07-01-microservice14-database.md`

## Core Principles

- Storage choice is an architecture decision, not a product popularity contest.
- Start from the hardest requirement or bottleneck, then choose the storage model that handles that constraint best.
- Do not ask "RDBMS or NoSQL" in the abstract; ask what data shape, consistency need, access path, and scale limit you actually face.
- When one storage style cannot satisfy all constraints cleanly, combine complementary techniques instead of forcing a false binary choice.
- Make scope boundaries explicit in data access. Tenant or partition filtering should be safe by default, not an optional caller convention.
- Separate shared data from scoped data explicitly.
- When the domain shape does not fit the storage shape, pay the translation cost deliberately through indexes, projections, or materialized structures.
- Judge schema and index strategy by dominant operations, especially at realistic scale.
- Moving complexity from read time to write time is often worth it when the target queries dominate the business value.
- If SQL or storage-native logic becomes too awkward, some indexing or reshaping logic belongs in the application layer.

## Tradeoff Patterns

### Multi-Tenancy

- Isolation, cost, and operational simplicity trade against each other.
- If the target is large-scale SaaS, the data model must scale with tenant count, not only with one tenant's convenience.
- Provide an access abstraction that makes one tenant feel logically isolated even when physical storage is shared.

### Tree-Like Data On Relational Storage

- Tree structures do not naturally fit flat relational tables.
- Choose representation by the operations that matter most: recursive search, move, delete, or maintenance cost.
- Benchmark realistic data volume before concluding that the most intuitive schema is acceptable.
- Precomputed range indexes or equivalent materialization can be worth the write-time maintenance cost.

### RDBMS And NoSQL

- RDBMS excels at normalized relational queries and delegated index/query optimization.
- NoSQL excels at object-shaped state, key-based access, and scale-out-friendly patterns.
- Once service boundaries eliminate cross-database joins anyway, precise API and access-path design matter more than nostalgia for SQL flexibility.

## Article-Specific Warnings

- Do not let early developer convenience override the scale target.
- Do not assume one elegant schema solves every query shape efficiently.
- Do not postpone all indexing and materialization decisions if the dominant workload is already clear.
