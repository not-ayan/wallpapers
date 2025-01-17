import os
from PIL import Image

def convert_jpg_to_png(input_folder, output_folder):
    """
    Convert all .jpg or .jpeg images in the input folder to .png format
    and save them in the output folder.

    :param input_folder: Path to the folder containing .jpg/.jpeg images.
    :param output_folder: Path to the folder where .png images will be saved.
    """
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Iterate through all files in the input folder
    for file_name in os.listdir(input_folder):
        file_path = os.path.join(input_folder, file_name)

        # Process only files with .jpg or .jpeg extensions
        if os.path.isfile(file_path) and file_name.lower().endswith(('.jpg', '.jpeg')):
            try:
                # Open the image
                with Image.open(file_path) as img:
                    # Convert to PNG format
                    base_name = os.path.splitext(file_name)[0]
                    output_path = os.path.join(output_folder, f"{base_name}.png")

                    # Save the image as PNG
                    img.save(output_path, "PNG")
                    print(f"Converted {file_name} to {output_path}")

            except Exception as e:
                print(f"Error converting {file_name}: {e}")

# Example usage
input_dir = "./"  # Replace with your input folder path
output_dir = "./"  # Replace with your output folder path
convert_jpg_to_png(input_dir, output_dir)
