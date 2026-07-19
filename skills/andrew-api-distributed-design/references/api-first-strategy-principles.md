# API First Strategy Principles

This reference distills Andrew's article:

- Source article: `docs/_posts/2022/2022-10-26-apifirst.md`

## Core Principles

- Put the API contract first when the service interface is strategic, long-lived, or shared across teams.
- Treat the API as the exposed form of a domain service, not as a wrapper around today's UI flow.
- Validate the contract before heavy implementation so change remains cheap.
- Prefer stable, minimal API surfaces.
- Use API boundaries as communication boundaries between teams and systems.
- Focus on domain fit before framework completeness.

## Article-Specific Warnings

- Do not design the API around one current screen flow if the goal is reuse.
- Do not assume more endpoints mean a better API.
- Do not skip early contract feedback and hope later refactoring will stay cheap.
