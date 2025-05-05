from paddleocr import PaddleOCR
import cv2
import numpy as np
from symspellpy.symspellpy import SymSpell, Verbosity




# *****************************************
# ******************OCR********************
# *****************************************
def detect_and_recognize_words_with_positions(image_path) :
    ocr = PaddleOCR(
        use_angle_cls=False,
        lang='en',
        det_model_dir='ch_PP-OCRv4_det_server_infer',
        rec_model_dir='Text_Rec_Model/best_accuracy',
        rec_image_shape='3, 32, 320',
        show_log=False
    )

    # Perform OCR
    result = ocr.ocr(image_path, cls=False)


    # Initializing the dictionary
    sym_spell = SymSpell(max_dictionary_edit_distance=3, prefix_length=7)
    dictionary_path = "frequency_dictionary_en_82_765.txt"
    sym_spell.load_dictionary(dictionary_path, term_index=0, count_index=1)
                                

    # Replace incorrect words with corrected words in the detection structure
    for detection in result:
        if detection:
            for line in detection:
                corrected_words = []
                for word in line[1][0].split():
                    word = word.replace('+', 't')
                    suggestions = sym_spell.lookup(word, Verbosity.CLOSEST, max_edit_distance=2)
                    if suggestions:
                        corrected_words.append(suggestions[0].term + " ")
                    else:
                        corrected_words.append(word + " ") 
                line[1] = (' '.join(corrected_words), line[1][1])
    return result
