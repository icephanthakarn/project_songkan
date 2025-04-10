from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, flash
from sqlalchemy import or_, and_, func,cast, Integer
from sqlalchemy.orm import aliased
from werkzeug.utils import secure_filename
import os
from models import db, ProjectModel, UserModel, PdfFileModel, KeywordModel, ProjectKeywordModel,ProjectStudentModel,CorrectionLogModel
from ocr_logic import process_pdf_to_data
from werkzeug.security import check_password_hash, generate_password_hash  # <- ถ้าต้องการใช้ generate_password_hash
from flask_migrate import Migrate
import random
from pdf2image import convert_from_path
import math
import re
from ocr_logic import correct_word, process_pdf_to_data

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# === Settings ===
UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydb.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)


def get_page_range(current_page, total_pages):
    if total_pages <= 5:
        return list(range(1, total_pages + 1))
    
    if current_page <= 3:
        return [1, 2, 3, 4, '...', total_pages]
    elif current_page >= total_pages - 2:
        return [1, '...', total_pages - 3, total_pages - 2, total_pages - 1, total_pages]
    else:
        return [1, '...', current_page - 1, current_page, current_page + 1, '...', total_pages]

def extract_name(full_name):
    prefixes = ['นาย', 'นางสาว', 'นาง']
    for prefix in prefixes:
        if full_name.startswith(prefix):
            return full_name[len(prefix):].strip()
    return full_name.strip()

# === Index page ===
@app.route('/')
def index():
    query = request.args.get('q', '')
    year = request.args.get('year', '')
    faculty = request.args.get('faculty', '')
    department = request.args.get('department', '')
    sort_by = request.args.get('sort_by', 'default')

    projects_query = ProjectModel.query

    # เงื่อนไขค้นหา
    if query:
        keywords = query.strip().split()
        for kw in keywords:
            keyword_condition = or_(
                ProjectModel.title_th.contains(kw),
                ProjectModel.author.contains(kw),
                ProjectModel.keywords.contains(kw)
            )
            projects_query = projects_query.filter(keyword_condition)

    # เงื่อนไขกรอง
    if year:
        projects_query = projects_query.filter_by(academic_year=year)
    if faculty:
        projects_query = projects_query.filter_by(faculty=faculty)
    if department:
        if department in ['คณิตศาสตร์', 'คณิตศาสตร์ประยุกต์']:
            projects_query = projects_query.filter(
                or_(
                    ProjectModel.department == 'คณิตศาสตร์',
                    ProjectModel.department == 'คณิตศาสตร์ประยุกต์'
                )
            )
        else:
            projects_query = projects_query.filter_by(department=department)

    # เงื่อนไขการเรียงลำดับ
    if sort_by == 'title_asc':
        projects_query = projects_query.order_by(
            ProjectModel.academic_year.desc(),
            ProjectModel.title_th.asc()
        )
    elif sort_by == 'title_desc':
        projects_query = projects_query.order_by(
            ProjectModel.academic_year.desc(),
            ProjectModel.title_th.desc()
        )
    elif sort_by == 'year_desc':
        projects_query = projects_query.order_by(
            ProjectModel.academic_year.desc(),
            ProjectModel.title_th.asc()
        )
    elif sort_by == 'year_asc':
        projects_query = projects_query.order_by(
            ProjectModel.academic_year.asc(),
            ProjectModel.title_th.asc()
        )


    else:
        # 🟢 Default
        projects_query = projects_query.order_by(
            ProjectModel.academic_year.desc(),
            ProjectModel.title_th.asc()
        )

    projects = projects_query.all()

    # แบ่งหน้า
    page = request.args.get('page', 1, type=int)
    per_page = 8

    total_projects = projects_query.count()
    total_pages = math.ceil(total_projects / per_page)

    projects = projects_query.offset((page - 1) * per_page).limit(per_page).all()


    # สร้าง range สำหรับ pagination
    page_range = get_page_range(page, total_pages)

    return render_template('index.html',
                           projects=projects,
                           total_pages=total_pages,
                           current_page=page,
                           page_range=page_range,
                           total_projects=total_projects)
                           
