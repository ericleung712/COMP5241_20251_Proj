from flask import Blueprint, request, jsonify, session
from src.models.course import Course, course_enrollments
from src.models.document import Document
from src.models.activity import Activity
from src.models.user import User
from src.database import db
from src.ai.ai_service import AIService
import os
import PyPDF2
import docx

ai_qa_bp = Blueprint('ai_qa', __name__)
ai_service = AIService()

def require_auth():
    """验证用户是否已登录"""
    user_id = session.get('user_id')
    if not user_id:
        return None
    return User.query.get(user_id)

def extract_text_from_pdf(file_path):
    """从PDF文件提取文本"""
    try:
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"无法读取PDF文件: {str(e)}"

def extract_text_from_docx(file_path):
    """从DOCX文件提取文本"""
    try:
        doc = docx.Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except Exception as e:
        return f"无法读取DOCX文件: {str(e)}"

def extract_text_from_txt(file_path):
    """从TXT文件提取文本"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        return f"无法读取TXT文件: {str(e)}"

def extract_document_content(document):
    """提取文档内容"""
    if not os.path.exists(document.file_path):
        return None
    
    file_ext = document.file_type.lower()
    content = None
    
    if file_ext == 'pdf':
        content = extract_text_from_pdf(document.file_path)
    elif file_ext in ['docx', 'doc']:
        content = extract_text_from_docx(document.file_path)
    elif file_ext == 'txt':
        content = extract_text_from_txt(document.file_path)
    else:
        # 对于其他格式，返回基本信息
        content = f"文档：{document.title or document.filename}\n描述：{document.description or '无描述'}"
    
    return content

@ai_qa_bp.route('/course/<int:course_id>/ask', methods=['POST'])
def ask_question(course_id):
    """向AI提问关于课程的问题"""
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
    
    data = request.get_json()
    question = data.get('question', '').strip()
    
    if not question:
        return jsonify({'error': '问题不能为空'}), 400
    
    try:
        # 获取课程信息
        course_info = {
            'course_name': course.course_name,
            'course_code': course.course_code,
            'description': course.description
        }
        
        # 获取课程文档（仅已上架的文档）
        documents_query = Document.query.filter_by(course_id=course_id, is_active=True)
        if user.role == 'student':
            # 学生只能看到已上架的文档
            documents = documents_query.all()
        else:
            # 教师可以看到所有文档
            documents = documents_query.all()
        
        # 提取文档内容
        documents_data = []
        for doc in documents:
            content = extract_document_content(doc)
            documents_data.append({
                'id': doc.id,
                'title': doc.title or doc.filename,
                'filename': doc.filename,
                'description': doc.description,
                'content': content
            })
        
        # 获取课程活动
        activities = Activity.query.filter_by(course_id=course_id).all()
        activities_data = []
        for activity in activities:
            activities_data.append({
                'id': activity.id,
                'title': activity.title,
                'description': activity.description,
                'activity_type': activity.activity_type,
                'config': activity.get_config(),
                'status': activity.status
            })
        
        # 构建上下文
        course_context = {
            'course_info': course_info,
            'documents': documents_data,
            'activities': activities_data
        }
        
        # 调用AI服务回答问题
        answer = ai_service.answer_question(question, course_context)
        
        return jsonify({
            'answer': answer,
            'question': question,
            'course_id': course_id,
            'course_name': course.course_name
        })
        
    except Exception as e:
        return jsonify({'error': f'处理问题失败: {str(e)}'}), 500

@ai_qa_bp.route('/general/ask', methods=['POST'])
def ask_general_question():
    """向通用AI助手提问"""
    user = require_auth()
    if not user:
        return jsonify({'error': '未登录'}), 401
    
    data = request.get_json()
    question = data.get('question', '').strip()
    
    if not question:
        return jsonify({'error': '问题不能为空'}), 400
    
    try:
        # 获取用户的课程列表
        user_courses = []
        if user.role == 'teacher':
            courses = Course.query.filter_by(teacher_id=user.id).all()
            user_courses = [{'course_name': c.course_name, 'course_code': c.course_code, 'id': c.id} for c in courses]
        elif user.role == 'student':
            # 获取学生注册的课程
            enrollments = db.session.query(course_enrollments).filter(
                course_enrollments.c.user_id == user.id
            ).all()
            course_ids = [e.course_id for e in enrollments]
            courses = Course.query.filter(Course.id.in_(course_ids)).all()
            user_courses = [{'course_name': c.course_name, 'course_code': c.course_code, 'id': c.id} for c in courses]
        
        # 调用AI服务回答问题
        answer = ai_service.answer_general_question(question, user_courses)
        
        return jsonify({
            'answer': answer,
            'question': question
        })
        
    except Exception as e:
        return jsonify({'error': f'处理问题失败: {str(e)}'}), 500

