import os
import json
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
import torch
from torchvision import models, transforms
import hashlib

Image.MAX_IMAGE_PIXELS = None  # Allow processing large images

# Define main tags for categorization
MAIN_TAGS = {
    "Art": ["Comic book", "Dust jacket", "T-shirt", "Painting", "Quilt", "Velvet", "Tray"],
    "Technology": ["Computer mouse", "Keyboard", "Laptop", "Digital clock", "Spotlight", "Modem", "Projector"],
    "Vehicles": ["Airship", "Sports car", "Taxicab", "Scooter", "Aircraft carrier", "Race car", "Ocean liner"],
    "Nature": ["Coral reef", "Jellyfish", "Lakeshore", "Alp", "Volcano", "Seashore", "Sunflower"],
    "Outdoor Structures": ["Stupa", "Dome", "Patio", "Lighthouse", "Thatched roof"],
    "Fashion": ["Sunglasses", "Sandal", "Swimsuit", "Buckle", "Sarong", "Scarf"],
    "Home Decor": ["Lampshade", "Vase", "Curtain", "Pillow", "Furniture", "Clock"],
    "Sports & Recreation": ["Ski", "Race car", "Soccer ball", "Bobsleigh", "Paddle", "Tent"],
    "Marine": ["Scuba diver", "Snorkel", "Submarine", "Shipwreck", "Motorboat"],
    "Fantasy/Imagination": ["Airship", "Pirate ship", "Maze", "Comic book", "Spotlight"],
    "Wildlife": ["Tiger shark", "Ant", "Toucan", "Spider", "Beaver", "Langur"],
    "Infrastructure": ["Traffic light", "Crane (machine)", "Parking meter", "Bridge", "Traffic sign"],
    "Household Items": ["Envelopes", "Ring binder", "Hook", "Scissors", "Screwdriver"],
    "Space/Science": ["Telescope", "Rocket", "Solar system", "Barometer", "Weighing scale"],
    "Anime": ["Anime character", "Manga", "Anime scene", "Cosplay"],
    "Miscellaneous": []
}

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

# CSS3 colors mapped to broader categories
COLOR_CATEGORIES = {
    "red": ["red", "darkred", "indianred", "crimson", "firebrick"],
    "blue": ["blue", "darkblue", "deepskyblue", "dodgerblue", "mediumblue"],
    "green": ["green", "darkgreen", "limegreen", "forestgreen"],
    "yellow": ["yellow", "gold", "khaki", "lightgoldenrodyellow"],
    "orange": ["orange", "darkorange", "coral", "chocolate"],
    "purple": ["purple", "indigo", "darkmagenta", "orchid", "mediumpurple"],
    "pink": ["pink", "deeppink", "hotpink", "lightpink"],
    "gray": ["gray", "darkgray", "dimgray", "lightgray"],
    "white": ["white", "ivory", "snow", "floralwhite"],
    "black": ["black"],
    "brown": ["brown", "saddlebrown", "peru", "chocolate"],
    "cyan": ["cyan", "aqua", "darkcyan"],
    "magenta": ["magenta", "fuchsia"],
}

CSS3_COLORS_TO_RGB = {
    "red": (255, 0, 0),
    "darkred": (139, 0, 0),
    "indianred": (205, 92, 92),
    "crimson": (220, 20, 60),
    "firebrick": (178, 34, 34),
    "blue": (0, 0, 255),
    "darkblue": (0, 0, 139),
    "deepskyblue": (0, 191, 255),
    "dodgerblue": (30, 144, 255),
    "mediumblue": (0, 0, 205),
    "green": (0, 128, 0),
    "darkgreen": (0, 100, 0),
    "limegreen": (50, 205, 50),
    "forestgreen": (34, 139, 34),
    "yellow": (255, 255, 0),
    "gold": (255, 215, 0),
    "khaki": (240, 230, 140),
    "lightgoldenrodyellow": (250, 250, 210),
    "orange": (255, 165, 0),
    "darkorange": (255, 140, 0),
    "coral": (255, 127, 80),
    "chocolate": (210, 105, 30),
    "purple": (128, 0, 128),
    "indigo": (75, 0, 130),
    "darkmagenta": (139, 0, 139),
    "orchid": (218, 112, 214),
    "mediumpurple": (147, 112, 219),
    "pink": (255, 192, 203),
    "deeppink": (255, 20, 147),
    "hotpink": (255, 105, 180),
    "lightpink": (255, 182, 193),
    "gray": (128, 128, 128),
    "darkgray": (169, 169, 169),
    "dimgray": (105, 105, 105),
    "lightgray": (211, 211, 211),
    "white": (255, 255, 255),
    "ivory": (255, 255, 240),
    "snow": (255, 250, 250),
    "floralwhite": (255, 250, 240),
    "black": (0, 0, 0),
    "brown": (165, 42, 42),
    "saddlebrown": (139, 69, 19),
    "peru": (205, 133, 63),
    "chocolate": (210, 105, 30),
    "cyan": (0, 255, 255),
    "aqua": (0, 255, 255),
    "darkcyan": (0, 139, 139),
    "magenta": (255, 0, 255),
    "fuchsia": (255, 0, 255),
}

