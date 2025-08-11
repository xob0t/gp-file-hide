from dataclasses import dataclass


@dataclass
class Config:
    """Configuration for media steganography operations."""

    chunk_size: int = 1024 * 1024  # 1 MB default
    separator: bytes = b"FILE_DATA_BEGIN"
    is_video: bool = False  # False for image, True for video
    restored_suffix: str = ".restored"

    # Media generation settings
    image_width: int = 320
    image_height: int = 240
    video_width: int = 1280
    video_height: int = 720
    video_duration: int = 1  # seconds
