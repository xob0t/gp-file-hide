## Why?
Google Photos allows only media uploads.
You'd find this useful if you want to:
* Store not supported files
* Hide your media from Google, this way you can even store it encrypted

### hide_as_media.py
This script generates a media (with random color!), then appends your file's bytes to it.  
The original file's filename is also saved within, so you can rename the output if you need to.  
The output file structure is:
  1. Media
  2. Separator string
  3. Filename length
  4. Filename
  5. Target file

### undo.py
Restores the file as it was before running `hide_as_media.py`.  
Done by searching for the separator, and exctracting info in it found.
