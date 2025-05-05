import os
import sys
from tkinter import Tk, filedialog, messagebox
from PIL import Image
import pillow_heif
import fitz
from create_pdf import make_pdf


# this function is used for obtaining the valid and invalid files
def check_folder():
    valid_files = [f for f in os.listdir(user_input_dir) if f.lower().endswith(valid_extensions)]
    invalid_files = [
        f for f in os.listdir(user_input_dir)
        if os.path.isfile(os.path.join(user_input_dir, f)) and not f.lower().endswith(valid_extensions)
    ]
    return valid_files, invalid_files

def introduction():
    # This outputs a windows to the user to interact with
    # This step was introduce to provide a user friendly-experience
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    # when file is empty, this ensures you don't get ask again to enter images
    first_prompt_shown = False

    # ensures that there is something in the file before error checking
    while True:
        valid_files, invalid_files = check_folder()
        # exit loop when there is something added
        if valid_files or invalid_files:
            break
        # open up the folder where we expect images from user
        else:
            first_prompt_shown = True
            filedialog.askopenfilename(
            title="INSERT AT LEAST ONE IMAGE.",
            initialdir=user_input_dir,
            parent=root)

    # This step is checking for invalid files and ending the program
    valid_files, invalid_files = check_folder()
    if invalid_files:
        messagebox.showerror(
            "INVALID FILES DETECTED",
            f"The following files are not valid:\n\n" + "\n".join(invalid_files) +
            "\n\nPlease remove them and re-run the program.",
            parent=root
        )
        sys.exit(0)

    # if it is the users first time adding images
    # and if images are already in the file ask the user to validate files:
    if valid_files and not first_prompt_shown:
        response = messagebox.askyesno(
            "CONFIRM THE IMAGES",
            f"Is this what you want to process? :\n\n" + "\n".join(valid_files),
            parent=root
        )
        if not response:
            filedialog.askopenfilename(
                title="Replace or add Images.",
                initialdir=user_input_dir,
                parent=root
            )

    # Recheck and check the folder's new images
    valid_files, invalid_files = check_folder()
    if invalid_files:
        messagebox.showerror(
            "INVALID FILES DETECTED",
            f"After changes, invalid files were found:\n\n".join(invalid_files) +
            "\n\nPlease fix and restart the program.",
            parent=root
        )
        sys.exit(0)

    if valid_files and not invalid_files:
        print(f'{valid_files} were added.')

# This is the folder where the user is expected to put their images
user_input_dir = 'user_input_dir'

# checking to see if the folder exists
if not os.path.exists(user_input_dir):
        os.makedirs(user_input_dir)

# A list of our valid extensions
valid_extensions = ('.png', '.jpg', '.jpeg', '.heic', '.heif')

# starts here: =================================================================================================
# step to confirm images from user
introduction()

# step to digitally enhance (preprocessing)

# convert iphone images into png...
# Desktop images cannot natively open Iphone images so we converted them into png

# Register HEIF support
pillow_heif.register_heif_opener()


for file in os.listdir(user_input_dir):
    if file.lower().endswith(('.heic', '.heif')):
        iphone_path = os.path.join(user_input_dir, file)
        image = Image.open(iphone_path)

        # Save as PNG
        save_conv_path = os.path.splitext(iphone_path)[0] + ".png"
        image.save(save_conv_path, "PNG")
        print(f"Converted: {file} into {os.path.basename(save_conv_path)}")

        # Delete original file
        os.remove(iphone_path)
        print(f"Deleted original: {file}")


# emoving files in the inter_dir directory
for filename in os.listdir('inter_dir/'):
    file_path = os.path.join('inter_dir/', filename)
    if os.path.isfile(file_path) or os.path.islink(file_path):
        os.remove(file_path)


# generate pdf!
merged_pdf = fitz.open()
for file in os.listdir(user_input_dir):
    if file.endswith(('.png', '.jpg', '.jpeg', '.heic', '.heif')):
        input_path =  os.path.join(user_input_dir, file) 
        page_pdf = make_pdf(input_image_path = input_path,  inter_dir = 'inter_dir')
        merged_pdf.insert_pdf(page_pdf)

merged_pdf.save('output_dir/result.pdf')
merged_pdf.close() 
print(f'Finished. Saved Result in: output_dir/result.pdf')
        
    