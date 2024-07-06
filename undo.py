import os
import struct

# File names
TARGET_FILE_PATH_STRING = "hello_world.test.bmp"
MARKER = b"FILE_DATA_BEGIN"
marker_size = len(MARKER)
CHUNK_SIZE = 1024 * 1024  # 1 MB
RESTORED_FILE_SUFFIX = ".restored"


# Step 1: Locate the marker in the combined file and extract the filename
def find_marker_and_filename(file_path, marker, CHUNK_SIZE):
    with open(file_path, "rb") as file:
        buffer = b""
        file_position = 0
        while True:
            chunk = file.read(CHUNK_SIZE)
            if not chunk:
                break
            buffer += chunk
            marker_position = buffer.find(marker)
            if marker_position != -1:
                # Calculate the position of the marker and filename
                file.seek(file_position + marker_position + marker_size)
                filename_length = struct.unpack("I", file.read(4))[0]
                filename = file.read(filename_length).decode("utf-8")
                return file_position + marker_position, filename
            if len(buffer) > CHUNK_SIZE:
                file_position += len(buffer) - CHUNK_SIZE
                buffer = buffer[-CHUNK_SIZE:]
    return -1, None


marker_position, original_filename = find_marker_and_filename(TARGET_FILE_PATH_STRING, MARKER, CHUNK_SIZE)

if marker_position == -1:
    raise ValueError(f"Marker `{MARKER}` not found in the input file.")

# Step 2: Read the combined file and split it
with open(TARGET_FILE_PATH_STRING, "rb") as combined_file, open(original_filename + RESTORED_FILE_SUFFIX, "wb") as extracted_data_file:

    # Copy the original video part up to the marker
    combined_file.seek(0)
    remaining_size = marker_position
    while remaining_size > 0:
        chunk = combined_file.read(min(CHUNK_SIZE, remaining_size))
        remaining_size -= len(chunk)

    # Skip the marker, filename length, and filename
    combined_file.seek(marker_position + marker_size)
    filename_length = struct.unpack("I", combined_file.read(4))[0]
    combined_file.seek(filename_length, os.SEEK_CUR)

    # Copy the injected data part
    while True:
        chunk = combined_file.read(CHUNK_SIZE)
        if not chunk:
            break
        extracted_data_file.write(chunk)

print(f"Extracted injected data to: {original_filename}")
