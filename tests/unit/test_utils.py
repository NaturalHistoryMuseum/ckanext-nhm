from datetime import datetime as dt
from datetime import timezone
from unittest.mock import MagicMock, patch

import pytest
from ckan.plugins import toolkit
from freezegun import freeze_time

from ckanext.nhm.lib.utils import get_ingest_status

test_cases = [
    {
        'test_comment': 'on scheduled day, before 10',
        'right_now': dt(2026, 2, 24, 8, 30, tzinfo=timezone.utc),
        'last_ingest_date': dt(2026, 2, 23, 10, 30, tzinfo=timezone.utc),
        'expected_state': 'good',
    },
    {
        'test_comment': 'on scheduled day, after 10 - before 12',
        'right_now': dt(2026, 2, 24, 11, 00, tzinfo=timezone.utc),
        'last_ingest_date': dt(2026, 2, 23, 10, 30, tzinfo=timezone.utc),
        'expected_state': 'ok',
    },
    {
        'test_comment': 'on scheduled day, after 10 - before 12 - ingest happened',
        'right_now': dt(2026, 2, 24, 11, 00, tzinfo=timezone.utc),
        'last_ingest_date': dt(2026, 2, 24, 10, 30, tzinfo=timezone.utc),
        'expected_state': 'good',
    },
    {
        'test_comment': 'on scheduled day, after 12 - ingest happened',
        'right_now': dt(2026, 2, 24, 12, 1, tzinfo=timezone.utc),
        'last_ingest_date': dt(2026, 2, 24, 10, 30, tzinfo=timezone.utc),
        'expected_state': 'good',
    },
    {
        'test_comment': 'on scheduled day, after 12 - ingest didnt happen',
        'right_now': dt(2026, 2, 24, 12, 1, tzinfo=timezone.utc),
        'last_ingest_date': dt(2026, 2, 23, 10, 30, tzinfo=timezone.utc),
        'expected_state': 'bad',
    },
    {
        'test_comment': 'on scheduled day - last day didnt happen - pre 10',
        'right_now': dt(2026, 2, 24, 9, 00, tzinfo=timezone.utc),
        'last_ingest_date': dt(2026, 2, 22, 10, 30, tzinfo=timezone.utc),
        'expected_state': 'bad',
    },
    {
        'test_comment': 'on scheduled day - last day didnt happen, after 10 - before 12',
        'right_now': dt(2026, 2, 24, 11, 00, tzinfo=timezone.utc),
        'last_ingest_date': dt(2026, 2, 22, 10, 30, tzinfo=timezone.utc),
        'expected_state': 'bad',
    },
    {
        'test_comment': 'on scheduled day - last day didnt happen, after 12',
        'right_now': dt(2026, 2, 24, 12, 1, tzinfo=timezone.utc),
        'last_ingest_date': dt(2026, 2, 22, 10, 30, tzinfo=timezone.utc),
        'expected_state': 'bad',
    },
    {
        'test_comment': 'on scheduled day - sunday - last day did happen - pre 10',
        'right_now': dt(2026, 3, 1, 9, 00, tzinfo=timezone.utc),
        'last_ingest_date': dt(2026, 2, 26, 10, 30, tzinfo=timezone.utc),
        'expected_state': 'good',
    },
    {
        'test_comment': 'on scheduled day - sunday - last day did happen, after 10 - before 12',
        'right_now': dt(2026, 3, 1, 11, 00, tzinfo=timezone.utc),
        'last_ingest_date': dt(2026, 2, 26, 10, 30, tzinfo=timezone.utc),
        'expected_state': 'ok',
    },
    {
        'test_comment': 'on scheduled day - sunday - today did happen, after 12',
        'right_now': dt(2026, 3, 1, 12, 1, tzinfo=timezone.utc),
        'last_ingest_date': dt(2026, 3, 1, 10, 30, tzinfo=timezone.utc),
        'expected_state': 'good',
    },
    {
        'test_comment': 'on scheduled day - sunday - today didnt happen, after 12',
        'right_now': dt(2026, 3, 1, 12, 1, tzinfo=timezone.utc),
        'last_ingest_date': dt(2026, 2, 26, 10, 30, tzinfo=timezone.utc),
        'expected_state': 'bad',
    },
    {
        'test_comment': 'on scheduled day - sunday - last day didnt happen - pre 10',
        'right_now': dt(2026, 3, 1, 9, 00, tzinfo=timezone.utc),
        'last_ingest_date': dt(2026, 2, 22, 10, 30, tzinfo=timezone.utc),
        'expected_state': 'bad',
    },
    {
        'test_comment': 'on scheduled day - sunday - last day didnt happen, after 10 - before 12',
        'right_now': dt(2026, 3, 1, 11, 00, tzinfo=timezone.utc),
        'last_ingest_date': dt(2026, 2, 22, 10, 30, tzinfo=timezone.utc),
        'expected_state': 'bad',
    },
    {
        'test_comment': 'on scheduled day - sunday - last day didnt happen, after 12',
        'right_now': dt(2026, 3, 1, 12, 1, tzinfo=timezone.utc),
        'last_ingest_date': dt(2026, 2, 22, 10, 30, tzinfo=timezone.utc),
        'expected_state': 'bad',
    },
    {
        'test_comment': 'on scheduled day - sunday - unscheduled happen - pre 10',
        'right_now': dt(2026, 3, 1, 9, 00, tzinfo=timezone.utc),
        'last_ingest_date': dt(2026, 2, 27, 16, 30, tzinfo=timezone.utc),
        'expected_state': 'good',
    },
    {
        'test_comment': 'on scheduled day - sunday - unscheduled happened, after 10 - before 12',
        'right_now': dt(2026, 3, 1, 11, 00, tzinfo=timezone.utc),
        'last_ingest_date': dt(2026, 3, 1, 1, 30, tzinfo=timezone.utc),
        'expected_state': 'ok',
    },
    {
        'test_comment': 'on scheduled day - sunday - unscheduled happened - today didnt, after 12',
        'right_now': dt(2026, 3, 1, 12, 1, tzinfo=timezone.utc),
        'last_ingest_date': dt(2026, 2, 28, 11, 30, tzinfo=timezone.utc),
        'expected_state': 'bad',
    },
    {
        'test_comment': 'on non-scheduled day - last scheduled day didnt happen - pre 10',
        'right_now': dt(2026, 2, 28, 9, 00, tzinfo=timezone.utc),
        'last_ingest_date': dt(2026, 2, 25, 10, 30, tzinfo=timezone.utc),
        'expected_state': 'bad',
    },
    {
        'test_comment': 'on non-scheduled day - last scheduled day didnt happen, after 10 - before 12',
        'right_now': dt(2026, 2, 27, 11, 00, tzinfo=timezone.utc),
        'last_ingest_date': dt(2026, 2, 24, 10, 30, tzinfo=timezone.utc),
        'expected_state': 'bad',
    },
    {
        'test_comment': 'on non-scheduled day - last scheduled day didnt happen, after 12',
        'right_now': dt(2026, 2, 28, 12, 1, tzinfo=timezone.utc),
        'last_ingest_date': dt(2026, 2, 23, 10, 30, tzinfo=timezone.utc),
        'expected_state': 'bad',
    },
    {
        'test_comment': 'on non-scheduled day - last scheduled day did happen - pre 10',
        'right_now': dt(2026, 2, 28, 9, 00, tzinfo=timezone.utc),
        'last_ingest_date': dt(2026, 2, 26, 10, 30, tzinfo=timezone.utc),
        'expected_state': 'good',
    },
    {
        'test_comment': 'on non-scheduled day - last scheduled day did happen, after 10 - before 12',
        'right_now': dt(2026, 2, 27, 11, 00, tzinfo=timezone.utc),
        'last_ingest_date': dt(2026, 2, 26, 10, 30, tzinfo=timezone.utc),
        'expected_state': 'good',
    },
    {
        'test_comment': 'on non-scheduled day - last scheduled day did happen, after 12',
        'right_now': dt(2026, 2, 28, 12, 1, tzinfo=timezone.utc),
        'last_ingest_date': dt(2026, 2, 26, 10, 30, tzinfo=timezone.utc),
        'expected_state': 'good',
    },
    {
        'test_comment': 'on non-scheduled day - unscheduled ingest - pre 10',
        'right_now': dt(2026, 2, 28, 9, 00, tzinfo=timezone.utc),
        'last_ingest_date': dt(2026, 2, 27, 16, 30, tzinfo=timezone.utc),
        'expected_state': 'good',
    },
    {
        'test_comment': 'on non-scheduled day - unscheduled ingest, after 10 - before 12',
        'right_now': dt(2026, 2, 27, 11, 00, tzinfo=timezone.utc),
        'last_ingest_date': dt(2026, 2, 27, 10, 30, tzinfo=timezone.utc),
        'expected_state': 'good',
    },
    {
        'test_comment': 'on non-scheduled day - unscheduled ingest, after 12',
        'right_now': dt(2026, 2, 28, 12, 1, tzinfo=timezone.utc),
        'last_ingest_date': dt(2026, 2, 28, 10, 30, tzinfo=timezone.utc),
        'expected_state': 'good',
    },
]


@pytest.mark.parametrize('test_case', test_cases)
def test_ingest_date_check(test_case):
    def _mock_get(action_name):
        if action_name == 'vds_version_round':
            last_ingest_ts = test_case['last_ingest_date'].timestamp() * 1000
            return MagicMock(return_value=last_ingest_ts)
        return toolkit.get_action(action_name)

    with freeze_time(test_case['right_now']):
        with patch('ckan.plugins.toolkit.get_action') as mock_get_action:
            mock_get_action.side_effect = _mock_get
            status_dict = get_ingest_status()
            assert status_dict['state'] == test_case['expected_state'], (
                f'Failed test case: {test_case["test_comment"]}'
            )
