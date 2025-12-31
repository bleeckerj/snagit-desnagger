import os
import zipfile
import json
import shutil
import re
from datetime import datetime

def get_date_from_filename(filename):
    """
    Extracts date from filename assuming format YYYY-MM-DD_HH-MM-SS.snagx
    Returns datetime object or None.
    """
    # Match YYYY-MM-DD pattern at start of filename
    match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
    if match:
        try:
            return datetime.strptime(match.group(1), "%Y-%m-%d")
        except ValueError:
            pass
    return None

def update_index(output_dir, metadata, original_filename, new_filename):
    """
    Updates (or creates) a JSON index file in the output directory with the new file's metadata.
    """
    index_path = os.path.join(output_dir, 'index.json')
    index_data = []

    if os.path.exists(index_path):
        try:
            with open(index_path, 'r') as f:
                index_data = json.load(f)
        except Exception as e:
            print(f"Warning: Could not read existing index.json: {e}")

    # Prepare new entry
    entry = {
        'original_filename': original_filename,
        'extracted_filename': new_filename,
        'processed_at': datetime.now().isoformat(),
        'metadata': metadata
    }

    # Check if entry exists and update it, otherwise append
    updated = False
    for i, item in enumerate(index_data):
        if item.get('extracted_filename') == new_filename:
            index_data[i] = entry
            updated = True
            break
    
    if not updated:
        index_data.append(entry)

    try:
        with open(index_path, 'w') as f:
            json.dump(index_data, f, indent=2)
        # print(f"Updated index at {index_path}") # Reduce verbosity
    except Exception as e:
        print(f"Error writing index.json: {e}")

def construct_output_filename(date_str, original_filename, extension):
    """
    Constructs the new filename.
    If the original filename is just a date (e.g. 2025-01-01...), returns {date_str}{extension}.
    If the original filename has text (e.g. MyScreenshot), returns {date_str}_{MyScreenshot}{extension}.
    """
    base_name = os.path.splitext(original_filename)[0]
    
    # Check if the original filename starts with a date pattern
    if re.match(r'^\d{4}-\d{2}-\d{2}', base_name):
        return f"{date_str}{extension}"
    else:
        # Sanitize the original name to be safe for filenames
        # Keep alphanumeric, dashes, underscores, spaces
        safe_name = "".join([c for c in base_name if c.isalnum() or c in (' ', '-', '_')]).strip()
        safe_name = safe_name.replace(' ', '_')
        
        if not safe_name:
            return f"{date_str}{extension}"
            
        return f"{date_str}_{safe_name}{extension}"

def process_media_file(file_path, output_dir, force=False):
    """
    Processes a raw media file (video/image) that is NOT a .snagx archive.
    Copies it to the output directory, organized by year.
    """
    filename = os.path.basename(file_path)
    
    # Try to get date from filename
    dt = get_date_from_filename(filename)
    
    # Fallback to file modification time if no date in filename
    if not dt:
        try:
            mtime = os.path.getmtime(file_path)
            dt = datetime.fromtimestamp(mtime)
            print(f"Using file modification time for {filename}: {dt}")
        except Exception as e:
            print(f"Error getting file time for {filename}: {e}")
            dt = datetime.now() # Last resort

    date_str = dt.strftime("%Y-%m-%d_%H-%M-%S")
    
    # Determine year folder
    year_folder = str(dt.year)
    year_dir = os.path.join(output_dir, year_folder)
    if not os.path.exists(year_dir):
        os.makedirs(year_dir)

    # Preserve original extension
    _, ext = os.path.splitext(filename)
    
    # Construct new filename preserving original text if present
    new_filename = construct_output_filename(date_str, filename, ext)
    
    output_path = os.path.join(year_dir, new_filename)
    
    # Check for duplicates
    if os.path.exists(output_path):
        if not force:
            # print(f"Skipping {os.path.join(year_folder, new_filename)}: File already exists.")
            return
        else:
            print(f"Overwriting {os.path.join(year_folder, new_filename)}...")

    # Copy the file
    print(f"Copying to: {output_path}")
    try:
        shutil.copy2(file_path, output_path)
        
        # Update index with basic metadata
        metadata = {
            'source': 'raw_file',
            'original_path': file_path,
            'size': os.path.getsize(file_path),
            'inferred_date': date_str
        }
        relative_path = os.path.join(year_folder, new_filename)
        update_index(output_dir, metadata, filename, relative_path)
        
    except Exception as e:
        print(f"Error copying file {filename}: {e}")

