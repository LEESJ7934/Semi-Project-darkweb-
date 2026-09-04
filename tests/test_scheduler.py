import os
import unittest
from unittest.mock import patch

from scheduler.scheduler import (
    CRAWLER_SCRIPTS,
    build_scheduler,
    read_positive_int,
)


class SchedulerConfigurationTests(
    unittest.TestCase
):
    @patch.dict(
        os.environ,
        {"TEST_INTERVAL": "15"},
    )
    def test_positive_integer_is_accepted(self):
        self.assertEqual(
            read_positive_int(
                "TEST_INTERVAL",
                30,
            ),
            15,
        )

    @patch.dict(
        os.environ,
        {"TEST_INTERVAL": "invalid"},
    )
    def test_non_integer_is_rejected(self):
        with self.assertRaises(ValueError):
            read_positive_int(
                "TEST_INTERVAL",
                30,
            )

    @patch.dict(
        os.environ,
        {"TEST_INTERVAL": "0"},
    )
    def test_zero_is_rejected(self):
        with self.assertRaises(ValueError):
            read_positive_int(
                "TEST_INTERVAL",
                30,
            )

    def test_all_crawlers_are_registered_once(self):
        scheduler = build_scheduler()
        jobs = scheduler.get_jobs()

        expected_ids = {
            script_name.removesuffix(".py")
            for script_name in CRAWLER_SCRIPTS
        }
        actual_ids = {
            job.id
            for job in jobs
        }

        self.assertEqual(
            len(jobs),
            len(CRAWLER_SCRIPTS),
        )
        self.assertEqual(
            actual_ids,
            expected_ids,
        )

        for job in jobs:
            self.assertEqual(
                job.max_instances,
                1,
            )
            self.assertTrue(job.coalesce)


if __name__ == "__main__":
    unittest.main()