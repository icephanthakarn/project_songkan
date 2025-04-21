from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, desc
from sqlalchemy.orm import relationship

import re
import uuid
from datetime import datetime
db = SQLAlchemy()

def generate_custom_id(prefix, length=6):
    def generate():
        # เลือก Model ตาม prefix
        if prefix == 'user':
            model = UserModel
        elif prefix == 'SC':
            model = ProjectModel
        elif prefix == 'kw':
            model = KeywordModel
        else:
            raise ValueError("Unknown prefix")

        # หา id ล่าสุดที่ขึ้นต้นด้วย prefix แล้ว sort เอาตัวสุดท้าย (desc)
        last_obj = db.session.query(model)\
            .filter(model.id.like(f"{prefix}%"))\
            .order_by(desc(model.id)).first()

        if last_obj:
            # ดึงตัวเลขท้าย id ด้วย regex เช่น 'SC000004' -> 4
            last_number = int(re.sub(r"\D", "", last_obj.id))
            next_number = last_number + 1
        else:
            next_number = 1

        return f"{prefix}{str(next_number).zfill(length)}"
    return generate


class UserModel(db.Model):
    __tablename__ = 'users'

    student_id = Column(String(10), primary_key=True)
    email = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default='student')
    student_name = Column(String(100))
    faculty = Column(String(100), default='วิทยาศาสตร์')  
    student_major = Column(String(100))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.now)
    projects = relationship('ProjectModel', secondary='project_student', back_populates='students')



class ProjectModel(db.Model):
    __tablename__ = 'projects'
    id = Column(String(10), primary_key=True, default=generate_custom_id('SC', 6))
    title_th = Column(String(255), nullable=False)
    title_en = Column(String(255))
    academic_year = Column(String(10))
    abstract_th = Column(Text)
    abstract_en = Column(Text)
    department = Column(String(100))
    faculty = Column(String(100))
    
    author = Column(String(255))
    advisor = Column(String(255))
    keywords_rel = relationship('KeywordModel', secondary='project_keyword', back_populates='projects')

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.now)

    created_by = Column(String(10), ForeignKey('users.student_id', name='fk_created_by_user'))
    updated_by = Column(String(10), ForeignKey('users.student_id', name='fk_updated_by_user'))


    creator = relationship('UserModel', foreign_keys=[created_by], backref='created_projects')
    updater = relationship('UserModel', foreign_keys=[updated_by], backref='updated_projects')
    # One-to-Many: 1 Project -> N Users
    #users = relationship('UserModel', back_populates='project')

    # Many-to-Many กับ Keyword
    keywords_rel = relationship('KeywordModel', secondary='project_keyword', back_populates='projects')

    # One-to-One กับไฟล์ pdf
    # uselist=False บอกว่า relationship นี้คือ 1:1
    pdf_file = relationship('PdfFileModel', back_populates='project', uselist=False)

    students = relationship('UserModel', secondary='project_student', back_populates='projects')

    @property
    def keywords_list(self):
        return self.keywords_rel

class KeywordModel(db.Model):
    __tablename__ = 'keywords'

    id = Column(String(10), primary_key=True, default=generate_custom_id('kw', 6))  # ✅ ใส่ default generator
    keyword_text = Column(String(100), nullable=False)

    projects = relationship('ProjectModel', secondary='project_keyword', back_populates='keywords_rel')


class ProjectKeywordModel(db.Model):
    __tablename__ = 'project_keyword'

    project_id = Column(String(10), ForeignKey('projects.id'), primary_key=True)
    keyword_id = Column(String(10), ForeignKey('keywords.id'), primary_key=True)


class PdfFileModel(db.Model):
    __tablename__ = 'pdf_file'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(255), nullable=False)
    thumbnail_path = Column(String(255))
    uploaded_at = Column(DateTime, default=datetime.now)

    # บังคับ One-to-One => unique=True เพื่อป้องกันการซ้ำ
    project_id = Column(String(10), ForeignKey('projects.id'), unique=True)  

    # กำหนด back_populates ให้ตรงกับ pdf_file
    project = relationship('ProjectModel', back_populates='pdf_file')

class ProjectStudentModel(db.Model):
    __tablename__ = 'project_student'

    project_id = Column(String(10), ForeignKey('projects.id'), primary_key=True)
    student_id = Column(String(10), ForeignKey('users.student_id'), primary_key=True)


class CorrectionModel(db.Model):
    __tablename__ = 'correction' #เก็บคำผิด

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    incorrected_word = Column(String(255), nullable=False)  # คำที่ผิด
    corrected_word = Column(String(255), nullable=False)  # คำที่ถูก
    student_id = Column(String(10), ForeignKey('users.student_id'))  
    created_at = Column(DateTime, default=datetime.now)


    project_id = Column(String(10), ForeignKey('projects.id'))   

    count = Column(db.Integer, default=1)  
    last_date = Column(DateTime, onupdate=datetime.now)

    project = relationship('ProjectModel', backref='corrections')

    student = relationship('UserModel')  


# ตัวเสริม: property นี้สำหรับดึง keywords ของ Project
@property
def keywords_list(self):
    return self.keywords_rel