def extract_snagx(file_path, output_dir, force=False):
    """
    Extracts the main image from a .snagx file (ZIP archive) and renames it based on metadata.
    """
    # Check for empty files (Dropbox placeholders)
    try:
        if os.path.getsize(file_path) == 0:
            print(f"Skipping {os.path.basename(file_path)}: File is empty (0 bytes). Likely an offline Dropbox file.")
            return
    except OSError:
        pass

    if not zipfile.is_zipfile(file_path):
        print(f"Error: {file_path} is not a valid ZIP/snagx file.")
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with zipfile.ZipFile(file_path, 'r') as z:
        # List all files
        files = z.namelist()
        
        # Find the largest PNG file (likely the main image)
        png_files = [f for f in files if f.lower().endswith('.png')]
        if not png_files:
            print("No PNG images found in the archive.")
            return

        # Sort by size, largest first
        png_files.sort(key=lambda x: z.getinfo(x).file_size, reverse=True)
        main_image_name = png_files[0]
        print(f"Identified main image: {main_image_name}")

        # Try to find metadata
        metadata = {}
        date_str = None
        
        # Check metadata.json first
        if 'metadata.json' in files:
            try:
                with z.open('metadata.json') as f:
                    metadata = json.load(f)
                    # Look for common date fields
                    if 'CaptureDate' in metadata:
                        # Format: "2025-12-30 22:15:54"
                        raw_date = metadata['CaptureDate']
                        try:
                            # Parse and reformat to be filename safe
                            dt = datetime.strptime(raw_date, "%Y-%m-%d %H:%M:%S")
                            date_str = dt.strftime("%Y-%m-%d_%H-%M-%S")
                            print(f"Using CaptureDate from metadata: {date_str}")
                        except ValueError:
                            print(f"Warning: Could not parse CaptureDate '{raw_date}'.")
                            date_str = raw_date.replace(' ', '_').replace(':', '-')
                    elif 'date' in metadata:
                        date_str = metadata['date']
                    elif 'created' in metadata:
                        date_str = metadata['created']
            except Exception as e:
                print(f"Warning: Could not read metadata.json: {e}")

        # If no date in metadata.json, try the file modification time from the zip info
        if not date_str:
            # Use the modification time of the main image in the zip
            info = z.getinfo(main_image_name)
            # date_time is a tuple (year, month, day, hour, min, sec)
            dt = datetime(*info.date_time)
            date_str = dt.strftime("%Y-%m-%d_%H-%M-%S")
            print(f"Using zip timestamp: {date_str}")
        else:
             # Clean up date string if necessary (implementation depends on format)
             # For now, assume it might need parsing. 
             # If it's ISO format, we might want to standardize it.
             pass

        # Construct new filename preserving original text if present
        new_filename = construct_output_filename(date_str, os.path.basename(file_path), ".png")
        
        # Determine year folder
        year_folder = date_str[:4]
        if not year_folder.isdigit() or len(year_folder) != 4:
             year_folder = "misc"
             
        year_dir = os.path.join(output_dir, year_folder)
        if not os.path.exists(year_dir):
            os.makedirs(year_dir)

        output_path = os.path.join(year_dir, new_filename)
        
        # Check for duplicates
        if os.path.exists(output_path):
            if not force:
                print(f"Skipping {os.path.join(year_folder, new_filename)}: File already exists (use --force to overwrite).")
                return
            else:
                print(f"Overwriting {os.path.join(year_folder, new_filename)}...")

        # Extract the file
        print(f"Extracting to: {output_path}")
        with z.open(main_image_name) as source, open(output_path, 'wb') as target:
            shutil.copyfileobj(source, target)
            
        print("Extraction complete.")
        
        # Update the index
        relative_path = os.path.join(year_folder, new_filename)
        update_index(output_dir, metadata, os.path.basename(file_path), relative_path)


