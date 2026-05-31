---
name: article-review
description: Review professional article drafts, especially abstracts, motivation, intros, case-driven technical essays, and method writeups. Use when the user wants feedback on structure, argument consistency, professional rigor, or revision principles for ongoing article review.
---

- version: 0.1.0
- created: 2026-03-25

# Article Review

Use this skill when reviewing draft articles, blog posts, talk manuscripts, or professional sharing content.

Prioritize structural judgment over sentence polishing. If the article is incomplete, review only the completed parts and do not treat placeholders as content failures.

## Review Order

Review in this order unless the user asks otherwise:

1. Segment purpose: determine what this section is supposed to do.
2. Structural fit: check whether the section supports the article's stated main theme.
3. Professional rigor: check whether the argument, model, and decision logic are defensible.
4. Writing quality: refine clarity, pacing, redundancy, and wording.

## Core Principles

### 1. Judge each section by its job

Before reviewing any paragraph, identify its role.

- `abstract`: define the question, method, scope, and conclusion direction.
- `motivation`: explain why the article is worth writing now.
- `intro` or `writing up front`: anchor the reading path and set expectations.
- `case section`: prove the argument instead of competing with it.
- `conclusion`: compress the takeaway instead of opening a new topic.

Do not review a section as if it were trying to do the whole article's work.

### 2. Structure first, prose later

Check structure before line edits.

- Is the core thesis visible early enough?
- Do title, abstract, motivation, introduction, and first main section point to the same claim?
- Does the article keep one main thread, or does it drift into a second article?
- Are there duplicate sections, old drafts, or mixed versions in the same file?

If structure is unstable, fix that before polishing wording.

### 3. One paragraph should mainly do one thing

A paragraph should usually have one main function:

- background
- claim
- method
- evidence
- implication

If one paragraph tries to handle background, motivation, method, and conclusion at once, recommend splitting it.

### 4. Abstracts should stay narrow

An `abstract` should usually do four things:

1. State the core question.
2. State the case, method, or lens used to answer it.
3. State what this article is really about.
4. Point to the conclusion direction without expanding the full argument.

Avoid overloading the abstract with:

- long quotations
- detailed tool comparisons
- internal workflow jargon introduced too early
- detailed reading guides
- extended personal reflection better suited for motivation

### 5. Motivation should add value, not repeat the abstract

The `motivation` section should answer:

- Why does this problem matter now?
- Why is this article worth reading?
- Why is the author using this specific case or framing?

If motivation only restates the abstract, flag it as repetition.

### 6. Cases must prove the main point

Case material is supporting evidence, not a competing main story.

For each case, check:

- What is this case validating?
- Why was this case selected?
- Which architectural stress or decision does it expose?
- Does it strengthen the thesis, or distract from it?

### 7. Prefer explicit models over scattered insight

For professional sharing content, look for four required components:

1. The abstract model used for thinking.
2. The key process after the abstraction.
3. The reasons behind decisions, choices, and design tradeoffs.
4. A simple real-world analogy or comparison when helpful.

If these are missing, the article risks becoming opinion without method.

### 8. Watch for the four recurring structural risks

These are high-priority checks:

1. Consistency before and after validation.
2. Alignment with the article's main theme based on title, abstract, introduction, and opening remarks.
3. Breaks in continuity where reasoning jumps without a bridge.
4. Repetition where the same point is restated without adding new information.

### 9. Delay jargon until it earns its place

Do not introduce internal terms, abbreviations, or framework labels too early unless they are necessary for that section.

If jargon is required:

- define it on first use
- explain its role in this article
- keep one stable vocabulary instead of several overlapping ones

### 10. Be explicit about scope

When a draft contains multiple outlines, partial rewrites, notes, or talk fragments, separate:

- the active main draft
- backup draft fragments
- outline notes
- speaker notes or presentation copy

Flag scope mixing as a structural issue.

## Review Output Guidance

When asked for a full article review, organize the feedback in three lenses:

1. Content structure
2. Professional angle
3. Writing and manuscript quality

Within those lenses, prioritize findings in this order:

1. Main-theme drift or inconsistency
2. Missing model, decision logic, or validation path
3. Continuity gaps
4. Redundancy
5. Sentence-level clarity issues

When the user asks to review one specific section, respond with:

1. What is already working
2. What is structurally off
3. What to rewrite or tighten
4. A suggested revised version if useful

## Focused Checklist

### Abstract Checklist

- Is the main question explicit?
- Is the article method or case explicit?
- Is the scope clear?
- Is the core thesis visible?
- Is anything included that belongs in motivation or body sections instead?

### Motivation Checklist

- Does it explain why the article should exist?
- Does it avoid repeating the abstract?
- Does it introduce urgency, context, or author intent cleanly?
- Does it prepare the reader for the article's method?

### Structural Consistency Checklist

- Do title, abstract, motivation, and opening sections agree?
- Does each major section serve the same main thesis?
- Are there hidden draft merges or duplicated versions?
- Does every case section tie back to the promised argument?

### Professional Content Checklist

- Is the argument based on a clear system model?
- Are decision reasons explicit?
- Are tradeoffs and invariants identifiable?
- Are there concrete examples or simple comparisons where needed?

## Maintenance Rule

This skill should evolve through repeated article reviews.

Only add new rules when they are both:

- recurrent across multiple review sessions
- generalizable beyond one specific article

If a rule turns out to be too article-specific, narrow it or remove it in the next revision.
