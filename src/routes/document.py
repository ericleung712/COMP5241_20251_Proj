from flask import Blueprint, request, jsonify, session, redirect
from src.models.document import Document
from src.models.course import Course, course_enrollments
from src.models.user import User
from src.database import db
from datetime import datetime
import os
import uuid
from werkzeug.utils import secure_filename
from src.utils.supabase_storage import supabase, BUCKET_NAME

document_bp = Blueprint('document', __name__)

# 允许的文件类型
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 'txt', 'zip', 'rar'}
# 最大文件大小（50MB）
MAX_FILE_SIZE = 50 * 1024 * 1024

def require_auth():
    """验证用户是否已登录"""
    user_id = session.get('user_id')
    if not user_id:
        return None
    return User.query.get(user_id)

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@document_bp.route('/course/<int:course_id>', methods=['GET'])
def get_course_documents(course_id):
    """获取课程的所有文档（教师和学生）"""
    user = require_auth()
    if not user:
        return jsonify({'error': '未登录'}), 401
    
    course = Course.query.get_or_404(course_id)
    
    # 权限检查
    if user.role == 'teacher':
        if course.teacher_id != user.id:
            return jsonify({'error': '权限不足'}), 403
    elif user.role == 'student':
        # 检查学生是否注册了该课程
        enrollment = db.session.query(course_enrollments).filter(
            course_enrollments.c.course_id == course_id,
            course_enrollments.c.user_id == user.id
        ).first()
        if not enrollment:
            return jsonify({'error': '未注册该课程'}), 403
    else:
        return jsonify({'error': '权限不足'}), 403
    
    # 获取文档列表
    if user.role == 'teacher':
        # 教师可以看到所有文档（包括下架的）
        documents = Document.query.filter_by(course_id=course_id).order_by(Document.created_at.desc()).all()
    else:
        # 学生只能看到激活的文档
        documents = Document.query.filter_by(course_id=course_id, is_active=True).order_by(Document.created_at.desc()).all()
    
    return jsonify([doc.to_dict() for doc in documents])