def closest_color_name(rgb):
    """Convert an RGB color to its closest main category color."""
    min_distance = float("inf")
    closest_name = None
    for name, color_rgb in CSS3_COLORS_TO_RGB.items():
        distance = math.sqrt(
            (color_rgb[0] - rgb[0]) ** 2 +
            (color_rgb[1] - rgb[1]) ** 2 +
            (color_rgb[2] - rgb[2]) ** 2
        )
        if distance < min_distance:
            min_distance = distance
            closest_name = name

    # Map the closest CSS3 color to its broader category
    for category, colors in COLOR_CATEGORIES.items():
        if closest_name in colors:
            return category
    return "unknown"  # In case no match is found



# Simplified color mapping
def map_color(color_name):
    color_mapping = {
        "red": ["red", "crimson", "darkred", "firebrick"],
        "blue": ["blue", "darkblue", "dodgerblue", "skyblue"],
        "green": ["green", "lime", "darkgreen", "forestgreen"],
        "yellow": ["yellow", "gold", "khaki", "lemonchiffon"],
        "purple": ["purple", "violet", "magenta", "indigo"],
        "orange": ["orange", "darkorange", "chocolate", "coral"],
        "pink": ["pink", "deeppink", "hotpink", "lightpink"],
        "brown": ["brown", "sienna", "tan", "burlywood"],
        "gray": ["gray", "darkgray", "lightgray", "dimgray"],
        "black": ["black", "darkslategray"],
        "white": ["white", "ivory", "azure", "ghostwhite"]
    }
    for key, values in color_mapping.items():
        if color_name in values:
            return key
    return "other"

def categorize_tags(tags):
    """Categorize tags based on MAIN_TAGS."""
    categories = set()
    for tag in tags:
        for category, keywords in MAIN_TAGS.items():
            if tag in keywords:
                categories.add(category)
    return list(categories) if categories else ["Miscellaneous"]

def sha256_file(file_path):
    """Calculate SHA-256 of a file."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

def analyze_image(file_path, tags_json, tags_txt, colors_txt):
    """Analyze a single image for tags, categories, and colors."""
    try:
        with Image.open(file_path) as img:
            # Get resolution and determine platform
            resolution = f"{img.width}x{img.height}"
            platform = "Mobile" if img.height > img.width else "Desktop"
            file_hash = sha256_file(file_path)

            # Skip already processed images
            if file_hash in tags_json:
                print(f"Skipping {file_path}: Already processed.")
                return

            # Generate tags using ResNet
            rgb_img = img.convert("RGB")
            tensor = transform(rgb_img).unsqueeze(0)
            with torch.no_grad():
                outputs = model(tensor)
                _, indices = torch.topk(outputs, 5)
                tags = [LABELS[idx] for idx in indices[0]]

            # Categorize tags
            categories = categorize_tags(tags)

            # Analyze colors
            step = max(1, min(img.width, img.height) // 50)  # Adjust step for color sampling
            raw_colors = [closest_color_name(rgb_img.getpixel((x, y)))
                          for x in range(0, img.width, step)
                          for y in range(0, img.height, step)]
            mapped_colors = list(set(map(map_color, raw_colors)))  # Map to simplified colors and remove duplicates

            # Save results to tags.json
            tags_json[file_hash] = {
                "tags": tags,
                "categories": categories,
                "colors": mapped_colors,
                "resolution": resolution,
                "platform": platform
            }

            with open(tags_txt, "a") as tf:
                tf.write(f"{file_hash}: Tags: {', '.join(tags)}\n")

            with open(colors_txt, "a") as cf:
                cf.write("\n".join(mapped_colors) + "\n")

            print(f"Processed {file_path}")

    except Exception as e:
        print(f"Error processing {file_path}: {e}")

def analyze_images(input_folder, tags_file="tags.json", tags_txt="tags.txt", colors_txt="colors.txt", max_workers=8):
    """Analyze all PNG images in the input folder."""
    tags_json = {}
    if os.path.exists(tags_file):
        with open(tags_file) as tf:
            tags_json = json.load(tf)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for file in os.listdir(input_folder):
            file_path = os.path.join(input_folder, file)
            if os.path.isfile(file_path) and file.lower().endswith(".png"):
                futures.append(executor.submit(analyze_image, file_path, tags_json, tags_txt, colors_txt))

        for future in futures:
            future.result()

    # Save updated tags.json
    with open(tags_file, "w") as tf:
        json.dump(tags_json, tf, indent=4)

# Example usage
input_dir = "./wallpapers"
analyze_images(input_dir)