# === Login ===
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = UserModel.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user'] = {
                'student_id': user.student_id,
                'name': user.student_name,
                'role': user.role
            }
            return redirect(url_for('admin_page') if user.role == 'admin' else url_for('index'))
        else:
            error = 'อีเมลหรือรหัสผ่านไม่ถูกต้อง'  # ❗ ไม่ใช้ flash แล้ว
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# === Upload PDF + OCR ===
@app.route('/upload', methods=['GET', 'POST'])
def upload_project():
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))

    if request.method == 'POST':
        uploaded_file = request.files['pdf_file']
        if uploaded_file:
            filename = secure_filename(uploaded_file.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            uploaded_file.save(save_path)
            session['uploaded_filename'] = filename
            session['uploaded_file_path'] = save_path
            ocr_data = process_pdf_to_data(save_path)


            for key in ocr_data:
                if isinstance(ocr_data[key], str):
                    ocr_data[key] = correct_word(ocr_data[key])

    
            return render_template('upload.html', uploaded_filename=filename, ocr_data=ocr_data)

    return redirect(url_for('profile'))

# === Submit project info and save to DB ===
@app.route('/submit-info', methods=['POST'])
def fill_project_info():
    file_path = session.get('uploaded_file_path')
    user_info = session.get('user')
    user = UserModel.query.get(user_info['student_id']) if user_info else None

    pdf_filename = session['uploaded_filename']
    pdf_full_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename)

    department = request.form['department'].strip()

    # ✅ รายการภาควิชาที่อนุญาต
    all_departments = [
        'วิทยาการคอมพิวเตอร์',
        'ชีววิทยา',
        'ฟิสิกส์',
        'เคมี',
        'คณิตศาสตร์',
        'สถิติ'
    ]

    department_error = None
    if not department:
        department_error = 'กรุณากรอกชื่อภาควิชา'
    elif department not in all_departments:
        department_error = (
            'ไม่พบภาควิชานี้ กรุณากรอกตามรายการ: ' + ', '.join(all_departments)
        )

    if department_error:
        return render_template(
            'upload.html',
            ocr_data=session.get('ocr_data'),
            uploaded_filename=session.get('uploaded_filename'),
            department_error=department_error,
            request=request
        )

    # ✅ 1. สร้าง ProjectModel
    project = ProjectModel(
        title_th=request.form['title'],
        title_en=request.form['alt_title'],
        author=request.form['author'] or user.student_name,
        abstract_th=request.form['abstract'],
        abstract_en=request.form['abstract_en'],
        faculty=request.form['faculty'],
        department=department,
        academic_year=request.form.get('academic_year', ''),
        advisor=request.form['advisor'],
        keywords=request.form['keywords'],
        file_path=os.path.join('static', 'uploads', pdf_filename)
    )
    db.session.add(project)
    db.session.commit()

    # ✅ 2. สร้าง thumbnail จากหน้าแรก PDF
    pages = convert_from_path(pdf_full_path, 200)
    if pages:
        thumb_filename = pdf_filename.rsplit('.', 1)[0] + "_thumb.jpg"
        thumb_full_path = os.path.join(app.config['UPLOAD_FOLDER'], thumb_filename)
        pages[0].save(thumb_full_path, 'JPEG')

        thumbnail_path = os.path.join('uploads', thumb_filename).replace('\\', '/')
        project.thumbnail_path = thumbnail_path
        db.session.commit()

    # ✅ 3. สร้างความสัมพันธ์ต่างๆ

    # 3.1 ProjectStudent
    if user:
        db.session.add(ProjectStudentModel(project_id=project.id, student_id=user.student_id))

    # 3.2 PdfFile
    db.session.add(PdfFileModel(
        file_name=pdf_filename,
        file_path=project.file_path,
        project_id=project.id
    ))

    # 3.3 Keywords (เช็ค keyword ซ้ำ)
    keyword_list = list(set([kw.strip() for kw in request.form['keywords'].split(',') if kw.strip()]))

    for kw in keyword_list:
        keyword_obj = KeywordModel.query.filter_by(keyword_text=kw).first()
        if not keyword_obj:
            keyword_obj = KeywordModel(keyword_text=kw)
            db.session.add(keyword_obj)
            db.session.flush()

        existing_relation = ProjectKeywordModel.query.filter_by(
            project_id=project.id,
            keyword_id=keyword_obj.id
        ).first()

        if not existing_relation:
            db.session.add(ProjectKeywordModel(
                project_id=project.id,
                keyword_id=keyword_obj.id
            ))

    db.session.commit()

    # ✅ ล้าง session upload
    session['user_project'] = {
        'title': project.title_th,
        'alt_title': project.title_en,
        'year': project.academic_year,
        'faculty': project.faculty,
        'department': project.department
    }
    session.pop('uploaded_file_path', None)
    session.pop('uploaded_filename', None)

    return redirect(url_for('profile'))