@document_bp.route('/course/<int:course_id>', methods=['POST'])
def upload_document(course_id):
    """上传文档（仅教师）"""
    user = require_auth()
    if not user or user.role != 'teacher':
        return jsonify({'error': '权限不足'}), 403
    
    course = Course.query.get_or_404(course_id)
    if course.teacher_id != user.id:
        return jsonify({'error': '权限不足'}), 403
    
    # 检查是否有文件上传
    if 'file' not in request.files:
        return jsonify({'error': '没有上传文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '文件名为空'}), 400
    
    # 检查文件类型
    if not allowed_file(file.filename):
        return jsonify({'error': f'不支持的文件类型。支持的类型: {", ".join(ALLOWED_EXTENSIONS)}'}), 400
    
    try:
        # 读取文件内容检查大小
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({'error': f'文件大小超过限制（最大 {MAX_FILE_SIZE / (1024 * 1024)}MB）'}), 400
        
        # 生成唯一文件名
        file_ext = file.filename.rsplit('.', 1)[1].lower()
        stored_filename = f"{uuid.uuid4().hex}.{file_ext}"
        
        # 上传到Supabase
        supabase_path = f"{course_id}/{stored_filename}"
        file_data = file.read()  # Read file data
        
        try:
            bucket = supabase.storage.from_(BUCKET_NAME)
            response = bucket.upload(
                supabase_path, 
                file_data, 
                file_options={"content-type": f"application/{file_ext}"}
            )
        except Exception as upload_error:
            return jsonify({'error': f'上传到Supabase失败: {str(upload_error)}'}), 500
        
        # 获取标题和描述
        title = request.form.get('title', '').strip() or file.filename
        description = request.form.get('description', '').strip()
        
        # 创建文档记录
        document = Document(
            course_id=course_id,
            uploader_id=user.id,
            filename=secure_filename(file.filename),
            stored_filename=stored_filename,
            file_path=supabase_path,  # Store Supabase path
            file_size=file_size,
            file_type=file_ext,
            title=title,
            description=description,
            is_active=True
        )
        
        db.session.add(document)
        db.session.commit()
        
        return jsonify(document.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        # 如果文件已保存，删除它
        if 'file_path' in locals() and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass
        return jsonify({'error': f'上传失败: {str(e)}'}), 500

@document_bp.route('/<int:document_id>', methods=['GET'])
def get_document(document_id):
    """获取文档信息"""
    user = require_auth()
    if not user:
        return jsonify({'error': '未登录'}), 401
    
    document = Document.query.get_or_404(document_id)
    course = document.course
    
    # 权限检查
    if user.role == 'teacher':
        if course.teacher_id != user.id:
            return jsonify({'error': '权限不足'}), 403
    elif user.role == 'student':
        if not document.is_active:
            return jsonify({'error': '文档已下架'}), 403
        # 检查学生是否注册了该课程
        enrollment = db.session.query(course_enrollments).filter(
            course_enrollments.c.course_id == document.course_id,
            course_enrollments.c.user_id == user.id
        ).first()
        if not enrollment:
            return jsonify({'error': '未注册该课程'}), 403
    else:
        return jsonify({'error': '权限不足'}), 403
    
    return jsonify(document.to_dict())

@document_bp.route('/<int:document_id>/download', methods=['GET'])
def download_document(document_id):
    """下载文档"""
    user = require_auth()
    if not user:
        return jsonify({'error': '未登录'}), 401
    
    document = Document.query.get_or_404(document_id)
    course = document.course
    
    # 权限检查
    if user.role == 'teacher':
        if course.teacher_id != user.id:
            return jsonify({'error': '权限不足'}), 403
    elif user.role == 'student':
        if not document.is_active:
            return jsonify({'error': '文档已下架'}), 403
        # 检查学生是否注册了该课程
        enrollment = db.session.query(course_enrollments).filter(
            course_enrollments.c.course_id == document.course_id,
            course_enrollments.c.user_id == user.id
        ).first()
        if not enrollment:
            return jsonify({'error': '未注册该课程'}), 403
    else:
        return jsonify({'error': '权限不足'}), 403
    
    # 检查文件是否存在（通过Supabase）
    try:
        bucket = supabase.storage.from_(BUCKET_NAME)
        # Check if file exists
        bucket.info(document.file_path)
    except Exception:
        return jsonify({'error': '文件不存在'}), 404
    
    # 更新下载次数
    document.download_count += 1
    db.session.commit()
    
    # 生成签名URL
    try:
        signed_url_dict = bucket.create_signed_url(document.file_path, expires_in=3600)  # 1 hour expiry
        signed_url = signed_url_dict['signedURL']
        return redirect(signed_url)
    except Exception as e:
        return jsonify({'error': f'生成下载链接失败: {str(e)}'}), 500

@document_bp.route('/<int:document_id>', methods=['PUT'])
def update_document(document_id):
    """更新文档信息（仅教师）"""
    user = require_auth()
    if not user or user.role != 'teacher':
        return jsonify({'error': '权限不足'}), 403
    
    document = Document.query.get_or_404(document_id)
    course = document.course
    
    if course.teacher_id != user.id:
        return jsonify({'error': '权限不足'}), 403
    
    data = request.get_json()
    
    if 'title' in data:
        document.title = data['title'].strip()
    if 'description' in data:
        document.description = data['description'].strip()
    if 'is_active' in data:
        document.is_active = bool(data['is_active'])
    
    document.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify(document.to_dict())

@document_bp.route('/<int:document_id>', methods=['DELETE'])
def delete_document(document_id):
    """删除文档（仅教师）"""
    user = require_auth()
    if not user or user.role != 'teacher':
        return jsonify({'error': '权限不足'}), 403
    
    document = Document.query.get_or_404(document_id)
    course = document.course
    
    if course.teacher_id != user.id:
        return jsonify({'error': '权限不足'}), 403
    
    # 删除文件
    try:
        bucket = supabase.storage.from_(BUCKET_NAME)
        bucket.remove([document.file_path])
    except Exception as e:
        pass  # 即使文件删除失败，也继续删除数据库记录
    
    # 删除数据库记录
    db.session.delete(document)
    db.session.commit()
    
    return jsonify({'message': '文档已删除'}), 200

