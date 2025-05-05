Please note that the addresses in the files may differ from the actual addresses
that exist on the git structure, since we had to run some of these files 
outside of the git environment

# 1_Preprocess_Images.py
    This python file automatically preprocesses the 1500 kaggle images.
    It runs morphological operations and other enhancements on the images, 
    and then has 2 extracted outputs:
    guide-texts (what is said in each image in a .txt file), and handwritten
    image portions of the original image.
    NOTE: After this step, there is a manual preprocessing step as well, 
    which involved us manually separating each line in each image and matching the
    guide_text.txt file to each line, so that we could train the paddle OCR model on 
    the data. Otherwise the data would be useless.

# Util Files
    This folder contains python files that further supported the preprocessing of the data.
    Each file's purpose is explained in its header comments.

# 2_Train_OCR_Model.py
    This python file trains the model. It took around 9 hours (with gpu-compute CUDA) on a PC with the following specs:
    Processor       12th Gen Intel(R) Core(TM) i7-12700K   3.60 GHz
    Graphics Card   NVIDIA GeForce RTX 3080 12 GB VRAM
    Installed RAM   32.0 GB (31.8 GB usable)
    System type     64-bit operating system, x64-based processor

    The configuration for training the model is made inside the file itself.

# Text_Rec_Model
    Contains the trained recognition mode, 
    as well as inference models for detection and classification