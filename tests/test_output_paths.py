from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.main import _build_output_prefix, _extract_video_key
from src.pipeline import _parse_subtitle_payload


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

    def test_parse_subtitle_payload_uses_track_ext_for_json3(self) -> None:
        raw = '{"events":[{"segs":[{"utf8":"こんにちは"},{"utf8":"。"}]}]}'

        parsed = _parse_subtitle_payload(
            raw,
            sub_url="https://example.com/api/timedtext?lang=ja",
            track_ext="json3",
        )

        self.assertEqual(parsed, "こんにちは。")

    def test_parse_subtitle_payload_uses_url_query_for_json3(self) -> None:
        raw = '{"events":[{"segs":[{"utf8":"日本語"},{"utf8":"字幕"}]}]}'

        parsed = _parse_subtitle_payload(
            raw,
            sub_url="https://example.com/api/timedtext?lang=ja&fmt=json3",
            track_ext=None,
        )

        self.assertEqual(parsed, "日本語字幕")


if __name__ == "__main__":
    unittest.main()
