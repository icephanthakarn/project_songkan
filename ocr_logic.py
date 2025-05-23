# ocr_logic.py

import os
import re
import cv2
import pytesseract
from pdf2image import convert_from_path
import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import CorrectionModel

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


engine = create_engine('sqlite:///instance/mydb.sqlite3')  # ✅ ปรับ path ให้ตรง
Session = sessionmaker(bind=engine)
session = Session()

def correct_word(text):
    """
    ฟังก์ชันแก้คำผิดพื้นฐาน
    """

    
    try:
        corrections = session.query(CorrectionModel).all()
        for item in corrections:
            wrong = item.incorrected_word.strip()
            right = item.corrected_word.strip()
            if wrong and wrong in text:
                text = text.replace(wrong, right)
    except Exception as e:
        print("❌ error loading corrections:", e)

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
        'abstract_en': r'Abstract\s*(.*?)(?=\s*Keywords\s*:|$)',

        'title_en': r'(?:Title\s*:?)\s*(.*?)(?=\s(Students  |Student )|$)',  

        'คำสำคัญ': r'(?:คำสำคัญ : |คำสำคัญ:)\s*(.*?)(?=\sTitle|$)',
        'keywords_en': r'(?:Keywords\s*:?)\s*(.*?)(?=\s*กิตติกรรมประกาศ|$)',

    }
    data = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            data[key] = clean_text(match.group(1))
        else:
            data[key] = 'ไม่พบข้อมูล'


        # รวมคำสำคัญไทย + อังกฤษ
    thai = data.get('คำสำคัญ', '')
    eng = data.get('keywords_en', '')

    combined = []
    if thai != 'ไม่พบข้อมูล':
        combined.append(thai)
    if eng != 'ไม่พบข้อมูล':
        combined.append(eng)

    data['คำสำคัญ'] = ', '.join(combined)

    if 'ชื่อนักศึกษา' in data:
    # แยกตามคำว่า "รหัสนักศึกษา" แล้วขึ้นบรรทัดใหม่
        formatted = re.sub(r'(รหัสนักศึกษา \d+)', r'\1\n', data['ชื่อนักศึกษา'])
        data['ชื่อนักศึกษา'] = formatted.strip()

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
        images = convert_from_path(pdf_path, poppler_path=poppler_path, dpi=150, first_page=4, last_page=7)
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
