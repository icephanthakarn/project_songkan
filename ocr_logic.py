# ocr_logic.py

import os
import re
import cv2
import pytesseract
from pdf2image import convert_from_path
import numpy as np

# ตั้งค่า path ของ Tesseract และ Poppler (แก้ให้ตรงกับเครื่องของคุณ)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
poppler_path = r'C:\Program Files\poppler-24.08.0\Library\bin'

# ตัวอย่าง config Tesseract (ปรับตามโมเดลที่คุณเทรน)
custom_oem_psm_config = r'--oem 1 --psm 4 -l ocr_train+eng_500'

def preprocess_image(image):
    """
    Convert เป็น Grayscale + Threshold เพื่อช่วยให้ OCR แม่นขึ้น
    """
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)
    return binary

def correct_word(text):
    """
    ฟังก์ชันแก้คำผิดพื้นฐาน
    """
    corrections = {
        "ชือนักศึกษา": "ชื่อนักศึกษา",
        "บทคดยอ": "บทคัดย่อ",
        "ชือนักศึกษา": "ชื่อนักศึกษา",
        "อาจารย์ทีปรึกษา": "อาจารย์ที่ปรึกษา",
        "บทคดยอ": "บทคัดย่อ",
        "บพคัดย่อ": "บทคัดย่อ",
        "คําสําคัญ": "คำสำคัญ",
        "บทพคัดย่อ": "บทคัดย่อ",
        "ภาควิซา": "ภาควิชา",
        "บพทคัตย่อ": "บทคัดย่อ",
        "บพคัตย่อ": "บทคัดย่อ",
        "บทคัตย่อ": "บทคัดย่อ",
        "ซื่อนักศึกษา": "ชื่อนักศึกษา",
        "คศาสาคญ": "คำสำคัญ",
    }
    for wrong, right in corrections.items():
        text = re.sub(wrong, right, text)
    return text

def clean_text(text):
    """
    ลบช่องว่างซ้ำซ้อน
    """
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_data_with_context(text):
    """
    ใช้ regex เพื่อจับฟิลด์: บทคัดย่อ, คำสำคัญ, ภาควิชา, ฯลฯ
    ปรับ pattern ตามลักษณะเอกสารจริง
    """
    patterns = {
        'หัวข้อ': r'(?:หัวข้อ(?:ปัญหาพิเศษ|สหกิจศึกษา|โครงงานพิเศษ)|สหกิจศึกษา)\s*(.*?)(?=\sชื่อนักศึกษา |$)',
        'ชื่อนักศึกษา': r'ชื่อนักศึกษา \s*(.*?)(?=\sปริญญา|$)',
        'ปริญญา': r'ปริญญา\s*(.*?)(?=\sภาควิชา|$)',
        'ภาควิชา': r'ภาควิชา\s*(.*?)(?=\sคณะ|ปีการศึกษา|$)',
        'คณะ': r'คณะ\s*(.*?)(?=\sมหาวิทยาลัย|$)',
        'มหาวิทยาลัย': r'มหาวิทยาลัย\s*(.*?)(?=\sปีการศึกษา|$)',
        'ปีการศึกษา': r'ปีการศึกษา\s*(\d+)',
        'อาจารย์ที่ปรึกษา': r'อาจารย์ที่ปรึกษา\s*(.*?)(?=\sบทคัดย่อ|$)',
        'บทคัดย่อ': r'(?:บทคัดย่อ)\s*(.*?)(?=\s(คำสำคัญ : |คำสำคัญ:)|$)',
        'คำสำคัญ': r'(?:คำสำคัญ : |คำสำคัญ:)\s*(.*?)(?=\sTitle|$)',
    }
    data = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            data[key] = clean_text(match.group(1))
        else:
            data[key] = 'ไม่พบข้อมูล'
    return data

def process_pdf_to_data(pdf_path):
    """
    ฟังก์ชันหลัก: 
    1) convert pdf -> images
    2) OCR
    3) correct_word / extract_data_with_context
    4) return dict
    """
    if not os.path.isfile(pdf_path):
        print("File not found:", pdf_path)
        return None
    
    try:
        images = convert_from_path(pdf_path, poppler_path=poppler_path, dpi=150, first_page=4, last_page=5)
        if not images:
            print("No images found in PDF.")
            return None

        full_text = ""
        for img in images:
            preprocessed = preprocess_image(img)
            text = pytesseract.image_to_string(preprocessed, config=custom_oem_psm_config)
            full_text += text + "\n"

        # แก้คำผิด
        full_text = correct_word(full_text)
        # ดึงฟิลด์
        data = extract_data_with_context(full_text)
        return data
    except Exception as e:
        print("Error in process_pdf_to_data:", e)
        return None
