"""Test subreddit_stats."""
import mock
from prawtools.stats import SubRedditStats

from . import IntegrationTest


class StatsTest(IntegrationTest):
    def setUp(self):
        """Setup runs before all test cases."""
        self.srs = SubRedditStats('redditdev', None, None, None)
        super(StatsTest, self).setUp(self.srs.reddit._core._requestor._http)

    def test_prev_stat(self):
        self.assertEqual(0, self.srs.min_date)
        self.assertEqual(None, self.srs.prev_srs)
        with self.recorder.use_cassette('StatsTest.prev_stat'):
            self.srs.prev_stat('10agf2')
        self.assertGreater(self.srs.min_date, 0)
        self.assertEqual('10agf2', self.srs.prev_srs.id)

    def test_recent(self):
        with self.recorder.use_cassette('StatsTest.recent'):
            self.assertTrue(
                self.srs.fetch_recent_submissions(
                    max_duration=7, after=None, exclude_self=False,
                    exclude_link=False))
            self.assertTrue(len(self.srs.submissions) > 1)
            prev = 0
            for submission in self.srs.submissions:
                self.assertTrue(prev < submission.created_utc)
                prev = submission.created_utc

    def test_recent_with_prev_stat(self):
        self.srs.subreddit = self.srs.reddit.subreddit('reddit_api_test')
        with self.recorder.use_cassette('StatsTest.recent_with_prev_stat'):
            self.assertFalse(
                self.srs.fetch_recent_submissions(
                    max_duration=7, after=None, exclude_self=False,
                    exclude_link=False))
        self.assertEqual(0, len(self.srs.submissions))

    def test_recent_type_eror(self):
        self.assertRaises(TypeError, self.srs.fetch_recent_submissions,
                          exclude_self=True, exclude_link=True, after=None,
                          max_duration=7)

    @mock.patch('time.sleep', return_value=None)
    def test_top(self, _sleep_mock):
        with self.recorder.use_cassette('StatsTest.top'):
            self.assertTrue(
                self.srs.fetch_top_submissions('week', None, None))
            self.assertTrue(len(self.srs.submissions) > 1)
            prev = 0
            for submission in self.srs.submissions:
                self.assertTrue(prev < submission.created_utc)
                prev = submission.created_utc

    def test_top_type_eror(self):
        self.assertRaises(TypeError, self.srs.fetch_top_submissions,
                          exclude_self=True, exclude_link=True)
