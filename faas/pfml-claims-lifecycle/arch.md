---
slug: pfml-claims-lifecycle
feature: PFML Claims Lifecycle
---

# ARCH: PFML Claims Lifecycle

## Responsibilities

### Doings
- Accept and validate claim submission → `SubmitClaimUseCase` (Controller, L3)
- Check eligibility (wages + leave balance) → `CheckEligibilityUseCase` (Controller, L3)
- Record employer response → `RecordEmployerResponseUseCase` (Controller, L3)
- Handle employer window expiration → `HandleEmployerTimeoutUseCase` (Controller, L3)
- Apply adjudication result to claim → `ApplyAdjudicationResultUseCase` (Controller, L3)
- Create adjudication case from escalation → `CreateAdjudicationCaseUseCase` (Controller, L3)
- Record adjudicator decision → `DecideAdjudicationUseCase` (Controller, L3)
- Calculate weekly benefit amount → `BenefitCalculator` (Service Provider, L1)
- Create payment schedule on approval → `CreatePaymentScheduleUseCase` (Controller, L3)
- Disburse a scheduled payment → `DisbursePaymentUseCase` (Controller, L3)
- Evaluate eligibility rules → `EligibilityPolicy` (Service Provider, L1)
- Publish domain events → `EventBus` port (Interfacer, L4)
- Persist/retrieve claims → `ClaimRepository` port (Interfacer, L4)
- Persist/retrieve adjudication cases → `AdjudicationCaseRepository` port (Interfacer, L4)
- Persist/retrieve payment schedules → `PaymentScheduleRepository` port (Interfacer, L4)
- Query wage records → `WageReportingGateway` port (Interfacer, L4)
- Initiate payment disbursement → `PaymentGateway` port (Interfacer, L4)

### Knowings
- Claim state and transitions → `Claim` (Structurer/Aggregate, L2)
- Document metadata → `Document` (Information Holder, L2)
- Employer response data → `EmployerResponse` (Information Holder, L1)
- Eligibility rules (wages exist, ≤20 weeks) → `EligibilityPolicy` (Service Provider, L1)
- Wage report and records → `EmployerWageReport` / `EmployeeWageRecord` (Structurer / Information Holder, L2)
- Adjudication case state → `AdjudicationCase` (Structurer/Aggregate, L2)
- Payment schedule and payments → `PaymentSchedule` / `Payment` (Structurer / Information Holder, L2)
- Payment method details → `PaymentMethod` (Information Holder, L1)
- Benefit ceiling configuration → `BenefitConfig` (Information Holder, L1)
- Domain events → `ClaimSubmitted`, `ClaimApproved`, `ClaimEscalated`, `ClaimDenied`, `AdjudicationCompleted`, `PaymentDisbursed`, `PaymentFailed`, `EmployerNotified` (Information Holder, L1)

## CRC Cards

### Claim
**Front:** Core aggregate — owns claim lifecycle and state transitions | Structurer | L2
**Knows:** claimId, employeeSSN, employerFEIN, leaveType, leaveStartDate, leaveEndDate, status, documents, employerResponse, denialReason
**Does:** Transition status (submitted → eligibility_check → awaiting_employer → approved/denied/escalated), validate transitions, attach documents, record employer response
**Decides:** Whether a state transition is valid (enforces allowed transitions)
**Collaborators:** Document, EmployerResponse

### EligibilityPolicy
**Front:** Stateless rule engine for eligibility determination | Service Provider | L1
**Knows:** Rules: must have wages in past year, must have <20 weeks used
**Does:** Evaluate eligibility given wage history and prior leave weeks used → (eligible: bool, reason: str | None)
**Collaborators:** None (pure function)

### BenefitCalculator
**Front:** Stateless calculation of weekly benefit amount | Service Provider | L1
**Knows:** Formula: min(avgQuarterlyWages / 13, ceiling)
**Does:** Calculate weekly benefit given list of quarterly wages and state ceiling → Decimal
**Collaborators:** None (pure function)

