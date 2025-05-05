# Purpose of file:
# We chose 200 of the 1500 images of handwriting. The reason for this
# is that many of the 1500 images had cursive handwriting, which can 
# be difficult to train. Now that we had chosen 200 of the images,
# we needed a method to also find their corresponding text files ( the ones
# generated in 1_Preprocess_Images.py). This file finds the texts for the 
# selected images, and copies them to the selected folder.



import os
import shutil

#Addressing (won't necessarily match git structure)
png_folder = 'data_100(bottom)_images'
text_folder = '../../Handwriting Dataset/archive/guide_texts/'
output_folder = 'data_100(bottom)_text'
os.makedirs(output_folder, exist_ok=True)

# Processing files
for filename in os.listdir(png_folder):
    if filename.endswith('.png') and filename.startswith('handwritten_'):
        # Extracting core ID by removing extra bits
        base_name = filename.replace('handwritten_', '').replace('.png', '')

        # Finding the text file
        for txt_filename in os.listdir(text_folder):
            if txt_filename.endswith('.txt') and txt_filename.endswith(base_name + '.txt'):
                # Copying matching text file
                src_path = os.path.join(text_folder, txt_filename)
                dst_path = os.path.join(output_folder, txt_filename)
                shutil.copyfile(src_path, dst_path)
                print(f"Copied: {txt_filename}")
                break
        else:
            print(f"No match found for {filename}")

print("Done.")
