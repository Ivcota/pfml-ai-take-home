# Ubiquitous Language

## Claim lifecycle

| Term | Definition | Aliases to avoid |
|------|-----------|-----------------|
| **Claim** | An employee's formal request for paid family or medical leave benefits | Application, request, case, ticket |
| **Leave Type** | The statutory reason for a Claim: either BONDING or MEDICAL | Category, kind |
| **Bonding Leave** | Leave taken to bond with a newborn or newly adopted child | Parental leave, baby leave |
| **Medical Leave** | Leave taken for the employee's own serious health condition or to care for a family member | Sick leave, FMLA |
| **Leave Duration** | The number of weeks between a Claim's start and end dates | Length, period |
| **Annual Leave Cap** | The maximum 20 weeks of paid leave an employee may take in a single calendar year | Quota, allowance, entitlement |
| **Denial Reason** | A human-readable explanation of why a Claim was denied | Rejection reason |

### Claim statuses

| Status | Definition |
|--------|-----------|
| **Submitted** | Initial state — the Claim has been filed but not yet evaluated |
| **Eligibility Check** | The system is verifying wage history and annual leave balance |
| **Awaiting Employer** | The Claim passed eligibility and the employer has been notified for response |
| **Approved** | The Claim has been granted — either automatically or by an Adjudicator |
| **Denied** | The Claim has been refused — due to ineligibility or Adjudicator decision |
| **Escalated** | The Claim requires human review because the employer objected or an edge case was detected |

## Employer response

| Term | Definition | Aliases to avoid |
|------|-----------|-----------------|
| **Employer Response** | The employer's formal reaction to a notified Claim | Employer decision, employer review |
| **No Objection** | The employer does not contest the Claim | Approval, acceptance |
| **Objected** | The employer contests the Claim, triggering escalation | Denied, rejected, disputed |
| **Window Expired** | The employer did not respond within the Response Window; treated as No Objection | Timeout, lapsed, defaulted |
| **Response Window** | The 10-calendar-day period an employer has to respond after notification | Deadline, SLA, grace period |

## Wage reporting

| Term | Definition | Aliases to avoid |
|------|-----------|-----------------|
| **Employer Wage Report** | A quarterly payroll submission from an employer containing wages for all covered employees | Wage filing, payroll report, contribution report |
| **Employee Wage Record** | A single employee's wage entry within an Employer Wage Report | Wage line, payroll record |
| **Quarter** | A calendar quarter identified as "YYYY-Q#" (e.g. "2025-Q3") | Period, reporting period |
| **Qualifying Wages** | At least one quarter with wages greater than zero in the lookback window | Sufficient earnings |
| **Lookback Window** | The four most recent consecutive quarters examined for eligibility | Wage history, base period |

## Payments

| Term | Definition | Aliases to avoid |
|------|-----------|-----------------|
| **Payment Schedule** | The full set of weekly Payments generated for an approved Claim | Payment plan, disbursement schedule |
| **Payment** | A single weekly benefit disbursement to the employee | Installment, payout, transfer |
| **Weekly Benefit Amount** | The calculated dollar amount disbursed per week, capped at the State Ceiling | Benefit rate, weekly rate |
| **State Ceiling** | The maximum weekly benefit amount set by state policy | Cap, max benefit, ceiling |
| **Benefit Calculation** | The formula: min(average quarterly wages / 13, State Ceiling) | Benefit formula |
| **Payment Method** | How the employee receives funds: either Check or Direct Deposit | Disbursement method |
| **Direct Deposit** | ACH transfer to the employee's bank account | Bank transfer, EFT |

### Payment statuses

| Status | Definition |
|--------|-----------|
| **Scheduled** | Payment created, awaiting its weekly processing date |
| **Processing** | Payment submitted to the Payment Gateway, awaiting confirmation |
| **Disbursed** | Payment successfully transferred to the employee |
| **Failed** | The Payment Gateway returned an error |

## Adjudication

| Term | Definition | Aliases to avoid |
|------|-----------|-----------------|
| **Adjudication Case** | A human review case created when a Claim is escalated | Review, ticket, appeal |
| **Adjudicator** | The human reviewer who decides an escalated Claim | Reviewer, examiner, case worker, analyst |
| **Escalation Reason** | The explanation of why the Claim was routed to human review | Reason, trigger |
| **Adjudicator Notes** | The Adjudicator's written reasoning supporting their decision | Comments, rationale |

### Adjudication case statuses

