# Interview Abstraction Principles

This reference distills Andrew's article:

- Source article: `docs/_posts/2020/2020-03-10-interview-abstraction.md`

## Core Principles

- Treat abstraction as extracting focus and hiding detail.
- Choose the abstraction boundary from the main design pain point, not from surface categories of known cases.
- The concrete output of abstraction is a stable contract.
- Keep the main flow responsible only for stable questions such as input, output, and ordering.
- Hide variable logic behind implementations.
- Introduce richer context only when the current signature can no longer carry the needed information.
- Preserve rule order when later evaluation depends on earlier results.
- Use coordination markers only for cross-rule collaboration, not as a substitute for the domain model.
- Judge success by extension cost: new rules should usually add implementations, not rewrite orchestration.

## Derived Workflow

### Modeling

- Collect concrete cases, but do not let those cases become the architecture.
- Write one contract sentence for the stable interaction.

### Class

- Define minimal shared entities, the abstract contract, and the result object.
- Push specialized behavior into concrete implementations.

### Scenario

- Prove the design with a no-special-case baseline first.
- Add structurally different rules one at a time.

### POC

- Keep the example executable and inspectable.
- Demonstrate that a second or third rule can be added without rewriting the main flow.

## Article-Specific Warnings

- Do not rely on inductive categorization alone.
- Do not leak engineering workaround flags into business-facing setup unless the tradeoff is explicit.
- Do not confuse a successful calculation with a successful abstraction.
