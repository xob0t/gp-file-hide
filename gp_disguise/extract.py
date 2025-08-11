import os
import struct
from pathlib import Path
from typing import Optional, Tuple

from gp_disguise.config import Config


class MediaExtractor:
    """Handles extracting hidden data from media files."""

    def __init__(self, config: Config) -> None:
        """Initialize the MediaExtractor with configuration."""
        self.config = config

    def extract_file(self, media_file: Path, output_dir: Optional[Path] = None) -> Path:
        """
        Extract hidden data from a media file.

        Args:
            media_file: Path to the media file containing hidden data
            output_dir: Optional output directory (current dir if None)

        Returns:
            Path to the extracted file

        Raises:
            FileNotFoundError: If media file doesn't exist
            ValueError: If separator not found in file
        """
        if not media_file.exists():
            raise FileNotFoundError(f"Media file not found: {media_file}")

        # Find separator and extract filename
        separator_pos, original_filename = self._find_separator_and_filename(media_file)

        if separator_pos == -1 or original_filename is None:
            raise ValueError(f"No hidden data found in {media_file}")

        # Determine output path
        if output_dir:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / f"{original_filename}{self.config.restored_suffix}"
        else:
            output_path = Path(f"{original_filename}{self.config.restored_suffix}")

        # Extract data
        self._extract_data(media_file, output_path, separator_pos)

        return output_path

    def _find_separator_and_filename(self, file_path: Path) -> Tuple[int, Optional[str]]:
        """
        Locate the separator and extract the original filename.

        Args:
            file_path: Path to the media file

        Returns:
            Tuple of (separator position, original filename)
            Returns (-1, None) if separator not found
        """
        with open(file_path, "rb") as file:
            buffer = b""
            file_position = 0

            while True:
                chunk = file.read(self.config.chunk_size)
                if not chunk:
                    break

                buffer += chunk
                separator_position = buffer.find(self.config.separator)

                if separator_position != -1:
                    # Calculate absolute position
                    absolute_pos = file_position + separator_position

                    # Read filename metadata
                    file.seek(absolute_pos + len(self.config.separator))

                    try:
                        filename_length = struct.unpack("I", file.read(4))[0]
                        filename = file.read(filename_length).decode("utf-8")
                        return absolute_pos, filename
                    except (struct.error, UnicodeDecodeError):
                        # Invalid data after separator, continue searching
                        pass

                # Keep last chunk_size bytes for overlapping search
                if len(buffer) > self.config.chunk_size:
                    file_position += len(buffer) - self.config.chunk_size
                    buffer = buffer[-self.config.chunk_size :]

            return -1, None

    def _extract_data(self, media_file: Path, output_file: Path, separator_pos: int) -> None:
        """
        Extract the hidden data from the media file.

        Args:
            media_file: Path to the media file
            output_file: Path where extracted data will be saved
            separator_pos: Position of the separator in the file
        """
        with open(media_file, "rb") as mf, open(output_file, "wb") as of:
            # Skip to the data section
            mf.seek(separator_pos + len(self.config.separator))

            # Skip filename metadata
            filename_length = struct.unpack("I", mf.read(4))[0]
            mf.seek(filename_length, os.SEEK_CUR)

            # Copy hidden data
            while True:
                chunk = mf.read(self.config.chunk_size)
                if not chunk:
                    break
                of.write(chunk)
