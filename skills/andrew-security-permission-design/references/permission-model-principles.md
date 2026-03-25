# Permission Model Principles

This reference distills Andrew's article:

- Source article: `docs/_posts/2024/2024-05-01-permission-design.md`

## Core Principles

- Permission management is a business problem before it is a technical one.
- Evaluate permission models by both precision and management complexity.
- Role and permission are useful abstractions because they reduce combinatorial explosion, but bad grouping loses critical precision.
- Identity and role checks can solve simple scenarios, but richer systems need explicit permission and operation models.
- A general authorization decision needs at least:
  - who is acting
  - what action is intended
  - what permission data is configured
- Separate the front-side authorization interface from the admin-side permission-definition model.
- Use standard identity abstractions such as principal and identity when they fit.
- Cache or precompute permission sets by stable session context and coarse feature context when direct per-action checks are too expensive.
- Grouping by module, role, group, or policy can turn impossible multiplication of combinations into manageable additive structures.
- Keep data-scope authorization in the model; action permission alone is not enough.

## Derived Workflow

### Model Definition

- Define subject, role, permission, session, and operation.
- Decide what the smallest manageable permission unit is.

### Decision Surface

- Define a permission-check interface that balances correctness and runtime cost.
- Precompute or cache where the same checks repeat densely.

### Management Structure

- Use role, group, policy, or contract layers deliberately to simplify administration.
- Preserve enough expressiveness for critical business boundaries.

## Article-Specific Warnings

- Do not expose a permission matrix so detailed that nobody can operate it.
- Do not hide business-critical scope rules inside ad hoc code.
- Do not assume role checks alone will scale to every product surface.
