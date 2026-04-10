# PFML System Design — Take-Home

## How I approached this

The prompt came from [`brief.md`](./brief.md). State is launching a Paid Family and Medical Leave program — employees apply for up to 20 weeks of paid leave, the system needs to handle the full lifecycle from application through weekly payments.

I read through the brief and started thinking through the design tree — what are all the things we actually have to account for here? Eligibility checks against wage history, employer notification windows with silent consent, escalation to human adjudicators, weekly benefit payments with a state-defined ceiling. I worked through all of that and wrote it up in the [design doc](./design.md). - AI rubber ducking approach via design tree walk through prompting.

## The methodology

From the design doc, I ran through a methodology I use called FAAS (Find, Arch, Automate, Specify-Test-Refine) - picked up this approach via breeding domain driven design and responsibility driven design together. You can see the artifacts in [`faas/pfml-claims-lifecycle/`](./faas/pfml-claims-lifecycle/).

The **Find** step is where I mapped out every entry point and exit point of the system — both the driving side (API endpoints, scheduled events) and the driven side (database, S3, EventBridge, payment gateway, KMS). Then I listed out all 12 scenarios that cover the claim lifecycle end to end. Each scenario has acceptance criteria and a test outline. (AI assisted for scenario concepting)

The **Arch** step is where I assigned responsibilities using CRC cards — who knows what, who does what, who collaborates with who. This gave me the full file change list and the implementation order.

The **Automate** step is where I scaffolded out all the tests first. 58 tests across L1 (unit), L2 (domain), L3 (use case), and L5 (slice) layers — all failing with `NotImplementedError`. Clean scaffold, all imports resolving, fakes wiring correctly. Zero errors, just 58 red tests waiting for implementations.

## How the code got written

Once the test scaffolding was in place, I AI-generated the majority of the stubs. The tests were designed from the Find step and the design doc, so the AI had clear acceptance criteria to work against. Most of the domain logic inside the stubs — claim state transitions, eligibility rules, benefit calculation — was generated and then verified against the tests.

There's also an [integration test](./tests/integration/test_claim_lifecycle.py) that wires up all four bounded contexts with in-memory fakes and runs through the happy path, the escalation path, and both denial paths end to end. That one is the real proof that the contexts integrate correctly through domain events.

## Architectural decisions worth calling out

Anything that touches external infrastructure — AWS services like EventBridge for the event bus, RDS Postgres for persistence, S3 for document storage, KMS for field-level encryption — is decoupled from the domain layer behind ports (Python Protocols). The domain doesn't know or care about any of that. Same goes for authentication and the payment gateway. Those need anti-corruption layers.

The reason I separated all of that out is that these are big architectural decisions that need to be made with the team. Which payment processor? What does the state's identity infrastructure look like? How exactly are we integrating with the existing wage reporting system that employers have been submitting to for over a year? The internal design of the system shouldn't be coupled to those answers, because if there's ever a need to migrate away from any of them, you should be able to swap an adapter without touching domain logic.

The system is structured as a modular monolith with four bounded contexts — Claims, Wage Reporting, Payments, and Adjudication. They communicate through domain events. If any of them needs to be extracted into its own service later, the event-driven integration means that's a deployment change, not a redesign. I went with this decision because I'm aware of at least knowledge of how some projects like to do things where teams own like a vertical slice of functionality. And this was a good way to do that as a conceptual architectural decision very early in the design of this application to support teams being able to come in and build and own a bounded context, which is a concept from DDD.

## What's here vs. what's not

**What's here:** The full domain model, all use cases, domain events, cross-context event wiring, test fakes, and comprehensive test coverage across all layers. A [ubiquitous language glossary](./UBIQUITOUS_LANGUAGE.md) that pins down every term in the domain so there's no ambiguity.

**What's not here:** Real infrastructure adapters (Postgres repositories, S3 client, EventBridge publisher, KMS encryption). Auth middleware. The actual payment gateway integration. Those are all behind ports — the contracts are defined, the implementations are pluggable, but the concrete adapters are out of scope for this exercise.

## Running the tests

```bash
uv sync
uv run pytest
```
