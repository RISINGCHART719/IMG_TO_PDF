# This file creates a key-value pair of line images and their corresponding text.
# It puts the address of the line image, and the plain text itself in a file named train.txt

import os
import re


# This function is for extracting index from a name (folder or file)
def extract_numeric_prefix(name):
    match = re.search(r'(\d+)', name)
    return int(match.group(1)) if match else float('inf')


# Addressing
image_root = "Crop_lines"
text_root = "data_Texts"
output_label_file = "train.txt"


with open(output_label_file, "w", encoding="utf-8") as out_file:
    for folder_name in sorted(os.listdir(image_root), key=extract_numeric_prefix):
        image_dir = os.path.join(image_root, folder_name)

        if not os.path.isdir(image_dir):
            continue

        # Inferring guide-text filename based on folder name.
        # The folders and guide-text files are named similarly
        guide_text_name = folder_name.replace("handwritten", "guide_text") + ".txt"
        text_path = os.path.join(text_root, guide_text_name)

        if not os.path.exists(text_path):
            print(f"Missing text file for {folder_name}")
            continue

        # Reading text lines. Each line in the text file should correspond to each image in the 
        # similarly-named folder
        with open(text_path, "r", encoding="utf-8") as f:
            text_lines = [line.strip() for line in f if line.strip()]

        # Listing and sortting images by numeric index
        image_files = sorted(
            [f for f in os.listdir(image_dir) if f.endswith((".jpg"))],
            key=extract_numeric_prefix
        )

        # Checking if the number of text lines is equal to the number of images in folder
        if len(image_files) != len(text_lines):
            print(f"Mismatch: {folder_name} — {len(image_files)} images vs {len(text_lines)} texts")
            continue

        # Writing to the text file
        for img, txt in zip(image_files, text_lines):
            img_path = os.path.join(image_dir, img)
            out_file.write(f"{img_path}\t{txt}\n")

print(f"\nFinished. Label file saved as: {output_label_file}")

