# Paid Family and Medical Leave System Design

## 1. Overview & Problem Statement

The state is launching a Paid Family and Medical Leave (PFML) program. Employers have been contributing payroll deductions for over a year. Employees will soon be able to apply for up to 20 weeks of paid leave per year for child bonding or medical reasons. State staff will adjudicate claims that require human review.

This document describes the system that manages the full lifecycle: application intake, eligibility verification, employer notification, adjudication, and weekly benefit payments. The design follows Domain-Driven Design principles, organizing the system around bounded contexts with domain events as the integration mechanism.

## 2. Goals

- Accept and process employee leave applications with required documentation
- Verify eligibility based on wage history and prior leave usage
- Notify employers and enforce a fixed response window for discretionary decisions
- Auto-approve claims that pass all checks; escalate edge cases to human adjudicators
- Calculate and disburse weekly benefit payments based on wage history with a state-defined ceiling
- Securely handle PII including SSNs, bank accounts, and medical documents

## 3. Non-Goals

- **Employer-facing wage reporting portal** — employers have been contributing for over a year; that intake system already exists
- **Detailed GRC implementation** — the brief explicitly defers this; we identify areas of concern but do not detail controls
- **Cloud provider evaluation** — AWS is the given platform
- **Fraud detection** — important for a future phase, not v1
- **Appeals process** — denied claimants will need a path to appeal, but this is out of scope for initial launch
- **Reporting and analytics** — the state will want operational dashboards; this is a separate concern
- **Multi-language support and accessibility** — critical for a public-facing government system but not a backend design concern

## 4. Bounded Contexts & Context Map

The system is decomposed into four bounded contexts, each with its own ubiquitous language, aggregates, and lifecycle.

### Claims

Owns the full lifecycle of a leave request — from submission through eligibility determination, employer response, and final status (approved, denied, or escalated). This is the core orchestrating context.

### Wage Reporting

Owns employer payroll contribution data. Quarterly wage reports exist independently of any claim — employers have been submitting them for over a year. Multiple consumers depend on this data: Claims for eligibility checks, Payments for benefit calculation.

### Payments

Owns benefit calculation, weekly payment scheduling, and disbursement. Activated when a claim is approved. Manages payment methods (check, direct deposit) and individual payment lifecycle.

### Adjudication

Owns the human review workflow for escalated claims. Operates as a work queue — claims that cannot be auto-approved or auto-denied are surfaced to state adjudicators for decision.

### Context Relationships

- **Claims ↔ Wage Reporting**: Claims queries Wage Reporting synchronously via an anti-corruption layer to determine eligibility. This is a blocking check — a claim cannot proceed without wage history.
- **Claims → Adjudication**: Claims publishes `ClaimEscalated` domain events. Adjudication consumes them and creates review cases.
- **Adjudication → Claims**: Adjudication publishes `AdjudicationCompleted` events. Claims consumes them and transitions claim status.
- **Claims → Payments**: Claims publishes `ClaimApproved` events. Payments consumes them and creates payment schedules.
- **Wage Reporting → Payments**: Payments queries Wage Reporting to calculate benefit amounts.

## 5. Domain Model

### Claims Context

**Claim** (Aggregate Root)
- `claimId`: unique identifier
- `employeeSSN`: encrypted, identifies the applicant
- `employerFEIN`: identifies the employer
- `leaveType`: `BONDING` | `MEDICAL`
- `leaveStartDate`, `leaveEndDate`: requested leave period
- `status`: `SUBMITTED` | `ELIGIBILITY_CHECK` | `AWAITING_EMPLOYER` | `APPROVED` | `DENIED` | `ESCALATED`
- `documents`: list of `Document` entities
- `employerResponse`: `EmployerResponse` value object
- `denialReason`: nullable, set on denial

**Document** (Entity)
- `documentId`: unique identifier
- `type`: `BIRTH_CERTIFICATE` | `DOCTORS_NOTE` | `OTHER`
- `storageReference`: S3 key
- `uploadedAt`: timestamp

