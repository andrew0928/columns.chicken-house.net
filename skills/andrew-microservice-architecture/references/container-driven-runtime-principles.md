# Container-Driven Runtime Principles

This reference distills stable ideas from:

- `docs/_posts/2017/2017-05-28-aspnet-msa-labs1.md`
- `docs/_posts/2018/2018-05-12-msa-labs2-selfhost.md`

## Core Principles

- A service is usually more than one web endpoint; runtime roles may include proxy, worker, scheduler, SDK, and updater.
- Container-driven design works best when deployment shape is considered early, not after implementation.
- One process per container is a strong default because lifecycle becomes explicit and controllable.
- In containerized systems, runtime hosts should align with container lifecycle.
- Choose self-hosted service processes when startup, shutdown, health reporting, or deregistration timing must be precise.
- Do not keep heavyweight hosting layers if orchestration already provides equivalent lifecycle and management behavior.
- Treat image build, volume boundaries, and runtime composition as part of the design contract.

## Derived Workflow

### Model Runtime Roles

- Identify all executable roles needed around the capability.
- Decide which roles scale independently and which stay single-purpose.

### Align Lifecycle With The Platform

- Ensure service registration, health signaling, and shutdown handling map cleanly to process start and stop.
- Let orchestration own restart and placement concerns when possible.

### Package For Repeatability

- Build images as immutable deployable artifacts.
- Keep external storage and configuration surfaces explicit.
- Use composition files or equivalent manifests as repeatable runtime definitions.

## Article-Specific Warnings

- Do not assume IIS-style hosting is automatically the right fit inside containers.
- Do not hide startup and shutdown behavior behind hosting layers you cannot precisely control.
- Do not treat containerization as only a deployment step; it changes runtime design choices too.
