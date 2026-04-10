from decimal import Decimal

from src.payments.domain.benefit_calculator import calculate_weekly_benefit


class TestBenefitCalculator:
    def test_benefit_below_ceiling(self):
        # avg quarterly = 10000, weekly = 10000/13 ≈ 769.23
        result = calculate_weekly_benefit(
            quarterly_wages=[
                Decimal("10000"), Decimal("10000"), Decimal("10000"), Decimal("10000"),
            ],
            state_ceiling=Decimal("1200.00"),
        )
        assert result == Decimal("10000") / 13

    def test_benefit_capped_at_ceiling(self):
        # avg quarterly = 50000, weekly = 50000/13 ≈ 3846.15, capped at 1200
        result = calculate_weekly_benefit(
            quarterly_wages=[
                Decimal("50000"), Decimal("50000"), Decimal("50000"), Decimal("50000"),
            ],
            state_ceiling=Decimal("1200.00"),
        )
        assert result == Decimal("1200.00")

    def test_benefit_with_uneven_quarters(self):
        # avg quarterly = (8000+12000+10000+10000)/4 = 10000, weekly = 10000/13
        result = calculate_weekly_benefit(
            quarterly_wages=[Decimal("8000"), Decimal("12000"), Decimal("10000"), Decimal("10000")],
            state_ceiling=Decimal("1200.00"),
        )
        assert result == Decimal("10000") / 13

    def test_benefit_with_single_quarter(self):
        result = calculate_weekly_benefit(
            quarterly_wages=[Decimal("5200")],
            state_ceiling=Decimal("1200.00"),
        )
        assert result == Decimal("5200") / 13