**EmployerResponse** (Value Object)
- `decision`: `OBJECTED` | `NO_OBJECTION` | `WINDOW_EXPIRED`
- `respondedAt`: timestamp
- `reason`: nullable, provided if objected

### Wage Reporting Context

**EmployerWageReport** (Aggregate Root)
- `reportId`: unique identifier
- `employerFEIN`: identifies the employer
- `quarter`: year + quarter (e.g., 2025-Q3)
- `submittedAt`: timestamp
- `employeeWageRecords`: list of `EmployeeWageRecord` entities

**EmployeeWageRecord** (Entity)
- `recordId`: unique identifier
- `employeeSSN`: encrypted
- `wagesReported`: decimal amount for the quarter

### Payments Context

**PaymentSchedule** (Aggregate Root)
- `scheduleId`: unique identifier
- `claimId`: reference to the originating claim
- `weeklyBenefitAmount`: calculated amount after applying state formula and ceiling
- `paymentMethod`: `PaymentMethod` value object
- `startDate`, `endDate`: payment period
- `payments`: list of `Payment` entities

**Payment** (Entity)
- `paymentId`: unique identifier
- `weekStartDate`: the week this payment covers
- `amount`: decimal
- `status`: `SCHEDULED` | `PROCESSING` | `DISBURSED` | `FAILED`
- `disbursedAt`: nullable timestamp

**PaymentMethod** (Value Object)
- `type`: `CHECK` | `DIRECT_DEPOSIT`
- `mailingAddress`: nullable, for checks
- `bankRoutingNumber`: encrypted, nullable, for direct deposit
- `bankAccountNumber`: encrypted, nullable, for direct deposit

### Adjudication Context

**AdjudicationCase** (Aggregate Root)
- `caseId`: unique identifier
- `claimId`: reference to the escalated claim
- `escalationReason`: why auto-processing couldn't resolve it
- `status`: `PENDING` | `IN_REVIEW` | `COMPLETED`
- `decision`: nullable, `APPROVED` | `DENIED`
- `adjudicatorNotes`: text
- `decidedAt`: nullable timestamp

## 6. Domain Events & Integration

### Claims Lifecycle Events

These events represent the state transitions of a claim as it moves through the system:

1. **`ClaimSubmitted`** — Employee files the application. Contains claim details, leave type, dates, and document references.

2. **`EligibilityCheckStarted`** — Triggers a synchronous query to Wage Reporting to retrieve the last 4 quarters of wages and a check against prior leave usage.

3. **`EligibilityDetermined`** — Result of the eligibility check.
   - If **ineligible** (no wages in past year or 20 weeks exhausted): transitions directly to `ClaimDenied`.
   - If **eligible**: proceeds to employer notification.

4. **`EmployerNotified`** — Employer is notified of the claim. Starts the fixed response window. An EventBridge scheduled event is created for the window deadline.

5. **`EmployerResponseReceived`** — Employer explicitly responds within the window. If objected, claim is escalated. If no objection, claim proceeds.

6. **`EmployerResponseWindowExpired`** — Timeout event fires. Silence is treated as no objection. Claim proceeds.

7. **`ClaimAutoApproved`** — All checks passed, no employer objection. Published to Payments context to initiate payment scheduling.

8. **`ClaimEscalated`** — Employer objected or edge case detected. Published to Adjudication context.

9. **`ClaimDenied`** — Auto-denied due to ineligibility.

### Cross-Context Events

- **`AdjudicationCompleted`** (Adjudication → Claims) — Carries the adjudicator's decision. Claims consumes this and transitions the claim to `APPROVED` or `DENIED`. If approved, Claims publishes `ClaimApproved` to Payments.

- **`ClaimApproved`** (Claims → Payments) — Triggers creation of a `PaymentSchedule`. Payments queries Wage Reporting for benefit calculation.

