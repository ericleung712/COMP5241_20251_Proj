from flask import Blueprint, request, jsonify, session
from src.models.activity import Activity
from src.models.course import Course, course_enrollments
from src.models.user import User
from src.database import db
from src.ai.ai_service import AIService
from datetime import datetime
import os
from src.routes.ai_qa import extract_text_from_pdf, extract_text_from_docx, extract_text_from_txt, extract_document_content

activity_bp = Blueprint('activity', __name__)

def require_auth():
    """验证用户是否已登录"""
    user_id = session.get('user_id')
    if not user_id:
        return None
    return User.query.get(user_id)

@activity_bp.route('/', methods=['GET'])
def get_activities():
    """获取活动列表"""
    user = require_auth()
    if not user:
        return jsonify({'error': '未登录'}), 401
    
    course_id = request.args.get('course_id')
    activity_type = request.args.get('type')
    status = request.args.get('status')
    
    query = Activity.query
    
    if course_id:
        query = query.filter_by(course_id=course_id)
    
    if activity_type:
        query = query.filter_by(activity_type=activity_type)
    
    if status:
        query = query.filter_by(status=status)
    
    # 权限过滤
    if user.role == 'teacher':
        query = query.filter_by(creator_id=user.id)
    elif user.role == 'student':
        # 学生只能看到已注册课程的活动
        query = query.join(Course).join(Course.students).filter(
            User.id == user.id
        )
    
    activities = query.order_by(Activity.created_at.desc()).all()
    return jsonify([activity.to_dict() for activity in activities])

@activity_bp.route('/<int:activity_id>', methods=['GET'])
def get_activity(activity_id):
    """获取特定活动详情"""
    user = require_auth()
    if not user:
        return jsonify({'error': '未登录'}), 401
    
    activity = Activity.query.get_or_404(activity_id)
    
    # 权限检查
    if user.role == 'teacher' and activity.creator_id != user.id:
        return jsonify({'error': '权限不足'}), 403
    elif user.role == 'student':
        # 检查学生是否注册了该课程
        enrollment = db.session.query(course_enrollments).filter(
            course_enrollments.c.course_id == activity.course_id,
            course_enrollments.c.user_id == user.id
        ).first()
        if not enrollment:
            return jsonify({'error': '未注册该课程'}), 403
    
    return jsonify(activity.to_dict())

@activity_bp.route('/', methods=['POST'])
def create_activity():
    """创建新活动（仅教师）"""
    user = require_auth()
    if not user or user.role != 'teacher':
        return jsonify({'error': '权限不足'}), 403
    
    data = request.get_json()
    if not data or not all(k in data for k in ['title', 'activity_type', 'course_id']):
        return jsonify({'error': '缺少必要字段'}), 400
    
    # 验证课程权限
    course = Course.query.get_or_404(data['course_id'])
    if course.teacher_id != user.id:
        return jsonify({'error': '权限不足'}), 403
    
    activity = Activity(
        title=data['title'],
        description=data.get('description', ''),
        activity_type=data['activity_type'],
        course_id=data['course_id'],
        creator_id=user.id,
        duration_minutes=data.get('duration_minutes', 10),
        is_ai_generated=data.get('is_ai_generated', False)
    )
    
    # 设置活动配置
    if 'config' in data:
        activity.set_config(data['config'])
    
    db.session.add(activity)
    db.session.commit()
    
    return jsonify({
        'message': '活动创建成功',
        'activity': activity.to_dict()
    }), 201

@activity_bp.route('/<int:activity_id>', methods=['PUT'])
def update_activity(activity_id):
    """更新活动（仅教师）"""
    user = require_auth()
    if not user or user.role != 'teacher':
        return jsonify({'error': '权限不足'}), 403
    
    activity = Activity.query.get_or_404(activity_id)
    if activity.creator_id != user.id:
        return jsonify({'error': '权限不足'}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({'error': '没有提供数据'}), 400
    
    if 'title' in data:
        activity.title = data['title']
    if 'description' in data:
        activity.description = data['description']
    if 'config' in data:
        activity.set_config(data['config'])
    if 'duration_minutes' in data:
        activity.duration_minutes = data['duration_minutes']
    if 'status' in data:
        activity.status = data['status']
    
    db.session.commit()
    
    return jsonify({
        'message': '活动更新成功',
        'activity': activity.to_dict()
    })

@activity_bp.route('/<int:activity_id>', methods=['DELETE'])
def delete_activity(activity_id):
    """删除活动（仅教师）"""
    user = require_auth()
    if not user or user.role != 'teacher':
        return jsonify({'error': '权限不足'}), 403
    
    activity = Activity.query.get_or_404(activity_id)
    if activity.creator_id != user.id:
        return jsonify({'error': '权限不足'}), 403
    
    db.session.delete(activity)
    db.session.commit()
    
    return jsonify({'message': '活动删除成功'})

@activity_bp.route('/<int:activity_id>/start', methods=['POST'])
def start_activity(activity_id):
    """开始活动（仅教师）"""
    user = require_auth()
    if not user or user.role != 'teacher':
        return jsonify({'error': '权限不足'}), 403
    
    activity = Activity.query.get_or_404(activity_id)
    if activity.creator_id != user.id:
        return jsonify({'error': '权限不足'}), 403
    
    activity.status = 'active'
    activity.start_time = datetime.utcnow()
    
    if activity.duration_minutes:
        from datetime import timedelta
        activity.end_time = activity.start_time + timedelta(minutes=activity.duration_minutes)
    
    db.session.commit()
    
    return jsonify({
        'message': '活动已开始',
        'activity': activity.to_dict()
    })

@activity_bp.route('/<int:activity_id>/stop', methods=['POST'])
def stop_activity(activity_id):
    """结束活动（仅教师）"""
    user = require_auth()
    if not user or user.role != 'teacher':
        return jsonify({'error': '权限不足'}), 403
    
    activity = Activity.query.get_or_404(activity_id)
    if activity.creator_id != user.id:
        return jsonify({'error': '权限不足'}), 403
    
    activity.status = 'completed'
    activity.end_time = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'message': '活动已结束',
        'activity': activity.to_dict()
    })

