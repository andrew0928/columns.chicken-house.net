# API First Strategy Principles

This reference distills the current skill draft from Andrew's article:

- Source article: `docs/_posts/2022/2022-10-26-apifirst.md`
- Current scope: API-first strategy and contract-first planning

## Core Principles

- Put the API contract first when the service interface is strategic, long-lived, or shared across teams.
- Treat the API as the exposed form of a domain service, not as a thin wrapper around today's UI flow.
- Validate the contract before heavy implementation so stakeholders can react while change is still cheap.
- Prefer stable, minimal API surfaces. Add SDKs, BFFs, templates, or helper layers before adding UI-specific complexity to the core contract.
- Use API boundaries as team communication boundaries. Poor API design may reflect a team or ownership problem, not only a technical problem.
- Focus on doing the right thing before doing the thing well. Early contract validation reduces expensive downstream rework.
- Avoid API-first theater. A well-documented API that does not match the domain is still a failed design.

## Derived Workflow

### Problem Analysis

- Ask why the API should exist and what value it exposes.
- Identify the intended consumers and the long-term reuse expectation.
- Clarify whether the API is exposing data, behavior, workflow, or a combination.

### Contract First

- Define the contract before writing major implementation code.
- Use mocks or low-cost prototypes so front-end, QA, docs, and SDK work can start early.
- Keep the earliest validation focused on domain fit, not framework completeness.

### Boundary Design

- Expose domain-level services and resources, not screen-level details.
- Keep the API smaller than the product surface when possible.
- Push composition and presentation concerns outward unless they are truly core business capabilities.

## Article-Specific Warnings

- Do not let naming standards or framework conventions distract from whether the API solves the business problem.
- Do not assume more endpoints mean a better API.
- Do not design the API around one current app if the goal is long-term reuse across systems.
- Do not skip early feedback on the contract and hope refactoring later will be cheap.