| Status | Definition |
|--------|-----------|
| **Pending** | Case created, not yet picked up by an Adjudicator |
| **In Review** | An Adjudicator is actively reviewing the case |
| **Completed** | The Adjudicator has recorded a decision (Approved or Denied) |

## People and identifiers

| Term | Definition | Aliases to avoid |
|------|-----------|-----------------|
| **Employee** | A person who files a Claim for paid leave benefits | Worker, claimant, applicant, member |
| **Employer** | An organization that employs the Employee and submits Wage Reports | Company, business, firm |
| **SSN** | Social Security Number — the unique identifier for an Employee (encrypted at rest) | Social, TIN |
| **FEIN** | Federal Employer Identification Number — the unique identifier for an Employer | EIN, tax ID |

## Documents

| Term | Definition | Aliases to avoid |
|------|-----------|-----------------|
| **Document** | A file uploaded to support a Claim (e.g. birth certificate, doctor's note) | Attachment, upload, file |
| **Storage Reference** | The S3 key pointing to an encrypted Document in object storage | File path, URL, location |

## Infrastructure concepts with domain meaning

| Term | Definition | Aliases to avoid |
|------|-----------|-----------------|
| **Domain Event** | An immutable record that something meaningful happened in the domain | Message, notification, signal |
| **Event Bus** | The mechanism that publishes Domain Events and routes them to subscribers | Message broker, queue |
| **Payment Gateway** | The external service that processes Check and Direct Deposit disbursements | Payment processor, bank API |
| **Wage Reporting Gateway** | The anti-corruption layer port through which Claims and Payments query wage data | Wage service, wage API |

## Relationships

- A **Claim** is filed by exactly one **Employee** against exactly one **Employer**
- A **Claim** may have zero or more **Documents** attached
- A **Claim** has at most one **Employer Response**
- An **Employer Response** of **Objected** triggers exactly one **Adjudication Case**
- An approved **Claim** produces exactly one **Payment Schedule**
- A **Payment Schedule** contains one **Payment** per week of leave
- An **Employer Wage Report** contains one or more **Employee Wage Records**
- **Eligibility** requires **Qualifying Wages** in the **Lookback Window** and fewer than 20 weeks used against the **Annual Leave Cap**
- The **Weekly Benefit Amount** is derived from wage data via the **Benefit Calculation** formula

## Example dialogue

> **Dev:** "When an **Employee** submits a **Claim**, what happens first?"
> **Domain expert:** "The **Claim** enters **Eligibility Check**. We pull the last four **Quarters** from the **Lookback Window** via the **Wage Reporting Gateway** and verify they have **Qualifying Wages** and haven't exceeded the **Annual Leave Cap**."
> **Dev:** "If they're eligible, does the **Claim** get approved immediately?"
> **Domain expert:** "No — an eligible **Claim** moves to **Awaiting Employer**. We notify the **Employer** and start the **Response Window**. They have 10 calendar days to respond."
> **Dev:** "What if the **Employer** submits an **Objected** response?"
> **Domain expert:** "The **Claim** gets **Escalated** and we create an **Adjudication Case**. An **Adjudicator** reviews the case, writes their **Adjudicator Notes**, and records a decision. That decision flows back to the **Claim** — either **Approved** or **Denied**."
> **Dev:** "And once a **Claim** is **Approved**, we start paying?"
> **Domain expert:** "Right. The **Payments** context creates a **Payment Schedule** with one **Payment** per week. The **Weekly Benefit Amount** is calculated using the **Benefit Calculation** — average quarterly wages divided by 13, capped at the **State Ceiling**. Each **Payment** goes through **Scheduled** → **Processing** → **Disbursed** via the **Payment Gateway**."

## Flagged ambiguities

- **"Case"** is used in the Adjudication context to mean **Adjudication Case**, but could be confused with a general support case or the **Claim** itself. Use **Adjudication Case** when referring to the human review record; use **Claim** when referring to the leave request.
- **"Decision"** appears in two contexts: **Employer Decision** (No Objection / Objected / Window Expired) and **Adjudication Decision** (Approved / Denied). Always qualify which decision is meant — never use "decision" alone.
- **"Approved"** and **"Denied"** appear as both **Claim** statuses and **Adjudication Case** outcomes. The Adjudication decision *causes* the Claim status transition, but they are distinct domain events. Be explicit: "the **Adjudicator** decided to approve" vs. "the **Claim** is now **Approved**."
- **"Account"** does not appear in this domain. Do not introduce it — use **Employee** for the person and **SSN** for their identifier.
- **"Application"** should not be used as a synonym for **Claim**. "Application" is ambiguous with the software application itself.
