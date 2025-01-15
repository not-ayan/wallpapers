import os
from concurrent.futures import ThreadPoolExecutor
from PIL import Image

Image.MAX_IMAGE_PIXELS = None  # Disable the decompression bomb warning

WEBP_MAX_DIMENSION = 16383  # WebP maximum dimension for width or height

def resize_if_needed(img):
    """Resize the image if it exceeds WebP's maximum dimension."""
    if img.width > WEBP_MAX_DIMENSION or img.height > WEBP_MAX_DIMENSION:
        scaling_factor = WEBP_MAX_DIMENSION / max(img.width, img.height)
        new_width = int(img.width * scaling_factor)
        new_height = int(img.height * scaling_factor)
        print(f"Resizing image from {img.size} to ({new_width}, {new_height})")
        return img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    return img

def process_image(file_path, output_folder, quality):
    """Process and optimize a single PNG image."""
    try:
        optimized_path = os.path.join(output_folder, os.path.splitext(os.path.basename(file_path))[0] + ".webp")

        # Skip if the optimized image already exists
        if os.path.exists(optimized_path):
            print(f"Skipping already optimized: {optimized_path}")
            return

        with Image.open(file_path) as img:
            # Convert to RGB (to handle PNGs with transparency)
            img = img.convert("RGB")

            # Resize if dimensions exceed WebP limits
            img = resize_if_needed(img)

            # Check if the image exceeds WebP limits (e.g., dimensions or file size)
            while True:
                try:
                    # Try saving the image in WebP format
                    img.save(optimized_path, "WEBP", optimize=True, quality=quality)
                    print(f"Optimized and saved: {optimized_path}")
                    break
                except OSError:
                    # Reduce quality further if compression fails
                    quality = max(quality - 10, 10)  # Ensure quality does not go below 10
                    print(f"Retrying {file_path} with reduced quality: {quality}")

    except Exception as e:
        print(f"Skipping {file_path}: {e}")

def optimize_images(input_folder, output_folder, quality=40, max_workers=8):
    """
    Optimize PNG images for web viewing by converting them to WebP format and save them in the specified cache folder.

    :param input_folder: Path to the folder containing images to process
    :param output_folder: Path to the cache folder where optimized images will be saved
    :param quality: Quality level for the optimized images (default: 50)
    :param max_workers: Maximum number of threads to use (default: 8)
    """
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    tasks = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for file in os.listdir(input_folder):
            file_path = os.path.join(input_folder, file)
            if os.path.isfile(file_path) and file.lower().endswith(".png"):
                tasks.append(executor.submit(process_image, file_path, output_folder, quality))

        # Wait for all tasks to complete
        for task in tasks:
            task.result()

# Example usage
input_dir = "./"  # Specify the main folder
cache_dir = os.path.join(input_dir, "cache/webp")
optimize_images(input_dir, cache_dir)
