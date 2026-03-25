# Delivery And System-As-Code Principles

This reference distills stable ideas from:

- `docs/_posts/2016/2016-09-16-blog-as-code.md`
- `docs/_posts/2017/2017-08-05-what-cicd-do-you-need.md`

## Core Principles

- Start from the delivery problem you need to solve, not from the tool you want to install.
- The minimum reliable delivery baseline is:
  - version control
  - automated build and tests
  - artifact management
  - release management
- Package feeds or image registries should become the trusted handoff point between build and deployment.
- Production artifacts should come from the controlled pipeline, not from a developer laptop.
- Treat content, templates, routing rules, deployment definitions, and build scripts as source-controlled code.
- If a capability does not need runtime decision-making, prefer static generation and simpler hosting.
- Developer-native text formats and version-control workflows can outperform heavyweight admin systems when the domain permits it.
- Keep branch and release flow only as complex as the actual delivery needs.

## Derived Workflow

### Define The Minimal Flow

- Decide how code is versioned.
- Decide how builds and tests are triggered.
- Decide where release artifacts live.
- Decide how environments pull trusted artifacts.

### Simplify Before Scaling

- Reuse existing tools if they are already good enough.
- Add automation gradually after the foundations are stable.

### Move Unnecessary Runtime To Build Time

- Ask whether the system is really making decisions at runtime.
- If not, pre-generate the output and reduce the operational surface.
- Prefer source-controlled, reproducible workflows over opaque admin-only operations.

## Article-Specific Warnings

- Do not overdesign CI/CD before the baseline flow works.
- Do not keep a runtime system alive just to serve precomputed content.
- Do not allow ad hoc production deployments that bypass versioned source and reproducible builds.
