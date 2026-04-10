---
slug: pfml-claims-lifecycle
feature: PFML Claims Lifecycle
---

# Find: PFML Claims Lifecycle

## Feature Goal

Build the full Paid Family and Medical Leave claims lifecycle — from employee application through eligibility verification, employer response, adjudication, and weekly benefit payments. Four bounded contexts (Claims, Wage Reporting, Payments, Adjudication) integrated via domain events.

## Entry Points

| Level | Location | Who initiates | Data flow |
|-------|----------|---------------|-----------|
| L5 (Driving) | POST `/claims` | Employee | SSN, FEIN, leave type, dates, docs, payment prefs → Claim created |
| L5 (Driving) | POST `/claims/{id}/documents` | Employee | Document upload → S3 reference stored |
| L5 (Driving) | POST `/claims/{id}/employer-response` | Employer | Decision + optional reason → employer response recorded |
| L5 (Driving) | GET `/adjudication/cases` | Adjudicator | List pending/in-review cases |
| L5 (Driving) | PUT `/adjudication/cases/{id}` | Adjudicator | Decision + notes → case completed |
| L5 (Driving) | Scheduled: employer window timeout | EventBridge | Fires when employer response deadline passes |
| L5 (Driving) | Scheduled: weekly payment trigger | EventBridge Scheduler | Fires per-claim on payment day |
| L4 (Driven) | Wage Reporting query | Claims/Payments | SSN + quarter range → wage records |
| L4 (Driven) | RDS PostgreSQL | All contexts | CRUD across claims.*, wages.*, payments.*, adjudication.* schemas |
| L4 (Driven) | S3 document storage | Claims/Adjudication | Upload/download via pre-signed URLs |
| L4 (Driven) | EventBridge event bus | Cross-context | Domain events: ClaimSubmitted, ClaimApproved, ClaimEscalated, etc. |
| L4 (Driven) | Payment gateway | Payments | ACH/check disbursement, status checks |
| L4 (Driven) | AWS KMS | All contexts | Encrypt/decrypt SSN, bank details |

## Scenarios

### Scenario 1: Employee submits a valid claim
**AC:** Given an employee with SSN and employer FEIN, when they submit a claim with leave type, dates, documents, and payment preferences, then a Claim is created with status `SUBMITTED` and a `ClaimSubmitted` event is published.
**Entry points involved:** POST `/claims`, POST `/claims/{id}/documents`, RDS, S3, KMS, EventBridge
**Test outline:** Slice integration (L5) — assert claim persisted, event published, SSN encrypted

### Scenario 2: Eligibility check — eligible
**AC:** Given a submitted claim, when the eligibility check finds wages in the past 4 quarters AND fewer than 20 weeks used this year, then the claim transitions to `AWAITING_EMPLOYER` and an `EmployerNotified` event is published with a scheduled timeout.
**Entry points involved:** Wage Reporting query, RDS, EventBridge, EventBridge Scheduler
**Test outline:** Use case integration (L3) — assert status transition, event published, timeout scheduled

### Scenario 3: Eligibility check — ineligible (no wages)
**AC:** Given a submitted claim, when the eligibility check finds no wages in the past year, then the claim transitions to `DENIED` with denial reason "no qualifying wages" and a `ClaimDenied` event is published.
**Entry points involved:** Wage Reporting query, RDS, EventBridge
**Test outline:** Use case integration (L3) — assert denial with correct reason

### Scenario 4: Eligibility check — ineligible (20 weeks exhausted)
**AC:** Given a submitted claim, when the eligibility check finds the employee has already used 20 weeks this year, then the claim transitions to `DENIED` with denial reason "annual leave exhausted" and a `ClaimDenied` event is published.
**Entry points involved:** Wage Reporting query, RDS, EventBridge
**Test outline:** Use case integration (L3) — assert denial with correct reason

### Scenario 5: Employer responds — no objection
**AC:** Given a claim in `AWAITING_EMPLOYER` status, when the employer responds with `NO_OBJECTION`, then the claim transitions to `APPROVED` and a `ClaimApproved` event is published.
**Entry points involved:** POST `/claims/{id}/employer-response`, RDS, EventBridge
**Test outline:** Slice integration (L5) — assert status transition and approval event