# === Profile Page ===
@app.route('/profile')
def profile():
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))

    is_admin = user.get('role') == 'admin'

    if is_admin:
        admin_projects = ProjectModel.query.all()
        return render_template('profile.html',
                               user_name="Admin",
                               student_id=user['student_id'],
                               faculty="Admin",
                               department="Admin",
                               user_role='admin',
                               admin_projects=admin_projects)
    else:
        # ✅ ดึงข้อมูลนักศึกษาจาก DB
        student = UserModel.query.get(user['student_id'])

        student_project_link = ProjectStudentModel.query.filter_by(student_id=student.student_id).first()
        project = ProjectModel.query.get(student_project_link.project_id) if student_project_link else None

        return render_template('profile.html',
                               user_name=student.student_name,
                               student_id=student.student_id,
                               faculty=student.faculty,
                               student_major=student.student_major,
                               user_role='student',
                               user_project=project,
                               project=project)

# === Project Detail ===
@app.route('/project/<string:project_id>')
def project_detail(project_id):
    project = ProjectModel.query.get_or_404(project_id)
    return render_template('project_detail.html', project=project)


@app.route('/download/<string:project_id>')
def download_file(project_id):
    project = ProjectModel.query.get_or_404(project_id)
    if project and project.file_path:
        file_path = os.path.join(app.root_path, project.file_path.replace('\\', '/'))

        if os.path.exists(file_path):
            return send_from_directory(
                directory=os.path.dirname(file_path),
                path=os.path.basename(file_path),
                as_attachment=True
            )
        else:
            return "File not found", 404
    return "Thesis or file path not found", 404


@app.route('/delete-project', methods=['POST'])
def delete_project():
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))

    user_in_db = UserModel.query.get(user['student_id'])

    # ลบเฉพาะโปรเจกต์ที่เป็นของ user หรือถ้า user เป็น admin
    project = ProjectModel.query.filter_by(author=user['name']).first()

    # สมมติเราอนุญาตให้ admin ลบได้หมด
    if user_in_db.role == 'admin':
        # ดึงโปรเจกต์จาก request.form หรือดูเองว่าจะใช้แบบไหน
        project_id = request.form.get('project_id', None)
        if project_id:
            project = ProjectModel.query.get(project_id)
    else:
        # ถ้าไม่ใช่ admin ใช้เงื่อนไขเดิม
        student_project_link = ProjectStudentModel.query.filter_by(student_id=user['student_id']).first()
        project = None
        if student_project_link:
            project = ProjectModel.query.get(student_project_link.project_id)


    if project:
        # ลบ record
        db.session.delete(project)
        db.session.commit()

    session.pop('user_project', None)
    return redirect(url_for('profile'))



@app.route('/edit/<string:project_id>', methods=['GET', 'POST'])
def edit_project(project_id):
    project = ProjectModel.query.get_or_404(project_id)

    if request.method == 'POST':
        project.title_th = request.form['title']
        project.title_en = request.form['alt_title']
        project.author = request.form['author']
        project.abstract_th = request.form['abstract']
        project.faculty = request.form['faculty']
        project.department = request.form['department']
        project.academic_year = request.form['academic_year']
        project.advisor = request.form['advisor']
        project.keywords = request.form['keywords']
        db.session.commit()
        return redirect(url_for('profile'))

    return render_template('edit_project.html', project=project)

