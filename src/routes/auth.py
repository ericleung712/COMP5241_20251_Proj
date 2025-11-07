from flask import Blueprint, request, jsonify, session
from src.models.user import User
from src.database import db
from datetime import datetime
from src.utils.email_validator import validate_polyu_email

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.get_json()
    
    if not data or not all(k in data for k in ['username', 'email', 'password', 'full_name', 'role']):
        return jsonify({'error': '缺少必要字段'}), 400
    
    # 验证邮箱格式
    is_valid, error_msg = validate_polyu_email(data['email'])
    if not is_valid:
        return jsonify({'error': error_msg}), 400
    
    # 检查用户名和邮箱是否已存在
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': '用户名已存在'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': '邮箱已存在'}), 400
    
    # 验证角色
    if data['role'] not in ['teacher', 'student', 'admin']:
        return jsonify({'error': '无效的用户角色'}), 400
    
    # 创建新用户
    user = User(
        username=data['username'],
        email=data['email'],
        full_name=data['full_name'],
        role=data['role'],
        student_id=data.get('student_id'),
        department=data.get('department')
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'message': '注册成功',
        'user': user.to_dict()
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()
    
    if not data or not all(k in data for k in ['username', 'password']):
        return jsonify({'error': '缺少用户名或密码'}), 400
    
    user = User.query.filter_by(username=data['username']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'error': '用户名或密码错误'}), 401
    
    # 更新最后登录时间
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    # 设置会话
    session['user_id'] = user.id
    session['username'] = user.username
    session['role'] = user.role
    
    return jsonify({
        'message': '登录成功',
        'user': user.to_dict()
    })

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """用户登出"""
    session.clear()
    return jsonify({'message': '登出成功'})

@auth_bp.route('/profile', methods=['GET'])
def get_profile():
    """获取当前用户信息"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': '未登录'}), 401
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    return jsonify(user.to_dict())

@auth_bp.route('/profile', methods=['PUT'])
def update_profile():
    """更新用户信息"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': '未登录'}), 401
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({'error': '没有提供数据'}), 400
    
    # 更新允许的字段
    if 'full_name' in data:
        user.full_name = data['full_name']
    if 'email' in data:
        # 验证邮箱格式
        is_valid, error_msg = validate_polyu_email(data['email'])
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        user.email = data['email']
    if 'department' in data:
        user.department = data['department']
    if 'student_id' in data:
        user.student_id = data['student_id']
    
    db.session.commit()
    
    return jsonify({
        'message': '信息更新成功',
        'user': user.to_dict()
    })

@auth_bp.route('/change-password', methods=['POST'])
def change_password():
    """修改密码"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': '未登录'}), 401
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    data = request.get_json()
    if not data or not all(k in data for k in ['old_password', 'new_password']):
        return jsonify({'error': '缺少必要字段'}), 400
    
    if not user.check_password(data['old_password']):
        return jsonify({'error': '原密码错误'}), 401
    
    user.set_password(data['new_password'])
    db.session.commit()
    
    return jsonify({'message': '密码修改成功'})
