from flask import Blueprint, request, jsonify, session
from src.models.course import Course, course_enrollments
from src.models.user import User
from src.database import db
from datetime import datetime
from src.utils.email_validator import validate_polyu_email
import pandas as pd
import io

course_bp = Blueprint('course', __name__)

def require_auth():
    """验证用户是否已登录"""
    user_id = session.get('user_id')
    if not user_id:
        return None
    return User.query.get(user_id)

@course_bp.route('/', methods=['GET'])
def get_courses():
    """获取课程列表"""
    user = require_auth()
    if not user:
        return jsonify({'error': '未登录'}), 401
    
    if user.role == 'teacher':
        # 教师查看自己教授的课程
        courses = Course.query.filter_by(teacher_id=user.id).all()
    elif user.role == 'student':
        # 学生查看自己注册的课程
        courses = Course.query.join(course_enrollments).filter(
            course_enrollments.c.user_id == user.id
        ).all()
    elif user.role == 'admin':
        # 管理员查看所有课程
        courses = Course.query.all()
    else:
        return jsonify({'error': '权限不足'}), 403
    
    return jsonify([course.to_dict() for course in courses])

@course_bp.route('/available', methods=['GET'])
def get_available_courses():
    """获取所有可用课程（供学生注册）"""
    user = require_auth()
    if not user:
        return jsonify({'error': '未登录'}), 401
    
    if user.role == 'student':
        # 学生查看所有活跃的课程
        courses = Course.query.filter_by(is_active=True).all()
        return jsonify([course.to_dict() for course in courses])
    else:
        return jsonify({'error': '权限不足'}), 403

@course_bp.route('/<int:course_id>', methods=['GET'])
def get_course(course_id):
    """获取特定课程详情"""
    user = require_auth()
    if not user:
        return jsonify({'error': '未登录'}), 401
    
    course = Course.query.get_or_404(course_id)
    
    # 权限检查
    if user.role == 'teacher' and course.teacher_id != user.id:
        return jsonify({'error': '权限不足'}), 403
    elif user.role == 'student':
        # 检查学生是否注册了该课程
        enrollment = db.session.query(course_enrollments).filter(
            course_enrollments.c.course_id == course_id,
            course_enrollments.c.user_id == user.id
        ).first()
        if not enrollment:
            return jsonify({'error': '未注册该课程'}), 403
    
    return jsonify(course.to_dict())

@course_bp.route('/', methods=['POST'])
def create_course():
    """创建新课程（仅教师）"""
    user = require_auth()
    if not user or user.role != 'teacher':
        return jsonify({'error': '权限不足'}), 403
    
    data = request.get_json()
    if not data or not all(k in data for k in ['course_code', 'course_name', 'semester', 'academic_year']):
        return jsonify({'error': '缺少必要字段'}), 400
    
    # 检查课程代码是否已存在
    if Course.query.filter_by(course_code=data['course_code']).first():
        return jsonify({'error': '课程代码已存在'}), 400
    
    course = Course(
        course_code=data['course_code'],
        course_name=data['course_name'],
        description=data.get('description', ''),
        teacher_id=user.id,
        semester=data['semester'],
        academic_year=data['academic_year']
    )
    
    db.session.add(course)
    db.session.commit()
    
    return jsonify({
        'message': '课程创建成功',
        'course': course.to_dict()
    }), 201

