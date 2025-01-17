import os
import re
from PIL import Image
import torch
from transformers import BlipProcessor, BlipForConditionalGeneration
from concurrent.futures import ThreadPoolExecutor

# Initialize model and processor from Hugging Face
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

# Function to generate caption for an image
def generate_caption(image_path):
    # Load image
    image = Image.open(image_path).convert("RGB")

    # Preprocess the image and generate the caption
    inputs = processor(images=image, return_tensors="pt")
    out = model.generate(**inputs)
    caption = processor.decode(out[0], skip_special_tokens=True)
    return caption

# Function to clean and format the caption into a more human-like filename
def format_caption(caption):
    # Remove unnecessary words or phrases
    caption = re.sub(r"\b(photo|picture|image|of|a|an|the)\b", "", caption)
    
    # Replace spaces with a single space and remove non-alphabetic characters
    caption = caption.strip()
    caption = re.sub(r"\s+", " ", caption)  # Replace multiple spaces with a single space
    caption = re.sub(r"[^a-zA-Z0-9\s]", "", caption)  # Remove non-alphanumeric characters
    
    # Capitalize each word in the caption
    caption = caption.title()
    
    # Ensure the filename is not too short or meaningless
    if len(caption) < 5:
        caption = "Untitled Image"
    
    return caption

# Function to rename a single .png file
def rename_png_file(image_path):
    # Get the filename from the path
    filename = os.path.basename(image_path)
    
    # Generate caption for the image
    caption = generate_caption(image_path)
    
    # Format the caption to be more human-friendly
    new_name = format_caption(caption) + ".png"
    
    # Make sure the new filename is not the same as the original
    if new_name != filename:
        new_path = os.path.join(os.path.dirname(image_path), new_name)
        os.rename(image_path, new_path)
        print(f'Renamed: {filename} -> {new_name}')

# Function to process all .png files in the directory (ignoring folders)
def process_directory(directory):
    # Collect all .png files (ignoring folders)
    png_files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(".png") and os.path.isfile(os.path.join(directory, f))]
    
    # Use ThreadPoolExecutor to process files in parallel with 8 threads
    with ThreadPoolExecutor(max_workers=8) as executor:
        executor.map(rename_png_file, png_files)

# Specify the directory containing the .png files
directory = "./wallpapers"
process_directory(directory)
