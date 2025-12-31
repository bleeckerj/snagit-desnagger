import sys
import os
import argparse
import re
from datetime import datetime
from src.analyzer import analyze_file
from src.extractor import extract_snagx, process_media_file, get_date_from_filename

def parse_date_arg(date_str):
    """Parses YYYY-MM-DD string to datetime object."""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        print(f"Error: Invalid date format '{date_str}'. Use YYYY-MM-DD.")
        sys.exit(1)

def process_directory(directory, output_dir, start_date=None, end_date=None, force=False):
    """
    Processes all .snagx and video files in the directory.
    If start_date or end_date is provided, filters by that range (excluding non-dated files).
    If NO date range is provided, ONLY processes non-dated files.
    """
    # Supported extensions
    extensions = ('.snagx', '.mp4', '.mov', '.avi', '.mkv')
    
    files = [f for f in os.listdir(directory) if f.lower().endswith(extensions)]
    files.sort()
    
    print(f"Found {len(files)} supported files in {directory}")
    
    processed_count = 0
    skipped_date_parse = 0
    skipped_range = 0
    skipped_dated = 0
    
    for filename in files:
        file_path = os.path.join(directory, filename)
        file_date = get_date_from_filename(filename)
        
        if start_date or end_date:
            # Date filtering mode: Only process files with dates in range
            if not file_date:
                skipped_date_parse += 1
                continue
            
            if start_date and file_date < start_date:
                skipped_range += 1
                continue
            if end_date and file_date > end_date:
                skipped_range += 1
                continue
        else:
            # No date filter mode: Only process files WITHOUT dates
            if file_date:
                skipped_dated += 1
                continue
        
        print(f"Processing {filename}...")
        
        if filename.lower().endswith('.snagx'):
            extract_snagx(file_path, output_dir, force=force)
        else:
            # Handle video/raw files
            process_media_file(file_path, output_dir, force=force)
            
        processed_count += 1
        
    print(f"\nBatch processing complete.")
    print(f"Processed: {processed_count}")
    if start_date or end_date:
        print(f"Skipped (out of date range): {skipped_range}")
        print(f"Skipped (no date in filename): {skipped_date_parse}")
    else:
        print(f"Skipped (dated files): {skipped_dated}")

def main():
    parser = argparse.ArgumentParser(description="Snagit Desnagger: Analyze and extract images from .snagx files.")
    parser.add_argument("input_path", help="Path to the .snagx file or directory to analyze/extract")
    parser.add_argument("output_dir", nargs="?", help="Directory to extract images to (optional)")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files if they already exist")
    parser.add_argument("--start", help="Start date (YYYY-MM-DD) for batch processing")
    parser.add_argument("--end", help="End date (YYYY-MM-DD) for batch processing")
    
    args = parser.parse_args()

    if not os.path.exists(args.input_path):
        print(f"Error: Path '{args.input_path}' not found.")
        sys.exit(1)

    # Parse dates if provided
    start_date = parse_date_arg(args.start) if args.start else None
    end_date = parse_date_arg(args.end) if args.end else None

    if os.path.isdir(args.input_path):
        if not args.output_dir:
            print("Error: Output directory is required when processing a directory.")
            sys.exit(1)
        process_directory(args.input_path, args.output_dir, start_date, end_date, args.force)
    else:
        # Single file mode
        if args.output_dir:
            print(f"Extracting from {args.input_path} to {args.output_dir}...")
            extract_snagx(args.input_path, args.output_dir, force=args.force)
        else:
            print(f"Analyzing {args.input_path}...")
            analyze_file(args.input_path)
            print("\nTip: Provide an output directory to extract the image.")
            print("Usage: python main.py <file_path> <output_dir> [--force]")

if __name__ == "__main__":
    main()
