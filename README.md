# 🔓 Snagit Desnagger

**Liberating creative history from the proprietary `.snagx` archives.**

## Intersection: Computation & Creativity

In my work spanning engineering and creative foresight, I often encounter the friction between **capturing ideas** and **archiving them**. We use tools to seize moments of inspiration, but those moments often get locked away in proprietary wrappers, destined for digital obsolescence.

I built **Snagit Desnagger** because I value the durability of our digital artifacts. This isn't just a conversion script—it is a computational intervention to reclaim ownership of visual data. It treats file formats not as black boxes, but as puzzles to be solved, ensuring that the "future history" of our creative output remains accessible, portable, and open.

## What This Tool Does

This utility applies forensic file analysis to opaque `.snagx` files (and other binary formats) to locate, extract, and organize the core visual data within.

- **🕵️‍♀️ Deep Analysis**: It doesn't just read file extensions; it scans binary signatures (magic numbers) to identify embedded PNGs, JPEGs, and ZIP structures within raw data.
- **📦 Intelligent Extraction**: It surgically removes the "fused" image (your screenshot + annotations) from the archive.
- **⏳ Temporal Reconstruction**: It hunts for metadata timestamps to reconstruct the original timeline of your work, renaming and organizing files chronologically (e.g., `2025/2025-01-01_Idea.png`) so your archive tells a story.

## Usage

### 1. Analyze a File
Get a nuts-and-bolts view of what's inside a file. Useful for debugging or digital archeology.
```bash
python main.py <path_to_file>
```

### 2. Batch Extraction & Organization
The tool supports sophisticated batch processing strategies to groom your media library.

**Mode A: The "clean sweep" (Non-Dated Files)**
Ideal for processing a messy "Inbox" folder. This mode targets files that have not yet been organized (i.e., they lack a date stamp), extracts their content, and moves them to a structured output.
```bash
python main.py <input_directory> <output_directory>
```

**Mode B: Targeted Archival (Date Range)**
For managing specific epochs of work. This mode filters files that *already* have dates, processing only those within a specific window.
```bash
python main.py <input_directory> <output_directory> --start 2025-01-01 --end 2025-12-31
```

## Tech Stack
*   **Python 3**: Core logic & file I/O.
*   **Stream Processing**: Efficient handling of binary streams to locate valid image chunks.
*   **Standard Lib Only**: Designed to be lightweight and dependency-free where possible.

---
*Built by [Julian Bleecker](https://github.com/bleeckerj) — Engineer, Designer, Futurist.*
