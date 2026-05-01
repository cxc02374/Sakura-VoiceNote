from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.main import _build_output_prefix, _extract_video_key


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

    def test_build_output_prefix_creates_unique_name(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            first = _build_output_prefix(base)
            (base / f"{first}_transcript.txt").write_text("dummy", encoding="utf-8")
            second = _build_output_prefix(base)

            self.assertNotEqual(first, second)
            self.assertRegex(first, r"^\d{14}$")
            self.assertRegex(second, r"^\d{14}_2$")


if __name__ == "__main__":
    unittest.main()
