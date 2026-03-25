# Interview Abstraction Principles

This reference distills the current skill draft from Andrew's article:

- Source article: `docs/_posts/2020/2020-03-10-interview-abstraction.md`
- Current scope: first draft only, based on the 2020-03-10 article

## Core Principles

- Treat abstraction as "extract focus, hide detail."
- Choose the abstraction boundary based on the main system's pain point, not by grouping surface-level examples.
- Treat interface or contract design as the concrete output of abstraction work.
- Keep the main flow responsible only for stable questions such as "what inputs exist?" and "what result came back?"
- Hide variable calculation or rule logic behind concrete implementations.
- Use encapsulation to isolate detail and polymorphism to let the main flow treat different implementations the same way.
- Start from a minimal model and refactor only when the current signature no longer carries enough information.
- Introduce a context object when rule processing needs accumulated state, prior discounts, or cross-step visibility.
- Preserve rule order when later rules depend on earlier results.
- Use tags or markers as coordination data for exclusion or pairing, but do not let tag mechanics replace core business semantics.
- Judge success by extension cost: adding a new rule should usually add a new implementation, not rewrite the main flow.
- Balance rigor and flexibility. Avoid both over-designed schema and endless workaround flags.

## Derived Workflow

### Modeling

- Collect concrete cases, but do not let those cases become the architecture.
- Ask which part of the system must remain stable as examples change.
- Write a single contract sentence for the main flow.

### Class

- Define the minimal shared entities, abstract contract, and result object.
- Push specialized behavior into concrete implementations.
- Add context, priority, or coordination metadata only when the scenario proves they are needed.

### Scenario

- Prove the design with a no-special-case baseline first.
- Add different rule shapes one at a time.
- Include stress cases that challenge the boundary: exclusion, pairing, state-sensitive thresholds, and composition.

### POC

- Keep the example executable and inspectable.
- Show input items, applied results, and final outcome.
- Demonstrate that a second or third rule can be added without rewriting the orchestration.

## Article-Specific Warnings

- Do not rely on inductive categorization alone. It handles known examples but fails on future variants.
- Do not leak engineering workaround flags into business-facing setup unless the user explicitly accepts that tradeoff.
- Do not globalize one composite edge case into mandatory fields for every rule.
- Do not mutate shared context everywhere if a result-returning design is sufficient.
- Do not confuse a successful calculation with a successful abstraction. The real test is whether the main flow remains stable.
