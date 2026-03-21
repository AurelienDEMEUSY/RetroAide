import pytest

from core.calculator import (
    calculate_departure_age,
    estimate_quarters_worked,
    quarters_remaining,
)


@pytest.mark.parametrize(
    ("birth_year", "expected"),
    [
        (1970, 64),
        (1968, 64),
        (1967, 63),
        (1961, 63),
        (1960, 62),
    ],
)
def test_calculate_departure_age(birth_year: int, expected: int) -> None:
    assert calculate_departure_age(birth_year) == expected


def test_estimate_quarters_worked_prd_reference_year() -> None:
    # PRD: years = 2026 - start_work_year, min(years * 4, 172)
    assert estimate_quarters_worked("avant_20", 1971, reference_year=2026) == (2026 - 1990) * 4
    assert estimate_quarters_worked("avant_20", 1971, reference_year=2026) == 144


def test_estimate_quarters_worked_cap_at_172() -> None:
    assert estimate_quarters_worked("avant_20", 1961, reference_year=2026) == 172
    assert estimate_quarters_worked("avant_20", 1964, reference_year=2026) == 172  # 43 * 4 = 172


def test_estimate_quarters_worked_future_start_returns_zero() -> None:
    assert estimate_quarters_worked("avant_20", 2011, reference_year=2026) == 0


def test_quarters_remaining() -> None:
    assert quarters_remaining(128) == 44
    assert quarters_remaining(172) == 0
    assert quarters_remaining(200) == 0
