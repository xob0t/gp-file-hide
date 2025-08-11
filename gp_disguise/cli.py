import argparse
import sys
from pathlib import Path

from gp_disguise.hide import MediaHider
from gp_disguise.extract import MediaExtractor
from gp_disguise.config import Config


def hide_command(args: argparse.Namespace) -> int:
    """Handle the hide command."""
    config = Config(
        is_video=(args.type == "video"),
        separator=args.separator.encode("utf-8"),
    )

    hider = MediaHider(config)

    # Process input files
    input_files = []
    for pattern in args.files:
        pattern_path = Path(pattern)
        if pattern_path.exists():
            paths = [pattern_path]
        else:
            paths = list(Path().glob(pattern))
        if not paths:
            # If glob doesn't match, treat as literal path
            path = Path(pattern)
            if path.exists():
                input_files.append(path)
            else:
                print(f"Warning: '{pattern}' not found, skipping", file=sys.stderr)
        else:
            input_files.extend(paths)

    if not input_files:
        print("Error: No input files found", file=sys.stderr)
        return 1

    success_count = 0
    for input_file in input_files:
        output_file = Path(args.output) if args.output else None

        # For batch processing with explicit output, append filename
        if output_file and len(input_files) > 1:
            suffix = ".bmp" if args.type == "image" else ".mp4"
            output_file = output_file.parent / f"{output_file.stem}_{input_file.name}{suffix}"

        try:
            result = hider.hide_file(input_file, output_file)
            print(f"✓ Created: {result}")
            success_count += 1
        except Exception as e:
            print(f"✗ Failed to process '{input_file}': {e}", file=sys.stderr)

    print(f"\nProcessed {success_count}/{len(input_files)} files successfully")
    return 0 if success_count == len(input_files) else 1


def extract_command(args: argparse.Namespace) -> int:
    """Handle the extract command."""
    config = Config(
        separator=args.separator.encode("utf-8"),
        restored_suffix=args.suffix,
    )

    extractor = MediaExtractor(config)

    # Process input files
    input_files = []
    for pattern in args.files:
        pattern_path = Path(pattern)
        if pattern_path.exists():
            paths = [pattern_path]
        else:
            paths = list(Path().glob(pattern))
        if not paths:
            # If glob doesn't match, treat as literal path
            path = Path(pattern)
            if path.exists():
                input_files.append(path)
            else:
                print(f"Warning: '{pattern}' not found, skipping", file=sys.stderr)
        else:
            input_files.extend(paths)

    if not input_files:
        print("Error: No input files found", file=sys.stderr)
        return 1

    success_count = 0
    for media_file in input_files:
        output_dir = Path(args.output) if args.output else None

        try:
            result = extractor.extract_file(media_file, output_dir)
            print(f"✓ Extracted: {result}")
            success_count += 1
        except Exception as e:
            print(f"✗ Failed to extract from '{media_file}': {e}", file=sys.stderr)

    print(f"\nExtracted {success_count}/{len(input_files)} files successfully")
    return 0 if success_count == len(input_files) else 1


def main() -> int:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        prog="gp-disguise",
        description="Hide and extract data in media files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Hide a single file as an image
  gpd hide secret.txt
  
  # Hide multiple files as videos
  gpd hide -t video *.pdf
  
  # Extract hidden data from media files
  gpd extract *.bmp *.mp4
  
  # Batch process with custom output directory
  gpd hide -o output/ *.txt
  gpd extract -o extracted/ media/*.bmp
""",
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Hide subcommand
    hide_parser = subparsers.add_parser("hide", help="Hide data in media files")
    hide_parser.add_argument(
        "files",
        nargs="+",
        help="Files to hide (supports wildcards)",
    )
    hide_parser.add_argument(
        "-t",
        "--type",
        choices=["image", "video"],
        default="image",
        help="Media type to create (default: image)",
    )
    hide_parser.add_argument(
        "-o",
        "--output",
        help="Output file or directory (default: auto-generated)",
    )
    hide_parser.add_argument(
        "-s",
        "--separator",
        default="FILE_DATA_BEGIN",
        help="Separator string (default: FILE_DATA_BEGIN)",
    )

    # Extract subcommand
    extract_parser = subparsers.add_parser("extract", help="Extract hidden data from media files")
    extract_parser.add_argument(
        "files",
        nargs="+",
        help="Media files to extract from (supports wildcards)",
    )
    extract_parser.add_argument(
        "-o",
        "--output",
        help="Output directory (default: current directory)",
    )
    extract_parser.add_argument(
        "-s",
        "--separator",
        default="FILE_DATA_BEGIN",
        help="Separator string (default: FILE_DATA_BEGIN)",
    )
    extract_parser.add_argument(
        "--suffix",
        default=".restored",
        help="Suffix for restored files (default: .restored)",
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    if args.command == "hide":
        return hide_command(args)
    if args.command == "extract":
        return extract_command(args)

    return 0


if __name__ == "__main__":
    sys.exit(main())
