from datetime import datetime as dt
from datetime import timezone
from unittest.mock import MagicMock, patch

import pytest
import pytz
from ckan.plugins import toolkit
from freezegun import freeze_time

from ckanext.nhm.lib.utils import get_ingest_status

# set timezone
uk_tz = pytz.timezone('Europe/London')


def set_uk_tz(year, month, day, hour, minute=0):
    """
    Create a UTC datetime from a UK local time.
    """
    return uk_tz.localize(dt(year, month, day, hour, minute), is_dst=False).astimezone(
        timezone.utc
    )


# test cases
test_cases = [
    {
        'test_comment': 'on scheduled day, before 10',
        'right_now': set_uk_tz(2026, 2, 24, 8, 30),
        'last_ingest_date': set_uk_tz(2026, 2, 23, 10, 30),
        'expected_state': 'good',
    },
    {
        'test_comment': 'on scheduled day, after 10 - before 12',
        'right_now': set_uk_tz(2026, 2, 24, 11, 0),
        'last_ingest_date': set_uk_tz(2026, 2, 23, 10, 30),
        'expected_state': 'ok',
    },
    {
        'test_comment': 'on scheduled day, after 10 - before 12 - ingest happened',
        'right_now': set_uk_tz(2026, 2, 24, 11, 0),
        'last_ingest_date': set_uk_tz(2026, 2, 24, 10, 30),
        'expected_state': 'good',
    },
    {
        'test_comment': 'on scheduled day, after 12 - ingest happened',
        'right_now': set_uk_tz(2026, 2, 24, 12, 1),
        'last_ingest_date': set_uk_tz(2026, 2, 24, 10, 30),
        'expected_state': 'good',
    },
    {
        'test_comment': 'on scheduled day, after 12 - ingest didnt happen',
        'right_now': set_uk_tz(2026, 2, 24, 12, 1),
        'last_ingest_date': set_uk_tz(2026, 2, 23, 10, 30),
        'expected_state': 'bad',
    },
    {
        'test_comment': 'on scheduled day - last day didnt happen - pre 10',
        'right_now': set_uk_tz(2026, 2, 24, 9, 0),
        'last_ingest_date': set_uk_tz(2026, 2, 22, 10, 30),
        'expected_state': 'bad',
    },
    {
        'test_comment': 'on scheduled day - last day didnt happen, after 10 - before 12',
        'right_now': set_uk_tz(2026, 2, 24, 11, 0),
        'last_ingest_date': set_uk_tz(2026, 2, 22, 10, 30),
        'expected_state': 'bad',
    },
    {
        'test_comment': 'on scheduled day - last day didnt happen, after 12',
        'right_now': set_uk_tz(2026, 2, 24, 12, 1),
        'last_ingest_date': set_uk_tz(2026, 2, 22, 10, 30),
        'expected_state': 'bad',
    },
    {
        'test_comment': 'on scheduled day - sunday - last day did happen - pre 10',
        'right_now': set_uk_tz(2026, 3, 1, 9, 0),
        'last_ingest_date': set_uk_tz(2026, 2, 26, 10, 30),
        'expected_state': 'good',
    },
    {
        'test_comment': 'on scheduled day - sunday - last day did happen, after 10 - before 12',
        'right_now': set_uk_tz(2026, 3, 1, 11, 0),
        'last_ingest_date': set_uk_tz(2026, 2, 26, 10, 30),
        'expected_state': 'ok',
    },
    {
        'test_comment': 'on scheduled day - sunday - today did happen, after 12',
        'right_now': set_uk_tz(2026, 3, 1, 12, 1),
        'last_ingest_date': set_uk_tz(2026, 3, 1, 10, 30),
        'expected_state': 'good',
    },
    {
        'test_comment': 'on scheduled day - sunday - today didnt happen, after 12',
        'right_now': set_uk_tz(2026, 3, 1, 12, 1),
        'last_ingest_date': set_uk_tz(2026, 2, 26, 10, 30),
        'expected_state': 'bad',
    },
    {
        'test_comment': 'on scheduled day - sunday - last day didnt happen - pre 10',
        'right_now': set_uk_tz(2026, 3, 1, 9, 0),
        'last_ingest_date': set_uk_tz(2026, 2, 22, 10, 30),
        'expected_state': 'bad',
    },
    {
        'test_comment': 'on scheduled day - sunday - last day didnt happen, after 10 - before 12',
        'right_now': set_uk_tz(2026, 3, 1, 11, 0),
        'last_ingest_date': set_uk_tz(2026, 2, 22, 10, 30),
        'expected_state': 'bad',
    },
    {
        'test_comment': 'on scheduled day - sunday - last day didnt happen, after 12',
        'right_now': set_uk_tz(2026, 3, 1, 12, 1),
        'last_ingest_date': set_uk_tz(2026, 2, 22, 10, 30),
        'expected_state': 'bad',
    },
    {
        'test_comment': 'on scheduled day - sunday - unscheduled happen - pre 10',
        'right_now': set_uk_tz(2026, 3, 1, 9, 0),
        'last_ingest_date': set_uk_tz(2026, 2, 27, 16, 30),
        'expected_state': 'good',
    },
    {
        'test_comment': 'on scheduled day - sunday - unscheduled happened, after 10 - before 12',
        'right_now': set_uk_tz(2026, 3, 1, 11, 0),
        'last_ingest_date': set_uk_tz(2026, 3, 1, 1, 30),
        'expected_state': 'ok',
    },
    {
        'test_comment': 'on scheduled day - sunday - unscheduled happened - today didnt, after 12',
        'right_now': set_uk_tz(2026, 3, 1, 12, 1),
        'last_ingest_date': set_uk_tz(2026, 2, 28, 11, 30),
        'expected_state': 'bad',
    },
    {
        'test_comment': 'on non-scheduled day - last scheduled day didnt happen - pre 10',
        'right_now': set_uk_tz(2026, 2, 28, 9, 0),
        'last_ingest_date': set_uk_tz(2026, 2, 25, 10, 30),
        'expected_state': 'bad',
    },
    {
        'test_comment': 'on non-scheduled day - last scheduled day didnt happen, after 10 - before 12',
        'right_now': set_uk_tz(2026, 2, 27, 11, 0),
        'last_ingest_date': set_uk_tz(2026, 2, 24, 10, 30),
        'expected_state': 'bad',
    },
    {
        'test_comment': 'on non-scheduled day - last scheduled day didnt happen, after 12',
        'right_now': set_uk_tz(2026, 2, 28, 12, 1),
        'last_ingest_date': set_uk_tz(2026, 2, 23, 10, 30),
        'expected_state': 'bad',
    },
    {
        'test_comment': 'on non-scheduled day - last scheduled day did happen - pre 10',
        'right_now': set_uk_tz(2026, 2, 28, 9, 0),
        'last_ingest_date': set_uk_tz(2026, 2, 26, 10, 30),
        'expected_state': 'good',
    },
    {
        'test_comment': 'on non-scheduled day - last scheduled day did happen, after 10 - before 12',
        'right_now': set_uk_tz(2026, 2, 27, 11, 0),
        'last_ingest_date': set_uk_tz(2026, 2, 26, 10, 30),
        'expected_state': 'good',
    },
    {
        'test_comment': 'on non-scheduled day - last scheduled day did happen, after 12',
        'right_now': set_uk_tz(2026, 2, 28, 12, 1),
        'last_ingest_date': set_uk_tz(2026, 2, 26, 10, 30),
        'expected_state': 'good',
    },
    {
        'test_comment': 'on non-scheduled day - unscheduled ingest - pre 10',
        'right_now': set_uk_tz(2026, 2, 28, 9, 0),
        'last_ingest_date': set_uk_tz(2026, 2, 27, 16, 30),
        'expected_state': 'good',
    },
    {
        'test_comment': 'on non-scheduled day - unscheduled ingest, after 10 - before 12',
        'right_now': set_uk_tz(2026, 2, 27, 11, 0),
        'last_ingest_date': set_uk_tz(2026, 2, 27, 10, 30),
        'expected_state': 'good',
    },
    {
        'test_comment': 'on non-scheduled day - unscheduled ingest, after 12',
        'right_now': set_uk_tz(2026, 2, 28, 12, 1),
        'last_ingest_date': set_uk_tz(2026, 2, 28, 10, 30),
        'expected_state': 'good',
    },
    {
        'test_comment': 'on scheduled day, before 10-summer',
        'expected_state': 'good',
        'right_now': set_uk_tz(2026, 4, 7, 8, 30),
        'last_ingest_date': set_uk_tz(2026, 4, 6, 10, 30),
    },
    {
        'test_comment': 'on scheduled day, after 10 - before 12-summer',
        'expected_state': 'ok',
        'right_now': set_uk_tz(2026, 4, 7, 11, 0),
        'last_ingest_date': set_uk_tz(2026, 4, 6, 10, 30),
    },
    {
        'test_comment': 'on scheduled day, after 10 - before 12 - ingest happened-summer',
        'expected_state': 'good',
        'right_now': set_uk_tz(2026, 4, 7, 11, 0),
        'last_ingest_date': set_uk_tz(2026, 4, 7, 10, 30),
    },
    {
        'test_comment': 'on scheduled day, after 12 - ingest happened-summer',
        'expected_state': 'good',
        'right_now': set_uk_tz(2026, 4, 7, 12, 1),
        'last_ingest_date': set_uk_tz(2026, 4, 7, 10, 30),
    },
    {
        'test_comment': 'on scheduled day, after 12 - ingest didnt happen-summer',
        'expected_state': 'bad',
        'right_now': set_uk_tz(2026, 4, 7, 12, 1),
        'last_ingest_date': set_uk_tz(2026, 4, 6, 10, 30),
    },
    {
        'test_comment': 'on scheduled day - last day didnt happen - pre 10-summer',
        'expected_state': 'bad',
        'right_now': set_uk_tz(2026, 4, 7, 9, 0),
        'last_ingest_date': set_uk_tz(2026, 4, 5, 10, 30),
    },
    {
        'test_comment': 'on scheduled day - last day didnt happen, after 10 - before 12-summer',
        'expected_state': 'bad',
        'right_now': set_uk_tz(2026, 4, 7, 11, 0),
        'last_ingest_date': set_uk_tz(2026, 4, 5, 10, 30),
    },
    {
        'test_comment': 'on scheduled day - last day didnt happen, after 12-summer',
        'expected_state': 'bad',
        'right_now': set_uk_tz(2026, 4, 7, 12, 1),
        'last_ingest_date': set_uk_tz(2026, 4, 5, 10, 30),
    },
    {
        'test_comment': 'on scheduled day - sunday - last day did happen - pre 10-summer',
        'expected_state': 'good',
        'right_now': set_uk_tz(2026, 4, 12, 9, 0),
        'last_ingest_date': set_uk_tz(2026, 4, 9, 10, 30),
    },
    {
        'test_comment': 'on scheduled day - sunday - last day did happen, after 10 - before 12-summer',
        'expected_state': 'ok',
        'right_now': set_uk_tz(2026, 4, 12, 11, 0),
        'last_ingest_date': set_uk_tz(2026, 4, 9, 10, 30),
    },
    {
        'test_comment': 'on scheduled day - sunday - today did happen, after 12-summer',
        'expected_state': 'good',
        'right_now': set_uk_tz(2026, 4, 12, 12, 1),
        'last_ingest_date': set_uk_tz(2026, 4, 12, 10, 30),
    },
    {
        'test_comment': 'on scheduled day - sunday - today didnt happen, after 12-summer',
        'expected_state': 'bad',
        'right_now': set_uk_tz(2026, 4, 12, 12, 1),
        'last_ingest_date': set_uk_tz(2026, 4, 9, 10, 30),
    },
    {
        'test_comment': 'on scheduled day - sunday - last day didnt happen - pre 10-summer',
        'expected_state': 'bad',
        'right_now': set_uk_tz(2026, 4, 12, 9, 0),
        'last_ingest_date': set_uk_tz(2026, 4, 5, 10, 30),
    },
    {
        'test_comment': 'on scheduled day - sunday - last day didnt happen, after 10 - before 12-summer',
        'expected_state': 'bad',
        'right_now': set_uk_tz(2026, 4, 12, 11, 0),
        'last_ingest_date': set_uk_tz(2026, 4, 5, 10, 30),
    },
    {
        'test_comment': 'on scheduled day - sunday - last day didnt happen, after 12-summer',
        'expected_state': 'bad',
        'right_now': set_uk_tz(2026, 4, 12, 12, 1),
        'last_ingest_date': set_uk_tz(2026, 4, 5, 10, 30),
    },
    {
        'test_comment': 'on scheduled day - sunday - unscheduled happen - pre 10-summer',
        'expected_state': 'good',
        'right_now': set_uk_tz(2026, 4, 12, 9, 0),
        'last_ingest_date': set_uk_tz(2026, 4, 10, 16, 30),
    },
    {
        'test_comment': 'on scheduled day - sunday - unscheduled happened, after 10 - before 12-summer',
        'expected_state': 'ok',
        'right_now': set_uk_tz(2026, 4, 12, 11, 0),
        'last_ingest_date': set_uk_tz(2026, 4, 12, 1, 30),
    },
    {
        'test_comment': 'on scheduled day - sunday - unscheduled happened - today didnt, after 12-summer',
        'expected_state': 'bad',
        'right_now': set_uk_tz(2026, 4, 12, 12, 1),
        'last_ingest_date': set_uk_tz(2026, 4, 11, 11, 30),
    },
    {
        'test_comment': 'on non-scheduled day - last scheduled day didnt happen - pre 10-summer',
        'expected_state': 'bad',
        'right_now': set_uk_tz(2026, 4, 11, 9, 0),
        'last_ingest_date': set_uk_tz(2026, 4, 8, 10, 30),
    },
    {
        'test_comment': 'on non-scheduled day - last scheduled day didnt happen, after 10 - before 12-summer',
        'expected_state': 'bad',
        'right_now': set_uk_tz(2026, 4, 10, 11, 0),
        'last_ingest_date': set_uk_tz(2026, 4, 7, 10, 30),
    },
    {
        'test_comment': 'on non-scheduled day - last scheduled day didnt happen, after 12-summer',
        'expected_state': 'bad',
        'right_now': set_uk_tz(2026, 4, 11, 12, 1),
        'last_ingest_date': set_uk_tz(2026, 4, 6, 10, 30),
    },
    {
        'test_comment': 'on non-scheduled day - last scheduled day did happen - pre 10-summer',
        'expected_state': 'good',
        'right_now': set_uk_tz(2026, 4, 11, 9, 0),
        'last_ingest_date': set_uk_tz(2026, 4, 9, 10, 30),
    },
    {
        'test_comment': 'on non-scheduled day - last scheduled day did happen, after 10 - before 12-summer',
        'expected_state': 'good',
        'right_now': set_uk_tz(2026, 4, 10, 11, 0),
        'last_ingest_date': set_uk_tz(2026, 4, 9, 10, 30),
    },
    {
        'test_comment': 'on non-scheduled day - last scheduled day did happen, after 12-summer',
        'expected_state': 'good',
        'right_now': set_uk_tz(2026, 4, 11, 12, 1),
        'last_ingest_date': set_uk_tz(2026, 4, 9, 10, 30),
    },
    {
        'test_comment': 'on non-scheduled day - unscheduled ingest - pre 10-summer',
        'expected_state': 'good',
        'right_now': set_uk_tz(2026, 4, 11, 9, 0),
        'last_ingest_date': set_uk_tz(2026, 4, 10, 16, 30),
    },
    {
        'test_comment': 'on non-scheduled day - unscheduled ingest, after 10 - before 12-summer',
        'expected_state': 'good',
        'right_now': set_uk_tz(2026, 4, 10, 11, 0),
        'last_ingest_date': set_uk_tz(2026, 4, 10, 10, 30),
    },
    {
        'test_comment': 'on non-scheduled day - unscheduled ingest, after 12-summer',
        'expected_state': 'good',
        'right_now': set_uk_tz(2026, 4, 11, 12, 1),
        'last_ingest_date': set_uk_tz(2026, 4, 11, 10, 30),
    },
]


@pytest.mark.parametrize('test_case', test_cases, ids=lambda x: x['test_comment'])
def test_ingest_date_check(test_case):
    def _mock_get(action_name):
        if action_name == 'vds_version_round':
            last_ingest_ts = test_case['last_ingest_date'].timestamp() * 1000
            return MagicMock(return_value=last_ingest_ts)
        return toolkit.get_action(action_name)

    with freeze_time(test_case['right_now'], tz_offset=0):
        with patch('ckan.plugins.toolkit.get_action') as mock_get_action:
            mock_get_action.side_effect = _mock_get
            get_ingest_status.cache_clear()
            status_dict = get_ingest_status()
            assert status_dict['state'] == test_case['expected_state'], (
                f'Failed test case: {test_case["test_comment"]}'
            )
