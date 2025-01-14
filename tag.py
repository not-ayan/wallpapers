import os
import json
from PIL import Image

def analyze_images_in_folder(folder_path, output_file):
    data = []

    for root, dirs, files in os.walk(folder_path):
        # Skip the "cache" folder
        if "cache" in root.split(os.sep):
            continue

        for file in files:
            file_path = os.path.join(root, file)
            
            try:
                with Image.open(file_path) as img:
                    width, height = img.size
                    resolution = f"{width}x{height}"
                    tag = "Mobile" if height > width else "Desktop"

                    data.append({
                        "name": file,
                        "resolution": resolution,
                        "tag": tag
                    })
            except Exception as e:
                # Ignore files that cannot be opened as images
                print(f"Skipping {file}: {e}")

    # Write the data to a JSON file
    with open(output_file, 'w') as json_file:
        json.dump(data, json_file, indent=4)

    print(f"Analysis complete. Results saved to {output_file}")

# Example usage
folder_to_analyze = "./"
output_json_file = "image_analysis.json"
analyze_images_in_folder(folder_to_analyze, output_json_file)