import pytest
from ckanext.nhm.lib.utils import ingest_date_check
from datetime import datetime as dt, timezone

test_cases =[
    {
        'test_comment': 'on scheduled day, before 10',
        'right_now': dt(2026, 2, 24, 8,30, tzinfo=timezone.utc),
        'last_ingest_date': dt(2026, 2, 23, 10, 30, tzinfo=timezone.utc),
        'expected_state': 'good'
    },
    {
        'test_comment': 'on scheduled day, after 10 - before 12',
        'right_now':dt(2026, 2, 24, 11, 00, tzinfo=timezone.utc),
        'last_ingest_date':dt(2026, 2, 23, 10, 30, tzinfo=timezone.utc),
        'expected_state': 'ok'
    },
    {
        'test_comment': 'on scheduled day, after 10 - before 12 - ingest happened',
        'right_now': dt(2026, 2, 24, 11, 00, tzinfo=timezone.utc),
        'last_ingest_date': dt(2026, 2, 24, 10, 30, tzinfo=timezone.utc),
        'expected_state': 'good'
    },
    {
        'test_comment': 'on scheduled day, after 12 - ingest happened',
        'right_now': dt(2026, 2, 24, 12, 1, tzinfo=timezone.utc),
        'last_ingest_date': dt(2026, 2, 24, 10, 30, tzinfo=timezone.utc),
        'expected_state': 'good'
    },{
        'test_comment': 'on scheduled day, after 12 - ingest didnt happen',
        'right_now': dt(2026, 2, 24, 12, 1, tzinfo=timezone.utc),
        'last_ingest_date': dt(2026, 2, 23, 10, 30, tzinfo=timezone.utc),
        'expected_state': 'bad'
    },{
        'test_comment': 'on scheduled day - last day didnt happen - pre 10',
        'right_now': dt(2026, 2, 24, 9, 00, tzinfo=timezone.utc),
        'last_ingest_date': dt(2026, 2, 22, 10, 30, tzinfo=timezone.utc),
        'expected_state': 'bad'
    },{
        'test_comment': 'on scheduled day - last day didnt happen, after 10 - before 12',
        'right_now': dt(2026, 2, 24, 11, 00, tzinfo=timezone.utc),
        'last_ingest_date': dt(2026, 2, 22, 10, 30, tzinfo=timezone.utc),
        'expected_state': 'bad'
    },{
        'test_comment': 'on scheduled day - last day didnt happen, after 12',
        'right_now': dt(2026, 2, 24, 12, 1, tzinfo=timezone.utc),
        'last_ingest_date': dt(2026, 2, 22, 10, 30, tzinfo=timezone.utc),
        'expected_state': 'bad'
    },{
        'test_comment': 'on scheduled day - sunday - last day did happen - pre 10',
        'right_now': dt(2026, 3, 1, 9, 00, tzinfo=timezone.utc),
        'last_ingest_date': dt(2026, 2, 26, 10, 30, tzinfo=timezone.utc),
        'expected_state': 'good'
    },{
        'test_comment': 'on scheduled day - sunday - last day did happen, after 10 - before 12',
        'right_now': dt(2026, 3, 1, 11, 00, tzinfo=timezone.utc),
        'last_ingest_date': dt(2026, 2, 26, 10, 30, tzinfo=timezone.utc),
        'expected_state': 'ok'
    },{
        'test_comment': 'on scheduled day - sunday - today did happen, after 12',
        'right_now': dt(2026, 3, 1, 12, 1, tzinfo=timezone.utc),
        'last_ingest_date': dt(2026, 3, 1, 10, 30, tzinfo=timezone.utc),
        'expected_state': 'good'
    },{
        'test_comment': 'on scheduled day - sunday - today didnt happen, after 12',
        'right_now': dt(2026, 3, 1, 12, 1, tzinfo=timezone.utc),
        'last_ingest_date': dt(2026, 2, 26, 10, 30, tzinfo=timezone.utc),
        'expected_state': 'bad'
    },{
        'test_comment': 'on scheduled day - sunday - last day didnt happen - pre 10',
        'right_now': dt(2026, 3, 1, 9, 00, tzinfo=timezone.utc),
        'last_ingest_date': dt(2026, 2, 22, 10, 30, tzinfo=timezone.utc),
        'expected_state': 'bad'
    },{
        'test_comment': 'on scheduled day - sunday - last day didnt happen, after 10 - before 12',
        'right_now': dt(2026, 3, 1, 11, 00, tzinfo=timezone.utc),
        'last_ingest_date': dt(2026, 2, 22, 10, 30, tzinfo=timezone.utc),
        'expected_state': 'bad'
    },{
        'test_comment': 'on scheduled day - sunday - last day didnt happen, after 12',
        'right_now': dt(2026, 3, 1, 12, 1, tzinfo=timezone.utc),
        'last_ingest_date': dt(2026, 2, 22, 10, 30, tzinfo=timezone.utc),
        'expected_state': 'bad'
    },{
        'test_comment': 'on scheduled day - sunday - unscheduled happen - pre 10',
        'right_now': dt(2026, 3, 1, 9, 00, tzinfo=timezone.utc),
        'last_ingest_date': dt(2026, 2, 27, 16, 30, tzinfo=timezone.utc),
        'expected_state': 'good'
    },{
        'test_comment': 'on scheduled day - sunday - unscheduled happened, after 10 - before 12',
        'right_now': dt(2026, 3, 1, 11, 00, tzinfo=timezone.utc),
        'last_ingest_date':dt(2026, 3, 1, 1, 30, tzinfo=timezone.utc) ,
        'expected_state': 'ok'
    },{
        'test_comment': 'on scheduled day - sunday - unscheduled happened - today didnt, after 12',
        'right_now': dt(2026, 3, 1, 12, 1, tzinfo=timezone.utc),
        'last_ingest_date': dt(2026, 2, 28, 11, 30, tzinfo=timezone.utc),
        'expected_state': 'bad'
    },{
        'test_comment': 'on non-scheduled day - last scheduled day didnt happen - pre 10',
        'right_now': dt(2026, 2, 28, 9, 00, tzinfo=timezone.utc),
        'last_ingest_date': dt(2026, 2, 25, 10, 30, tzinfo=timezone.utc),
        'expected_state': 'bad'
    },{
        'test_comment': 'on non-scheduled day - last scheduled day didnt happen, after 10 - before 12',
        'right_now':  dt(2026, 2, 27, 11, 00, tzinfo=timezone.utc),
        'last_ingest_date': dt(2026, 2, 24, 10, 30, tzinfo=timezone.utc),
        'expected_state': 'bad'
    },{
        'test_comment': 'on non-scheduled day - last scheduled day didnt happen, after 12',
        'right_now': dt(2026, 2, 28, 12, 1, tzinfo=timezone.utc),
        'last_ingest_date':dt(2026, 2, 23, 10, 30, tzinfo=timezone.utc) ,
        'expected_state': 'bad'
    },{
        'test_comment': 'on non-scheduled day - last scheduled day did happen - pre 10',
        'right_now': dt(2026, 2, 28, 9, 00, tzinfo=timezone.utc),
        'last_ingest_date': dt(2026, 2, 26, 10, 30, tzinfo=timezone.utc),
        'expected_state': 'good'
    },{
        'test_comment': 'on non-scheduled day - last scheduled day did happen, after 10 - before 12',
        'right_now': dt(2026, 2, 27, 11, 00, tzinfo=timezone.utc),
        'last_ingest_date': dt(2026, 2, 26, 10, 30, tzinfo=timezone.utc),
        'expected_state': 'good'
    },{
        'test_comment': 'on non-scheduled day - last scheduled day did happen, after 12',
        'right_now': dt(2026, 2, 28, 12, 1, tzinfo=timezone.utc),
        'last_ingest_date': dt(2026, 2, 26, 10, 30, tzinfo=timezone.utc),
        'expected_state': 'good'
    },{
        'test_comment': 'on non-scheduled day - unscheduled ingest - pre 10',
        'right_now': dt(2026, 2, 28, 9, 00, tzinfo=timezone.utc),
        'last_ingest_date': dt(2026, 2, 27, 16, 30, tzinfo=timezone.utc),
        'expected_state': 'good'
    },{
        'test_comment': 'on non-scheduled day - unscheduled ingest, after 10 - before 12',
        'right_now': dt(2026, 2, 27, 11, 00, tzinfo=timezone.utc),
        'last_ingest_date': dt(2026, 2, 27, 10, 30, tzinfo=timezone.utc),
        'expected_state': 'good'
    },{
        'test_comment': 'on non-scheduled day - unscheduled ingest, after 12',
        'right_now': dt(2026, 2, 28, 12, 1, tzinfo=timezone.utc),
        'last_ingest_date': dt(2026, 2, 28, 10, 30, tzinfo=timezone.utc),
        'expected_state': 'good'
    }
]

@pytest.mark.parametrize("test_case",test_cases)
def test_ingest_date_check(test_case):
    state = ingest_date_check(ingest_date_check(test_case['last_ingest_date'], test_case['right_now']))
    assert state == test_case['expected_state'], f"Failed test case: {test_case['test_comment']}"