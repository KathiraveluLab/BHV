from PIL import Image
import os

def get_image_metadata(file_path):
    try:
        with Image.open(file_path) as img:
            return {
                'width': img.width,
                'height': img.height,
                'format': img.format,
                'mode': img.mode
            }
    except Exception as e:
        print(f"Error extracting metadata: {e}")
        return None

def get_file_size(file_path):
    try:
        return os.path.getsize(file_path)
    except OSError:
        return 0