### Document
**Front:** Uploaded document metadata | Information Holder | L2
**Knows:** documentId, type, storageReference, uploadedAt
**Does:** Nothing (data holder, immutable after creation)
**Collaborators:** None

### EmployerResponse
**Front:** Employer's response to a claim notification | Information Holder | L1
**Knows:** decision (OBJECTED/NO_OBJECTION/WINDOW_EXPIRED), respondedAt, reason
**Does:** Nothing (value object, immutable)
**Collaborators:** None

### AdjudicationCase
**Front:** Aggregate for human review workflow | Structurer | L2
**Knows:** caseId, claimId, escalationReason, status, decision, adjudicatorNotes, decidedAt
**Does:** Transition status (pending → in_review → completed), record decision with notes
**Decides:** Whether a status transition is valid
**Collaborators:** None

### PaymentSchedule
**Front:** Aggregate for benefit disbursement over leave period | Structurer | L2
**Knows:** scheduleId, claimId, weeklyBenefitAmount, paymentMethod, startDate, endDate, payments
**Does:** Generate weekly Payment entities for the leave period
**Collaborators:** Payment, PaymentMethod, BenefitConfig

### Payment
**Front:** Individual weekly payment | Information Holder | L2
**Knows:** paymentId, weekStartDate, amount, status, disbursedAt, gatewayReference
**Does:** Transition status (scheduled → processing → disbursed/failed)
**Collaborators:** None

### PaymentMethod
**Front:** How to pay the employee | Information Holder | L1
**Knows:** type (CHECK/DIRECT_DEPOSIT), mailingAddress, bankRoutingNumber, bankAccountNumber
**Does:** Nothing (value object, immutable)
**Collaborators:** None

### BenefitConfig
**Front:** State-defined benefit parameters | Information Holder | L1
**Knows:** stateCeiling (Decimal)
**Does:** Nothing (configuration value object)
**Collaborators:** None

### EmployerWageReport
**Front:** Quarterly employer wage submission | Structurer | L2
**Knows:** reportId, employerFEIN, quarter, submittedAt, employeeWageRecords
**Does:** Look up wage records by employee SSN
**Collaborators:** EmployeeWageRecord

### EmployeeWageRecord
**Front:** Individual employee wages for a quarter | Information Holder | L2
**Knows:** recordId, employeeSSN, wagesReported
**Does:** Nothing (data holder)
**Collaborators:** None

### Domain Events
**Front:** Immutable event records for cross-context integration | Information Holder | L1
- `ClaimSubmitted` — claimId, employeeSSN, employerFEIN, leaveType, dates, timestamp
- `ClaimApproved` — claimId, employeeSSN, employerFEIN, leaveStartDate, leaveEndDate, timestamp
- `ClaimDenied` — claimId, denialReason, timestamp
- `ClaimEscalated` — claimId, escalationReason, timestamp
- `EmployerNotified` — claimId, employerFEIN, deadlineAt, timestamp
- `AdjudicationCompleted` — caseId, claimId, decision, timestamp
- `PaymentDisbursed` — paymentId, scheduleId, amount, timestamp
- `PaymentFailed` — paymentId, scheduleId, reason, timestamp

## File Change List

### Shared
- CREATE `src/shared/__init__.py`
- CREATE `src/shared/domain_event.py` — Base DomainEvent dataclass (L1)
- CREATE `src/shared/event_bus.py` — EventBus Protocol (L4 port)
- CREATE `src/shared/in_memory_event_bus.py` — In-memory EventBus for tests/dev (L4 adapter)
- CREATE `src/shared/types.py` — SSN, FEIN type aliases