- **`PaymentDisbursed`** / **`PaymentFailed`** (Payments, internal) — Tracks individual payment outcomes for auditability.

## 7. Infrastructure & AWS Architecture

### Application Layer

**Modular Monolith** deployed on **ECS Fargate** behind an **Application Load Balancer**. The four bounded contexts are organized as internal modules with clear interfaces — separate packages/namespaces, not separate services. They share a deployment unit but enforce boundaries through domain events and explicit APIs between modules.

This gives clean separation of concerns with low operational overhead. If a context needs to be extracted into its own service later (e.g., Payments for independent scaling or compliance isolation), the event-driven integration makes that a deployment change, not a redesign.

### Data Layer

**Amazon RDS PostgreSQL** — single primary instance. The data model is relational and the query patterns are predictable (claims by status, wage records by SSN + quarter, payments by schedule). PostgreSQL handles this naturally.

Tables are organized by bounded context with schema-level separation (e.g., `claims.*`, `wages.*`, `payments.*`, `adjudication.*`). This enforces access boundaries at the database level and provides a clear extraction path if a context is split into its own service.

### Encryption

- **RDS encryption at rest** — baseline for all data
- **Field-level encryption via AWS KMS** — applied to SSN, bank routing/account numbers. These fields are encrypted before storage and decrypted only when needed by authorized operations. KMS key policies restrict which IAM roles can decrypt, providing an additional access control layer beyond database permissions.

### Event Infrastructure

**Amazon EventBridge** serves as the event bus for domain events between bounded contexts. EventBridge also handles:

- **Scheduled events** for employer response window timeouts (per-claim deadline)
- **Per-claim payment schedules** — each approved claim registers its own weekly payment event via EventBridge Scheduler

This event-driven approach means a failure in one payment doesn't block others, and each claim's lifecycle is independently observable.

### Document Storage

**Amazon S3** with:
- Server-side encryption (SSE-S3 or SSE-KMS)
- Bucket policies restricting access to the application layer
- Pre-signed URLs for secure upload/download by employees and adjudicators
- Lifecycle policies for retention management

### Authentication & Authorization

Authentication and authorization are treated as external dependencies. The system requires:

- **MFA** for all user types
- **Role-based access control** with distinct roles: employee (applicant), employer, state adjudicator, system administrator
- **Session management** with appropriate timeouts
- **Separate authentication paths** for public users (employees/employers) and internal users (state staff)

The implementation would integrate with the state's existing identity infrastructure — the specific provider is outside the scope of this design.

### Payment Gateway

Payments are disbursed through an external payment gateway that supports ACH (direct deposit) and check disbursement. The system defines a **payment gateway interface** with operations:

- `initiateDisbursement(paymentId, amount, paymentMethod)` → `disbursementReference`
- `checkDisbursementStatus(disbursementReference)` → `status`
- `cancelDisbursement(disbursementReference)` → `success/failure`

The specific vendor is a procurement decision. The interface supports either a SaaS payment platform or direct ACH integration behind an adapter.

## 8. Data Model

### claims schema

```
claims.claim
  - claim_id          UUID PRIMARY KEY
  - employee_ssn      BYTEA (encrypted)
  - employer_fein     VARCHAR
  - leave_type        VARCHAR (BONDING, MEDICAL)
  - leave_start_date  DATE
  - leave_end_date    DATE
  - status            VARCHAR
  - denial_reason     VARCHAR NULLABLE
  - submitted_at      TIMESTAMP
  - updated_at        TIMESTAMP

claims.document
  - document_id       UUID PRIMARY KEY
  - claim_id          UUID REFERENCES claims.claim
  - type              VARCHAR
  - s3_key            VARCHAR
  - uploaded_at       TIMESTAMP

claims.employer_response
  - claim_id          UUID PRIMARY KEY REFERENCES claims.claim
  - decision          VARCHAR
  - reason            TEXT NULLABLE
  - responded_at      TIMESTAMP
```

### wages schema

