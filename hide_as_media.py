import shutil
import struct
from pathlib import Path
import subprocess

TARGET_FILE_PATH_STRING = "hello_world.test"
HIDE_AS_IMAGE = True        # False to hide as video
IMAGE_FILE_SUFFIX = ".bmp"
VIDEO_FILE_SUFFIX = ".mp4"

# Step 1: Create an empty BMP image file
def create_empty_bmp(file_path):
    width, height, color = 320, 240, (0, 0, 0)
    # BMP Header
    file_size = 54 + (width * height * 3)  # header size + pixel data
    bmp_header = b'BM' + struct.pack('<I', file_size) + b'\x00\x00' + b'\x00\x00' + b'\x36\x00\x00\x00'
    
    # DIB Header
    dib_header = (
        b'\x28\x00\x00\x00' + struct.pack('<I', width) + struct.pack('<I', height) +
        b'\x01\x00' + b'\x18\x00' + b'\x00\x00\x00\x00' + struct.pack('<I', width * height * 3) +
        b'\x13\x0B\x00\x00' + b'\x13\x0B\x00\x00' + b'\x00\x00\x00\x00' + b'\x00\x00\x00\x00'
    )
    
    # Pixel Data
    pixel_data = bytearray()
    for _ in range(height):
        for _ in range(width):
            pixel_data.extend(color)
    
    # Write to file
    with open(file_path, 'wb') as f:
        f.write(bmp_header)
        f.write(dib_header)
        f.write(pixel_data)

def create_empty_mp4(output_path):
    command = [
        'ffmpeg',
        '-y',                    # Overwrite output file without asking
        '-f', 'lavfi',           # Use lavfi format
        '-t', '1',               # Duration of 1 second
        '-pix_fmt', 'yuv420p',   # Pixel format for web compatibility
        output_file
    ]
    subprocess.run(command, check=True)

# Create a 320x240 black BMP image
target_file_path = Path(TARGET_FILE_PATH_STRING)
if HIDE_AS_IMAGE:
    output_file_name = target_file_path.name + IMAGE_FILE_SUFFIX
    create_empty_bmp(output_file_name)
else:
    output_file_name = target_file_path.name + VIDEO_FILE_SUFFIX
    create_empty_mp4(output_file_name)

# Step 2: Define the marker and append the bytes to the BMP file
marker = b"FILE_DATA_BEGIN"
filename = target_file_path.name.encode("utf-8")
filename_length = struct.pack("I", len(filename))
chunk_size = 1024 * 1024  # 1 MB

# Create a temporary output file
output_temp_file = output_file_name + '.temp'

with open(output_file_name, "rb") as media_file, \
     open(target_file_path, "rb") as inject_file, \
     open(output_temp_file, "wb") as new_media_file:
    
    # Copy the original media file to the new media file
    shutil.copyfileobj(media_file, new_media_file, chunk_size)
    
    # Write the marker, filename length, and filename
    new_media_file.write(marker)
    new_media_file.write(filename_length)
    new_media_file.write(filename)
    
    # Append the data file to the new media file
    shutil.copyfileobj(inject_file, new_media_file, chunk_size)

# Replace the original output file with the new one
Path(output_temp_file).replace(output_file_name)

print(f"Created media with injected data: {output_file_name}")