### Claims Context
- CREATE `src/claims/__init__.py`
- CREATE `src/claims/domain/__init__.py`
- CREATE `src/claims/domain/claim.py` — Claim aggregate (L2)
- CREATE `src/claims/domain/document.py` — Document entity (L2)
- CREATE `src/claims/domain/employer_response.py` — EmployerResponse value object (L1)
- CREATE `src/claims/domain/eligibility_policy.py` — EligibilityPolicy pure function (L1)
- CREATE `src/claims/domain/events.py` — Claims domain events (L1)
- CREATE `src/claims/application/__init__.py`
- CREATE `src/claims/application/submit_claim.py` — SubmitClaimUseCase (L3)
- CREATE `src/claims/application/check_eligibility.py` — CheckEligibilityUseCase (L3)
- CREATE `src/claims/application/record_employer_response.py` — RecordEmployerResponseUseCase (L3)
- CREATE `src/claims/application/handle_employer_timeout.py` — HandleEmployerTimeoutUseCase (L3)
- CREATE `src/claims/application/apply_adjudication_result.py` — ApplyAdjudicationResultUseCase (L3)
- CREATE `src/claims/ports/__init__.py`
- CREATE `src/claims/ports/claim_repository.py` — ClaimRepository Protocol (L4 port)
- CREATE `src/claims/ports/wage_reporting_gateway.py` — WageReportingGateway Protocol (L4 port)
- CREATE `src/claims/adapters/__init__.py`
- CREATE `src/claims/adapters/api.py` — FastAPI router (L5)

### Wages Context
- CREATE `src/wages/__init__.py`
- CREATE `src/wages/domain/__init__.py`
- CREATE `src/wages/domain/wage_report.py` — EmployerWageReport aggregate (L2)
- CREATE `src/wages/domain/wage_record.py` — EmployeeWageRecord entity (L2)

### Adjudication Context
- CREATE `src/adjudication/__init__.py`
- CREATE `src/adjudication/domain/__init__.py`
- CREATE `src/adjudication/domain/adjudication_case.py` — AdjudicationCase aggregate (L2)
- CREATE `src/adjudication/domain/events.py` — AdjudicationCompleted event (L1)
- CREATE `src/adjudication/application/__init__.py`
- CREATE `src/adjudication/application/create_case.py` — CreateAdjudicationCaseUseCase (L3)
- CREATE `src/adjudication/application/decide_case.py` — DecideAdjudicationUseCase (L3)
- CREATE `src/adjudication/ports/__init__.py`
- CREATE `src/adjudication/ports/case_repository.py` — AdjudicationCaseRepository Protocol (L4 port)
- CREATE `src/adjudication/adapters/__init__.py`
- CREATE `src/adjudication/adapters/api.py` — FastAPI router (L5)

### Payments Context
- CREATE `src/payments/__init__.py`
- CREATE `src/payments/domain/__init__.py`
- CREATE `src/payments/domain/payment_schedule.py` — PaymentSchedule aggregate (L2)
- CREATE `src/payments/domain/payment.py` — Payment entity (L2)
- CREATE `src/payments/domain/payment_method.py` — PaymentMethod value object (L1)
- CREATE `src/payments/domain/benefit_calculator.py` — BenefitCalculator pure function (L1)
- CREATE `src/payments/domain/benefit_config.py` — BenefitConfig value object (L1)
- CREATE `src/payments/domain/events.py` — PaymentDisbursed, PaymentFailed (L1)
- CREATE `src/payments/application/__init__.py`
- CREATE `src/payments/application/create_payment_schedule.py` — CreatePaymentScheduleUseCase (L3)
- CREATE `src/payments/application/disburse_payment.py` — DisbursePaymentUseCase (L3)
- CREATE `src/payments/ports/__init__.py`
- CREATE `src/payments/ports/schedule_repository.py` — PaymentScheduleRepository Protocol (L4 port)
- CREATE `src/payments/ports/payment_gateway.py` — PaymentGateway Protocol (L4 port)

### App Wiring
- CREATE `src/app.py` — FastAPI app, mount routers, wire event subscriptions

