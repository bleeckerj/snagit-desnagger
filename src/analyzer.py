import binascii
import struct
import zipfile
import os

def parse_png(data, start_offset):
    """
    Parses PNG chunks to find the end of the image.
    Returns the end offset if successful, None otherwise.
    """
    offset = start_offset + 8  # Skip signature
    try:
        while offset < len(data):
            if offset + 8 > len(data):
                break
            length = struct.unpack('>I', data[offset:offset+4])[0]
            chunk_type = data[offset+4:offset+8]
            
            # Move past Length (4), Type (4), Data (length), CRC (4)
            offset += 8 + length + 4
            
            if chunk_type == b'IEND':
                return offset
    except Exception:
        pass
    return None

def analyze_file(file_path):
    """
    Analyzes the given file to infer its structure and identify potential image data.
    """
    print(f"Analyzing {file_path}...")
    
    # Check if it's a valid ZIP file first
    if zipfile.is_zipfile(file_path):
        print("\n[!] The file is a valid ZIP archive.")
        try:
            with zipfile.ZipFile(file_path, 'r') as z:
                print("\n--- ZIP Contents ---")
                for info in z.infolist():
                    print(f"{info.filename} (Size: {info.file_size} bytes, Compressed: {info.compress_size} bytes)")
                
                # If it's a zip, we might want to stop here or continue deep scanning
                # For now, let's continue scanning to see if we can find embedded images 
                # that might be uncompressed or if the user wants to treat it as a blob.
        except Exception as e:
            print(f"Error reading ZIP contents: {e}")

    with open(file_path, 'rb') as f:
        data = f.read()
        print(f"File size: {len(data)} bytes")
        
        signatures = {
            b'\x89PNG\r\n\x1a\n': 'PNG',
            b'\xff\xd8\xff': 'JPEG',
            b'GIF87a': 'GIF',
            b'GIF89a': 'GIF',
            b'BM': 'BMP',
            b'II*\x00': 'TIFF (Intel)',
            b'MM\x00*': 'TIFF (Motorola)',
            b'RIFF': 'RIFF Container (Potential WEBP)',
            b'PK\x03\x04': 'ZIP Local File Header',
        }

        found_images = []

        print("\n--- Scanning for Image Signatures ---")
        for sig, format_name in signatures.items():
            start = 0
            while True:
                index = data.find(sig, start)
                if index == -1:
                    break
                
                # Filter out likely false positives for short signatures like BMP
                if format_name == 'BMP' and index + 10 < len(data):
                    # Basic BMP check: reserved fields should be 0
                    # Offset 6-9 are reserved and should be 0
                    try:
                        reserved = struct.unpack('<I', data[index+6:index+10])[0]
                        if reserved != 0:
                            start = index + 1
                            continue
                    except:
                        pass

                print(f"Found {format_name} signature at offset: {index} (0x{index:x})")
                
                image_info = {'format': format_name, 'offset': index}
                
                # Try to determine size for PNG
                if format_name == 'PNG':
                    end_offset = parse_png(data, index)
                    if end_offset:
                        size = end_offset - index
                        print(f"  -> Valid PNG detected. Size: {size} bytes. Ends at: {end_offset}")
                        image_info['size'] = size
                        image_info['end'] = end_offset

                found_images.append(image_info)
                start = index + 1
        
        if not found_images:
            print("No obvious image signatures found.")
        else:
            print(f"\nFound {len(found_images)} potential image start points.")