def is_admin():
    user_session = session.get('user')
    if not user_session:
        return False
    user_in_db = UserModel.query.get(user_session['student_id'])  # ✅ ใช้ตัวแปรที่ประกาศไว้
    if user_in_db and user_in_db.role == 'admin':
        return True
    return False




@app.route('/admin', methods=['GET'])
def admin_page():
    if not is_admin():
        flash("คุณไม่มีสิทธิ์เข้าถึงหน้านี้")
        return redirect(url_for('index'))

    # 🔍 รับค่าจาก query string
    query = request.args.get('q', '')
    year = request.args.get('year', '')
    faculty = request.args.get('faculty', '')
    department = request.args.get('department', '')

    # 🔎 เริ่ม query ทั้งหมด
    projects_query = ProjectModel.query

    # 🔍 ค้นหาด้วยคำ
    if query:
        keywords = query.strip().split()
        for kw in keywords:
            keyword_condition = or_(
                ProjectModel.title_th.contains(kw),
                ProjectModel.author.contains(kw),
                ProjectModel.keywords.contains(kw)
            )
            projects_query = projects_query.filter(keyword_condition)

    # 🗂 filter ปี / คณะ / ภาค
    if year:
        projects_query = projects_query.filter_by(academic_year=year)
    if faculty:
        projects_query = projects_query.filter_by(faculty=faculty)
    if department:
        if department in ['คณิตศาสตร์', 'คณิตศาสตร์ประยุกต์']:
            projects_query = projects_query.filter(
                or_(
                    ProjectModel.department == 'คณิตศาสตร์',
                    ProjectModel.department == 'คณิตศาสตร์ประยุกต์'
                )
            )
        else:
            projects_query = projects_query.filter_by(department=department)

    # ✅ เรียงจากรายการที่เพิ่มล่าสุดก่อน (id มาก → น้อย)
    filtered_projects = projects_query.order_by(ProjectModel.id.desc()).all()

    # 🗂 สร้าง year list สำหรับ filter sidebar
    year_list = sorted(
        list({p.academic_year for p in filtered_projects if p.academic_year}),
        reverse=True
    )

    return render_template('admin.html', projects=filtered_projects, year_list=year_list)



# ส่วน Admin: ลบโปรเจกต์ใด ๆ ก็ตาม
@app.route('/admin/delete-project/<string:project_id>', methods=['POST'])
def admin_delete_project(project_id):
    if not is_admin():
        flash("คุณไม่มีสิทธิ์เข้าถึงฟังก์ชันนี้")
        return redirect(url_for('index'))
    
    project = ProjectModel.query.get_or_404(project_id)
    # ลบไฟล์จริงในโฟลเดอร์ (ถ้าต้องการ)
    if project.file_path:
        file_full_path = os.path.join(app.root_path, project.file_path)
        if os.path.exists(file_full_path):
            os.remove(file_full_path)
    # ลบข้อมูลใน DB
    db.session.delete(project)
    db.session.commit()
    flash(f"ลบโปรเจกต์ #{project_id} เรียบร้อยแล้ว")
    return redirect(url_for('admin_page'))


@app.route('/create_admin')
def create_admin():
    admin_user = UserModel(
        student_id="admin001",  
        email="admin@example.com",
        password=generate_password_hash("admin123"),
        role="admin",
        student_name="System Administrator"
    )
    db.session.add(admin_user)
    db.session.commit()
    return "Admin created!"

