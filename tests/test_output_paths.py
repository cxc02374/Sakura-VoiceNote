from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.main import _build_run_output_dir, _extract_video_key


class OutputPathTests(unittest.TestCase):
    def test_extract_video_key_from_youtube_watch_url(self) -> None:
        self.assertEqual(
            _extract_video_key("https://www.youtube.com/watch?v=PygUK16aQgk&ab_channel=test"),
            "PygUK16aQgk",
        )

    def test_extract_video_key_from_short_url(self) -> None:
        self.assertEqual(
            _extract_video_key("https://youtu.be/PygUK16aQgk"),
            "PygUK16aQgk",
        )

    def test_build_run_output_dir_creates_unique_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            first = _build_run_output_dir(base, "https://www.youtube.com/watch?v=PygUK16aQgk")
            second = _build_run_output_dir(base, "https://www.youtube.com/watch?v=PygUK16aQgk")

            self.assertTrue(first.exists())
            self.assertTrue(second.exists())
            self.assertNotEqual(first, second)
            self.assertEqual(first.parent, base)
            self.assertEqual(second.parent, base)


if __name__ == "__main__":
    unittest.main()
