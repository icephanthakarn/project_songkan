from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import CorrectionModel, db
import uuid
import datetime

# 1️⃣ เชื่อมต่อฐานข้อมูล SQLite
engine = create_engine('sqlite:///instance/mydb.sqlite3')
Session = sessionmaker(bind=engine)
session = Session()

# 2️⃣ คำผิดที่ต้องการเพิ่ม (dictionary)
corrections_dict = {
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
        "ซ่วยในหาค่าการถ่ายเทความร้อน": "ช่วยในการหาค่าการถ่ายเทความร้อน",
        "ชนิต": "ชนิด",
        "ค่าเฉลีย": "ค่าเฉลี่ย",
        "แอปพลิเคซัน": "แอปพลิเคชัน",
        "กระเบือง": "กระเบื้อง",
        "พิเศนษ": "พิเศษ",
        "UD": "UI",
        "สําหรับ": "สำหรับ",
        "บีใด้นําเสนอ": "นี้ได้นำเสนอ",
        "โมเดลการทํางานของกดูโคส อินซูสิน": "โมเดลการทำงานของกลูโคส อินซูลิน",
        "ผศ.ตดร.": "ผศ.ดร.",
        "๒๐กล๕๕": "2025",
        "fluted": "Fibonacci Retracement",
        "2 มกราคม wa. 2563": "2 มกราคม พ.ศ. 2563",
        "แลตอบแทน": "ผลตอบแทน",
        "ฟีโบนัชชี (๒๐กล๕๕ Retracement)": "ฟีโบนัชชี (Fibonacci Retracement)",
        "แบบจําลองตด้วยโปรแกรม": "แบบจําลองด้วยโปรแกรม",
        "สำหรับหลักทรัพย์ของ PTT คือ fluted (Fibonacci Retracement)": "สำหรับหลักทรัพย์ของ PTT คือ ฟีโบนัชชี (Fibonacci Retracement)",
        "สาดกระบัง": "ลาดกระบัง",
        "เบียประกันภัย": "เบี้ยประกันภัย",
        "ซนิดาภา": "ชนิดาภา",
        "พนะจอมเกล้าเจ้าคุณทหารลาดกระบัง": "พระจอมเกล้าเจ้าคุณทหารลาดกระบัง",
        "การติดเชื่อ": "การติดเชื้อ",
        "ความบ่าช้า": "ความล่าช้า",
        "551 HD": "SET HD",
        "ราคาตํากว่าที่ วิเคราะห์ได้": "ราคาต่ำกว่าที่วิเคราะห์ได้",
        "ซีววิทยา": "ชีววิทยา",
        "น้ากล้วยหอม": "น้ำกล้วยหอม",
        "น้้านมโค": "น้ำนมโค",
        "Kefin": "Kefir",
        "น้านมอัลมอนด์": "น้ำนมอัลมอนด์",
        "เปอร์เซ็นต์แอลกอฮอล์ตํา": "เปอร์เซ็นต์แอลกอฮอล์ต่ำ",
        "ซําระราคา": "ชำระราคา",
        "เซ่น": "เช่น",
        "การตังค่า": "การตั้งค่า",
        "แเละใช้ (0เ๒๑กล": "และใช้ Kibana",
        "Managernent": "Management",
        "Cl": "CI",
        "การจัดจําแนกสารพันธุ์": "การจำแนกสายพันธุ์",
        "เตรท": "เทรต",
        "ซ่วย": "ช่วย",
        "ขีตจํากัดตําสุด": "ขีดจำกัดต่ำสุด",
        "ตรวจวัต": "ตรวจวัด",
        "เรื่องแสง": "เรืองแสง",
        "ซ้้าบน": "ซ้ำบน",
        "การประมวณผลภาพ": "การประมวลผลภาพ",
        "ฟังก์ซัน": "ฟังก์ชัน",
        "เข้มขัน": "เข้มข้น",
        "คพเก8": "RMP8",
        "มือยู่ใน": "มีอยู่ใน",
        "ณัชซา": "ณัชชา",
        "60๒16": "Solid pH6",
        "บล็อกเซน": "บล็อกเชน",
        "หั้วโลก": "ทั่วโลก",
        "อํานาจรัฐ": "อำนาจรัฐ",
        "ผลตอบเทน": "ผลตอบแทน",
        "ซึ้นส่วน": "ชิ้นส่วน",
        "พื่นฐาน": "พื้นฐาน",
        "เแปลง": "แปลง",
        "PERFORMANCE MODELS 1": "Performance Model 1",
        "หมอบหมาย": "มอบหมาย",
        "สาขาวิซา": "สาขาวิชา",
        "เปลือกไขไก่": "เปลือกไข่ไก่",
        "ตกผลึกใหม่ cABRE": "ตกผลึกใหม่ CABRE",
        "wien 3 vila": "วัตถุดิบ 3 ชนิด",
        "5เซมเว": "5CMW",
        "ฟอสฟอริกเข้มขัน": "ฟอสฟอริกเข้มข้น",
        "rnobile applications": "mobile applications",
        "systern": "system",
        "becorne": "become",
        "ข่องทาง": "ช่องทาง",
        "ตําเนินการ": "ดำเนินการ",
        "SOL Server": "SQL Server",
        "anf": "and",
        "เอทิลืนไวนิลอะซิเทต": "เอทิลีนไวนิลอะซิเทต",
        "ขึมผ่าน": "ซึมผ่าน",
        "เแนะนํา": "แนะนำ",
        "พัฒนาและส่วนของหลังบ้าน": "พัฒนา และส่วนของหลังบ้าน",
        "น้้าตาล": "น้ำตาล",
        "แอลฟาอะไมเลส": "อัลฟาอะไมเลส",
        "Cellic CTec2": "Cellic CTec2 (เซลลูเลส)",
        "ซนิภา": "ชนิภา",
        "ตะกัว": "ตะกั่ว",
        "ซีวาพร": "ชีวาพร",
        "ซ้าลง": "ช้าลง",
        "DTPA ใช้ afin Cd": "DTPA ใช้สกัด Cd",
        "ถ่านซีวภาพ": "ถ่านชีวภาพ",
        "ตดิน": "ดิน",
        "ดัดเแปลง": "ดัดแปลง",
        "ความสืนเปลือง": "ความสิ้นเปลือง",
        "ศักยภาพของสารเอซิลทีมี": "ศักยภาพของสารเอซิลที่มี",
        "ซ่องปาก": "ช่องปาก",
        "เพิ่มจํานวนของแบคทีเรียก่อโรค": "เพิ่มจำนวนแบคทีเรียก่อโรค",
        "5. 4๐0กทน5": "5.400 µg/mL",
        "อัลกอริท็ม": "อัลกอริทึม",
        "ประสิทฑธิภาพ": "ประสิทธิภาพ",
        "0๑๕[51๐ก Trees": "Decision Trees",
        "Support Vector Machines uaz k-Nearest Neighbors": "Support Vector Machines และ k-Nearest Neighbors",
        "ส่วนหน้าบ้าน (กก๐ก1-ิก4)": "ส่วนหน้าบ้าน (Front-End)",
        "โดยตลอดไธ] จัย": "โดยตลอดการวิจัย",
        "ระบบการ์ดเกมออนไลน์ Cuisine 51ก๑": "ระบบการ์ดเกมออนไลน์ Cuisine Strike!!",
        "การออกแบบรธีม": "การออกแบบธีม",
        "โดยแบ่งเป็น ๕0๑ก1": "โดยแบ่งเป็น client",
        "คอมเมนต์ทีไม่เหมาะสม": "คอมเมนต์ที่ไม่เหมาะสม",
        "เพิม": "เพิ่ม",
        "เครื่องมีอะเทคโนโลยี": "เครื่องมือเทคโนโลยี",
        "กรณีการใช้งาน(ป5๑ Case)": "กรณีการใช้งาน(Use Case)",
        "แผนภาพการทฑํางาน": "แผนภาพการทำงาน",
        "(Sequence [วเลรูเลทก)": "(Sequence Diagram)",
        "มากยิงขึ้น": "มากยิ่งขึ้น",
        "หลักการ๐8บ0": "หลักการCRUD",
        "ถูกจัดเก็บในรูปแบบไฟล์ ม|": "ถูกจัดเก็บในรูปแบบไฟล์ YAML",
        "ภายใต้ขื่อ รเวนเฉรน์อก.ทกา!": "ภายใต้ขื่อ application yml",
        "ข้อมูลซุดเดียวกัน": "ข้อมูลชุดเดียวกัน",
        "ของเว็บแอป เดเจ้จเจ เว < eww yu . พลิเคชันนี่": "ของเว็บแอปพลิเคชันนี้",
        "สะดวกและลดความ เสียง": "สะดวกและลดความเสี่ยง",
        "ข้อมูล รวมทัง": "ข้อมูล รวมทั้ง",
        "คณะ: ไม่พบข้อมูล": "คณะ: วิทยาศาสตร์",
        "มหาวิทยาลัย: ไม่พบข้อมูล": "มหาวิทยาลัย: สถาบันเทคโนโลยีพระจอมเกล้าเจ้าคุณทหารลาดกระบัง",
        "อ. สันธนะ อู่อุดมยิง": "อ. สันธนะ อู่อุดมยิ่ง",
        "การตําเนินโครงงาน": "การดำเนินโครงงาน",
        "หลักการ Process Improvement และ |ล[26ก": "หลักการ Process Improvement และ Kaizen",
        "a 4 da ' a a ป s I] การเลือกซื้อแล็ปท็อป": "การเลือกซื้อแล็ปท็อป",
        "อาจเป็น ซ่ 1 เด 2 aM ona ว Hd aa eo a =. 2 a a เรื่องยุ่งยาก": "อาจเป็น เรื่องยุ่งยาก",
        "และใช้ oo สซ่ๆ or a = Ig o, I] ol = a o 2 2 ระบบผู้เชี่ยวชาญที": "และระบบผู้เชี่ยวชาญที่",
        "เพิมเติม": "เพิ่มเติม",
        "การ 2.1.8 ao o a o_o > ET 1] a ar แสดง": "การแสดง",
        "ในระดับที่ดีมาก os uw oo oo x 4, ao Pr] x o": "ในระดับที่ดีมาก",
        "ระบบแซทบอท": "ระบบแชทบอท",
        "เชทบอท": "แชทบอท",
        "เกมคอมพิวเตอร์ a. - - a oo": "เกมคอมพิวเตอร์",
        "งานวิจัย 8๐55ฯ8 นี้": "งานวิจัยนี้",
        "ทําให้ผู้เล่น 8 และ PC": "ทําให้ผู้เล่น VR และ PC",
        "VR ua PC": "VR และ PC",
        "แบบสอบถาม 550": "แบบสอบถาม SSQ",
        "ผลการ ฑดสอบ": "ผลการทดสอบ",
        "การโต๊ตอบ": "การโต้ตอบ",
        "เคลือนไหว": "เคลื่อนไหว",
        "ในขณะทีผู้เล่น 0๐ ใช้": "ในขณะที่ผู้เล่นใช้",
        "Asymmetrical Virtual Reality Game, SSO": "Asymmetrical Virtual Reality Game, SSQ",
        "ตร.": "ดร.",
        "การพัฒนาโมเตลทํานายโทษของศาลเยาวซนและ ครอบครัว": "การพัฒนาโมเดลทํานายโทษของศาลเยาวชนและ ครอบครัว",
        "ผศ.ดร.วิสันต์ ตังวงษ์เจริญ ๐1": "ผศ.ดร.วิสันต์ ตั้งวงษ์เจริญ",
        "การจัดทําปัญหาพิเศษนี": "การจัดทําปัญหาพิเศษนี้",
        "ชีวภาพ NIST ของ aa = a = os - o o กรมสอบสวนคดีพิเศษ": "ชีวภาพ NIST ของกรมสอบสวนคดีพิเศษ",
        "ชุดข้อมูลลายนิวมือ": "ชุดข้อมูลลายนิ้วมือ",
        "นิวมือ": "นิ้วมือ",
        "ข้อมูลไฟล์ประเภท WSO": "ข้อมูลไฟล์ประเภท WSQ",
        "มีบริการ = a oo v, ซ์ ' 2 da 2 แปลงภาพสี": "มีบริการแปลงภาพสี",
        "สําหรับหลังบ้าน way postgresql": "สําหรับหลังบ้าน และ postgresql",
        "WSO": "WSQ",
        "ดึงตูด": "ดึงดูด",
        "พร้อมสือ": "พร้อมสื่อ",
        "เน้นย้าความรู้สึกที่มีความถิ": "เน้นย้ำความรู้สึกที่มีความถี่",
        "การทตสอบ": "การทดสอบ",
        "การปรับแต่งโมเตส": "การปรับแต่งโมเดล",
        "โมเตสตัง": "โมเดลดัง",
        "เน้นย้า": "เน้นย้ำ",
        "ทฤษฎีความรู้สึกพื่นฐาน": "ทฤษฎีความรู้สึกพื้นฐาน",
        "การวิเคราะห์ความถี": "การวิเคราะห์ความถี่",
        "การปรับแต่งคําสัง": "การปรับแต่งคําสั่ง",
        "การออกแบบคําสัง": "การออกแบบคําสั่ง",
        "ซุดคําสั่ง": "ชุดคําสั่ง",
        "ระบบจัดการเนื่อหาของเว็บไซต์": "ระบบจัดการเนื้อหาของเว็บไซต์",
        "เนื่องจากเป็น /เว๒๐ปิ๑๓": "เนื่องจากเป็น Application",
        "ให้บริการ oa 3 a a a a ซ I o o 7] บนบัญชีใลน์": "ให้บริการบนบัญชีไลน์",
        "สกายฟรือก": "สกายฟร็อก",
        "รูปแบบ BDD (Behavior Driven 0๑๑1อเทาลท1)": "รูปแบบ BDD (Behavior Driven Developer)",
        "nema. ปัทมา เจริญพร": "ผศ.ดร. ปัทมา เจริญพร",
        "วิดยาสโม aaa.": "วิดยาสโม สจล.",
        "เกียวกับ": "เกี่ยวกับ",
        "Online Fingerboard Shopping Application oo aa a. =a os ar ox": "Online Fingerboard Shopping Application",
        "การ ซําระเงิน": "การชำระเงิน",
        "ความล่าซ้า": "ความล่าช้า",
        "an ความผิดพลาด,": "ความผิดพลาด,",
        "ผู้ดูแลสระบบ": "ผู้ดูแลระบบ",
        "ตําแหน่ง Research /เ5515เลก1": "ตําแหน่ง Research Assistant",
        "การพัฒนา ห/๑|๒5๑ก๐๑": "การพัฒนา Webservice",
        "โดยใช้ไลบรารี่ กเล5«": "โดยใช้ไลบรารี่ Flask",
        "PYQTS GUI": "PYQT5 GUI",
        "โดยใช้ไลบรารี่ ๑น๕515": "โดยใช้ไลบรารี่ requests",
        "YOLOVS": "YOLOV5",
        "Flask requests \psycopg2": "Flask, requests, psycopg2",
        "สือสาร": "สื่อสาร",
        "ซุด": "ชุด",
        "การนําหมายเลขเทม | v = - wo ov a 57 I] o v | เพลต": "การนําหมายเลขเทมเพลต",
        "แห่งหนึง": "แห่งหนึ่ง",
        "ดอกเบีย": "ดอกเบี้ย",
        "เปลียนแปลงชือ": "เปลี่ยนแปลงชื่อ",
        "ข้อมูล a8 vo 3 = [3 o a = ‘ [JE – o อีกทัง": "ข้อมูลอีกทั้ง",
        "การดําเนินงาน a . a ต่ y *=- ๑, ซึ-วดี้. คือ": "การดําเนินงาน คือ",
        "(ป15๑ก Interfaces)": "(User Interfaces)",
        "ฟังก์ชันเดิม Sa yo SF ทีมือยู่ให้ดียิงขึน": "ฟังก์ชันเดิมที่มีอยู่ให้ดียิ่งขึ้น",
        "การพัฒนาระบบจัดการเนื้อหาในระบบขายหน้าร้าน ๐๑20๐5": "การพัฒนาระบบจัดการเนื้อหาในระบบขายหน้าร้าน easyPOS",
        "ให้สอดคล้องกับ o o or 3 a o vw ol ความ": "ให้สอดคล้องความ",
        "ออกแบบและ 2, 4 เม vo 4 37 ol a IZ a แก้ไข": "ออกแบบและแก้ไข",
        "โครงสร้าง ro] oer wy 17 a ous oe I] I] หรือระบบ": "โครงสร้าง หรือระบบ",
        "แอปพลิเคซัน": "แอปพลิเคชัน",
        "มีการเขียนโปรแกรมส่วนหน้าบ้าน(กก๐ก1-ิก4)": "มีการเขียนโปรแกรมส่วนหน้าบ้าน(Front-End)",
        "ไธ]จัยจะตั้งอยู่บนพื้นฐาน": "การวิจัยจะตั้งอยู่บนพื้นฐาน",
        "ดีมากยิงขึ้นได้": "ดีมากยิ่งขึ้นได้",
        "Cuisine 51ก๑": "CuisineStrike!!",
        "เซ่นYu-Gi-Oh!": "เช่นYu-Gi-Oh!",
        "ฒนาตัวต้นแบบของเกมขึ้นโดยแบ่งเป็น๕0๑ก1ที่ผู้เล่นใช้งานซึ่งพัฒนาบนG": "ตัวต้นแบบของเกมขึ้นโดยแบ่งเป็นclientที่ผู้เล่นใช้งานซึ่งพัฒนาบนGod",
        "โตย": "โดย",
        "uaz":"และ",
        "(05":"iOS",
        "๑ทหเทล๑สเลทาไทล":"o-Phenylenediamine",
        "๐เพ|":"KOH",
        "5กาล":"Smart",
        "น้ามัน":"น้ำมัน",

}

# ✅ กำหนด student_id ของผู้เพิ่ม (admin)
admin_id = "admin001"

# 3️⃣ วนลูปเพื่อเพิ่มคำใหม่
added_count = 0
for wrong, correct in corrections_dict.items():
    # ตรวจว่ามีคำนี้อยู่ในฐานข้อมูลหรือยัง
    exists = session.query(CorrectionModel).filter_by(
        original_word=wrong, corrected_word=correct
    ).first()

    if not exists:
        correction = CorrectionModel(
            id=str(uuid.uuid4()),
            original_word=wrong,
            corrected_word=correct,
            student_id=admin_id,     # ✅ ใส่ admin เป็นคนเพิ่ม
            project_id=None,
            created_at=datetime.datetime.now()
        )
        session.add(correction)
        added_count += 1

# 4️⃣ บันทึกลงฐานข้อมูล
session.commit()
print(f"✅ เพิ่มคำผิดใหม่ {added_count} รายการลงฐานข้อมูลโดย admin001")
