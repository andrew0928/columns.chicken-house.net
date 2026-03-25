# Deliberate Practice Principles

This reference distills the current skill draft from Andrew's article:

- Source article: `docs/_posts/2021/2021-03-01-practice-01.md`
- Current scope: deliberate practice for architecture and design capability building

## Core Principles

- Treat capability building as a design problem too. Convert vague growth goals into repeatable exercises with clear feedback.
- Build strong foundations before chasing tool breadth. Deep understanding compounds faster than surface familiarity with many frameworks.
- Maintain at least one end-to-end toolchain you can use fluently enough to turn an idea into a runnable experiment without much friction.
- Use deliberate practice to pull learning forward. Do not wait for late-project feedback to discover what the team should have understood earlier.
- Use code to define the problem whenever possible. Executable examples, tests, and metrics make design discussion precise.
- Start from a simple correct baseline, then iterate with measurement. Correctness first, then quality improvements.
- Use metrics as a coach. Each iteration should reveal whether the change improved or degraded the outcome.
- Estimate a theory limit or practical ceiling so optimization has a stopping rule.
- Use exercises to expose unknown unknowns and map missing foundations, not only to show current skill.
- Practice with peers when possible. Comparable code, tests, and metrics make it easier to learn from alternative designs.

## Derived Workflow

### Preparation

- Pick one target capability or design weakness to improve.
- Reduce the problem to a focused exercise that still preserves the essential tradeoff.
- Choose an environment that is cheap to reset, rerun, and share.

### Practice Loop

- Define the problem in code or another executable form.
- Define correctness checks before chasing performance or elegance.
- Define evaluation metrics that can compare multiple versions fairly.
- Build a baseline implementation that is obviously correct, even if not optimal.
- Change one thing at a time and record what the metrics do.

### Reflection

- Ask what missing theory or foundational knowledge blocked further progress.
- Trace the topic outward until you can see which underlying concepts you do not yet control.
- Translate the discovered gaps into the next practice target instead of collecting random new tools.

### Collaboration

- Make the exercise small enough that peers can attempt it independently.
- Compare solutions on shared tests, metrics, and assumptions rather than taste alone.
- Use alternate solutions as stimulus to expand the design space, not just to rank people.

## Article-Specific Warnings

- Do not confuse tool familiarity with deep design ability.
- Do not wait for work assignments alone to provide enough practice opportunities.
- Do not practice directly on noisy production code when a simpler isolated exercise would teach faster.
- Do not keep tuning endlessly once the likely ceiling is clear; switch to the next missing concept instead.