```
wages.employer_wage_report
  - report_id         UUID PRIMARY KEY
  - employer_fein     VARCHAR
  - quarter           VARCHAR (e.g., 2025-Q3)
  - submitted_at      TIMESTAMP

wages.employee_wage_record
  - record_id         UUID PRIMARY KEY
  - report_id         UUID REFERENCES wages.employer_wage_report
  - employee_ssn      BYTEA (encrypted)
  - wages_reported    DECIMAL(12,2)
```

### payments schema

```
payments.payment_schedule
  - schedule_id           UUID PRIMARY KEY
  - claim_id              UUID
  - weekly_benefit_amount DECIMAL(10,2)
  - payment_type          VARCHAR (CHECK, DIRECT_DEPOSIT)
  - mailing_address       TEXT NULLABLE
  - bank_routing_number   BYTEA NULLABLE (encrypted)
  - bank_account_number   BYTEA NULLABLE (encrypted)
  - start_date            DATE
  - end_date              DATE
  - created_at            TIMESTAMP

payments.payment
  - payment_id        UUID PRIMARY KEY
  - schedule_id       UUID REFERENCES payments.payment_schedule
  - week_start_date   DATE
  - amount            DECIMAL(10,2)
  - status            VARCHAR
  - disbursed_at      TIMESTAMP NULLABLE
  - gateway_reference VARCHAR NULLABLE
```

### adjudication schema

```
adjudication.case
  - case_id            UUID PRIMARY KEY
  - claim_id           UUID
  - escalation_reason  TEXT
  - status             VARCHAR
  - decision           VARCHAR NULLABLE
  - adjudicator_notes  TEXT NULLABLE
  - decided_at         TIMESTAMP NULLABLE
  - created_at         TIMESTAMP
```

## 9. Scaling Considerations

The system is designed to handle thousands of concurrent applications. At this scale, PostgreSQL and a horizontally scaled application layer are sufficient.

- **Application layer**: ECS Fargate tasks scale horizontally behind the ALB. Claim submission, eligibility checks, and adjudicator workflows are stateless request/response operations.
- **Database**: A properly indexed PostgreSQL RDS instance handles this throughput. Key indexes: `claim.employee_ssn` + `claim.status`, `employee_wage_record.employee_ssn` + `employer_wage_report.quarter`, `payment.status` + `payment.week_start_date`.
- **Event processing**: EventBridge natively handles the event throughput. Per-claim payment scheduling distributes payment processing load naturally — there is no single batch job that could become a bottleneck.
- **Document storage**: S3 scales without intervention.

If the program grows significantly beyond initial projections, the modular monolith architecture allows extracting bounded contexts into independent services. The event-driven integration means this is a deployment and infrastructure change, not an application redesign.

## 10. GRC Concerns

### PII Handling

**Risk**: The system stores SSNs, bank account numbers, and mailing addresses. A data breach exposes highly sensitive personal information for every applicant.

**Mitigation**:
- Field-level encryption (AES-256 via AWS KMS) for SSN and bank account fields. Raw values never exist in the database.
- KMS key policies restrict decryption to specific IAM roles — the application's read path for display and the payment gateway integration. Adjudicators see masked values (last 4 digits) unless explicitly authorized.
- All access to PII fields is audit-logged (CloudTrail for KMS decrypt calls).
- Database schema separation by bounded context limits the blast radius of a compromised module.
- Network isolation: RDS is in a private subnet, accessible only from the application layer.

### Medical Documentation

**Risk**: Doctor's notes and medical records create HIPAA-adjacent exposure. Even if the state program is not a HIPAA covered entity, leaking medical information carries severe legal and political consequences.

**Mitigation**:
- Documents are stored in S3 with server-side encryption and restrictive bucket policies.
- Access is role-restricted: adjudicators can view documents for cases assigned to them. Employers cannot access medical documentation under any circumstances.
- Pre-signed URLs with short expiration (minutes, not hours) for document access — no persistent download links.
- Retention policy required: medical documents should be purged after a state-defined period post-claim closure. S3 lifecycle policies enforce this automatically.
- Audit logging on all document access (S3 access logs + application-level logging).