@activity_bp.route('/ai/generate', methods=['POST'])
def generate_ai_activity():
    """AI生成活动（仅教师）"""
    user = require_auth()
    if not user or user.role != 'teacher':
        return jsonify({'error': '权限不足'}), 403
    
    data = request.get_json()
    if not data or not all(k in data for k in ['activity_type', 'course_content']):
        return jsonify({'error': '缺少必要字段'}), 400
    
    # 验证课程权限
    course_id = data.get('course_id')
    if course_id:
        course = Course.query.get_or_404(course_id)
        if course.teacher_id != user.id:
            return jsonify({'error': '权限不足'}), 403
    
    # 处理选中的文档
    document_ids = data.get('document_ids', [])
    document_content = ""
    if document_ids:
        from src.models.document import Document
        
        for doc_id in document_ids:
            document = Document.query.get(doc_id)
            if document and document.course_id == course_id and document.is_active:
                content = extract_document_content(document)
                if content:
                    document_content += f"\n\n文档：{document.title or document.filename}\n{content}"
    
    # 合并文档内容到课程内容
    full_course_content = data['course_content']
    if document_content:
        full_course_content += "\n\n--- 从上传文档提取的内容 ---\n" + document_content
    
    # 使用AI服务生成活动
    ai_service = AIService()
    generated_activity = ai_service.generate_activity(
        activity_type=data['activity_type'],
        course_content=full_course_content,
        web_resources=data.get('web_resources', ''),
        additional_prompt=data.get('additional_prompt', ''),
        time_limit=data.get('time_limit')
    )
    
    if 'error' in generated_activity:
        return jsonify(generated_activity), 500
    
    return jsonify({
        'message': 'AI活动生成成功',
        'generated_activity': generated_activity
    })

@activity_bp.route('/<int:activity_id>/ai-refine', methods=['POST'])
def refine_ai_activity(activity_id):
    """AI优化活动（仅教师）"""
    user = require_auth()
    if not user or user.role != 'teacher':
        return jsonify({'error': '权限不足'}), 403
    
    activity = Activity.query.get_or_404(activity_id)
    if activity.creator_id != user.id:
        return jsonify({'error': '权限不足'}), 403
    
    data = request.get_json()
    if not data or 'refinement_prompt' not in data:
        return jsonify({'error': '缺少优化提示'}), 400
    
    # 使用AI服务优化活动
    ai_service = AIService()
    refined_activity = ai_service.generate_activity(
        activity_type=activity.activity_type,
        course_content=data['refinement_prompt'],
        additional_prompt=f"请优化以下活动: {activity.title} - {activity.description}"
    )
    
    if 'error' in refined_activity:
        return jsonify(refined_activity), 500
    
    # 更新活动为AI优化状态
    activity.ai_refined = True
    activity.ai_prompt = data['refinement_prompt']
    db.session.commit()
    
    return jsonify({
        'message': 'AI活动优化成功',
        'refined_activity': refined_activity,
        'activity': activity.to_dict()
    })

@activity_bp.route('/types', methods=['GET'])
def get_activity_types():
    """获取支持的活动类型"""
    activity_types = [
        {
            'type': 'poll',
            'name': '投票活动',
            'description': '创建投票问题，收集学生意见',
            'icon': '📊'
        },
        {
            'type': 'quiz',
            'name': '测验活动',
            'description': '创建选择题测验，测试学生知识',
            'icon': '❓'
        },
        {
            'type': 'word_cloud',
            'name': '词云活动',
            'description': '收集关键词，生成词云',
            'icon': '☁️'
        },
        {
            'type': 'short_answer',
            'name': '简答题',
            'description': '创建开放性问题，收集详细回答',
            'icon': '✍️'
        },
        {
            'type': 'mini_game',
            'name': '迷你游戏',
            'description': '创建互动小游戏，增加学习趣味',
            'icon': '🎮'
        }
    ]
    
    return jsonify(activity_types)
