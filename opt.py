import os
from PIL import Image
Image.MAX_IMAGE_PIXELS = None 

def optimize_images(input_folder, output_folder, quality=25):
    """
    Optimize images for web viewing and save them in the specified cache folder.

    :param input_folder: Path to the folder containing images to process
    :param output_folder: Path to the cache folder where optimized images will be saved
    :param quality: Quality level for the optimized images (default: 85)
    """
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    for root, dirs, files in os.walk(input_folder):
        # Skip the "cache" folder
        if os.path.basename(root) == "cache":
            continue

        for file in files:
            file_path = os.path.join(root, file)
            try:
                with Image.open(file_path) as img:
                    # Convert to RGB (to handle PNGs with transparency)
                    img = img.convert("RGB")

                    # Define the output path in the cache folder
                    relative_path = os.path.relpath(root, input_folder)
                    output_dir = os.path.join(output_folder, relative_path)
                    os.makedirs(output_dir, exist_ok=True)

                    optimized_path = os.path.join(output_dir, file)

                    # Save optimized image
                    img.save(optimized_path, "JPEG", optimize=True, quality=quality)

                    print(f"Optimized and saved: {optimized_path}")

            except Exception as e:
                print(f"Skipping {file}: {e}")

# Example usage
input_dir = "./"
cache_dir = os.path.join(input_dir, "cache/png")
optimize_images(input_dir, cache_dir)