@course_bp.route('/<int:course_id>', methods=['PUT'])
def update_course(course_id):
    """更新课程信息（仅教师）"""
    user = require_auth()
    if not user or user.role != 'teacher':
        return jsonify({'error': '权限不足'}), 403
    
    course = Course.query.get_or_404(course_id)
    if course.teacher_id != user.id:
        return jsonify({'error': '权限不足'}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({'error': '没有提供数据'}), 400
    
    if 'course_name' in data:
        course.course_name = data['course_name']
    if 'description' in data:
        course.description = data['description']
    if 'semester' in data:
        course.semester = data['semester']
    if 'academic_year' in data:
        course.academic_year = data['academic_year']
    if 'is_active' in data:
        course.is_active = data['is_active']
    
    db.session.commit()
    
    return jsonify({
        'message': '课程更新成功',
        'course': course.to_dict()
    })

@course_bp.route('/<int:course_id>/enroll', methods=['POST'])
def enroll_student(course_id):
    """学生注册课程"""
    user = require_auth()
    if not user or user.role != 'student':
        return jsonify({'error': '权限不足'}), 403
    
    course = Course.query.get_or_404(course_id)
    if not course.is_active:
        return jsonify({'error': '课程未开放注册'}), 400
    
    # 检查是否已经注册
    enrollment = db.session.query(course_enrollments).filter(
        course_enrollments.c.course_id == course_id,
        course_enrollments.c.user_id == user.id
    ).first()
    
    if enrollment:
        return jsonify({'error': '已经注册该课程'}), 400
    
    # 添加注册记录
    db.session.execute(course_enrollments.insert().values(
        course_id=course_id,
        user_id=user.id,
        enrolled_at=datetime.utcnow()
    ))
    db.session.commit()
    
    return jsonify({'message': '注册成功'})

@course_bp.route('/<int:course_id>/enroll', methods=['DELETE'])
def unenroll_student(course_id):
    """学生取消注册课程"""
    user = require_auth()
    if not user or user.role != 'student':
        return jsonify({'error': '权限不足'}), 403
    
    # 删除注册记录
    db.session.execute(course_enrollments.delete().where(
        course_enrollments.c.course_id == course_id,
        course_enrollments.c.user_id == user.id
    ))
    db.session.commit()
    
    return jsonify({'message': '取消注册成功'})

@course_bp.route('/<int:course_id>/students', methods=['GET'])
def get_course_students(course_id):
    """获取课程学生列表（仅教师）"""
    user = require_auth()
    if not user or user.role != 'teacher':
        return jsonify({'error': '权限不足'}), 403
    
    course = Course.query.get_or_404(course_id)
    if course.teacher_id != user.id:
        return jsonify({'error': '权限不足'}), 403
    
    students = User.query.join(course_enrollments).filter(
        course_enrollments.c.course_id == course_id
    ).all()
    
    return jsonify([student.to_dict() for student in students])

@course_bp.route('/<int:course_id>/import-students', methods=['POST'])
def import_students(course_id):
    """批量导入学生（仅教师）"""
    user = require_auth()
    if not user or user.role != 'teacher':
        return jsonify({'error': '权限不足'}), 403
    
    course = Course.query.get_or_404(course_id)
    if course.teacher_id != user.id:
        return jsonify({'error': '权限不足'}), 403
    
    data = request.get_json()
    if not data or 'students' not in data:
        return jsonify({'error': '缺少学生数据'}), 400
    
    imported_count = 0
    errors = []
    
    for student_data in data['students']:
        if not all(k in student_data for k in ['student_id', 'full_name', 'email']):
            errors.append(f"学生数据不完整: {student_data}")
            continue
        
        # 检查学生是否已存在
        student = User.query.filter_by(student_id=student_data['student_id']).first()
        if not student:
            # 创建新学生账户
            student = User(
                username=student_data['student_id'],
                email=student_data['email'],
                full_name=student_data['full_name'],
                role='student',
                student_id=student_data['student_id'],
                department=student_data.get('department', '')
            )
            student.set_password(student_data.get('password', '123456'))  # 默认密码
            db.session.add(student)
            db.session.flush()  # 获取ID
        
        # 检查是否已经注册该课程
        enrollment = db.session.query(course_enrollments).filter(
            course_enrollments.c.course_id == course_id,
            course_enrollments.c.user_id == student.id
        ).first()
        
        if not enrollment:
            db.session.execute(course_enrollments.insert().values(
                course_id=course_id,
                user_id=student.id,
                enrolled_at=datetime.utcnow()
            ))
            imported_count += 1
    
    db.session.commit()
    
    return jsonify({
        'message': f'成功导入 {imported_count} 名学生',
        'imported_count': imported_count,
        'errors': errors
    })

@course_bp.route('/import-students-excel', methods=['POST'])
def import_students_excel():
    """通过Excel文件批量导入学生（仅教师）- 根据Excel中的course_code自动注册到对应课程"""
    user = require_auth()
    if not user or user.role != 'teacher':
        return jsonify({'error': '权限不足'}), 403
    
    # 检查是否有文件上传
    if 'file' not in request.files:
        return jsonify({'error': '没有上传文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '文件名为空'}), 400
    
    # 检查文件扩展名
    if not file.filename.endswith(('.xlsx', '.xls')):
        return jsonify({'error': '只支持Excel文件(.xlsx, .xls)'}), 400
    
    try:
        # 读取Excel文件
        file_content = file.read()
        df = pd.read_excel(io.BytesIO(file_content))
        
        # 检查必需的列
        required_columns = ['student_id', 'full_name', 'email']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return jsonify({
                'error': f'Excel文件缺少必需的列: {", ".join(missing_columns)}',
                'required_columns': required_columns,
                'found_columns': list(df.columns)
            }), 400
        
        imported_count = 0
        updated_count = 0
        skipped_count = 0
        enrolled_count = 0
        errors = []
        
        # 处理每一行数据
        for index, row in df.iterrows():
            try:
                # 获取学生信息
                student_id = str(row['student_id']).strip()
                full_name = str(row['full_name']).strip()
                email = str(row['email']).strip()
                department = str(row.get('department', '')).strip() if pd.notna(row.get('department')) else ''
                course_code = str(row.get('course_code', '')).strip() if pd.notna(row.get('course_code')) else ''
                
                # 验证必需字段
                if not student_id or not full_name or not email:
                    errors.append(f"第{index+2}行: 学生ID、姓名或邮箱为空")
                    skipped_count += 1
                    continue
                
                # 验证邮箱格式
                is_valid, error_msg = validate_polyu_email(email)
                if not is_valid:
                    errors.append(f"第{index+2}行: {error_msg} (邮箱: {email})")
                    skipped_count += 1
                    continue
                
                # 检查学生是否已存在
                student = User.query.filter_by(student_id=student_id).first()
                if not student:
                    # 检查用户名或邮箱是否已被使用
                    existing_user = User.query.filter(
                        (User.username == student_id) | (User.email == email)
                    ).first()
                    if existing_user:
                        errors.append(f"第{index+2}行: 用户名或邮箱已被使用 (学生ID: {student_id})")
                        skipped_count += 1
                        continue
                    
                    # 创建新学生账户
                    student = User(
                        username=student_id,
                        email=email,
                        full_name=full_name,
                        role='student',
                        student_id=student_id,
                        department=department
                    )
                    student.set_password('123456')  # 默认密码
                    db.session.add(student)
                    db.session.flush()  # 获取ID
                    imported_count += 1
                else:
                    # 更新现有学生信息（如果需要）
                    if student.full_name != full_name:
                        student.full_name = full_name
                    if student.email != email:
                        # 验证邮箱格式
                        is_valid, error_msg = validate_polyu_email(email)
                        if not is_valid:
                            errors.append(f"第{index+2}行: {error_msg} (邮箱: {email})")
                            skipped_count += 1
                            continue
                        # 检查新邮箱是否已被使用
                        existing_email = User.query.filter_by(email=email).first()
                        if existing_email and existing_email.id != student.id:
                            errors.append(f"第{index+2}行: 邮箱已被其他用户使用 (学生ID: {student_id})")
                            skipped_count += 1
                            continue
                        student.email = email
                    if department and student.department != department:
                        student.department = department
                    updated_count += 1
                
                # 如果Excel中有course_code，注册到对应课程
                if course_code:
                    course = Course.query.filter_by(course_code=course_code).first()
                    if course:
                        # 检查课程是否属于当前教师
                        if course.teacher_id != user.id:
                            errors.append(f"第{index+2}行: 课程 {course_code} 不属于当前教师")
                        else:
                            # 检查是否已经注册该课程
                            enrollment = db.session.query(course_enrollments).filter(
                                course_enrollments.c.course_id == course.id,
                                course_enrollments.c.user_id == student.id
                            ).first()
                            
                            if not enrollment:
                                db.session.execute(course_enrollments.insert().values(
                                    course_id=course.id,
                                    user_id=student.id,
                                    enrolled_at=datetime.utcnow()
                                ))
                                enrolled_count += 1
                    else:
                        errors.append(f"第{index+2}行: 课程代码 {course_code} 不存在")
                
            except Exception as e:
                errors.append(f"第{index+2}行: 处理失败 - {str(e)}")
                skipped_count += 1
                continue
        
        db.session.commit()
        
        return jsonify({
            'message': f'Excel导入完成',
            'imported_count': imported_count,
            'updated_count': updated_count,
            'enrolled_count': enrolled_count,
            'skipped_count': skipped_count,
            'total_rows': len(df),
            'errors': errors[:20]  # 只返回前20个错误
        })
        
    except pd.errors.EmptyDataError:
        return jsonify({'error': 'Excel文件为空'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'处理Excel文件时出错: {str(e)}'}), 500