### Scenario 6: Employer response window expires
**AC:** Given a claim in `AWAITING_EMPLOYER` status, when the response window deadline fires, then the employer response is recorded as `WINDOW_EXPIRED`, the claim transitions to `APPROVED`, and a `ClaimApproved` event is published.
**Entry points involved:** Scheduled event (EventBridge), RDS, EventBridge
**Test outline:** Use case integration (L3) — assert silent consent recorded, claim approved

### Scenario 7: Employer objects
**AC:** Given a claim in `AWAITING_EMPLOYER` status, when the employer responds with `OBJECTED` and a reason, then the claim transitions to `ESCALATED` and a `ClaimEscalated` event is published.
**Entry points involved:** POST `/claims/{id}/employer-response`, RDS, EventBridge
**Test outline:** Slice integration (L5) — assert escalation and event published

### Scenario 8: Adjudicator approves escalated claim
**AC:** Given an adjudication case in `PENDING` or `IN_REVIEW` status, when an adjudicator submits decision `APPROVED` with notes, then the case status is `COMPLETED`, an `AdjudicationCompleted` event is published, and the originating claim transitions to `APPROVED` with a `ClaimApproved` event.
**Entry points involved:** PUT `/adjudication/cases/{id}`, RDS, EventBridge
**Test outline:** Slice integration (L5) — assert case completed, claim approved, payment event published

### Scenario 9: Adjudicator denies escalated claim
**AC:** Given an adjudication case, when an adjudicator submits decision `DENIED` with notes, then the case is `COMPLETED`, an `AdjudicationCompleted` event is published, and the originating claim transitions to `DENIED`.
**Entry points involved:** PUT `/adjudication/cases/{id}`, RDS, EventBridge
**Test outline:** Slice integration (L5) — assert case completed, claim denied

### Scenario 10: Payment schedule created on approval
**AC:** Given a `ClaimApproved` event, when Payments consumes it, then it queries wage reporting for the last 4 quarters, calculates weekly benefit as `min(averageQuarterlyWages / 13, stateCeiling)`, and creates a `PaymentSchedule` with individual `Payment` entities (status `SCHEDULED`) for each week of the leave period.
**Entry points involved:** EventBridge (ClaimApproved), Wage Reporting query, RDS
**Test outline:** Use case integration (L3) — assert schedule created, correct number of payments, benefit capped at ceiling

### Scenario 11: Weekly payment disbursed successfully
**AC:** Given a `SCHEDULED` payment and a weekly trigger, when the payment gateway returns success, then the payment transitions to `DISBURSED` with a timestamp and gateway reference, and a `PaymentDisbursed` event is published.
**Entry points involved:** Scheduled event (EventBridge Scheduler), Payment gateway, RDS, EventBridge
**Test outline:** Use case integration (L3) — assert payment status, gateway reference stored

### Scenario 12: Weekly payment fails
**AC:** Given a `SCHEDULED` payment and a weekly trigger, when the payment gateway returns failure, then the payment transitions to `FAILED` and a `PaymentFailed` event is published.
**Entry points involved:** Scheduled event (EventBridge Scheduler), Payment gateway, RDS, EventBridge
**Test outline:** Use case integration (L3) — assert failure status and event published

## Benefit Calculation Formula (Working Assumption)

`weeklyBenefit = min(averageQuarterlyWages / 13, stateCeiling)`

Where `averageQuarterlyWages = sum(last 4 quarters of wages) / 4` and `stateCeiling` is a configurable value. Implemented as a pluggable strategy for future policy changes.

## What Does Done Look Like?

All 12 scenarios pass. An employee can submit a claim, have it checked for eligibility, go through employer notification (with timeout), get escalated or auto-approved, and receive weekly payments. The four bounded contexts communicate via domain events. PII is encrypted at the field level. The system handles the happy path and all denial/failure paths.
