# Snagx Desnaggification Algorithm

This document outlines the approach used to "desnaggify" (extract and organize) content from `.snagx` files and other media types. This is intended as a reference for porting the logic to a Node.js application.

## Core Concept
The tool processes a directory of files, identifying `.snagx` archives and raw media files. It extracts the primary content, determines the original capture date, rename the files systematically, and organizes them into year-based directories.

## File Processing Logic

### 1. File Discovery
- Scan the input directory for supported extensions: `.snagx`, `.mp4`, `.mov`, `.avi`, `.mkv`.
- Sort files alphabetically.
- (Optional) Apply date range filtering based on dates found in filenames.

### 2. Handling `.snagx` Files
A `.snagx` file is effectively a ZIP archive containing the captured image (often with annotations) and metadata.

**Algorithm:**
1.  **Validation**: Verify the file is a valid ZIP archive.
2.  **Identify Main Content**:
    - List all files within the archive.
    - Identify all files ending in `.png`.
    - **Selection Strategy**: Sort the `.png` files by size (descending). The largest PNG is assumed to be the "fused" image (screenshot + annotations).
3.  **Extract Metadata (Date)**:
    - Look for a `metadata.json` file in the archive root.
    - If found, parse JSON and look for `CaptureDate` (Format: `YYYY-MM-DD HH:MM:SS`).
    - **Fallback**: If `metadata.json` is missing or lacks a date, use the *Last Modified Time* of the selected main image file from the ZIP headers.
4.  **Destination Path Construction**:
    - Parse the date into a `YYYY` year component.
    - Create a year directory (e.g., `./output/2023/`).
    - Format a standardized filename: `YYYY-MM-DD_HH-MM-SS_{OriginalName}.png`.
        - *Sanitization*: The original filename is sanitized to remove special characters, keeping only alphanumerics, hyphens, and underscores.
5.  **Extraction**:
    - Extract the selected largest PNG to the new destination path.
6.  **Indexing**:
    - Build/Update an `index.json` file in the output root.
    - Record entry: `{ original_filename, extracted_filename, processed_at, metadata }`.

### 3. Handling Raw Media (Video/Images)
For files that are already in a standard format (e.g., `.mp4`, `.mov`), the process is simpler (Copy & Rename).

**Algorithm:**
1.  **Date Determination**:
    - **Primary**: Attempt to parse a date from the filename (Regex: `YYYY-MM-DD`).
    - **Fallback**: Use the file system `mtime` (Modification Time).
2.  **Organization**:
    - Create year directory.
    - Copy file to `YYYY-MM-DD_HH-MM-SS_{OriginalName}.{ext}`.
3.  **Indexing**:
    - Update `index.json` with the file mapping.

## Key Considerations for Node.js Implementation

- **Libraries**:
    - use `adm-zip` or `yauzl` for handling ZIP archives (`.snagx`).
    - use `fs` (or `fs/promises`) for file operations.
    - use `path` for robust path construction.
- **Async/Stream**: Large video files should be processed using streams to prevent memory issues.
- **Error Handling**: Invalid ZIPs or missing metadata keys should fail gracefully (fallback to mtime).
