# add_user.py

from app import app  # นำเข้า app จากไฟล์หลักของคุณ
from models import db, UserModel
from werkzeug.security import generate_password_hash

# ข้อมูลตัวอย่างนักศึกษา
sample_students = [
     {
        "student_id": "63050137",
        "student_name": "นางสาว ธนวรรณ วงศ์เพชรชารัต ",
        "student_major": "วิทยาการคอมพิวเตอร์",
        "email": "63050137@kmitl.ac.th",
        "password": "50137"  # จะถูก hash ก่อนเก็บ
    },
     {
        "student_id": " 63050097",
        "student_name": "นางสาว กัลยวรรธน์ ชื่นชมรติมงคล ",
        "student_major": "วิทยาการคอมพิวเตอร์",
        "email": "63050097@kmitl.ac.th",
        "password": "50097"  # จะถูก hash ก่อนเก็บ
    },

    {
        "student_id": "64050166",
        "student_name": "พันธกานต์ กิจนุกร",
        "student_major": "วิทยาการคอมพิวเตอร์",
        "email": "64050166@kmitl.ac.th",
        "password": "50166"  # จะถูก hash ก่อนเก็บ
    },

        {
        "student_id": "64050456",
        "student_name": "ดุสิตา บุญหนุน",
        "student_major": "วิทยาการคอมพิวเตอร์",
        "email": "64050456@kmitl.ac.th",
        "password": "50456"  # จะถูก hash ก่อนเก็บ
    },

        {    "student_id": "63050169",
        "student_name": "นางสาว aaa วvvต ",
        "student_major": "วิทยาการคอมพิวเตอร์",
        "email": "63050169@kmitl.ac.th",
        "password": "50169"  # จะถูก hash ก่อนเก็บ
        },
        {
                    "student_id": "63050176",
        "student_name": "นางสาว daga aggae ",
        "student_major": "วิทยาการคอมพิวเตอร์",
        "email": "63050176@kmitl.ac.th",
        "password": "501376"  # จะถูก hash ก่อนเก็บ
        },
        
        {
        "student_id": "admin001",     # ✅ เพิ่มบรรทัดนี้
        "student_name": "Admin",
        "email": "admin@kmitl.ac.th",
        "role": "admin",
        "password": "1234"
    },
 

]


with app.app_context():
    for student in sample_students:
        existing_user = UserModel.query.filter_by(email=student["email"]).first()

        if existing_user:
            print(f"⚠️ ผู้ใช้ {student['email']} มีอยู่แล้วในระบบ")
        else:
            hashed_password = generate_password_hash(student["password"])
            new_user = UserModel(
                student_id=student.get("student_id"),
                student_name=student.get("student_name"),
                student_major=student.get("student_major"),
                email=student["email"],
                password=hashed_password,
                role=student.get("role", "student")  # ถ้าไม่มี role ให้ใช้ student เป็น default
            )
            db.session.add(new_user)
            print(f"✅ เพิ่มผู้ใช้ใหม่: {student['email']}")

    db.session.commit()
    print("🎉 เสร็จสิ้นการเพิ่มข้อมูลผู้ใช้ลงในฐานข้อมูล")
