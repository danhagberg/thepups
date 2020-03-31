import math

import pytest
from datetime import date, datetime, timedelta

from thepups_workflow.calculate_shift_counts import app

# Common day used in following tests
test_day = date(2020, 1, 20)

# Test is within time frame
within_test_time = datetime(test_day.year, test_day.month, test_day.day, 8, 0)
within_test_time_prior_day = datetime(test_day.year, test_day.month, test_day.day - 1, 8, 0)
within_test_time_next_day = datetime(test_day.year, test_day.month, test_day.day + 1, 8, 0)
within_test_data = [
    (app.get_shift_schedule(test_day, (7, 30), (10, 30)), within_test_time, True),
    (app.get_shift_schedule(test_day, (7, 30), (8, 0)), within_test_time, True),
    (app.get_shift_schedule(test_day, (8, 00), (9, 0)), within_test_time, True),
    (app.get_shift_schedule(test_day, (7, 59), (8, 1)), within_test_time, True),
    (app.get_shift_schedule(test_day, (8, 00), (8, 0)), within_test_time, True),
    (app.get_shift_schedule(test_day, (7, 30), (10, 30)), within_test_time_prior_day, False),
    (app.get_shift_schedule(test_day, (7, 30), (10, 30)), within_test_time_next_day, False),
    (app.get_shift_schedule(test_day, (11, 0), (12, 0)), within_test_time, False)
]


@pytest.mark.parametrize("schedule, test_time, expected_answer", within_test_data)
def test_is_within_timeframe(schedule, test_time, expected_answer):
    answer = app.is_within_timeframe(schedule, test_time)
    assert answer == expected_answer


# Test is within or overlap time frame
is_overlap_test_time = app.get_shift_schedule(test_day, (7, 0), (10, 0))
is_overlap_test_time_prior_day = app.get_shift_schedule(test_day + timedelta(days=-1), (7, 0), (10, 0))
is_overlap_test_time_next_day = app.get_shift_schedule(test_day + timedelta(days=1), (7, 0), (10, 0))
is_overlap_test_data = [
    (app.get_shift_schedule(test_day, (7, 0), (10, 0)), is_overlap_test_time, True),
    (app.get_shift_schedule(test_day, (7, 30), (10, 0)), is_overlap_test_time, True),
    (app.get_shift_schedule(test_day, (6, 00), (8, 0)), is_overlap_test_time, True),
    (app.get_shift_schedule(test_day, (6, 59), (10, 1)), is_overlap_test_time, True),
    (app.get_shift_schedule(test_day, (7, 0), (7, 0)), is_overlap_test_time, True),
    (app.get_shift_schedule(test_day, (10, 0), (10, 0)), is_overlap_test_time, True),
    (app.get_shift_schedule(test_day, (7, 30), (10, 30)), is_overlap_test_time, True),
    (app.get_shift_schedule(test_day, (7, 30), (10, 30)), is_overlap_test_time_prior_day, False),
    (app.get_shift_schedule(test_day, (7, 30), (10, 30)), is_overlap_test_time_next_day, False),
    (app.get_shift_schedule(test_day, (11, 0), (12, 0)), is_overlap_test_time, False)
]


@pytest.mark.parametrize("schedule, test_shift, expected_answer", is_overlap_test_data)
def test_is_within_or_overlap(schedule, test_shift, expected_answer):
    answer = app.is_within_or_overlap(schedule, test_shift)
    assert answer == expected_answer


# Test shift overlap
overlap_test_time = app.get_shift_schedule(test_day, (7, 0), (10, 0))
overlap_test_time_prior_day = app.get_shift_schedule(test_day + timedelta(days=-1), (7, 0), (10, 0))
overlap_test_time_next_day = app.get_shift_schedule(test_day + timedelta(days=1), (7, 0), (10, 0))
overlap_test_data = [
    (app.get_shift_schedule(test_day, (7, 0), (10, 0)), overlap_test_time, 1.0),
    (app.get_shift_schedule(test_day, (7, 30), (10, 0)), overlap_test_time, 1.0),
    (app.get_shift_schedule(test_day, (6, 00), (8, 0)), overlap_test_time, .5),
    (app.get_shift_schedule(test_day, (6, 00), (9, 0)), overlap_test_time, .66666),
    (app.get_shift_schedule(test_day, (9, 00), (12, 0)), overlap_test_time, .33333),
    (app.get_shift_schedule(test_day, (7, 30), (10, 30)), overlap_test_time_prior_day, 0),
    (app.get_shift_schedule(test_day, (7, 30), (10, 30)), overlap_test_time_next_day, 0),
    (app.get_shift_schedule(test_day, (11, 0), (12, 0)), overlap_test_time, 0)
]


@pytest.mark.parametrize("schedule, test_shift, expected_overlap", overlap_test_data)
def test_get_shift_overlap(schedule, test_shift, expected_overlap):
    overlap = app.get_shift_overlap(schedule, test_shift)
    delta = math.fabs(overlap - expected_overlap)
    assert delta < 0.01
