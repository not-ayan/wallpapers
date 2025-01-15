import os
import json
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
import torch
from torchvision import models, transforms
import webcolors
Image.MAX_IMAGE_PIXELS = None
# Load ImageNet labels
LABELS_URL = "https://raw.githubusercontent.com/anishathalye/imagenet-simple-labels/master/imagenet-simple-labels.json"
LABELS_PATH = "imagenet_labels.json"
if not os.path.exists(LABELS_PATH):
    import urllib.request
    urllib.request.urlretrieve(LABELS_URL, LABELS_PATH)

with open(LABELS_PATH) as f:
    LABELS = json.load(f)

# Preprocessing transformation
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

# Load pre-trained ResNet model
model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
model.eval()

import math

def closest_color_name(rgb):
    """Convert an RGB color to its closest CSS3 color name."""
    css3_names_to_rgb = {
        "aliceblue": (240, 248, 255),
        "antiquewhite": (250, 235, 215),
        "aqua": (0, 255, 255),
        "aquamarine": (127, 255, 212),
        "azure": (240, 255, 255),
        "beige": (245, 245, 220),
        "bisque": (255, 228, 196),
        "black": (0, 0, 0),
        "blanchedalmond": (255, 235, 205),
        "blue": (0, 0, 255),
        "blueviolet": (138, 43, 226),
        "brown": (165, 42, 42),
        "burlywood": (222, 184, 135),
        "cadetblue": (95, 158, 160),
        "chartreuse": (127, 255, 0),
        "chocolate": (210, 105, 30),
        "coral": (255, 127, 80),
        "cornflowerblue": (100, 149, 237),
        "cornsilk": (255, 248, 220),
        "crimson": (220, 20, 60),
        "cyan": (0, 255, 255),
        "darkblue": (0, 0, 139),
        "darkcyan": (0, 139, 139),
        "darkgoldenrod": (184, 134, 11),
        "darkgray": (169, 169, 169),
        "darkgreen": (0, 100, 0),
        "darkkhaki": (189, 183, 107),
        "darkmagenta": (139, 0, 139),
        "darkolivegreen": (85, 107, 47),
        "darkorange": (255, 140, 0),
        "darkorchid": (153, 50, 204),
        "darkred": (139, 0, 0),
        "darksalmon": (233, 150, 122),
        "darkseagreen": (143, 188, 143),
        "darkslateblue": (72, 61, 139),
        "darkslategray": (47, 79, 79),
        "darkturquoise": (0, 206, 209),
        "darkviolet": (148, 0, 211),
        "deeppink": (255, 20, 147),
        "deepskyblue": (0, 191, 255),
        "dimgray": (105, 105, 105),
        "dodgerblue": (30, 144, 255),
        "firebrick": (178, 34, 34),
        "floralwhite": (255, 250, 240),
        "forestgreen": (34, 139, 34),
        "fuchsia": (255, 0, 255),
        "gainsboro": (220, 220, 220),
        "ghostwhite": (248, 248, 255),
        "gold": (255, 215, 0),
        "goldenrod": (218, 165, 32),
        "gray": (128, 128, 128),
        "green": (0, 128, 0),
        "greenyellow": (173, 255, 47),
        "honeydew": (240, 255, 240),
        "hotpink": (255, 105, 180),
        "indianred": (205, 92, 92),
        "indigo": (75, 0, 130),
        "ivory": (255, 255, 240),
        "khaki": (240, 230, 140),
        "lavender": (230, 230, 250),
        "lavenderblush": (255, 240, 245),
        "lawngreen": (124, 252, 0),
        "lemonchiffon": (255, 250, 205),
        "lightblue": (173, 216, 230),
        "lightcoral": (240, 128, 128),
        "lightcyan": (224, 255, 255),
        "lightgoldenrodyellow": (250, 250, 210),
        "lightgray": (211, 211, 211),
        "lightgreen": (144, 238, 144),
        "lightpink": (255, 182, 193),
        "lightsalmon": (255, 160, 122),
        "lightseagreen": (32, 178, 170),
        "lightskyblue": (135, 206, 250),
        "lightslategray": (119, 136, 153),
        "lightsteelblue": (176, 196, 222),
        "lightyellow": (255, 255, 224),
        "lime": (0, 255, 0),
        "limegreen": (50, 205, 50),
        "linen": (250, 240, 230),
        "magenta": (255, 0, 255),
        "maroon": (128, 0, 0),
        "mediumaquamarine": (102, 205, 170),
        "mediumblue": (0, 0, 205),
        "mediumorchid": (186, 85, 211),
        "mediumpurple": (147, 112, 219),
    }

    # Find the closest color by Euclidean distance in RGB space
    min_distance = float("inf")
    closest_name = None
    for name, color_rgb in css3_names_to_rgb.items():
        distance = math.sqrt(
            (color_rgb[0] - rgb[0])**2 +
            (color_rgb[1] - rgb[1])**2 +
            (color_rgb[2] - rgb[2])**2
        )
        if distance < min_distance:
            min_distance = distance
            closest_name = name

    return closest_name


# Analyze a single image
def analyze_image(file_path, tags_json, tags_txt, colors_txt):
    try:
        with Image.open(file_path) as img:
            # Get resolution
            resolution = f"{img.width}x{img.height}"
            platform = "Mobile" if img.height > img.width else "Desktop"

            file_name = os.path.basename(file_path)
            # Skip if the image is already in tags.json
            if file_name in tags_json:
                print(f"Skipping {file_path}: Already processed.")
                return

            # Process the image for tags
            rgb_img = img.convert("RGB")
            tensor = transform(rgb_img).unsqueeze(0)
            with torch.no_grad():
                outputs = model(tensor)
                _, indices = torch.topk(outputs, 5)
                tags = [LABELS[idx] for idx in indices[0]]

            # Process colors
            colors = [closest_color_name(rgb_img.getpixel((x, y))) for x in range(0, rgb_img.width, 50) for y in range(0, rgb_img.height, 50)]
            colors = list(set(colors))  # Deduplicate

            # Append tags to tags.json
            tags_json[file_name] = {
                "tags": tags,
                "colors": colors,
                "resolution": resolution,
                "platform": platform
            }
            with open(tags_txt, "a") as tf:
                tf.write(f"{file_name}: {', '.join(tags)}\n")

            # Append colors to colors.txt
            with open(colors_txt, "a") as cf:
                cf.write("\n".join(colors) + "\n")

            print(f"Processed {file_path}")

    except Exception as e:
        print(f"Error processing {file_path}: {e}")

# Main function
def analyze_images(input_folder, tags_file="tags.json", tags_txt="tags.txt", colors_txt="colors.txt", max_workers=8):
    # Load existing tags.json if present
    tags_json = {}
    if os.path.exists(tags_file):
        with open(tags_file) as tf:
            tags_json = json.load(tf)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for root, _, files in os.walk(input_folder):
            for file in files:
                if file.lower().endswith(".png"):
                    file_path = os.path.join(root, file)
                    futures.append(executor.submit(analyze_image, file_path, tags_json, tags_txt, colors_txt))

        # Wait for all tasks to complete
        for future in futures:
            future.result()

    # Save updated tags.json
    with open(tags_file, "w") as tf:
        json.dump(tags_json, tf, indent=4)

# Example usage
input_dir = "./"
analyze_images(input_dir)
