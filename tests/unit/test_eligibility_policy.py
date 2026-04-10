from decimal import Decimal

from src.claims.domain.eligibility_policy import check_eligibility


class TestEligibilityPolicy:
    def test_eligible_with_wages_and_no_prior_leave(self):
        result = check_eligibility(
            quarterly_wages=[Decimal("10000"), Decimal("10000"), Decimal("10000"), Decimal("10000")],
            weeks_used_this_year=0,
        )
        assert result.eligible is True
        assert result.reason is None

    def test_ineligible_no_wages_in_past_year(self):
        result = check_eligibility(
            quarterly_wages=[],
            weeks_used_this_year=0,
        )
        assert result.eligible is False
        assert result.reason == "no qualifying wages"

    def test_ineligible_all_zero_wages(self):
        result = check_eligibility(
            quarterly_wages=[Decimal("0"), Decimal("0"), Decimal("0"), Decimal("0")],
            weeks_used_this_year=0,
        )
        assert result.eligible is False
        assert result.reason == "no qualifying wages"

    def test_ineligible_20_weeks_exhausted(self):
        result = check_eligibility(
            quarterly_wages=[Decimal("10000"), Decimal("10000"), Decimal("10000"), Decimal("10000")],
            weeks_used_this_year=20,
        )
        assert result.eligible is False
        assert result.reason == "annual leave exhausted"

    def test_eligible_with_partial_prior_leave(self):
        result = check_eligibility(
            quarterly_wages=[Decimal("10000"), Decimal("10000"), Decimal("10000"), Decimal("10000")],
            weeks_used_this_year=10,
        )
        assert result.eligible is True
        assert result.reason is None
