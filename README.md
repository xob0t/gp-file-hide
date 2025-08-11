# gp_disguise

Hide and extract data in media files (BMP images and MP4 videos).  
Made to be compatible with Google Photos.

> **⚠️ Security Notice**  
> This tool **does not encrypt** your files. It only hides them by appending their raw data to a media file.  
> Anyone with access to the media file and knowledge of the format could recover the data without your password.  
> If you need confidentiality, encrypt your files first (e.g., with `gpg` or `openssl`) before using `gp_disguise`.

## Installation

```bash
pip install https://github.com/xob0t/gp_disguise/archive/refs/heads/main.zip
```

## Requirements

- Python 3.9+
- ffmpeg (for video generation)

## Usage

### Hide data in media files

```bash
# Hide a single file as an image
gpd hide secret.txt

# Hide multiple files as videos
gpd hide -t video *.pdf

# Specify output directory
gpd hide -o output/ document.docx

# Batch process with wildcards
gpd hide *.txt *.log
```

### Extract hidden data

```bash
# Extract from a single file
gpd extract image.bmp

# Extract from multiple files
gpd extract *.bmp *.mp4

# Extract to specific directory
gpd extract -o extracted/ media/*.bmp

# Custom separator (must match what was used to hide)
gpd extract -s "CUSTOM_SEP" file.bmp
```

### Batch Processing Examples

```bash
# Hide all documents in a folder
gpd hide documents/*.pdf documents/*.docx

# Hide with mixed patterns
gpd hide *.txt data/*.csv logs/**/*.log

# Process entire directory as videos
gpd hide -t video -o hidden/ sensitive/*

# Extract all media files from multiple directories
gpd extract input/*.bmp downloads/*.mp4 received/*.bmp

# Extract everything to organized output
gpd extract -o recovered/ **/*.bmp **/*.mp4
```

## Options

### Hide command

- `-t, --type`: Media type (`image` or `video`, default: `image`)
- `-o, --output`: Output file or directory
- `-s, --separator`: Custom separator string (default: `FILE_DATA_BEGIN`)

### Extract command

- `-o, --output`: Output directory for extracted files
- `-s, --separator`: Separator string (must match hide operation)
- `--suffix`: Suffix for restored files (default: `.restored`)

## Programmatic Usage

```python
from gp_disguise import MediaHider, MediaExtractor, Config
from pathlib import Path

# Hide a file
config = Config(is_video=False)  # False for image, True for video
hider = MediaHider(config)
output = hider.hide_file(Path("secret.txt"))

# Extract hidden data
extractor = MediaExtractor(config)
extracted = extractor.extract_file(output)
```

## How it works

### Hiding Process

The tool generates a media file with a random color background, then appends your file's data to it. The original filename is preserved within the hidden data, so you can rename the output file if needed.

**File structure after hiding:**

1. Media file (BMP/MP4)
2. Separator string
3. Filename length (4 bytes)
4. Original filename
5. Target file data

### Extraction Process

Searches for the separator string in the media file and extracts the hidden data if found, restoring the original filename.

## ⚠️ Important Warning

**Data will be lost if:**

- You upload the file in "Storage saver" quality
- You convert or re-encode the media file
- You edit the file in image/video editing software
- The platform strips metadata or trailing data

The hidden data is appended to the file and will be removed by any process that re-encodes or optimizes the media file. Always keep backups of important data!