### Employer Discretion Denials

**Risk**: Employers can effectively deny leave at their discretion. This creates risk of discriminatory denial patterns — e.g., systematically objecting to bonding leave for certain demographics. The state program could face legal liability if it enables discrimination without oversight.

**Mitigation**:
- Every employer response (objection, reason, timestamp) is recorded as an immutable audit trail.
- The system should surface aggregate denial patterns per employer to state administrators (e.g., employer X has objected to 90% of bonding leave claims).
- Employer objections do not auto-deny — they escalate to human adjudicators who can override.
- The adjudicator's decision and rationale are recorded, creating a reviewable record for each discretionary case.
- This is a strong candidate for future analytics and automated flagging of anomalous employer behavior.

## 11. Alternatives Considered

### Microservices vs Modular Monolith

We considered deploying each bounded context as an independent service. This would provide independent scaling, separate deployment lifecycles, and stronger isolation. However, for a v1 system with four bounded contexts and modest scale requirements, the operational overhead of managing multiple services, service discovery, distributed tracing, and network-based communication outweighs the benefits. The modular monolith provides clean separation through internal module boundaries and domain events. The event-driven architecture preserves the extraction path — any context can be split into its own service later without redesigning the integration layer.

### PII Vault vs Field-Level Encryption

A dedicated PII vault service (tokenizing SSNs and bank details, isolating them in a separate data store with independent access controls) would provide the strongest data protection posture. It limits breach blast radius to the vault service and simplifies compliance scope for the main application. We chose field-level encryption with KMS as a pragmatic middle ground for v1 — it provides strong protection without the operational complexity of a separate service. The vault pattern is the recommended evolution for a future phase, particularly as the system matures and GRC requirements are detailed.

### Fully Manual Adjudication vs Tiered Auto-Approve

The brief states that state staff are "prepared to adjudicate claims as they come in," which could imply all claims go through manual review. We chose a tiered approach where claims that pass all automated checks (eligible wages, leave balance available, no employer objection) are auto-approved, and only edge cases are escalated to human adjudicators. This reduces the burden on state staff, accelerates the happy path for applicants, and allows human attention to focus on cases that genuinely need judgment. The automated eligibility rules are straightforward and deterministic — there is low risk in auto-applying them.

### Batch Payment Processing vs Per-Claim Event-Driven Scheduling

A traditional approach would run a weekly batch job that queries all active claims and issues payments. This is simpler to reason about but creates a single point of failure — if the batch job fails, all payments are delayed. Per-claim scheduling via EventBridge Scheduler distributes the processing, provides individual payment observability, and means a failure for one payment doesn't affect others. The tradeoff is more moving parts to monitor, but EventBridge provides native observability for scheduled events.

## 12. Unresolved Questions

1. **Benefit calculation formula** — The system is designed to accept a configurable formula with inputs (quarterly wages, state ceiling, replacement rates). The specific formula — whether it uses a tiered replacement rate, a flat percentage, or another model — is a state policy decision that must be defined before implementation.

2. **Employer response window duration** — We've designed for a fixed window with silent consent, but the actual duration (5 business days? 10 calendar days?) is a policy decision with legal implications.

3. **Document retention policy** — How long are medical documents, claim records, and PII retained after a claim closes? This has GRC, storage cost, and legal discovery implications that need state input.

4. **Integration with existing wage reporting system** — Employers have been submitting payroll contributions for over a year. What is the API contract or data format of the existing system? Is it a database we query, an API we call, or a file feed we ingest?

5. **Overlapping leave edge cases** — Can an employee file for bonding leave and medical leave concurrently? Does concurrent leave count as one period or two against the 20-week annual cap? This is a domain question that requires stakeholder input and would surface naturally in event storming sessions.
