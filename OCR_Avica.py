import os
import sys
import subprocess
import warnings

def install_requirements():
    requirements = ['easyocr', 'opencv-python-headless', 'torch']
    for lib in requirements:
        try:
            if lib == 'opencv-python-headless':
                import cv2
            else:
                __import__(lib.replace('-', '_'))
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib, "--quiet"])

install_requirements()

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
warnings.filterwarnings("ignore")

import cv2
import easyocr
import torch

def ocr_process():
    zones = {
        "ID": [387, 331, 133, 41],
        "PASS": [393, 402, 130, 38]
    }

    desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')
    img_path = os.path.join(desktop, "pic.png")
    
    if not os.path.exists(img_path):
        return

    img = cv2.imread(img_path)
    if img is None:
        return

    use_gpu = torch.cuda.is_available()
    
    sys.stdout = open(os.devnull, 'w')
    try:
        reader = easyocr.Reader(['en'], gpu=use_gpu, verbose=False)
    finally:
        sys.stdout = sys.__stdout__
    
    id_val = ""
    pass_val = ""

    for label, (x, y, w, h) in zones.items():
        crop = img[y:y+h, x:x+w]
        ocr_res = reader.readtext(crop, detail=0)
        text = "".join(ocr_res).replace(" ", "")
        if label == "ID": 
            id_val = text
        else: 
            pass_val = text

    if id_val and pass_val:
        print(f"ID: {id_val}")
        print(f"PASS: {pass_val}")
        
        if 'GITHUB_OUTPUT' in os.environ:
            with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
                f.write(f"id={id_val}\n")
                f.write(f"pass={pass_val}\n")

if __name__ == "__main__":
    ocr_process()
