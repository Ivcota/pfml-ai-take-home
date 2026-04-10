---
slug: pfml-claims-lifecycle
feature: PFML Claims Lifecycle
---

# Automate: PFML Claims Lifecycle

## Test Map

| Scenario (from Find) | Test file | Test type | Status |
|---|---|---|---|
| 1: Submit valid claim | `tests/api/test_claims_api.py::TestSubmitClaimAPI` | L5 Slice | FAILING |
| 1: Submit valid claim | `tests/application/test_submit_claim.py` | L3 Use case | FAILING |
| 2: Eligible | `tests/application/test_check_eligibility.py::TestCheckEligibilityEligible` | L3 Use case | FAILING |
| 3: Ineligible (no wages) | `tests/application/test_check_eligibility.py::TestCheckEligibilityIneligibleNoWages` | L3 Use case | FAILING |
| 4: Ineligible (20 weeks) | `tests/application/test_check_eligibility.py::TestCheckEligibilityIneligible20Weeks` | L3 Use case | FAILING |
| 5: Employer no objection | `tests/api/test_claims_api.py::TestEmployerResponseAPI` | L5 Slice | FAILING |
| 5: Employer no objection | `tests/application/test_record_employer_response.py::TestRecordEmployerResponseNoObjection` | L3 Use case | FAILING |
| 6: Employer window expires | `tests/application/test_handle_employer_timeout.py` | L3 Use case | FAILING |
| 7: Employer objects | `tests/application/test_record_employer_response.py::TestRecordEmployerResponseObjection` | L3 Use case | FAILING |
| 8: Adjudicator approves | `tests/api/test_adjudication_api.py` | L5 Slice | FAILING |
| 8: Adjudicator approves | `tests/application/test_apply_adjudication_result.py::TestApplyAdjudicationResultApproved` | L3 Use case | FAILING |
| 9: Adjudicator denies | `tests/application/test_apply_adjudication_result.py::TestApplyAdjudicationResultDenied` | L3 Use case | FAILING |
| 10: Payment schedule created | `tests/application/test_create_payment_schedule.py` | L3 Use case | FAILING |
| 11: Payment disbursed | `tests/application/test_disburse_payment.py::TestDisbursePaymentSuccess` | L3 Use case | FAILING |
| 12: Payment fails | `tests/application/test_disburse_payment.py::TestDisbursePaymentFailure` | L3 Use case | FAILING |
| (supporting) Eligibility rules | `tests/unit/test_eligibility_policy.py` | L1 Unit | FAILING |
| (supporting) Benefit calculation | `tests/unit/test_benefit_calculator.py` | L1 Unit | FAILING |
| (supporting) Claim transitions | `tests/domain/test_claim.py` | L2 Domain | FAILING |
| (supporting) Adjudication transitions | `tests/domain/test_adjudication_case.py` | L2 Domain | FAILING |
| (supporting) Payment generation | `tests/domain/test_payment_schedule.py` | L2 Domain | FAILING |

## Test Results

- **58 tests collected**
- **58 failing** (all `NotImplementedError`)
- **0 errors** (imports and wiring correct)

## Weirdness Log

- None — clean scaffold, all imports resolve, fakes wire correctly.
