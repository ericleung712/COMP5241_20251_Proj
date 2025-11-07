from flask import Blueprint, request, jsonify, session
from src.models.response import ActivityResponse
from src.models.activity import Activity
from src.models.user import User
from src.database import db
from src.ai.ai_service import AIService
from datetime import datetime

response_bp = Blueprint('response', __name__)

def require_auth():
    """验证用户是否已登录"""
    user_id = session.get('user_id')
    if not user_id:
        return None
    return User.query.get(user_id)

@response_bp.route('/', methods=['POST'])
def submit_response():
    """提交活动响应（仅学生）"""
    user = require_auth()
    if not user or user.role != 'student':
        return jsonify({'error': '权限不足'}), 403
    
    data = request.get_json()
    if not data or not all(k in data for k in ['activity_id', 'response_data']):
        return jsonify({'error': '缺少必要字段'}), 400
    
    activity = Activity.query.get_or_404(data['activity_id'])
    
    # 检查活动状态
    if activity.status != 'active':
        return jsonify({'error': '活动未激活'}), 400
    
    # 检查是否已经提交过
    existing_response = ActivityResponse.query.filter_by(
        activity_id=data['activity_id'],
        student_id=user.id
    ).first()
    
    if existing_response:
        return jsonify({'error': '已经提交过回答'}), 400
    
    # 创建响应
    response = ActivityResponse(
        activity_id=data['activity_id'],
        student_id=user.id,
        time_spent_seconds=data.get('time_spent_seconds')
    )
    response.set_response_data(data['response_data'])
    
    db.session.add(response)
    db.session.commit()
    
    return jsonify({
        'message': '回答提交成功',
        'response': response.to_dict()
    }), 201

@response_bp.route('/<int:response_id>', methods=['GET'])
def get_response(response_id):
    """获取特定响应"""
    user = require_auth()
    if not user:
        return jsonify({'error': '未登录'}), 401
    
    response = ActivityResponse.query.get_or_404(response_id)
    
    # 权限检查
    if user.role == 'student' and response.student_id != user.id:
        return jsonify({'error': '权限不足'}), 403
    elif user.role == 'teacher' and response.activity.creator_id != user.id:
        return jsonify({'error': '权限不足'}), 403
    
    return jsonify(response.to_dict())

@response_bp.route('/activity/<int:activity_id>', methods=['GET'])
def get_activity_responses(activity_id):
    """获取活动的所有响应（教师）或自己的响应（学生）"""
    user = require_auth()
    if not user:
        return jsonify({'error': '未登录'}), 401
    
    activity = Activity.query.get_or_404(activity_id)
    
    if user.role == 'teacher':
        # 教师可以查看所有响应
        if activity.creator_id != user.id:
            return jsonify({'error': '权限不足'}), 403
        responses = ActivityResponse.query.filter_by(activity_id=activity_id).all()
        return jsonify([response.to_dict() for response in responses])
    elif user.role == 'student':
        # 学生只能查看自己的响应
        response = ActivityResponse.query.filter_by(
            activity_id=activity_id,
            student_id=user.id
        ).first()
        if not response:
            return jsonify({'error': '未找到响应'}), 404
        return jsonify([response.to_dict()])
    else:
        return jsonify({'error': '权限不足'}), 403

@response_bp.route('/<int:response_id>/feedback', methods=['POST'])
def add_feedback(response_id):
    """添加反馈（仅教师）"""
    user = require_auth()
    if not user or user.role != 'teacher':
        return jsonify({'error': '权限不足'}), 403
    
    response = ActivityResponse.query.get_or_404(response_id)
    if response.activity.creator_id != user.id:
        return jsonify({'error': '权限不足'}), 403
    
    data = request.get_json()
    if not data or 'feedback' not in data:
        return jsonify({'error': '缺少反馈内容'}), 400
    
    response.feedback = data['feedback']
    if 'score' in data:
        response.score = data['score']
    
    db.session.commit()
    
    return jsonify({
        'message': '反馈添加成功',
        'response': response.to_dict()
    })

@response_bp.route('/ai/analyze/<int:activity_id>', methods=['POST'])
def analyze_responses(activity_id):
    """AI分析活动响应（仅教师）"""
    user = require_auth()
    if not user or user.role != 'teacher':
        return jsonify({'error': '权限不足'}), 403
    
    activity = Activity.query.get_or_404(activity_id)
    if activity.creator_id != user.id:
        return jsonify({'error': '权限不足'}), 403
    
    responses = ActivityResponse.query.filter_by(activity_id=activity_id).all()
    if not responses:
        return jsonify({'error': '没有响应数据'}), 400
    
    # 准备响应数据
    response_data = []
    for resp in responses:
        resp_dict = resp.get_response_data()
        resp_dict['student_name'] = resp.student.full_name
        response_data.append(resp_dict)
    
    # 使用AI服务分析
    ai_service = AIService()
    analysis = ai_service.analyze_responses(response_data, activity.activity_type)
    
    if 'error' in analysis:
        return jsonify(analysis), 500
    
    return jsonify({
        'message': 'AI分析完成',
        'analysis': analysis,
        'activity_id': activity_id
    })

@response_bp.route('/ai/group-similar/<int:activity_id>', methods=['POST'])
def group_similar_responses(activity_id):
    """AI分组相似响应（仅教师）"""
    user = require_auth()
    if not user or user.role != 'teacher':
        return jsonify({'error': '权限不足'}), 403
    
    activity = Activity.query.get_or_404(activity_id)
    if activity.creator_id != user.id:
        return jsonify({'error': '权限不足'}), 403
    
    responses = ActivityResponse.query.filter_by(activity_id=activity_id).all()
    if not responses:
        return jsonify({'error': '没有响应数据'}), 400
    
    # 准备响应数据
    response_data = []
    for resp in responses:
        resp_dict = resp.get_response_data()
        resp_dict['student_name'] = resp.student.full_name
        resp_dict['response_id'] = resp.id
        response_data.append(resp_dict)
    
    # 使用AI服务分组
    ai_service = AIService()
    groups = ai_service.group_similar_answers(response_data)
    
    return jsonify({
        'message': 'AI分组完成',
        'groups': groups,
        'activity_id': activity_id
    })

@response_bp.route('/ai/feedback/<int:response_id>', methods=['POST'])
def generate_ai_feedback(response_id):
    """AI生成个性化反馈（仅教师）"""
    user = require_auth()
    if not user or user.role != 'teacher':
        return jsonify({'error': '权限不足'}), 403
    
    response = ActivityResponse.query.get_or_404(response_id)
    if response.activity.creator_id != user.id:
        return jsonify({'error': '权限不足'}), 403
    
    data = request.get_json()
    student_response = data.get('student_response', '')
    correct_answer = data.get('correct_answer', '')
    
    if not student_response:
        return jsonify({'error': '缺少学生回答'}), 400
    
    # 使用AI服务生成反馈
    ai_service = AIService()
    feedback = ai_service.generate_feedback(
        student_response=student_response,
        correct_answer=correct_answer,
        activity_type=response.activity.activity_type
    )
    
    return jsonify({
        'message': 'AI反馈生成成功',
        'feedback': feedback,
        'response_id': response_id
    })
