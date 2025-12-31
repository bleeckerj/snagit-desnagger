# Snagit Desnagger

A utility to analyze and extract image data from Snagit files (`.snagx`) or unknown binary formats.

## Features

- **Analyze**: Scans files for image signatures (PNG, JPEG, etc.) and ZIP structure.
- **Extract**: Automatically extracts the main image from `.snagx` files and renames it using the original capture timestamp found in the metadata.

## Usage

### Analyze a file
```bash
python main.py <path_to_file>
```

### Batch Processing

**Mode 1: Process Non-Dated Files**
If no date arguments are provided, the tool will **only** process files that do **not** have a date in their filename (e.g., `Capture.snagx`). Files like `2025-12-30_...snagx` will be skipped.
```bash
python main.py <input_directory> <output_directory>
```

**Mode 2: Filter by Date**
If `--start` or `--end` is provided, the tool will **only** process files that **do** have a date in their filename and fall within the specified range.
```bash
python main.py <input_directory> <output_directory> --start 2025-01-01 --end 2025-12-31
```
