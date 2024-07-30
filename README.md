## Google Photos allows only media uploads, but what if you want to upload other filetypes or hide your media from google?

### hide_as_media.py
This script generates a media (with random color!), then appends your file's bytes to it.
The original file's filename is also saved.
The output file structure is:
  1. Media
  2. Separator string
  3. Filename length
  4. Filename
  5. Target file

### undo.py
Restores the file as it was before running `hide_as_media.py`.  
Done by searching for the separator, and exctracting info in it found.
