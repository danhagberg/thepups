import math
from typing import Tuple

import pytest
from datetime import date, datetime, timedelta

from thepups_workflow.dependencies.python import the_pups

# DBS schedule is not within shift need period
# Shifts: (Timestamp('2020-04-02 07:30:00'), Timestamp('2020-04-08 16:00:00')),
# Needs: (Timestamp('2020-04-04 00:00:00'), Timestamp('2020-04-08 00:00:00'))

shift = datetime.fromisoformat('2020-04-02 07:30:00'), datetime.fromisoformat('2020-04-08 16:00:00')
needs = datetime.fromisoformat('2020-04-04 00:00:00'), datetime.fromisoformat('2020-04-08 00:00:00')

def test_shift_needs():
    answer = the_pups.is_within_or_overlap(shift, needs)
    assert answer is True

# Common day used in following tests
test_day = date(2020, 1, 20)


def create_time_frame(start_day: date, start_time: Tuple[int, int], end_time: Tuple[int, int]):
    return datetime(start_day.year, start_day.month, start_day.day, start_time[0], start_time[1]), \
           datetime(start_day.year, start_day.month, start_day.day, end_time[0], end_time[1])


# Test is within time frame
within_test_time = datetime(test_day.year, test_day.month, test_day.day, 8, 0)
within_test_time_prior_day = datetime(test_day.year, test_day.month, test_day.day - 1, 8, 0)
within_test_time_next_day = datetime(test_day.year, test_day.month, test_day.day + 1, 8, 0)
within_test_data = [
    (create_time_frame(test_day, (7, 30), (10, 30)), within_test_time, True),
    (create_time_frame(test_day, (7, 30), (8, 0)), within_test_time, True),
    (create_time_frame(test_day, (8, 00), (9, 0)), within_test_time, True),
    (create_time_frame(test_day, (7, 59), (8, 1)), within_test_time, True),
    (create_time_frame(test_day, (8, 00), (8, 0)), within_test_time, True),
    (create_time_frame(test_day, (7, 30), (10, 30)), within_test_time_prior_day, False),
    (create_time_frame(test_day, (7, 30), (10, 30)), within_test_time_next_day, False),
    (create_time_frame(test_day, (11, 0), (12, 0)), within_test_time, False)
]


@pytest.mark.parametrize("schedule, test_time, expected_answer", within_test_data)
def test_is_within_timeframe(schedule, test_time, expected_answer):
    answer = the_pups.is_within_timeframe(schedule, test_time)
    assert answer == expected_answer


# Test is within or overlap time frame
is_overlap_test_time = create_time_frame(test_day, (7, 0), (10, 0))
is_overlap_test_time_prior_day = create_time_frame(test_day + timedelta(days=-1), (7, 0), (10, 0))
is_overlap_test_time_next_day = create_time_frame(test_day + timedelta(days=1), (7, 0), (10, 0))
is_overlap_test_data = [
    (create_time_frame(test_day, (7, 0), (10, 0)), is_overlap_test_time, True),
    (create_time_frame(test_day, (7, 30), (10, 0)), is_overlap_test_time, True),
    (create_time_frame(test_day, (6, 00), (8, 0)), is_overlap_test_time, True),
    (create_time_frame(test_day, (6, 59), (10, 1)), is_overlap_test_time, True),
    (create_time_frame(test_day, (7, 0), (7, 0)), is_overlap_test_time, True),
    (create_time_frame(test_day, (10, 0), (10, 0)), is_overlap_test_time, True),
    (create_time_frame(test_day, (7, 30), (10, 30)), is_overlap_test_time, True),
    (create_time_frame(test_day, (7, 30), (10, 30)), is_overlap_test_time_prior_day, False),
    (create_time_frame(test_day, (7, 30), (10, 30)), is_overlap_test_time_next_day, False),
    (create_time_frame(test_day, (11, 0), (12, 0)), is_overlap_test_time, False)
]


@pytest.mark.parametrize("schedule, test_shift, expected_answer", is_overlap_test_data)
def test_is_within_or_overlap(schedule, test_shift, expected_answer):
    answer = the_pups.is_within_or_overlap(schedule, test_shift)
    assert answer == expected_answer
