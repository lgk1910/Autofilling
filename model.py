import argparse
from pytesseract import Output
from pdf2image import convert_from_path
import os
from utils import *
import cv2
import time
import img2pdf

os.environ['TESSDATA_PREFIX'] = os.path.join(os.path.abspath(os.getcwd()), "tessdata")

class Model:
    def __init__(self):
        pass
    def process_1(self, filepath):
        pages = convert_from_path(filepath, 300)
        entity_lsts = []
        for page in pages:
            image = np.array(page)

            return_dict = fields_detection(image)
            entity_lst = return_dict['entity_lst']
            font_size = return_dict['font_size']
            
            # print(entity_lst)
            entity_lsts.append(entity_lst)
            # break
        return entity_lsts, font_size

    def process_2(self, file_path, entity_lsts, font_size, fontpath, form_code, result_path):
        start = time.time()
        pages = convert_from_path(file_path, 100)
        print("File converting time: ", time.time() - start)
        start = time.time()
        image_paths = []
        index = 0
        for page in pages:
            image = np.array(page)
            image = data_filling(entity_lsts[index], image, int(font_size*image.shape[0]), fontpath)
            save_start = time.time()
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            save_path = os.path.join(result_path, form_code + str(index) + '.png')
            cv2.imwrite(save_path, image)
            image_paths.append(save_path)
            index += 1
            # break
        print(f"Filling time page {index}: {time.time() - save_start}")
        start = time.time()
        with open(os.path.join(result_path, form_code + ".pdf"),"wb") as f:
	        f.write(img2pdf.convert(image_paths))
        for image_path in image_paths:
            os.remove(image_path)
        print(f"PDF conversion time: {time.time() - save_start}")
        # return images