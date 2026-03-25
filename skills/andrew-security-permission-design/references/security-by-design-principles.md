# Security By Design Principles

This reference distills Andrew's article:

- Source article: `docs/_posts/2020/2020-11-23-security-talk.md`

## Core Principles

- Security is a quality requirement, not only a feature checklist.
- Quality problems are usually solved by correct design decisions early, not by late patching alone.
- Trust comes from doing the right thing structurally, not from promising to be careful.
- Prefer proven cryptographic algorithms and standard frameworks over custom mechanisms.
- Hash passwords instead of storing raw passwords.
- Validate signed or encrypted tokens on every relevant request; skipping checks creates blind spots.
- Authorization design must be centralized enough that one forgotten check cannot become the system's weakest link.
- Security requires reducing exposed surfaces and enforcing rules at the real data or API boundary.

## Article-Specific Warnings

- Do not sacrifice security first when time is tight.
- Do not rely on UI hiding as authorization.
- Do not assume one passed test means the system is secure.
