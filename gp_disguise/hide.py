import random
import shutil
import struct
import subprocess
from pathlib import Path
from typing import Optional, Tuple

from gp_disguise.config import Config


class MediaHider:
    """Handles hiding data in media files."""

    def __init__(self, config: Config) -> None:
        """Initialize the MediaHider with configuration."""
        self.config = config

    def hide_file(self, input_file: Path, output_file: Optional[Path] = None) -> Path:
        """
        Hide a file in a media container.

        Args:
            input_file: Path to the file to hide
            output_file: Optional output path (auto-generated if None)

        Returns:
            Path to the created media file

        Raises:
            FileNotFoundError: If input file doesn't exist
            subprocess.CalledProcessError: If video generation fails
        """
        if not input_file.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")

        # Generate output filename if not provided
        if output_file is None:
            suffix = ".mp4" if self.config.is_video else ".bmp"
            output_file = input_file.parent / f"{input_file.name}{suffix}"

        # Ensure output path has correct extension
        if self.config.is_video and not output_file.suffix == ".mp4":
            output_file = output_file.with_suffix(".mp4")
        elif not self.config.is_video and not output_file.suffix == ".bmp":
            output_file = output_file.with_suffix(".bmp")

        # Create media file
        if self.config.is_video:
            self._generate_video(output_file)
        else:
            self._generate_image(output_file)

        # Append hidden data
        self._append_data(output_file, input_file)

        return output_file

    def _generate_image(self, output_path: Path) -> None:
        """Generate a BMP image with random color."""
        color = self._generate_random_color()
        width = self.config.image_width
        height = self.config.image_height

        # BMP Header
        file_size = 54 + (width * height * 3)  # header size + pixel data
        bmp_header = b"BM" + struct.pack("<I", file_size) + b"\x00\x00" + b"\x00\x00" + b"\x36\x00\x00\x00"

        # DIB Header
        dib_header = (
            b"\x28\x00\x00\x00"
            + struct.pack("<I", width)
            + struct.pack("<I", height)
            + b"\x01\x00"
            + b"\x18\x00"
            + b"\x00\x00\x00\x00"
            + struct.pack("<I", width * height * 3)
            + b"\x13\x0b\x00\x00"
            + b"\x13\x0b\x00\x00"
            + b"\x00\x00\x00\x00"
            + b"\x00\x00\x00\x00"
        )

        # Pixel Data
        pixel_data = bytearray()
        for _ in range(height):
            for _ in range(width):
                pixel_data.extend(color)

        # Write to file
        with open(output_path, "wb") as f:
            f.write(bmp_header)
            f.write(dib_header)
            f.write(pixel_data)

    def _generate_video(self, output_path: Path) -> None:
        """Generate an MP4 video with random color background."""
        color = self._generate_random_color()
        color_hex = self._rgb_to_hex(*color)

        command = [
            "ffmpeg",
            "-y",  # Overwrite output file without asking
            "-f",
            "lavfi",  # Use lavfi format
            "-i",
            f"color={color_hex}:s={self.config.video_width}x{self.config.video_height}",
            "-t",
            str(self.config.video_duration),  # Duration
            "-pix_fmt",
            "yuv420p",  # Pixel format for web compatibility
            str(output_path),
        ]

        subprocess.run(command, check=True, capture_output=True, text=True)

    def _append_data(self, media_file: Path, data_file: Path) -> None:
        """Append hidden data to the media file."""
        # Prepare metadata
        filename = data_file.name.encode("utf-8")
        filename_length = struct.pack("I", len(filename))

        # Create temporary file
        temp_file = media_file.with_suffix(media_file.suffix + ".temp")

        with open(media_file, "rb") as mf, open(data_file, "rb") as df, open(temp_file, "wb") as tf:
            # Copy original media
            shutil.copyfileobj(mf, tf, self.config.chunk_size)

            # Write separator and metadata
            tf.write(self.config.separator)
            tf.write(filename_length)
            tf.write(filename)

            # Append data
            shutil.copyfileobj(df, tf, self.config.chunk_size)

        # Replace original with modified
        temp_file.replace(media_file)

    @staticmethod
    def _generate_random_color() -> Tuple[int, int, int]:
        """Generate a random RGB color."""
        return (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255),
        )

    @staticmethod
    def _rgb_to_hex(r: int, g: int, b: int) -> str:
        """Convert RGB color to hexadecimal string."""
        return f"#{r:02x}{g:02x}{b:02x}"
