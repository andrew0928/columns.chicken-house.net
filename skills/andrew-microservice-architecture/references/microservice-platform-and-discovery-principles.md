# Microservice Platform And Discovery Principles

This reference distills stable ideas from:

- `docs/_posts/2017/2017-07-11-microservice8-case-study-p3.md`
- `docs/_posts/2017/2017-12-31-microservice9-servicediscovery.md`
- `docs/_posts/2018/2018-10-10-microservice11-devopsdays-servicediscovery.md`

## Core Principles

- Microservice benefits depend on platform capabilities that make many services operable together.
- Shared capabilities usually include:
  - API gateway
  - service discovery
  - health checks
  - messaging or event infrastructure
  - centralized logging or tracing
  - configuration management
- Service discovery needs three basics:
  - register
  - query
  - health signal
- DNS is a useful mental model, but dynamic microservice systems usually need richer metadata, health awareness, and faster updates.
- Client-side discovery gives callers more control; server-side discovery centralizes routing and reduces client intrusion.
- Service metadata and tags can encode SLA tiers, regions, or other routing-relevant policy.
- Mature infrastructure products often solve these concerns better than custom code.

## Derived Workflow

### Define The Shared Platform Surface

- List what every service needs from the platform before selecting products.
- Keep the first version minimal, but do not ignore the capabilities the architecture already depends on.

### Design Discovery Explicitly

- Define how services appear, disappear, and prove health.
- Decide where routing logic should live.
- Make metadata part of the design when routing depends on class, region, tenant, or SLA.

### Unify Internal Routing

- Hide unnecessary internal topology from clients.
- Let gateways, registries, or message systems carry routing complexity where appropriate.

## Article-Specific Warnings

- Do not rely on static config files as the long-term answer for large internal service maps.
- Do not copy cloud-provider patterns blindly if the team cannot operate them.
- Do not build many services without first deciding how they will be found, checked, and diagnosed.