### Test Fakes (shared between L3 and L5 tests)
- CREATE `tests/__init__.py`
- CREATE `tests/conftest.py` — Shared fixtures and factories
- CREATE `tests/fakes/__init__.py`
- CREATE `tests/fakes/fake_claim_repository.py` — In-memory ClaimRepository
- CREATE `tests/fakes/fake_case_repository.py` — In-memory AdjudicationCaseRepository
- CREATE `tests/fakes/fake_schedule_repository.py` — In-memory PaymentScheduleRepository
- CREATE `tests/fakes/fake_wage_gateway.py` — In-memory WageReportingGateway
- CREATE `tests/fakes/fake_payment_gateway.py` — In-memory PaymentGateway

### Tests
- CREATE `tests/unit/test_eligibility_policy.py` — L1: pure eligibility rules
- CREATE `tests/unit/test_benefit_calculator.py` — L1: pure benefit calculation
- CREATE `tests/domain/test_claim.py` — L2: Claim aggregate transitions
- CREATE `tests/domain/test_adjudication_case.py` — L2: AdjudicationCase transitions
- CREATE `tests/domain/test_payment_schedule.py` — L2: PaymentSchedule generation
- CREATE `tests/application/test_submit_claim.py` — L3: SubmitClaimUseCase with fakes
- CREATE `tests/application/test_check_eligibility.py` — L3: CheckEligibilityUseCase with fakes
- CREATE `tests/application/test_record_employer_response.py` — L3: employer response scenarios
- CREATE `tests/application/test_handle_employer_timeout.py` — L3: timeout → silent consent
- CREATE `tests/application/test_apply_adjudication_result.py` — L3: adjudication → claim transition
- CREATE `tests/application/test_create_payment_schedule.py` — L3: schedule creation + benefit calc
- CREATE `tests/application/test_disburse_payment.py` — L3: disbursement success/failure
- CREATE `tests/api/test_claims_api.py` — L5: claim submission + employer response endpoints
- CREATE `tests/api/test_adjudication_api.py` — L5: adjudication case endpoints

## Pattern Decisions
- **Modular monolith:** 4 bounded contexts as separate Python packages under `src/`
- **Domain events:** Dataclasses inheriting from `DomainEvent`. Cross-context via `EventBus` Protocol.
- **Repository pattern:** Python Protocol classes as ports, in-memory fakes for L3/L5 tests
- **Anti-corruption layer:** Claims uses `WageReportingGateway` Protocol — never imports wages domain directly
- **Value objects:** Frozen Pydantic `BaseModel` (EmployerResponse, PaymentMethod, events)
- **Aggregates:** Pydantic `BaseModel` with methods for state transitions, raise on invalid transitions
- **Pluggable benefit formula:** `calculate_weekly_benefit(wages, ceiling)` pure function at L1

## Out of Scope
- PostgreSQL adapters (L4 adapter implementations) — stubs only in Phase 3
- S3 document storage adapter
- EventBridge adapter (real AWS integration)
- KMS field encryption adapter
- Authentication/authorization middleware
- Employer wage reporting portal
- Fraud detection
- Appeals process
- Reporting/analytics

## Implementation Steps (ordered)
1. Shared foundation — `domain_event.py`, `event_bus.py`, `in_memory_event_bus.py`, `types.py`
2. Claims domain — `Claim`, `Document`, `EmployerResponse`, `EligibilityPolicy`, events
3. Claims ports — `ClaimRepository`, `WageReportingGateway` Protocols
4. Claims use cases — `SubmitClaim`, `CheckEligibility`, `RecordEmployerResponse`, `HandleEmployerTimeout`
5. Claims API adapter — FastAPI router
6. Wages domain — `EmployerWageReport`, `EmployeeWageRecord`
7. Adjudication domain — `AdjudicationCase`, events
8. Adjudication ports + use cases — `CreateCase`, `DecideCase`
9. Adjudication API adapter — FastAPI router
10. Claims ← Adjudication integration — `ApplyAdjudicationResultUseCase` + event wiring
11. Payments domain — `PaymentSchedule`, `Payment`, `PaymentMethod`, `BenefitCalculator`, `BenefitConfig`
12. Payments ports + use cases — `CreatePaymentSchedule`, `DisbursePayment`
13. Test fakes — all in-memory repositories + gateways
14. Wire everything in `app.py` — routers, event subscriptions
