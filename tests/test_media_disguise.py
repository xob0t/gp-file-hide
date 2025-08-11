import tempfile
import unittest
from pathlib import Path

from gp_disguise import MediaHider, MediaExtractor, Config


class TestMediaDisguise(unittest.TestCase):
    """Test hiding and extracting data."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = Path(self.temp_dir.name)

    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()

    def test_hide_and_extract_image(self):
        """Test hiding data in BMP image and extracting it."""
        # Create test file
        test_file = self.test_dir / "test_data.txt"
        test_content = b"This is secret test data!\nLine 2\nLine 3"
        test_file.write_bytes(test_content)

        # Hide in image
        config = Config(is_video=False)
        hider = MediaHider(config)
        media_file = hider.hide_file(test_file, self.test_dir / "output.bmp")

        # Verify media file exists
        self.assertTrue(media_file.exists())
        self.assertEqual(media_file.suffix, ".bmp")

        # Extract data
        extractor = MediaExtractor(config)
        extracted_file = extractor.extract_file(media_file, self.test_dir)

        # Verify extracted content
        self.assertTrue(extracted_file.exists())
        extracted_content = extracted_file.read_bytes()
        self.assertEqual(extracted_content, test_content)

    def test_hide_and_extract_video(self):
        """Test hiding data in MP4 video and extracting it."""
        # Create test file
        test_file = self.test_dir / "secret.json"
        test_content = b'{"key": "value", "number": 42}'
        test_file.write_bytes(test_content)

        # Hide in video
        config = Config(is_video=True)
        hider = MediaHider(config)
        media_file = hider.hide_file(test_file, self.test_dir / "output.mp4")

        # Verify media file exists
        self.assertTrue(media_file.exists())
        self.assertEqual(media_file.suffix, ".mp4")

        # Extract data
        extractor = MediaExtractor(config)
        extracted_file = extractor.extract_file(media_file, self.test_dir)

        # Verify extracted content
        self.assertTrue(extracted_file.exists())
        extracted_content = extracted_file.read_bytes()
        self.assertEqual(extracted_content, test_content)

    def test_custom_separator(self):
        """Test using custom separator."""
        # Create test file
        test_file = self.test_dir / "data.bin"
        test_content = b"\x00\x01\x02\x03\x04\x05"
        test_file.write_bytes(test_content)

        # Hide with custom separator
        config = Config(is_video=False, separator=b"CUSTOM_MARKER_123")
        hider = MediaHider(config)
        media_file = hider.hide_file(test_file)

        # Extract with same separator
        extractor = MediaExtractor(config)
        extracted_file = extractor.extract_file(media_file, self.test_dir)

        # Verify content
        self.assertEqual(extracted_file.read_bytes(), test_content)

    def test_file_not_found(self):
        """Test error handling for missing files."""
        config = Config()
        hider = MediaHider(config)

        with self.assertRaises(FileNotFoundError):
            hider.hide_file(Path("nonexistent.txt"))

        extractor = MediaExtractor(config)
        with self.assertRaises(FileNotFoundError):
            extractor.extract_file(Path("nonexistent.bmp"))

    def test_no_hidden_data(self):
        """Test extracting from file without hidden data."""
        # Create regular BMP without hidden data
        clean_bmp = self.test_dir / "clean.bmp"
        clean_bmp.write_bytes(b"BM" + b"\x00" * 100)

        config = Config()
        extractor = MediaExtractor(config)

        with self.assertRaises(ValueError) as ctx:
            extractor.extract_file(clean_bmp)

        self.assertIn("No hidden data found", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