#จัดการนักศึกษา
@app.route('/admin/students')
def admin_student_page():
    if not is_admin():
        flash("คุณไม่มีสิทธิ์เข้าถึงหน้านี้")
        return redirect(url_for('index'))

    query = request.args.get('q', '')
    faculty = request.args.get('faculty', '')
    department = request.args.get('department', '')

    students_query = UserModel.query.filter_by(role='student')

    # 🔍 ค้นหาชื่อ / email / รหัส
    if query:
        q = f"%{query}%"
        students_query = students_query.filter(
            or_(
                UserModel.student_id.ilike(q),
                UserModel.student_name.ilike(q),
                UserModel.email.ilike(q)
            )
        )

    # 🏫 กรองคณะ
    if faculty:
        students_query = students_query.filter_by(faculty=faculty)

    # 🧪 กรองภาควิชา → ใช้ student_major
    if department:
        students_query = students_query.filter_by(student_major=department)

    students = students_query.order_by(UserModel.student_id.asc()).all()
    return render_template('admin_students.html', students=students)


@app.route('/admin/student/<string:student_id>/edit')
def edit_student(student_id):
    student = UserModel.query.get_or_404(student_id)
    return render_template('edit_student.html', student=student)

@app.route('/admin/student/<string:student_id>/update', methods=['POST'])
def update_student(student_id):
    student = UserModel.query.get_or_404(student_id)
    student.student_name = request.form['student_name']
    student.email = request.form['email']
    student.faculty = request.form['faculty']
    student.student_major = request.form['student_major']
    db.session.commit()

    # ✅ อัปเดต session ด้วย ถ้ากำลัง login อยู่
    if session.get('user') and session['user']['student_id'] == student.student_id:
        session['user']['name'] = student.student_name
        session['user']['faculty'] = student.faculty
        session['user']['student_major'] = student.student_major  # หรือ department เดิมที่ใช้


    flash('อัปเดตข้อมูลนักเรียนเรียบร้อยแล้ว')
    return redirect(url_for('admin_student_page'))

# === Context Processor ===
@app.context_processor
def inject_user():
    user = session.get('user')
    if user and 'student_id' in user:
        user_in_db = db.session.get(UserModel, user['student_id'])
        first_letter = user.get('name', 'U')[0].upper()
        colors = ['#ea5c0d', '#e67e22', '#16a085', '#2980b9', '#8e44ad']
        avatar_color = colors[hash(user['student_id']) % len(colors)]
        user_is_admin = (user_in_db.role == 'admin') if user_in_db else False

        return dict(
            user_logged_in=True,
            student_id=user['student_id'],
            first_letter=first_letter,
            avatar_color=avatar_color,
            user_is_admin=user_is_admin
        )
    return dict(user_logged_in=False)


@app.route('/replace', methods=['POST'])
def replace_word():
    original = request.form['original_word']
    corrected = request.form['corrected_word']
    field = request.form['field_name']  # แนะนำให้ส่งมาจาก hidden input ในฟอร์มด้วย
    student_id = session['user']['student_id']

    # 👉 ทำการแก้ไขฟอร์ม OCR
    ocr_data = session.get('ocr_data', {})
    if field in ocr_data and original in ocr_data[field]:
        ocr_data[field] = ocr_data[field].replace(original, corrected)
        session['ocr_data'] = ocr_data

    # 👉 บันทึก Log การแก้ไขคำ
    correction = CorrectionLogModel(
        original_word=original,
        corrected_word=corrected,
        field_name=field,
        student_id=student_id
    )
    db.session.add(correction)
    db.session.commit()

    return redirect(url_for('upload_project'))

@app.route('/log_correction', methods=['POST'])
def log_correction():
    data = request.get_json()
    original = data.get('wrong_word')   # รับค่าที่ส่งเข้ามาในฟิลด์ wrong_word
    correct = data.get('correct_word')

    if original and correct:
        student_id = session['user']['student_id']  # ดึง student_id จาก session
        log = CorrectionLogModel(
            original_word=original,
            corrected_word=correct,
            field_name=data.get('field_name'),  # ถ้ามีส่ง field_name มาด้วย
            student_id=student_id
        )
        db.session.add(log)
        db.session.commit()
        return {'status': 'ok'}

    return {'status': 'error'}, 400

if __name__ == '__main__':
    app.run(debug=True)