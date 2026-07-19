# Microservice Evolution And Build-Vs-Buy Principles

This reference distills stable ideas from:

- `docs/_posts/2016/2016-10-03-microservice2.md`
- `docs/_posts/2017/2017-05-20-microservice8-case-study-p2.md`

## Core Principles

- Prefer staged refactoring over rewrite-from-scratch.
- Stop enlarging the monolith before trying to split it.
- Move through reuse levels deliberately:
  - source code
  - library
  - component
  - service
- Modularization is often the prerequisite for later service extraction.
- Transitional glue code is acceptable when it lowers migration risk, but it should remain disposable.
- Choose extraction order by business impact and feasibility, not by trend.
- Use focused spikes and POCs to validate risky assumptions early.
- Not every capability should be self-built; a mature external service is often the better architectural choice.
- A good service owns a complete capability, not only a technical fragment.

## Derived Workflow

### Prepare The Codebase

- Introduce interfaces, factories, or other separation points before remote extraction.
- Reduce coupling locally before introducing network coupling.

### Migrate Incrementally

- Route new capabilities to new services before attacking all legacy code at once.
- Keep the system releasable during the migration.
- Accept temporary duplication when it buys safer evolution.

### Choose Build Vs Buy Deliberately

- Replace infrastructure-heavy custom components with proven services when that lowers long-term maintenance.
- Judge the choice by fit and operability, not by what is currently fashionable.

## Article-Specific Warnings

- Do not rewrite the system only because the old code is frustrating.
- Do not keep transitional glue forever and pretend it is final architecture.
- Do not adopt a popular tool if it does not solve the actual problem better than a mature alternative.
