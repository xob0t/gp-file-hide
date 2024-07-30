import os
import struct

# File names
TARGET_FILE_PATH_STRING = "hello_world.test.bmp"
SEPARATOR = b"FILE_DATA_BEGIN"
CHUNK_SIZE = 1024 * 1024  # 1 MB
RESTORED_FILE_SUFFIX = ".restored"


# Step 1: Locate the separator in the combined file and extract the filename
def find_separator_and_filename(file_path, separator, chunk_size):
    with open(file_path, "rb") as file:
        buffer = b""
        file_position = 0
        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                break
            buffer += chunk
            separator_position = buffer.find(separator)
            if separator_position != -1:
                # Calculate the position of the separator and filename
                file.seek(file_position + separator_position + len(separator))
                filename_length = struct.unpack("I", file.read(4))[0]
                filename = file.read(filename_length).decode("utf-8")
                return file_position + separator_position, filename
            if len(buffer) > chunk_size:
                file_position += len(buffer) - chunk_size
                buffer = buffer[-chunk_size:]
    return -1, None


separator_position, original_filename = find_separator_and_filename(TARGET_FILE_PATH_STRING, SEPARATOR, CHUNK_SIZE)

if separator_position == -1:
    raise ValueError(f"Marker `{SEPARATOR}` not found in the input file.")

# Step 2: Read the combined file and split it
with open(TARGET_FILE_PATH_STRING, "rb") as combined_file, open(original_filename + RESTORED_FILE_SUFFIX, "wb") as extracted_data_file:

    # Copy the original media part up to the separator
    combined_file.seek(0)
    remaining_size = separator_position
    while remaining_size > 0:
        chunk = combined_file.read(min(CHUNK_SIZE, remaining_size))
        remaining_size -= len(chunk)

    # Skip the separator, filename length, and filename
    combined_file.seek(separator_position + len(SEPARATOR))
    filename_length = struct.unpack("I", combined_file.read(4))[0]
    combined_file.seek(filename_length, os.SEEK_CUR)

    # Copy the injected data part
    while True:
        chunk = combined_file.read(CHUNK_SIZE)
        if not chunk:
            break
        extracted_data_file.write(chunk)

print(f"Extracted injected data to: {original_filename}")
